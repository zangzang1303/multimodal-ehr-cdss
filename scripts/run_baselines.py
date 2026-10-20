"""Train/evaluate Phase 1 baselines once patient-level processed splits are available."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
import yaml
from sklearn.preprocessing import StandardScaler
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.evaluation.metrics import compute_multiclass_metrics
from src.models.baselines import (
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
    ClassicalTabularBaseline,
    DummyTextBackbone,
    TabularDeepBaseline,
    TextOnlyBaseline,
)

BASELINE_CHOICES = ("all", "tabular_classic", "tabular_deep", "text_only")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Train and evaluate Phase 1 EHR baselines on train/val/test Parquet splits."
    )
    parser.add_argument(
        "--data_dir",
        type=Path,
        default=Path("data/processed"),
        help="Directory containing train.parquet, val.parquet and test.parquet.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/model_config.yaml"),
        help="Baseline hyperparameter YAML file.",
    )
    parser.add_argument(
        "--output_file",
        "--output_json",
        dest="output_file",
        type=Path,
        default=Path("data/baseline_results.json"),
        help="Destination JSON for validation/test metrics.",
    )
    parser.add_argument(
        "--baseline", choices=BASELINE_CHOICES, default="all", help="Baseline family to train."
    )
    parser.add_argument("--device", default="auto", help="auto, cpu, cuda, or a torch device.")
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Run offline dummy forward passes and metric validation without processed data.",
    )
    return parser


def load_config(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    required = {"training", "classical", "ft_transformer", "clinical_bert"}
    missing = required.difference(config or {})
    if missing:
        raise ValueError(f"Model config is missing sections: {sorted(missing)}")
    return config


def load_splits(data_dir: Path) -> dict[str, pd.DataFrame]:
    paths = {split: data_dir / f"{split}.parquet" for split in ("train", "val", "test")}
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "Processed patient-level splits are not available: " + ", ".join(missing)
        )
    frames = {split: pd.read_parquet(path) for split, path in paths.items()}
    for split, frame in frames.items():
        if "diagnosis_label" not in frame.columns:
            raise ValueError(f"{split}.parquet has no diagnosis_label column")
        if frame["diagnosis_label"].isna().any():
            raise ValueError(f"{split}.parquet contains missing diagnosis labels")
    return frames


def select_device(requested: str) -> torch.device:
    if requested == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    device = torch.device(requested)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested but torch.cuda.is_available() is False")
    return device


def evaluate_probabilities(y_true: np.ndarray, probabilities: np.ndarray) -> dict[str, float]:
    return compute_multiclass_metrics(y_true.astype(int), probabilities)


def run_classical(
    frames: dict[str, pd.DataFrame], config: dict[str, Any]
) -> dict[str, Any]:
    params = dict(config["classical"]["xgboost"])
    model = ClassicalTabularBaseline(
        estimator="xgboost",
        estimator_params=params,
        num_classes=int(config["training"]["num_classes"]),
    )
    features = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
    model.fit(frames["train"][features], frames["train"]["diagnosis_label"])
    result: dict[str, Any] = {"model": "XGBoost"}
    for split in ("val", "test"):
        probabilities = model.predict_proba(frames[split][features])
        result[split] = evaluate_probabilities(
            frames[split]["diagnosis_label"].to_numpy(), probabilities
        )
    return result


def _tensor_loader(
    features: np.ndarray, labels: np.ndarray, batch_size: int, shuffle: bool
) -> DataLoader:
    dataset = TensorDataset(
        torch.as_tensor(features, dtype=torch.float32),
        torch.as_tensor(labels, dtype=torch.long),
    )
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)


def _train_torch_model(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    *,
    device: torch.device,
    epochs: int,
    learning_rate: float,
    weight_decay: float,
    patience: int,
) -> nn.Module:
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=learning_rate, weight_decay=weight_decay
    )
    criterion = nn.CrossEntropyLoss()
    best_loss = float("inf")
    best_state: dict[str, torch.Tensor] | None = None
    stale_epochs = 0
    model.to(device)
    for _ in range(epochs):
        model.train()
        for features, labels in train_loader:
            optimizer.zero_grad(set_to_none=True)
            loss = criterion(model(features.to(device)), labels.to(device))
            loss.backward()
            optimizer.step()
        model.eval()
        losses = []
        with torch.no_grad():
            for features, labels in val_loader:
                losses.append(
                    criterion(model(features.to(device)), labels.to(device)).item()
                )
        val_loss = float(np.mean(losses))
        if val_loss < best_loss:
            best_loss = val_loss
            best_state = {
                key: value.detach().cpu().clone()
                for key, value in model.state_dict().items()
            }
            stale_epochs = 0
        else:
            stale_epochs += 1
            if stale_epochs >= patience:
                break
    if best_state is not None:
        model.load_state_dict(best_state)
    return model


def _predict_torch(
    model: nn.Module, loader: DataLoader, device: torch.device
) -> tuple[np.ndarray, np.ndarray]:
    labels, probabilities = [], []
    model.eval().to(device)
    with torch.no_grad():
        for features, target in loader:
            probabilities.append(torch.softmax(model(features.to(device)), dim=1).cpu().numpy())
            labels.append(target.numpy())
    return np.concatenate(labels), np.concatenate(probabilities)


def run_tabular_deep(
    frames: dict[str, pd.DataFrame], config: dict[str, Any], device: torch.device
) -> dict[str, Any]:
    cfg = config["ft_transformer"]
    scaler = StandardScaler()
    arrays = {
        "train": scaler.fit_transform(frames["train"][NUMERICAL_FEATURES]),
        "val": scaler.transform(frames["val"][NUMERICAL_FEATURES]),
        "test": scaler.transform(frames["test"][NUMERICAL_FEATURES]),
    }
    batch_size = int(cfg["batch_size"])
    loaders = {
        split: _tensor_loader(
            values,
            frames[split]["diagnosis_label"].to_numpy(),
            batch_size,
            shuffle=split == "train",
        )
        for split, values in arrays.items()
    }
    model = TabularDeepBaseline(
        n_features=len(NUMERICAL_FEATURES),
        num_classes=int(config["training"]["num_classes"]),
        d_token=int(cfg["d_token"]),
        n_blocks=int(cfg["n_blocks"]),
        attention_n_heads=int(cfg["attention_n_heads"]),
        attention_dropout=float(cfg["attention_dropout"]),
        ffn_dropout=float(cfg["ffn_dropout"]),
        ffn_d_hidden=int(cfg["ffn_d_hidden"]),
    )
    model = _train_torch_model(
        model,
        loaders["train"],
        loaders["val"],
        device=device,
        epochs=int(cfg.get("epochs", 20)),
        learning_rate=float(cfg["learning_rate"]),
        weight_decay=float(cfg["weight_decay"]),
        patience=int(config["training"]["early_stopping_patience"]),
    )
    result: dict[str, Any] = {"model": "FT-Transformer"}
    for split in ("val", "test"):
        labels, probabilities = _predict_torch(model, loaders[split], device)
        result[split] = evaluate_probabilities(labels, probabilities)
    return result


def smoke_test(config: dict[str, Any]) -> dict[str, Any]:
    rng = np.random.default_rng(int(config["training"]["seed"]))
    frame = pd.DataFrame(rng.normal(size=(24, len(NUMERICAL_FEATURES))), columns=NUMERICAL_FEATURES)
    frame["age"] = rng.integers(18, 90, size=len(frame))
    frame["gender"] = rng.choice(["M", "F", "OTHER"], size=len(frame))
    frame["smoking_status"] = rng.choice(["NEVER", "FORMER", "CURRENT"], size=len(frame))
    frame["history_hypertension"] = rng.integers(0, 2, size=len(frame))
    frame["history_diabetes"] = rng.integers(0, 2, size=len(frame))
    labels = np.tile(np.arange(4), 6)

    classical = ClassicalTabularBaseline(
        "random_forest", estimator_params={"n_estimators": 10, "max_depth": 3}
    ).fit(frame, labels)
    classical_shape = list(classical.predict_proba(frame.iloc[:3]).shape)
    deep_shape = list(TabularDeepBaseline()(torch.randn(3, 9)).shape)
    text = TextOnlyBaseline(backbone=DummyTextBackbone())
    text_shape = list(text(torch.randint(0, 32, (3, 12)), torch.ones(3, 12)).shape)
    probabilities = np.full((24, 4), 0.1)
    probabilities[np.arange(24), labels] = 0.7
    metrics = compute_multiclass_metrics(labels, probabilities)
    return {
        "classical_probability_shape": classical_shape,
        "tabular_deep_logits_shape": deep_shape,
        "text_only_logits_shape": text_shape,
        "metric_keys": sorted(metrics),
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = load_config(args.config)
    if args.smoke_test:
        print(json.dumps(smoke_test(config), indent=2))
        return 0

    frames = load_splits(args.data_dir)
    selected = (
        ("tabular_classic", "tabular_deep", "text_only")
        if args.baseline == "all"
        else (args.baseline,)
    )
    device = select_device(args.device)
    results: dict[str, Any] = {}
    if "tabular_classic" in selected:
        results["tabular_classic"] = run_classical(frames, config)
    if "tabular_deep" in selected:
        results["tabular_deep"] = run_tabular_deep(frames, config, device)
    if "text_only" in selected:
        results["text_only"] = {
            "status": "ready",
            "note": "Training starts in backlog 3 after de-identified notes join patient splits.",
        }

    payload = {
        "benchmark_metadata": {
            "evaluation_date": datetime.now(timezone.utc).isoformat(),
            "test_samples": len(frames["test"]),
            "num_classes": int(config["training"]["num_classes"]),
            "device": str(device),
        },
        "results": results,
    }
    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    args.output_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Saved results to {args.output_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
