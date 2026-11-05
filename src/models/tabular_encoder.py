"""
FT-Transformer Tabular Encoder Module
Multimodal EHR CDSS - Phase 2 / Backlog 04 (Member 1 / Member 3 Deliverable)

Implements:
- TabularTokenizer: Feature Tokenization for continuous and categorical EHR variables.
- FTTransformerEncoder: Transformer Encoder layers for high-order feature interactions.

Mathematical Specification:
docs/02_MULTIMODAL_ARCHITECTURE_AND_MATH.md
Gorishniy et al., "Revisiting Deep Learning Models for Tabular Data", NeurIPS 2021.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence
import torch
from torch import Tensor, nn


# Standard feature ordering aligned with data contracts
DEFAULT_NUMERICAL_FEATURES: List[str] = [
    "age",
    "systolic_bp",
    "diastolic_bp",
    "heart_rate",
    "respiratory_rate",
    "spo2",
    "temperature",
    "wbc_count",
    "crp",
]

DEFAULT_CATEGORICAL_FEATURES: List[str] = [
    "gender",
    "smoking_status",
    "history_hypertension",
    "history_diabetes",
]

# Cardinality mapping for categorical features
# gender: M, F, OTHER (3)
# smoking_status: NEVER, FORMER, CURRENT (3)
# history_hypertension: 0, 1 (2)
# history_diabetes: 0, 1 (2)
DEFAULT_CATEGORICAL_CARDINALITIES: Dict[str, int] = {
    "gender": 4,  # include unknown / buffer
    "smoking_status": 4,
    "history_hypertension": 2,
    "history_diabetes": 2,
}


class TabularTokenizer(nn.Module):
    """
    Feature Tokenizer Layer for Tabular EHR Data.
    
    Transforms M_num continuous features and M_cat categorical features
    into continuous embedding vectors of dimension d, prepended with a learnable [CLS] token.
    
    Output Tensor shape: [Batch, M + 1, d] where M = M_num + M_cat.
    """

    def __init__(
        self,
        n_numerical: int = len(DEFAULT_NUMERICAL_FEATURES),
        categorical_cardinalities: Optional[Sequence[int]] = None,
        embed_dim: int = 128,
        bias: bool = True,
    ) -> None:
        super().__init__()
        self.n_numerical = n_numerical
        self.embed_dim = embed_dim

        if categorical_cardinalities is None:
            categorical_cardinalities = list(DEFAULT_CATEGORICAL_CARDINALITIES.values())
        self.categorical_cardinalities = list(categorical_cardinalities)
        self.n_categorical = len(self.categorical_cardinalities)
        self.n_total_features = self.n_numerical + self.n_categorical

        # Linear projection parameters for each numerical feature: e_j = x_j * w_j + b_j
        self.num_weights = nn.Parameter(torch.empty(self.n_numerical, embed_dim))
        self.num_biases = nn.Parameter(torch.empty(self.n_numerical, embed_dim)) if bias else None

        # Lookup embeddings for categorical features
        self.cat_embeddings = nn.ModuleList([
            nn.Embedding(cardinality, embed_dim)
            for cardinality in self.categorical_cardinalities
        ])
        if bias:
            self.cat_biases = nn.Parameter(torch.empty(self.n_categorical, embed_dim))
        else:
            self.cat_biases = None

        # Learnable [CLS] token embedding
        self.cls_token = nn.Parameter(torch.empty(1, 1, embed_dim))

        self.reset_parameters()

    def reset_parameters(self) -> None:
        """Initialize parameters using Xavier uniform and normal distribution."""
        nn.init.xavier_uniform_(self.num_weights)
        if self.num_biases is not None:
            nn.init.zeros_(self.num_biases)
        if self.cat_biases is not None:
            nn.init.zeros_(self.cat_biases)
        for emb in self.cat_embeddings:
            nn.init.normal_(emb.weight, std=0.02)
        nn.init.normal_(self.cls_token, std=0.02)

    def forward(
        self,
        x_num: Tensor,
        x_cat: Optional[Tensor] = None,
    ) -> Tensor:
        """
        Tokenize continuous and categorical tabular tensors.

        Args:
            x_num: Continuous features tensor of shape [Batch, M_num].
            x_cat: Optional categorical features integer tensor of shape [Batch, M_cat].

        Returns:
            E_0: Tabular tokens matrix of shape [Batch, M + 1, embed_dim].
        """
        batch_size = x_num.shape[0]

        # 1. Numerical Tokenization: [Batch, M_num, 1] * [M_num, embed_dim] -> [Batch, M_num, embed_dim]
        num_tokens = x_num.unsqueeze(-1) * self.num_weights.unsqueeze(0)
        if self.num_biases is not None:
            num_tokens = num_tokens + self.num_biases.unsqueeze(0)

        tokens_list = [num_tokens]

        # 2. Categorical Tokenization (if present)
        if x_cat is not None and self.n_categorical > 0:
            cat_tokens_list = []
            for i, emb in enumerate(self.cat_embeddings):
                cat_col = x_cat[:, i].clamp(0, self.categorical_cardinalities[i] - 1)
                tok = emb(cat_col)  # [Batch, embed_dim]
                if self.cat_biases is not None:
                    tok = tok + self.cat_biases[i].unsqueeze(0)
                cat_tokens_list.append(tok.unsqueeze(1))
            cat_tokens = torch.cat(cat_tokens_list, dim=1)  # [Batch, M_cat, embed_dim]
            tokens_list.append(cat_tokens)

        # 3. Concatenate [CLS] + numerical tokens + categorical tokens
        cls = self.cls_token.expand(batch_size, -1, -1)  # [Batch, 1, embed_dim]
        all_tokens = torch.cat([cls, *tokens_list], dim=1)  # [Batch, M+1, embed_dim]

        return all_tokens


class FTTransformerEncoder(nn.Module):
    """
    Feature Tokenizer Transformer Encoder for Tabular EHR Data.

    Processes tokenized tabular representations through L Transformer Encoder layers.
    Outputs the contextualized tabular representation H_tab in R^[Batch, M+1, d].
    """

    def __init__(
        self,
        n_numerical: int = len(DEFAULT_NUMERICAL_FEATURES),
        categorical_cardinalities: Optional[Sequence[int]] = None,
        embed_dim: int = 128,
        n_blocks: int = 4,
        n_heads: int = 4,
        dim_feedforward: int = 256,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        if embed_dim % n_heads != 0:
            raise ValueError(f"embed_dim ({embed_dim}) must be divisible by n_heads ({n_heads})")

        self.tokenizer = TabularTokenizer(
            n_numerical=n_numerical,
            categorical_cardinalities=categorical_cardinalities,
            embed_dim=embed_dim,
        )

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=n_heads,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            activation="gelu",
            batch_first=True,
            norm_first=True,
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer,
            num_layers=n_blocks,
        )
        self.norm = nn.LayerNorm(embed_dim)

    def forward(
        self,
        x_num: Tensor,
        x_cat: Optional[Tensor] = None,
    ) -> Tensor:
        """
        Encode tabular features into contextual tokens.

        Returns:
            H_tab: [Batch, M+1, embed_dim]
        """
        e_0 = self.tokenizer(x_num, x_cat)
        h_tab = self.transformer_encoder(e_0)
        return self.norm(h_tab)

