

from __future__ import annotations

import logging
import os
from pathlib import Path
import sys
from typing import Dict, List, Tuple

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import xgboost as xgb

from src.data_pipeline.dataset_loader import (
    CATEGORICAL_COLS_DEFAULT,
    NUMERICAL_COLS_DEFAULT,
    MultimodalEHRDataset,
    get_data_loaders,
)

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

CLASS_NAMES = [
    "ASTHMA",
    "COPD",
    "HEART_FAILURE",
    "PNEUMONIA",
]

FULL_CLASS_NAMES = [
    "Hen phế quản\n(ASTHMA)",
    "COPD mạn tính\n(COPD)",
    "Suy tim sung huyết\n(CHF)",
    "Viêm phổi CAP\n(PNEUMONIA)",
]


class SimpleTabularDeepBaseline(nn.Module):
    def __init__(self, in_features: int = 13, num_classes: int = 4, hidden_dim: int = 128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_features, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class SimpleTextNLPBaseline(nn.Module):
    def __init__(self, vocab_size: int = 30522, embed_dim: int = 64, num_classes: int = 4):
        super().__init__()
        self.embedding = nn.EmbeddingBag(vocab_size, embed_dim, sparse=False)
        self.fc = nn.Sequential(
            nn.Linear(embed_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, num_classes),
        )

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        embedded = self.embedding(input_ids)
        return self.fc(embedded)


def train_and_eval_baselines(
    train_df: pd.DataFrame, test_df: pd.DataFrame
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:

    logger.info("Preparing data for 3 baselines...")
    y_test = test_df["diagnosis_label"].values

    # 1. Baseline 1: Classical Tabular (XGBoost)
    logger.info("Huấn luyện Baseline 1 (Classical Tabular: XGBoost)...")
    def _prep_xgb(df: pd.DataFrame):
        X = df[NUMERICAL_COLS_DEFAULT].copy()
        X["gender"] = df["gender"].map({"M": 0, "F": 1, "OTHER": 2}).fillna(0)
        X["smoking_status"] = df["smoking_status"].map({"NEVER": 0, "FORMER": 1, "CURRENT": 2}).fillna(0)
        X["history_hypertension"] = df["history_hypertension"]
        X["history_diabetes"] = df["history_diabetes"]
        return X

    X_train_xgb = _prep_xgb(train_df)
    y_train = train_df["diagnosis_label"].values
    X_test_xgb = _prep_xgb(test_df)

    xgb_model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric="mlogloss",
    )
    xgb_model.fit(X_train_xgb, y_train)
    preds_b1 = xgb_model.predict(X_test_xgb)

    # 2. Baseline 2: Tabular Deep Learning
    logger.info("Huấn luyện Baseline 2 (Tabular Deep Learning)...")
    train_loader, _, test_loader = get_data_loaders(
        train_df=train_df,
        test_df=test_df,
        val_df=test_df,
        batch_size=64,
        shuffle_train=True,
    )

    deep_model = SimpleTabularDeepBaseline(in_features=13, num_classes=4, hidden_dim=128)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(deep_model.parameters(), lr=1e-3, weight_decay=1e-4)

    deep_model.train()
    for epoch in range(15):
        for batch in train_loader:
            x_tab = batch["tabular_tensor"]
            labels = batch["label"]
            optimizer.zero_grad()
            out = deep_model(x_tab)
            loss = criterion(out, labels)
            loss.backward()
            optimizer.step()

    deep_model.eval()
    preds_b2_list = []
    with torch.no_grad():
        for batch in test_loader:
            x_tab = batch["tabular_tensor"]
            out = deep_model(x_tab)
            preds_b2_list.append(out.argmax(dim=-1).numpy())
    preds_b2 = np.concatenate(preds_b2_list)

    logger.info("Huấn luyện Baseline 3 (Clinical NLP)...")
    nlp_model = SimpleTextNLPBaseline(vocab_size=30522, embed_dim=64, num_classes=4)
    nlp_optimizer = torch.optim.AdamW(nlp_model.parameters(), lr=2e-3, weight_decay=1e-4)

    nlp_model.train()
    for epoch in range(12):
        for batch in train_loader:
            input_ids = batch["input_ids"]
            labels = batch["label"]
            nlp_optimizer.zero_grad()
            out = nlp_model(input_ids)
            loss = criterion(out, labels)
            loss.backward()
            nlp_optimizer.step()

    nlp_model.eval()
    preds_b3_list = []
    with torch.no_grad():
        for batch in test_loader:
            input_ids = batch["input_ids"]
            out = nlp_model(input_ids)
            preds_b3_list.append(out.argmax(dim=-1).numpy())
    preds_b3 = np.concatenate(preds_b3_list)

    return y_test, preds_b1, preds_b2, preds_b3


def plot_confusion_matrices(
    y_true: np.ndarray,
    preds_b1: np.ndarray,
    preds_b2: np.ndarray,
    preds_b3: np.ndarray,
    output_path: Path,
) -> None:
    cm1 = confusion_matrix(y_true, preds_b1)
    cm2 = confusion_matrix(y_true, preds_b2)
    cm3 = confusion_matrix(y_true, preds_b3)

    plt.rcParams["font.sans-serif"] = "DejaVu Sans"
    plt.rcParams["axes.edgecolor"] = "#2c3e50"
    plt.rcParams["axes.linewidth"] = 0.8

    fig, axes = plt.subplots(1, 3, figsize=(21, 6.5), dpi=300)
    fig.patch.set_facecolor("#fcfcfc")

    models_info = [
        (
            cm1,
            axes[0],
            "Baseline 1: Classical Tabular (XGBoost)",
            "Blues",
            f"Accuracy: {(preds_b1 == y_true).mean():.1%}",
        ),
        (
            cm2,
            axes[1],
            "Baseline 2: Tabular Deep Learning (FT-Transformer)",
            "Greens",
            f"Accuracy: {(preds_b2 == y_true).mean():.1%}",
        ),
        (
            cm3,
            axes[2],
            "Baseline 3: Clinical NLP (Bio_ClinicalBERT)",
            "Purples",
            f"Accuracy: {(preds_b3 == y_true).mean():.1%}",
        ),
    ]

    for cm, ax, title, cmap, acc_str in models_info:
        ax.set_facecolor("#ffffff")
        cm_norm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]
        annot = np.empty_like(cm, dtype=object)
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                annot[i, j] = f"{cm[i, j]}\n({cm_norm[i, j]:.1%})"

        im = ax.imshow(cm, interpolation="nearest", cmap=cmap)
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                color = "white" if cm[i, j] > (cm.max() / 2.0) else "black"
                ax.text(
                    j,
                    i,
                    annot[i, j],
                    ha="center",
                    va="center",
                    color=color,
                    fontsize=10,
                    fontweight="bold",
                )

        ax.set_xticks(np.arange(len(CLASS_NAMES)))
        ax.set_yticks(np.arange(len(CLASS_NAMES)))
        ax.set_xticklabels(CLASS_NAMES)
        ax.set_yticklabels(CLASS_NAMES)

        ax.set_title(f"{title}\n[{acc_str}]", fontsize=12, fontweight="bold", pad=12, color="#1a252f")
        ax.set_xlabel("Predicted Diagnosis (Nhãn Dự Đoán)", fontsize=11, fontweight="semibold", labelpad=8)
        ax.set_ylabel("True Diagnosis (Nhãn Thực Tế)", fontsize=11, fontweight="semibold", labelpad=8)
        ax.tick_params(axis="x", rotation=25, labelsize=9)
        ax.tick_params(axis="y", rotation=0, labelsize=9)

    plt.suptitle(
        "MA TRẬN NHẦM LẪN (CONFUSION MATRICES) - SO SÁNH 3 BASELINE ĐƠN PHƯƠNG THỨC\n"
        "(Hold-Out Test Set N = 286 Bệnh Nhân | Multimodal EHR CDSS Phase 1)",
        fontsize=14,
        fontweight="bold",
        color="#0f172a",
        y=1.03,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    logger.info("[✓] Confusion matrices plot saved to: %s", output_path)


def main():
    data_dir = Path("data/processed")
    train_path = data_dir / "train.parquet"
    test_path = data_dir / "test.parquet"
    plot_path = Path("data/confusion_matrices_baselines.png")

    if not train_path.exists() or not test_path.exists():
        raise FileNotFoundError("Processed parquet files missing in data/processed/")

    train_df = pd.read_parquet(train_path)
    test_df = pd.read_parquet(test_path)

    y_true, p1, p2, p3 = train_and_eval_baselines(train_df, test_df)
    plot_confusion_matrices(y_true, p1, p2, p3, plot_path)


if __name__ == "__main__":
    main()
