"""Baseline models used by the Phase 1 comparison study."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd
import torch
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from torch import Tensor, nn


NUMERICAL_FEATURES = [
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

CATEGORICAL_FEATURES = [
    "gender",
    "smoking_status",
    "history_hypertension",
    "history_diabetes",
]


class ClassicalTabularBaseline:
    """Sklearn-compatible preprocessing and multiclass classifier pipeline."""

    def __init__(
        self,
        estimator: str = "xgboost",
        *,
        numerical_features: Sequence[str] = NUMERICAL_FEATURES,
        categorical_features: Sequence[str] = CATEGORICAL_FEATURES,
        estimator_params: Mapping[str, Any] | None = None,
        num_classes: int = 4,
        random_state: int = 42,
    ) -> None:
        self.estimator_name = estimator.lower()
        self.numerical_features = list(numerical_features)
        self.categorical_features = list(categorical_features)
        self.num_classes = num_classes

        preprocessor = ColumnTransformer(
            transformers=[
                ("numerical", StandardScaler(), self.numerical_features),
                (
                    "categorical",
                    OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                    self.categorical_features,
                ),
            ],
            remainder="drop",
        )
        model = self._build_estimator(estimator_params or {}, random_state)
        self.pipeline = Pipeline([("preprocessor", preprocessor), ("model", model)])

    def _build_estimator(self, params: Mapping[str, Any], random_state: int) -> Any:
        options = dict(params)
        if self.estimator_name == "random_forest":
            defaults = {"n_estimators": 200, "max_depth": 12, "random_state": random_state}
            defaults.update(options)
            return RandomForestClassifier(**defaults)
        if self.estimator_name == "xgboost":
            from xgboost import XGBClassifier

            defaults = {
                "objective": "multi:softprob",
                "num_class": self.num_classes,
                "n_estimators": 300,
                "max_depth": 6,
                "learning_rate": 0.05,
                "subsample": 0.8,
                "colsample_bytree": 0.8,
                "eval_metric": "mlogloss",
                "random_state": random_state,
            }
            defaults.update(options)
            return XGBClassifier(**defaults)
        if self.estimator_name == "catboost":
            from catboost import CatBoostClassifier

            defaults = {
                "loss_function": "MultiClass",
                "iterations": 300,
                "depth": 6,
                "learning_rate": 0.05,
                "random_seed": random_state,
                "verbose": False,
            }
            defaults.update(options)
            return CatBoostClassifier(**defaults)
        raise ValueError(
            "estimator must be one of: random_forest, xgboost, catboost; "
            f"received {self.estimator_name!r}"
        )

    def _validate_columns(self, X: pd.DataFrame) -> None:
        if not isinstance(X, pd.DataFrame):
            raise TypeError("ClassicalTabularBaseline expects a pandas DataFrame")
        required = self.numerical_features + self.categorical_features
        missing = [column for column in required if column not in X.columns]
        if missing:
            raise ValueError(f"Missing required feature columns: {missing}")

    def fit(self, X: pd.DataFrame, y: Sequence[int]) -> "ClassicalTabularBaseline":
        self._validate_columns(X)
        self.pipeline.fit(X, np.asarray(y))
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        self._validate_columns(X)
        return self.pipeline.predict(X)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        self._validate_columns(X)
        return self.pipeline.predict_proba(X)


class TabularDeepBaseline(nn.Module):
    """Compact FT-Transformer for preprocessed numerical tabular tensors."""

    def __init__(
        self,
        n_features: int = 9,
        num_classes: int = 4,
        d_token: int = 128,
        n_blocks: int = 4,
        attention_n_heads: int = 4,
        attention_dropout: float = 0.1,
        ffn_dropout: float = 0.1,
        ffn_d_hidden: int = 256,
    ) -> None:
        super().__init__()
        if n_features < 1:
            raise ValueError("n_features must be positive")
        if d_token % attention_n_heads:
            raise ValueError("d_token must be divisible by attention_n_heads")

        self.n_features = n_features
        self.feature_weight = nn.Parameter(torch.empty(n_features, d_token))
        self.feature_bias = nn.Parameter(torch.empty(n_features, d_token))
        self.cls_token = nn.Parameter(torch.empty(1, 1, d_token))
        layer = nn.TransformerEncoderLayer(
            d_model=d_token,
            nhead=attention_n_heads,
            dim_feedforward=ffn_d_hidden,
            dropout=ffn_dropout,
            activation="gelu",
            batch_first=True,
            norm_first=False,
        )
        self.encoder = nn.TransformerEncoder(layer, num_layers=n_blocks)
        self.attention_dropout = nn.Dropout(attention_dropout)
        self.head = nn.Sequential(nn.LayerNorm(d_token), nn.Linear(d_token, num_classes))
        self.reset_parameters()

    def reset_parameters(self) -> None:
        nn.init.xavier_uniform_(self.feature_weight)
        nn.init.zeros_(self.feature_bias)
        nn.init.normal_(self.cls_token, std=0.02)

    def forward(self, features: Tensor) -> Tensor:
        if features.ndim != 2 or features.shape[1] != self.n_features:
            raise ValueError(
                f"Expected features with shape [batch, {self.n_features}], "
                f"received {tuple(features.shape)}"
            )
        tokens = features.float().unsqueeze(-1) * self.feature_weight + self.feature_bias
        cls = self.cls_token.expand(features.shape[0], -1, -1)
        encoded = self.encoder(self.attention_dropout(torch.cat([cls, tokens], dim=1)))
        return self.head(encoded[:, 0])


class TextOnlyBaseline(nn.Module):
    """Clinical Transformer backbone with dropout and a four-class head."""

    def __init__(
        self,
        model_name: str = "emilyalsentzer/Bio_ClinicalBERT",
        num_classes: int = 4,
        dropout_rate: float = 0.2,
        *,
        backbone: nn.Module | None = None,
        local_files_only: bool = False,
    ) -> None:
        super().__init__()
        if backbone is None:
            from transformers import AutoModel

            backbone = AutoModel.from_pretrained(model_name, local_files_only=local_files_only)
        self.backbone = backbone
        hidden_size = getattr(getattr(backbone, "config", None), "hidden_size", None)
        if not isinstance(hidden_size, int):
            raise ValueError("Transformer backbone must expose config.hidden_size")
        self.dropout = nn.Dropout(dropout_rate)
        self.classifier = nn.Linear(hidden_size, num_classes)

    def forward(self, input_ids: Tensor, attention_mask: Tensor | None = None) -> Tensor:
        outputs = self.backbone(input_ids=input_ids, attention_mask=attention_mask)
        last_hidden = getattr(outputs, "last_hidden_state", None)
        if last_hidden is None and isinstance(outputs, (tuple, list)):
            last_hidden = outputs[0]
        if last_hidden is None:
            raise RuntimeError("Transformer backbone did not return last_hidden_state")
        return self.classifier(self.dropout(last_hidden[:, 0]))


class DummyTextBackbone(nn.Module):
    """Small offline backbone for smoke tests; not intended for training."""

    def __init__(self, vocab_size: int = 32, hidden_size: int = 16) -> None:
        super().__init__()
        self.config = SimpleNamespace(hidden_size=hidden_size)
        self.embedding = nn.Embedding(vocab_size, hidden_size)

    def forward(self, input_ids: Tensor, attention_mask: Tensor | None = None) -> Any:
        del attention_mask
        return SimpleNamespace(last_hidden_state=self.embedding(input_ids))
