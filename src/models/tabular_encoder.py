"""Feature-token transformer for structured EHR inputs."""

from __future__ import annotations

from collections.abc import Sequence

import torch
from torch import Tensor, nn


class TabularTokenizer(nn.Module):
    """Make one token per numerical/categorical feature, preceded by CLS."""

    def __init__(
        self, n_numerical: int = 9, categorical_cardinalities: Sequence[int] = (3, 3, 2, 2),
        d_token: int = 128,
    ) -> None:
        super().__init__()
        if n_numerical < 0 or any(size < 1 for size in categorical_cardinalities):
            raise ValueError("Feature counts and cardinalities must be non-negative")
        if n_numerical + len(categorical_cardinalities) == 0 or d_token < 1:
            raise ValueError("At least one feature and a positive token width are required")
        self.n_numerical = n_numerical
        self.categorical_cardinalities = tuple(categorical_cardinalities)
        self.d_token = d_token
        self.n_tokens = 1 + n_numerical + len(self.categorical_cardinalities)
        self.numeric_weight = nn.Parameter(torch.empty(n_numerical, d_token))
        self.numeric_bias = nn.Parameter(torch.zeros(n_numerical, d_token))
        # Index zero is reserved for missing/unknown; observed categories start at one.
        self.embeddings = nn.ModuleList(
            nn.Embedding(size + 1, d_token, padding_idx=0)
            for size in self.categorical_cardinalities
        )
        self.cls = nn.Parameter(torch.empty(1, 1, d_token))
        nn.init.xavier_uniform_(self.numeric_weight)
        nn.init.normal_(self.cls, std=0.02)

    def forward(self, numerical: Tensor, categorical: Tensor) -> Tensor:
        if numerical.ndim != 2 or numerical.shape[1] != self.n_numerical:
            raise ValueError(f"numerical must have shape [batch, {self.n_numerical}]")
        if categorical.ndim != 2 or categorical.shape != (numerical.shape[0], len(self.embeddings)):
            raise ValueError(f"categorical must have shape [batch, {len(self.embeddings)}]")
        if not torch.isfinite(numerical).all():
            raise ValueError("Numerical features must be finite")
        batch = numerical.shape[0]
        pieces = [self.cls.expand(batch, -1, -1)]
        if self.n_numerical:
            pieces.append(numerical.float().unsqueeze(-1) * self.numeric_weight + self.numeric_bias)
        for column, embedding in enumerate(self.embeddings):
            values = categorical[:, column].long()
            if (values < 0).any() or (values >= embedding.num_embeddings).any():
                raise ValueError(f"Categorical feature {column} has an out-of-range index")
            pieces.append(embedding(values).unsqueeze(1))
        return torch.cat(pieces, dim=1)


class FTTransformerEncoder(nn.Module):
    """Four-block transformer returning all feature tokens for fusion."""

    def __init__(
        self, n_numerical: int = 9, categorical_cardinalities: Sequence[int] = (3, 3, 2, 2),
        d_token: int = 128, n_blocks: int = 4, n_heads: int = 4,
        ffn_hidden: int = 256, dropout: float = 0.1,
    ) -> None:
        super().__init__()
        if n_blocks < 1 or n_heads < 1 or d_token % n_heads:
            raise ValueError("n_blocks/n_heads must be positive and d_token divisible by n_heads")
        self.tokenizer = TabularTokenizer(n_numerical, categorical_cardinalities, d_token)
        layer = nn.TransformerEncoderLayer(
            d_model=d_token, nhead=n_heads, dim_feedforward=ffn_hidden,
            dropout=dropout, activation="gelu", batch_first=True, norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(layer, num_layers=n_blocks)
        self.norm = nn.LayerNorm(d_token)

    def forward(self, numerical: Tensor, categorical: Tensor) -> Tensor:
        return self.norm(self.encoder(self.tokenizer(numerical, categorical)))
