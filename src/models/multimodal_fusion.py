"""Tabular/text fusion heads for the Phase 2 ablation."""

from __future__ import annotations

import torch
from torch import Tensor, nn


class CrossAttentionFusion(nn.Module):
    """Tabular CLS queries non-padding text tokens, then uses a residual gate."""

    def __init__(self, d_token: int = 128, num_classes: int = 4, n_heads: int = 4,
                 dropout: float = 0.1) -> None:
        super().__init__()
        if d_token % n_heads or num_classes < 2:
            raise ValueError("Invalid attention width or class count")
        self.attention = nn.MultiheadAttention(d_token, n_heads, dropout=dropout, batch_first=True)
        self.gate = nn.Linear(2 * d_token, d_token)
        self.norm = nn.LayerNorm(d_token)
        self.head = nn.Linear(d_token, num_classes)

    def forward(self, tab_tokens: Tensor, text_tokens: Tensor, attention_mask: Tensor,
                *, tabular_present: Tensor | None = None,
                text_present: Tensor | None = None) -> Tensor:
        if tab_tokens.ndim != 3 or text_tokens.ndim != 3 or tab_tokens.shape[0] != text_tokens.shape[0]:
            raise ValueError("Expected [batch, tokens, width] for both modalities")
        if tab_tokens.shape[2] != self.head.in_features or text_tokens.shape[2] != self.head.in_features:
            raise ValueError("Modality widths must match d_token")
        if attention_mask.shape != text_tokens.shape[:2]:
            raise ValueError("attention_mask must match text token dimensions")
        batch = tab_tokens.shape[0]
        if tabular_present is None:
            tabular_present = torch.ones(batch, dtype=torch.bool, device=tab_tokens.device)
        if text_present is None:
            text_present = attention_mask.bool().any(dim=1)
        if tabular_present.shape != (batch,) or text_present.shape != (batch,):
            raise ValueError("Presence flags must have shape [batch]")
        if not torch.all(tabular_present | text_present):
            raise ValueError("At least one modality is required per row")
        valid = attention_mask.bool() & text_present[:, None]
        # MultiheadAttention cannot process a row with every key masked.
        safe_valid = valid.clone()
        safe_valid[~safe_valid.any(dim=1), 0] = True
        tab_cls = tab_tokens[:, :1]
        cross, _ = self.attention(tab_cls, text_tokens, text_tokens,
                                  key_padding_mask=~safe_valid, need_weights=False)
        tab_cls = tab_cls.squeeze(1)
        cross = cross.squeeze(1)
        gate = torch.sigmoid(self.gate(torch.cat([tab_cls, cross], dim=-1)))
        fused = gate * tab_cls + (1 - gate) * cross
        text_mean = (text_tokens * valid.unsqueeze(-1)).sum(1) / valid.sum(1).clamp_min(1).unsqueeze(-1)
        fused = torch.where(text_present[:, None], fused, tab_cls)
        fused = torch.where(tabular_present[:, None], fused, text_mean)
        return self.head(self.norm(fused))


class ConcatFusion(nn.Module):
    """Parameter-matched simple late-fusion comparator."""

    def __init__(self, d_token: int = 128, num_classes: int = 4, dropout: float = 0.1) -> None:
        super().__init__()
        self.head = nn.Sequential(nn.LayerNorm(2 * d_token), nn.Dropout(dropout),
                                  nn.Linear(2 * d_token, num_classes))

    def forward(self, tab_tokens: Tensor, text_tokens: Tensor, attention_mask: Tensor) -> Tensor:
        valid = attention_mask.bool()
        mean = (text_tokens * valid.unsqueeze(-1)).sum(1) / valid.sum(1).clamp_min(1).unsqueeze(-1)
        return self.head(torch.cat([tab_tokens[:, 0], mean], dim=-1))


class AblationModel(nn.Module):
    """Shared feature encoders with one of four explicit classification heads."""

    MODES = ("tabular", "text", "concat", "cross_attention")

    def __init__(self, mode: str, *, text_width: int = 768, d_token: int = 128,
                 num_classes: int = 4, n_blocks: int = 4, n_heads: int = 4,
                 dropout: float = 0.1) -> None:
        super().__init__()
        if mode not in self.MODES:
            raise ValueError(f"mode must be one of {self.MODES}")
        from src.models.tabular_encoder import FTTransformerEncoder

        self.mode = mode
        self.tabular = FTTransformerEncoder(d_token=d_token, n_blocks=n_blocks,
                                            n_heads=n_heads, dropout=dropout) if mode != "text" else None
        self.text_projection = nn.Linear(text_width, d_token) if mode != "tabular" else None
        if mode in ("tabular", "text"):
            self.head = nn.Sequential(nn.LayerNorm(d_token), nn.Linear(d_token, num_classes))
        elif mode == "concat":
            self.head = ConcatFusion(d_token, num_classes, dropout)
        else:
            self.head = CrossAttentionFusion(d_token, num_classes, n_heads, dropout)

    def forward(self, numerical: Tensor, categorical: Tensor, text_hidden: Tensor,
                attention_mask: Tensor) -> Tensor:
        tab = self.tabular(numerical, categorical) if self.tabular is not None else None
        text = self.text_projection(text_hidden.float()) if self.text_projection is not None else None
        if self.mode == "tabular":
            return self.head(tab[:, 0])
        if self.mode == "text":
            valid = attention_mask.bool()
            pooled = (text * valid.unsqueeze(-1)).sum(1) / valid.sum(1).clamp_min(1).unsqueeze(-1)
            return self.head(pooled)
        return self.head(tab, text, attention_mask)
