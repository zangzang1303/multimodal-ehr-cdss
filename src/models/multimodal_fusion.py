# ==============================================================================
# [MOCK / STAND-IN FILE - DÙNG TẠM THỜI CHO THÀNH VIÊN 3 KIỂM THỬ]
# File này được tạo tạm thời bởi Thành viên 3 để chạy tests/test_multimodal_model.py
# (Backlog 04 - Nhiệm vụ 3.2) trong lúc chờ Thành viên 1 hoàn thiện mạng
# CrossAttentionFusion và huấn luyện trọng số thực tế (Backlog 04 - Nhiệm vụ 1.2).
# ==============================================================================
"""
Cross-Attention Late Fusion Module
Multimodal EHR CDSS - Phase 2 / Backlog 04 (Member 1 / Member 3 Deliverable)

Implements:
- CrossAttentionFusion: Multi-head cross-attention layer mapping Tabular Queries to Text Keys/Values,
  combined with an adaptive Gated Residual Fusion mechanism and 4-class Classification Head.

Mathematical Specification:
docs/02_MULTIMODAL_ARCHITECTURE_AND_MATH.md Section 4
"""

from __future__ import annotations

from typing import Optional, Tuple
import torch
from torch import Tensor, nn


class CrossAttentionFusion(nn.Module):
    """
    Cross-Attention Late Fusion Layer between Tabular Stream and Text Stream.

    Tabular Stream (Query): H_tab in R^[Batch, M+1, d]
    Text Stream (Key/Value): H_text in R^[Batch, S+2, d]

    Fusion Mechanism:
    1. Cross-Attention: A = softmax(Q_tab K_text^T / sqrt(d)) V_text
    2. Adaptive Gating: g = sigmoid(W_g [h_tab^cls || h_cross^cls] + b_g)
    3. Fused Representation: h_fused = g * h_tab^cls + (1 - g) * h_cross^cls
    4. Classification: logits = Linear(h_fused) -> R^4
    """

    def __init__(
        self,
        embed_dim: int = 128,
        num_heads: int = 4,
        num_classes: int = 4,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        if embed_dim % num_heads != 0:
            raise ValueError(f"embed_dim ({embed_dim}) must be divisible by num_heads ({num_heads})")

        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.num_classes = num_classes

        # Multi-Head Cross Attention
        self.cross_attn = nn.MultiheadAttention(
            embed_dim=embed_dim,
            num_heads=num_heads,
            dropout=dropout,
            batch_first=True,
        )
        self.layer_norm_q = nn.LayerNorm(embed_dim)
        self.layer_norm_kv = nn.LayerNorm(embed_dim)

        # Gated fusion projection: g = sigmoid(W * [h_tab; h_cross] + b)
        self.gate_proj = nn.Sequential(
            nn.Linear(embed_dim * 2, embed_dim),
            nn.Sigmoid(),
        )
        self.dropout = nn.Dropout(dropout)
        self.post_norm = nn.LayerNorm(embed_dim)

        # Classification Head: h_fused -> K logits (ASTHMA, COPD, HEART_FAILURE, PNEUMONIA)
        self.classifier = nn.Linear(embed_dim, num_classes)

        self.reset_parameters()

    def reset_parameters(self) -> None:
        """Initialize linear layers with Xavier uniform."""
        nn.init.xavier_uniform_(self.classifier.weight)
        nn.init.zeros_(self.classifier.bias)

    def forward(
        self,
        h_tab: Tensor,
        h_text: Tensor,
        text_padding_mask: Optional[Tensor] = None,
        return_features: bool = False,
    ) -> Tuple[Tensor, Tensor] | Tuple[Tensor, Tensor, Tensor]:
        """
        Execute forward pass of Cross-Attention Late Fusion.

        Args:
            h_tab: Tabular representation [Batch, M+1, embed_dim].
            h_text: Text representation [Batch, S+2, embed_dim].
            text_padding_mask: Optional binary padding mask [Batch, S+2] (True for padding positions).
            return_features: Whether to also return the intermediate h_fused representation.

        Returns:
            logits: Classification logits [Batch, num_classes].
            attn_weights: Cross-attention weights [Batch, M+1, S+2].
            (Optional) h_fused: Fused feature representation [Batch, embed_dim].
        """
        if h_tab.ndim != 3 or h_tab.shape[-1] != self.embed_dim:
            raise ValueError(
                f"Expected h_tab of shape [Batch, M+1, {self.embed_dim}], got {tuple(h_tab.shape)}"
            )
        if h_text.ndim != 3 or h_text.shape[-1] != self.embed_dim:
            raise ValueError(
                f"Expected h_text of shape [Batch, S+2, {self.embed_dim}], got {tuple(h_text.shape)}"
            )

        q = self.layer_norm_q(h_tab)
        kv = self.layer_norm_kv(h_text)

        # Multi-Head Cross Attention: Query = Tabular, Key/Value = Text
        attn_out, attn_weights = self.cross_attn(
            query=q,
            key=kv,
            value=kv,
            key_padding_mask=text_padding_mask,
        )

        # Extract representations at [CLS] token position (index 0)
        h_tab_cls = h_tab[:, 0, :]        # [Batch, embed_dim]
        h_cross_cls = attn_out[:, 0, :]   # [Batch, embed_dim]

        # Compute dynamic gating weights: g in (0, 1)^d
        concat_cls = torch.cat([h_tab_cls, h_cross_cls], dim=-1)  # [Batch, 2 * embed_dim]
        gate = self.gate_proj(concat_cls)                         # [Batch, embed_dim]

        # Residual Gated Fusion
        h_fused = gate * h_tab_cls + (1.0 - gate) * h_cross_cls   # [Batch, embed_dim]
        h_fused = self.post_norm(self.dropout(h_fused))

        # Project to 4 diagnostic logits
        logits = self.classifier(h_fused)                         # [Batch, num_classes]

        if return_features:
            return logits, attn_weights, h_fused
        return logits, attn_weights
