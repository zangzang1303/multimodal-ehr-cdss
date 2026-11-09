# ==============================================================================
# [MOCK / STAND-IN FILE - DÙNG TẠM THỜI CHO THÀNH VIÊN 3 KIỂM THỬ]
# File này (bao gồm DummyClinicalBackbone mock offline) được tạo tạm thời bởi
# Thành viên 3 để chạy tests/test_multimodal_model.py (Backlog 04 - Nhiệm vụ 3.2)
# trong lúc chờ Thành viên 2 hoàn thiện ClinicalTextEncoder nạp Bio_ClinicalBERT
# thực tế (Backlog 04 - Nhiệm vụ 2.1).
# ==============================================================================
"""
Clinical Text Encoder Module
Multimodal EHR CDSS - Phase 2 / Backlog 04 (Member 2 / Member 3 Deliverable)

Implements:
- ClinicalTextEncoder: Wraps Biomedical BERT (Bio_ClinicalBERT / BioLinkBERT)
  and projects text representations from d_text (768) to multimodal dimension d (128).

Mathematical Specification:
docs/02_MULTIMODAL_ARCHITECTURE_AND_MATH.md Section 3
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Optional
import torch
from torch import Tensor, nn


class DummyClinicalBackbone(nn.Module):
    """
    Lightweight dummy transformer backbone for offline testing and fast CI execution.
    Outputs [Batch, Seq_len, hidden_size].
    """

    def __init__(self, vocab_size: int = 1000, hidden_size: int = 768) -> None:
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, hidden_size)
        self.proj = nn.Linear(hidden_size, hidden_size)

    def forward(
        self,
        input_ids: Tensor,
        attention_mask: Optional[Tensor] = None,
        **kwargs,
    ) -> SimpleNamespace:
        out = self.proj(self.embedding(input_ids))
        if attention_mask is not None:
            out = out * attention_mask.unsqueeze(-1).float()
        return SimpleNamespace(last_hidden_state=out)


class ClinicalTextEncoder(nn.Module):
    """
    Biomedical Clinical Text Encoder.

    Extracts contextual subword embeddings T_text in R^[Batch, S+2, 768]
    and projects them via W_proj to multimodal embedding space H_text in R^[Batch, S+2, 128].
    """

    def __init__(
        self,
        model_name: str = "emilyalsentzer/Bio_ClinicalBERT",
        embed_dim: int = 128,
        max_length: int = 256,
        dropout_rate: float = 0.1,
        *,
        backbone: Optional[nn.Module] = None,
        local_files_only: bool = False,
    ) -> None:
        super().__init__()
        self.model_name = model_name
        self.embed_dim = embed_dim
        self.max_length = max_length

        if backbone is not None:
            self.backbone = backbone
            d_text = getattr(backbone, "hidden_size", 768)
        else:
            try:
                from transformers import AutoModel
                self.backbone = AutoModel.from_pretrained(
                    model_name,
                    local_files_only=local_files_only,
                )
                d_text = getattr(self.backbone.config, "hidden_size", 768)
            except Exception:
                # Fallback to dummy backbone if offline or transformers model not cached
                self.backbone = DummyClinicalBackbone(hidden_size=768)
                d_text = 768

        # Linear projection W_proj from d_text (768) -> d (128)
        self.proj = nn.Linear(d_text, embed_dim)
        self.layer_norm = nn.LayerNorm(embed_dim)
        self.dropout = nn.Dropout(dropout_rate)

    def forward(
        self,
        input_ids: Tensor,
        attention_mask: Optional[Tensor] = None,
    ) -> Tensor:
        """
        Extract and project contextual tokens.

        Args:
            input_ids: Tensor of token ids with shape [Batch, S+2].
            attention_mask: Optional binary mask of shape [Batch, S+2].

        Returns:
            H_text: Projected contextual representations of shape [Batch, S+2, embed_dim].
        """
        outputs = self.backbone(input_ids=input_ids, attention_mask=attention_mask)
        if hasattr(outputs, "last_hidden_state"):
            t_text = outputs.last_hidden_state
        elif isinstance(outputs, tuple):
            t_text = outputs[0]
        else:
            t_text = outputs

        # Project: [Batch, S+2, 768] -> [Batch, S+2, 128]
        h_text = self.proj(t_text)
        h_text = self.layer_norm(h_text)
        h_text = self.dropout(h_text)

        if attention_mask is not None:
            h_text = h_text * attention_mask.unsqueeze(-1).float()

        return h_text
