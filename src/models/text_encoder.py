

from __future__ import annotations

from typing import Any, Sequence
import torch
from torch import Tensor, nn


DEFAULT_TEXT_MODEL = "emilyalsentzer/Bio_ClinicalBERT"


class ClinicalTextEncoder(nn.Module):
   

    def __init__(
        self,
        model_name: str = DEFAULT_TEXT_MODEL,
        d_token: int = 128,
        max_length: int = 512,
        *,
        backbone: nn.Module | None = None,
        freeze_backbone: bool = False,
        local_files_only: bool = False,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        self.model_name = model_name
        self.d_token = d_token
        self.max_length = max_length
        self.freeze_backbone = freeze_backbone
        self._tokenizer = None

        if backbone is None:
            from transformers import AutoConfig, AutoModel

            try:
                backbone = AutoModel.from_pretrained(
                    model_name, local_files_only=local_files_only
                )
            except OSError:
                config = AutoConfig.from_pretrained(
                    model_name, local_files_only=local_files_only
                )
                backbone = AutoModel.from_config(config)
        self.backbone = backbone

        if freeze_backbone:
            for parameter in self.backbone.parameters():
                parameter.requires_grad_(False)

        config_hidden = getattr(getattr(self.backbone, "config", None), "hidden_size", None)
        self.d_text = int(config_hidden) if isinstance(config_hidden, int) else 768

        self.proj = nn.Linear(self.d_text, d_token)
        self.norm = nn.LayerNorm(d_token)
        self.dropout = nn.Dropout(dropout)

    def forward(
        self,
        input_ids: Tensor,
        attention_mask: Tensor | None = None,
    ) -> Tensor:
       
        if input_ids.ndim != 2:
            raise ValueError("input_ids must have shape [batch_size, seq_len]")
        if attention_mask is not None and attention_mask.shape != input_ids.shape:
            raise ValueError("attention_mask must match input_ids dimensions")

        outputs = self.backbone(input_ids=input_ids, attention_mask=attention_mask)
        last_hidden = getattr(outputs, "last_hidden_state", None)
        if last_hidden is None and isinstance(outputs, (tuple, list)):
            last_hidden = outputs[0]
        if last_hidden is None and isinstance(outputs, Tensor):
            last_hidden = outputs
        if last_hidden is None:
            raise RuntimeError("Transformer backbone did not return valid hidden states")

        projected = self.proj(last_hidden.float())
        h_text = self.dropout(self.norm(projected))
        return h_text

    def get_tokenizer(self, local_files_only: bool = False):
        if self._tokenizer is None:
            from transformers import AutoTokenizer

            self._tokenizer = AutoTokenizer.from_pretrained(
                self.model_name, local_files_only=local_files_only
            )
        return self._tokenizer

    def tokenize(
        self,
        texts: Sequence[str] | str,
        max_length: int | None = None,
        local_files_only: bool = False,
    ) -> dict[str, Tensor]:
        tokenizer = self.get_tokenizer(local_files_only=local_files_only)
        limit = max_length or self.max_length
        return tokenizer(
            texts if isinstance(texts, list) else [texts],
            padding="max_length",
            truncation=True,
            max_length=limit,
            return_tensors="pt",
        )

