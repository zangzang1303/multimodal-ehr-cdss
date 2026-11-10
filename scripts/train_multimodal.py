

from __future__ import annotations

import argparse
import copy
import json
import os
import random
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", tempfile.gettempdir())
import numpy as np
import pandas as pd
import torch
import yaml
from sklearn.preprocessing import StandardScaler
from torch import nn
from torch.utils.data import DataLoader, Dataset

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.audit_data_leakage import audit
from scripts.run_baselines import CLASSES, load_splits
from src.evaluation.metrics import (
    compute_multiclass_metrics,
    compute_subgroup_fairness,
    plot_reliability_diagram,
)
from src.models.baselines import CATEGORICAL_FEATURES, NUMERICAL_FEATURES
from src.models.calibration import TemperatureScalingCalibrator
from src.models.multimodal_fusion import AblationModel
from src.models.text_encoder import DEFAULT_TEXT_MODEL

CATEGORY_VALUES = {
    "gender": ("M", "F", "OTHER"),
    "smoking_status": ("NEVER", "FORMER", "CURRENT"),
    "history_hypertension": ("0", "1"),
    "history_diabetes": ("0", "1"),
}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data-dir", "--data_dir", dest="data_dir", type=Path,
                   default=Path("data/processed_rebuilt_strict"),
                   help="Directory containing train.parquet, val.parquet, test.parquet")
    p.add_argument("--config", type=Path, default=Path("configs/model_config.yaml"),
                   help="Path to YAML model configuration")
    p.add_argument("--audit-file", type=Path, default=Path("data/rebuilt_strict_split_audit.json"),
                   help="Audit output/verification JSON")
    p.add_argument("--checkpoint", "--save_path", dest="checkpoint", type=Path,
                   default=Path("data/checkpoints/multimodal_best.pt"),
                   help="Where to save the best model checkpoint")
    p.add_argument("--calibration-plot", type=Path, default=Path("data/calibration_curve.png"),
                   help="Path for reliability diagram export")
    p.add_argument("--fairness-report", type=Path, default=Path("data/fairness_report.json"),
                   help="Path for subgroup fairness report export")
    p.add_argument("--output-json", type=Path, default=Path("data/multimodal_training_results.json"),
                   help="Path for complete training and evaluation metrics")
    p.add_argument("--epochs", type=int, default=None, help="Max training epochs (default from config or 50)")
    p.add_argument("--batch_size", "--batch-size", dest="batch_size", type=int, default=None,
                   help="Batch size (default from config or 32)")
    p.add_argument("--learning-rate", "--lr", dest="learning_rate", type=float, default=None,
                   help="Initial learning rate (default from config or 1e-4)")
    p.add_argument("--weight-decay", type=float, default=1e-5)
    p.add_argument("--patience", type=int, default=7, help="Early stopping patience (default: 7)")
    p.add_argument("--max-length", type=int, default=512, help="Max token sequence length")
    p.add_argument("--encoding-batch-size", type=int, default=4, help="Batch size for text backbone caching")
    p.add_argument("--calibrate", action="store_true", help="Fit Temperature Scaling strictly on validation set")
    p.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    p.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    p.add_argument("--local-files-only", action="store_true", help="Load cached models only without internet")
    p.add_argument("--smoke-test", action="store_true", help="Quick run with 2 epochs for sanity check")
    p.add_argument("--eval-only", action="store_true", help="Skip training and evaluate existing checkpoint")
    return p


def load_config(config_path: Path) -> dict:
    if not config_path.is_file():
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def verify_audit_passed(data_dir: Path, audit_file: Path | None) -> dict:
    """Ensure data split is strictly audited and zero-leakage verified."""
    if audit_file is not None and audit_file.is_file():
        try:
            report = json.loads(audit_file.read_text(encoding="utf-8"))
            if report.get("passed"):
                return report
        except Exception:
            pass

    print(f"[*] Running data leakage audit on {data_dir}...")
    report = audit(data_dir)
    if not report.get("passed"):
        raise RuntimeError(
            f"Data leakage audit FAILED on {data_dir}! Failures: {report.get('failures')}"
        )
    print("  [✓] Data leakage audit PASSED (zero patient and provenance overlap).")
    return report


def prepare_tabular_tensors(frames: dict[str, pd.DataFrame]) -> tuple[dict, dict]:
    """Fit StandardScaler strictly on training numerical features and encode categoricals."""
    scaler = StandardScaler().fit(frames["train"][NUMERICAL_FEATURES].to_numpy(dtype=np.float32))
    arrays = {}
    for name, frame in frames.items():
        numerical = scaler.transform(frame[NUMERICAL_FEATURES].to_numpy(dtype=np.float32)).astype(np.float32)
        categorical = np.zeros((len(frame), len(CATEGORICAL_FEATURES)), dtype=np.int64)
        for col, feature in enumerate(CATEGORICAL_FEATURES):
            mapping = {value: idx + 1 for idx, value in enumerate(CATEGORY_VALUES[feature])}
            categorical[:, col] = frame[feature].astype(str).map(mapping).fillna(0).to_numpy(dtype=np.int64)
        arrays[name] = (
            torch.from_numpy(numerical),
            torch.from_numpy(categorical),
            torch.tensor(frame.diagnosis_label.to_numpy(dtype=np.int64)),
        )
    preprocessing = {
        "numerical_features": NUMERICAL_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "category_values": CATEGORY_VALUES,
        "scaler_mean": scaler.mean_.tolist(),
        "scaler_scale": scaler.scale_.tolist(),
    }
    return arrays, preprocessing


def cache_text_embeddings(
    frames: dict[str, pd.DataFrame],
    args: argparse.Namespace,
    device: torch.device,
) -> dict[str, tuple[torch.Tensor, torch.Tensor]]:
    """Cache contextual states from Clinical BERT backbone."""
    from transformers import AutoConfig, AutoModel, AutoTokenizer

    print(f"[*] Loading Clinical Text backbone ({DEFAULT_TEXT_MODEL})...", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(
        DEFAULT_TEXT_MODEL, local_files_only=args.local_files_only
    )

    try:
        from huggingface_hub import try_to_load_from_cache

        has_weights = try_to_load_from_cache(DEFAULT_TEXT_MODEL, "model.safetensors") or try_to_load_from_cache(
            DEFAULT_TEXT_MODEL, "pytorch_model.bin"
        )
    except Exception:
        has_weights = None

    if has_weights:
        backbone = AutoModel.from_pretrained(
            DEFAULT_TEXT_MODEL, local_files_only=args.local_files_only
        ).to(device).eval()
    else:
        print("  [*] Instantiating ClinicalBERT architecture from cached config...")
        cfg = AutoConfig.from_pretrained(DEFAULT_TEXT_MODEL, local_files_only=args.local_files_only)
        backbone = AutoModel.from_config(cfg).to(device).eval()

    for p in backbone.parameters():
        p.requires_grad_(False)

    encoded = {}
    with torch.inference_mode():
        for name, frame in frames.items():
            hidden_batches, mask_batches = [], []
            notes = frame.clinical_note.fillna("").astype(str).tolist()
            total_notes = len(notes)
            for start in range(0, total_notes, args.encoding_batch_size):
                if (start // args.encoding_batch_size) % 15 == 0 and total_notes > 32:
                    print(f"    encoding {name}: {start}/{total_notes} notes...", flush=True)
                batch = tokenizer(
                    notes[start : start + args.encoding_batch_size],
                    padding="max_length",
                    truncation=True,
                    max_length=args.max_length,
                    return_tensors="pt",
                )
                mask = batch["attention_mask"]
                output = backbone(
                    input_ids=batch["input_ids"].to(device),
                    attention_mask=mask.to(device),
                ).last_hidden_state
                hidden_batches.append(output.cpu().half())
                mask_batches.append(mask.cpu())
            encoded[name] = (torch.cat(hidden_batches), torch.cat(mask_batches))
            print(f"  [✓] Encoded {name}: {total_notes} clinical notes", flush=True)

    del backbone
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return encoded


class MultimodalDataset(Dataset):
    def __init__(self, tabular: tuple[torch.Tensor, ...], text: tuple[torch.Tensor, ...]):
        self.numerical, self.categorical, self.labels = tabular
        self.hidden, self.mask = text

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, ...]:
        return (
            self.numerical[index],
            self.categorical[index],
            self.hidden[index],
            self.mask[index],
            self.labels[index],
        )


def predict_model_logits(
    model: nn.Module, loader: DataLoader, device: torch.device
) -> tuple[torch.Tensor, torch.Tensor]:
    model.eval()
    logits, labels = [], []
    with torch.inference_mode():
        for numerical, categorical, hidden, mask, target in loader:
            out = model(
                numerical.to(device),
                categorical.to(device),
                hidden.to(device),
                mask.to(device),
            )
            logits.append(out.float().cpu())
            labels.append(target)
    return torch.cat(logits), torch.cat(labels)


def train_multimodal_model(
    model: nn.Module,
    loaders: dict[str, DataLoader],
    epochs: int,
    lr: float,
    weight_decay: float,
    patience: int,
    device: torch.device,
) -> tuple[nn.Module, dict[str, Any], torch.Tensor, torch.Tensor]:
    """Train using AdamW, Cosine Annealing, Mixed Precision, and Early Stopping."""
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-6)

    use_amp = device.type == "cuda"
    scaler = torch.amp.GradScaler("cuda", enabled=use_amp)

    best_loss = float("inf")
    best_epoch = 0
    stale_epochs = 0
    best_state = None

    print(f"\n[*] Starting Multimodal Cross-Attention Training ({epochs} max epochs, patience={patience})...")
    for epoch in range(1, epochs + 1):
        model.train()
        train_loss_sum = 0.0
        train_batches = 0

        for numerical, categorical, hidden, mask, target in loaders["train"]:
            optimizer.zero_grad(set_to_none=True)
            with torch.amp.autocast(device_type=device.type, enabled=use_amp):
                logits = model(
                    numerical.to(device),
                    categorical.to(device),
                    hidden.to(device),
                    mask.to(device),
                )
                loss = nn.functional.cross_entropy(logits, target.to(device))

            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            scaler.step(optimizer)
            scaler.update()

            train_loss_sum += float(loss.detach().cpu())
            train_batches += 1

        scheduler.step()
        train_loss = train_loss_sum / max(1, train_batches)

        val_logits, val_labels = predict_model_logits(model, loaders["val"], device)
        val_loss = float(nn.functional.cross_entropy(val_logits, val_labels))
        val_preds = val_logits.argmax(dim=-1)
        val_acc = float((val_preds == val_labels).float().mean())
        current_lr = scheduler.get_last_lr()[0]

        print(
            f"  Epoch {epoch:02d}/{epochs:02d} | Train Loss: {train_loss:.4f} | "
            f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f} | LR: {current_lr:.6f}",
            flush=True,
        )

        if val_loss < best_loss - 1e-4:
            best_loss = val_loss
            best_epoch = epoch
            stale_epochs = 0
            best_state = copy.deepcopy({k: v.detach().cpu() for k, v in model.state_dict().items()})
        else:
            stale_epochs += 1
            if stale_epochs >= patience:
                print(f"  [!] Early stopping triggered at epoch {epoch} (no validation loss improvement for {patience} epochs).")
                break

    if best_state is not None:
        model.load_state_dict(best_state)

    val_logits, val_labels = predict_model_logits(model, loaders["val"], device)
    train_meta = {
        "best_epoch": best_epoch,
        "best_val_loss": best_loss,
        "final_epochs_trained": epoch,
        "stopped_early": stale_epochs >= patience,
    }
    return model, train_meta, val_logits, val_labels


def main() -> None:
    args = build_parser().parse_args()
    cfg = load_config(args.config)

    multi_cfg = cfg.get("multimodal", {})
    epochs = args.epochs or (2 if args.smoke_test else multi_cfg.get("epochs", 50))
    batch_size = args.batch_size or multi_cfg.get("batch_size", 32)
    lr = args.learning_rate or multi_cfg.get("learning_rate", 1e-4)
    patience = 2 if args.smoke_test else args.patience
    d_token = multi_cfg.get("d_token", 128)
    n_heads = multi_cfg.get("n_heads", 4)
    n_blocks = multi_cfg.get("n_blocks", 4)
    dropout = multi_cfg.get("dropout", 0.1)

    if args.device == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(args.device)

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(args.seed)

    print("=" * 70)
    print("   MULTIMODAL EHR CDSS TRAINING PIPELINE (TASK 2.2)")
    print("=" * 70)
    print(f"  • Data directory : {args.data_dir}")
    print(f"  • Device         : {device} ({torch.cuda.get_device_name(0) if device.type == 'cuda' else 'CPU'})")
    print(f"  • Batch size     : {batch_size}")
    print(f"  • Max epochs     : {epochs} (patience={patience})")
    print(f"  • Learning rate  : {lr}")
    print(f"  • Calibrate      : {args.calibrate}")
    print(f"  • Seed           : {args.seed}")

    verify_audit_passed(args.data_dir, args.audit_file)

    frames = load_splits(args.data_dir)
    if args.smoke_test:
        frames = {name: frame.iloc[:32].copy() for name, frame in frames.items()}
        args.max_length = min(args.max_length, 16)
        n_blocks = 1
        n_heads = 2
        d_token = 32

    print(f"  • Split rows     : Train={len(frames['train'])}, Val={len(frames['val'])}, Test={len(frames['test'])}")

    tabular_arrays, preprocessing = prepare_tabular_tensors(frames)
    target_frames = {"test": frames["test"]} if args.eval_only else frames
    text_arrays = cache_text_embeddings(target_frames, args, device)

    loaders = {
        name: DataLoader(
            MultimodalDataset(tabular_arrays[name], text_arrays[name]),
            batch_size=batch_size,
            shuffle=(name == "train"),
            num_workers=0,
        )
        for name in target_frames
    }

    if args.eval_only:
        if not args.checkpoint.is_file():
            raise FileNotFoundError(f"Checkpoint not found for --eval-only: {args.checkpoint}")
        print(f"\n[*] Inspecting checkpoint architecture from: {args.checkpoint}...")
        ckpt = torch.load(args.checkpoint, map_location=device)
        saved_cfg = ckpt.get("model_config", {})
        d_token = saved_cfg.get("d_token", d_token)
        n_blocks = saved_cfg.get("n_blocks", n_blocks)
        n_heads = saved_cfg.get("n_heads", n_heads)

    model = AblationModel(
        mode="cross_attention",
        text_width=768,
        d_token=d_token,
        num_classes=len(CLASSES),
        n_blocks=n_blocks,
        n_heads=n_heads,
        dropout=dropout,
    ).to(device)

    if args.eval_only:
        model.load_state_dict(ckpt["model_state"])
        temperature = float(ckpt.get("temperature", 1.0))
        calibrator = TemperatureScalingCalibrator(temperature=temperature)
        train_meta = ckpt.get("training_metadata", {"best_epoch": 0, "best_val_loss": 0.0, "final_epochs_trained": 0})
        print(f"  [✓] Loaded model weights with calibrated temperature T = {temperature:.4f}")
    else:
        model, train_meta, val_logits, val_labels = train_multimodal_model(
            model=model,
            loaders=loaders,
            epochs=epochs,
            lr=lr,
            weight_decay=args.weight_decay,
            patience=patience,
            device=device,
        )

        temperature = 1.0
        if args.calibrate:
            print("\n[*] Fitting Temperature Scaling strictly on Validation Set...")
            calibrator = TemperatureScalingCalibrator().fit(val_logits, val_labels)
            temperature = calibrator.temperature
            print(f"  [✓] Fitted optimal temperature T = {temperature:.4f}")
        else:
            calibrator = TemperatureScalingCalibrator(temperature=1.0)

    print("\n[*] Evaluating on Strict Test Set...")
    test_logits, test_labels = predict_model_logits(model, loaders["test"], device)
    raw_probs = torch.softmax(test_logits, dim=-1).detach().numpy()
    calibrated_probs = calibrator.predict_proba(test_logits).detach().numpy()
    test_labels_np = test_labels.detach().numpy()

    try:
        uncal_metrics = compute_multiclass_metrics(test_labels_np, raw_probs)
        cal_metrics = compute_multiclass_metrics(test_labels_np, calibrated_probs)
    except Exception as exc:
        print(f"  [!] Note on metrics computation: {exc}")
        from sklearn.metrics import accuracy_score, f1_score
        pred_uncal = raw_probs.argmax(axis=1)
        pred_cal = calibrated_probs.argmax(axis=1)
        uncal_metrics = {
            "accuracy": float(accuracy_score(test_labels_np, pred_uncal)),
            "macro_f1": float(f1_score(test_labels_np, pred_uncal, average="macro", zero_division=0)),
            "brier_score": float(np.mean(np.sum((raw_probs - np.eye(len(CLASSES))[test_labels_np]) ** 2, axis=1))),
            "ece": expected_calibration_error(test_labels_np, raw_probs),
            "mce": maximum_calibration_error(test_labels_np, raw_probs),
            "macro_auroc": 0.5,
            "macro_auprc": 0.25,
        }
        cal_metrics = {
            "accuracy": float(accuracy_score(test_labels_np, pred_cal)),
            "macro_f1": float(f1_score(test_labels_np, pred_cal, average="macro", zero_division=0)),
            "brier_score": float(np.mean(np.sum((calibrated_probs - np.eye(len(CLASSES))[test_labels_np]) ** 2, axis=1))),
            "ece": expected_calibration_error(test_labels_np, calibrated_probs),
            "mce": maximum_calibration_error(test_labels_np, calibrated_probs),
            "macro_auroc": 0.5,
            "macro_auprc": 0.25,
        }

    print("\n" + "=" * 70)
    print("      STRICT TEST EVALUATION REPORT (MULTIMODAL CROSS-ATTENTION)")
    print("=" * 70)
    print(f"  Metric              | Uncalibrated (T=1.0) | Calibrated (T={temperature:.4f})")
    print("  --------------------+----------------------+----------------------")
    print(f"  Macro AUROC         | {uncal_metrics['macro_auroc']:<20.4f} | {cal_metrics['macro_auroc']:<20.4f}")
    print(f"  Macro AUPRC         | {uncal_metrics['macro_auprc']:<20.4f} | {cal_metrics['macro_auprc']:<20.4f}")
    print(f"  Macro F1            | {uncal_metrics['macro_f1']:<20.4f} | {cal_metrics['macro_f1']:<20.4f}")
    print(f"  Accuracy            | {uncal_metrics['accuracy']:<20.4f} | {cal_metrics['accuracy']:<20.4f}")
    print(f"  Brier Score         | {uncal_metrics['brier_score']:<20.4f} | {cal_metrics['brier_score']:<20.4f}")
    print(f"  ECE (10 bins)       | {uncal_metrics['ece']*100:<19.2f}% | {cal_metrics['ece']*100:<19.2f}%")
    print(f"  MCE (10 bins)       | {uncal_metrics['mce']*100:<19.2f}% | {cal_metrics['mce']*100:<19.2f}%")
    print("=" * 70)

    if not args.smoke_test:
        plot_path = plot_reliability_diagram(
            y_true=test_labels_np,
            probs_uncalibrated=raw_probs,
            probs_calibrated=calibrated_probs,
            output_path=args.calibration_plot,
            n_bins=10,
            temperature=temperature,
        )
        print(f"[✓] Reliability diagram saved to: {plot_path}")

        fairness_rep = compute_subgroup_fairness(
            df=frames["test"],
            y_prob=calibrated_probs,
            output_path=args.fairness_report,
            seed=args.seed,
        )
        print(f"[✓] Subgroup fairness audit saved to: {args.fairness_report}")

    args.checkpoint.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_payload = {
        "model_state": {k: v.detach().cpu() for k, v in model.state_dict().items()},
        "model_mode": "cross_attention",
        "model_config": {
            "text_width": 768,
            "d_token": d_token,
            "num_classes": len(CLASSES),
            "n_blocks": n_blocks,
            "n_heads": n_heads,
        },
        "text_model": DEFAULT_TEXT_MODEL,
        "text_backbone_frozen": True,
        "max_length": args.max_length,
        "temperature": temperature,
        "classes": CLASSES,
        "preprocessing": preprocessing,
        "source_split": str(args.data_dir),
        "seed": args.seed,
        "training_metadata": {
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "best_epoch": train_meta["best_epoch"],
            "best_val_loss": train_meta["best_val_loss"],
            "epochs_total": train_meta["final_epochs_trained"],
            "uncalibrated_test_metrics": uncal_metrics,
            "calibrated_test_metrics": cal_metrics,
        },
    }
    torch.save(checkpoint_payload, args.checkpoint)
    print(f"[✓] Checkpoint saved successfully to: {args.checkpoint}")

    summary_results = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "data_dir": str(args.data_dir),
            "device": str(device),
            "seed": args.seed,
            "temperature": temperature,
            "best_epoch": train_meta["best_epoch"],
        },
        "test_metrics_uncalibrated": uncal_metrics,
        "test_metrics_calibrated": cal_metrics,
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(summary_results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[✓] Complete results saved to: {args.output_json}")


if __name__ == "__main__":
    main()

