"""Train four frozen-BioClinicalBERT ablations on the rebuilt strict split.

The text backbone is frozen and its contextual token states are cached once. This
keeps all four variants comparable on a small GPU. This experiment does not
claim to reproduce the Phase 1 fine-tuned text baseline.
"""

from __future__ import annotations

import argparse
import copy
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import StandardScaler
from torch import nn
from torch.utils.data import DataLoader, Dataset

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.run_baselines import CLASSES, load_splits
from src.evaluation.metrics import compute_multiclass_metrics
from src.models.baselines import CATEGORICAL_FEATURES, NUMERICAL_FEATURES
from src.models.calibration import TemperatureScalingCalibrator
from src.models.multimodal_fusion import AblationModel

TEXT_MODEL = "emilyalsentzer/Bio_ClinicalBERT"
MODES = AblationModel.MODES
CATEGORY_VALUES = {
    "gender": ("M", "F", "OTHER"),
    "smoking_status": ("NEVER", "FORMER", "CURRENT"),
    "history_hypertension": ("0", "1"),
    "history_diabetes": ("0", "1"),
}


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data-dir", type=Path, default=Path("data/processed_rebuilt_strict"))
    p.add_argument("--audit-file", type=Path, default=Path("data/rebuilt_strict_split_audit.json"))
    p.add_argument("--baseline-file", type=Path, default=Path("data/rebuilt_strict_results_2026-10-28.json"))
    p.add_argument("--output-file", type=Path, default=Path("data/ablation_results.json"))
    p.add_argument("--checkpoint", type=Path, default=Path("data/checkpoints/multimodal_best.pt"))
    p.add_argument("--max-length", type=int, default=512)
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--encoding-batch-size", type=int, default=4)
    p.add_argument("--epochs", type=int, default=12)
    p.add_argument("--patience", type=int, default=4)
    p.add_argument("--learning-rate", type=float, default=2e-4)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    p.add_argument("--local-files-only", action="store_true")
    return p


def validate_inputs(args: argparse.Namespace) -> dict[str, pd.DataFrame]:
    if args.max_length < 8 or args.batch_size < 1 or args.encoding_batch_size < 1 or args.epochs < 1:
        raise ValueError("Invalid batch size, sequence length, or epoch count")
    frames = load_splits(args.data_dir)
    audit = json.loads(args.audit_file.read_text(encoding="utf-8"))
    if not audit.get("passed") or audit.get("rows") != {k: len(v) for k, v in frames.items()}:
        raise ValueError("Audit failed or its row counts do not match the selected split")
    required = NUMERICAL_FEATURES + CATEGORICAL_FEATURES + ["clinical_note", "diagnosis_label"]
    for name, frame in frames.items():
        missing = set(required) - set(frame)
        if missing:
            raise ValueError(f"{name} is missing {sorted(missing)}")
        if set(frame.diagnosis_label.unique()) != set(range(4)):
            raise ValueError(f"{name} must contain all four diagnosis classes")
    return frames


def tabular_arrays(frames: dict[str, pd.DataFrame]) -> tuple[dict, dict]:
    scaler = StandardScaler().fit(frames["train"][NUMERICAL_FEATURES].to_numpy(dtype=np.float32))
    arrays = {}
    for name, frame in frames.items():
        numerical = scaler.transform(frame[NUMERICAL_FEATURES].to_numpy(dtype=np.float32)).astype(np.float32)
        categorical = np.zeros((len(frame), len(CATEGORICAL_FEATURES)), dtype=np.int64)
        for col, feature in enumerate(CATEGORICAL_FEATURES):
            mapping = {value: idx + 1 for idx, value in enumerate(CATEGORY_VALUES[feature])}
            categorical[:, col] = frame[feature].astype(str).map(mapping).fillna(0).to_numpy(dtype=np.int64)
        arrays[name] = (torch.from_numpy(numerical), torch.from_numpy(categorical),
                        torch.tensor(frame.diagnosis_label.to_numpy(dtype=np.int64)))
    preprocessing = {"numerical_features": NUMERICAL_FEATURES,
                     "categorical_features": CATEGORICAL_FEATURES,
                     "category_values": CATEGORY_VALUES,
                     "scaler_mean": scaler.mean_.tolist(), "scaler_scale": scaler.scale_.tolist()}
    return arrays, preprocessing


def encode_text(frames: dict[str, pd.DataFrame], args: argparse.Namespace,
                device: torch.device) -> dict[str, tuple[torch.Tensor, torch.Tensor]]:
    from transformers import AutoModel, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(TEXT_MODEL, local_files_only=args.local_files_only)
    backbone = AutoModel.from_pretrained(TEXT_MODEL, local_files_only=args.local_files_only).to(device).eval()
    for parameter in backbone.parameters():
        parameter.requires_grad_(False)
    encoded = {}
    with torch.inference_mode():
        for name, frame in frames.items():
            hidden_batches, mask_batches = [], []
            notes = frame.clinical_note.fillna("").astype(str).tolist()
            for start in range(0, len(notes), args.encoding_batch_size):
                batch = tokenizer(notes[start:start + args.encoding_batch_size],
                                  padding="max_length", truncation=True,
                                  max_length=args.max_length, return_tensors="pt")
                mask = batch["attention_mask"]
                output = backbone(input_ids=batch["input_ids"].to(device),
                                  attention_mask=mask.to(device)).last_hidden_state
                hidden_batches.append(output.cpu().half())
                mask_batches.append(mask.cpu())
            encoded[name] = (torch.cat(hidden_batches), torch.cat(mask_batches))
            print(f"encoded {name}: {len(notes)} notes", flush=True)
    del backbone
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return encoded


class CachedDataset(Dataset):
    def __init__(self, tabular: tuple[torch.Tensor, ...], text: tuple[torch.Tensor, ...]):
        self.numerical, self.categorical, self.labels = tabular
        self.hidden, self.mask = text

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, ...]:
        return (self.numerical[index], self.categorical[index], self.hidden[index],
                self.mask[index], self.labels[index])


def predict_logits(model: nn.Module, loader: DataLoader, device: torch.device) -> tuple[torch.Tensor, torch.Tensor]:
    model.eval()
    logits, labels = [], []
    with torch.inference_mode():
        for numerical, categorical, hidden, mask, target in loader:
            out = model(numerical.to(device), categorical.to(device), hidden.to(device), mask.to(device))
            logits.append(out.float().cpu())
            labels.append(target)
    return torch.cat(logits), torch.cat(labels)


def train_mode(mode: str, loaders: dict[str, DataLoader], args: argparse.Namespace,
               device: torch.device) -> tuple[AblationModel, dict, torch.Tensor, torch.Tensor]:
    torch.manual_seed(args.seed)
    model = AblationModel(mode).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate, weight_decay=1e-5)
    best_loss, best_state, stale, best_epoch = float("inf"), None, 0, 0
    for epoch in range(1, args.epochs + 1):
        model.train()
        for numerical, categorical, hidden, mask, target in loaders["train"]:
            optimizer.zero_grad(set_to_none=True)
            logits = model(numerical.to(device), categorical.to(device),
                           hidden.to(device), mask.to(device))
            loss = nn.functional.cross_entropy(logits, target.to(device))
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
        val_logits, val_labels = predict_logits(model, loaders["val"], device)
        val_loss = float(nn.functional.cross_entropy(val_logits, val_labels))
        print(f"{mode} epoch {epoch}: validation NLL={val_loss:.4f}", flush=True)
        if val_loss < best_loss - 1e-5:
            best_loss, best_epoch, stale = val_loss, epoch, 0
            best_state = copy.deepcopy({k: v.detach().cpu() for k, v in model.state_dict().items()})
        else:
            stale += 1
            if stale >= args.patience:
                break
    model.load_state_dict(best_state)
    val_logits, val_labels = predict_logits(model, loaders["val"], device)
    calibrator = TemperatureScalingCalibrator().fit(val_logits, val_labels)
    summary = {"selected_epoch": best_epoch, "validation_nll": best_loss,
               "temperature": calibrator.temperature}
    return model, summary, val_logits, val_labels


def main() -> None:
    args = parser().parse_args()
    frames = validate_inputs(args)
    device = torch.device("cuda" if args.device == "auto" and torch.cuda.is_available() else
                          "cpu" if args.device == "auto" else args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable")
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(args.seed)
    arrays, preprocessing = tabular_arrays(frames)
    text = encode_text(frames, args, device)
    loaders = {name: DataLoader(CachedDataset(arrays[name], text[name]),
                                batch_size=args.batch_size, shuffle=name == "train", num_workers=0)
               for name in frames}
    baseline = json.loads(args.baseline_file.read_text(encoding="utf-8"))
    if baseline["benchmark_metadata"]["test_samples"] != len(frames["test"]):
        raise ValueError("Baseline benchmark and ablation test splits differ in row count")
    baseline_scores = {name: value["macro_auroc"] for name, value in baseline["results"].items()}
    results = {}
    for mode in MODES:
        model, summary, _, _ = train_mode(mode, loaders, args, device)
        test_logits, test_labels = predict_logits(model, loaders["test"], device)
        calibrated = TemperatureScalingCalibrator(summary["temperature"])
        probs = calibrated.predict_proba(test_logits).detach().numpy()
        metrics = compute_multiclass_metrics(test_labels.numpy(), probs)
        results[mode] = {**summary, "test": metrics,
                         "delta_auroc_vs_strict_baselines": {
                             name: metrics["macro_auroc"] - score for name, score in baseline_scores.items()}}
        print(f"{mode} strict test AUROC={metrics['macro_auroc']:.4f}", flush=True)
        if mode == "cross_attention":
            args.checkpoint.parent.mkdir(parents=True, exist_ok=True)
            torch.save({"model_state": {k: v.detach().cpu() for k, v in model.state_dict().items()},
                        "model_mode": mode, "model_config": {"text_width": 768, "d_token": 128,
                                                                "num_classes": 4, "n_blocks": 4, "n_heads": 4},
                        "text_model": TEXT_MODEL, "text_backbone_frozen": True,
                        "max_length": args.max_length, "temperature": summary["temperature"],
                        "classes": CLASSES, "preprocessing": preprocessing,
                        "source_split": str(args.data_dir), "seed": args.seed}, args.checkpoint)
        del model
        if device.type == "cuda":
            torch.cuda.empty_cache()
    result = {"metadata": {"generated_at": datetime.now(timezone.utc).isoformat(),
                            "split": str(args.data_dir), "split_rows": {k: len(v) for k, v in frames.items()},
                            "audit_file": str(args.audit_file), "baseline_file": str(args.baseline_file),
                            "seed": args.seed, "device": str(device), "text_model": TEXT_MODEL,
                            "text_backbone_frozen": True, "max_length": args.max_length,
                            "epochs_max": args.epochs, "batch_size": args.batch_size,
                            "note": "Frozen text backbone; not directly equivalent to Phase 1 fine-tuned text baseline."},
              "strict_baseline_auroc": baseline_scores, "variants": results}
    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    args.output_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"saved {args.output_file} and {args.checkpoint}")


if __name__ == "__main__":
    main()
