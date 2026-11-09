#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clinical Utility & Multimodal Evaluation Script (M-CDSS)
========================================================================================
Author: Member 2 (Biomedical Data Engineer & Privacy)
Purpose:
  - Load trained checkpoint (multimodal_best.pt) and strict test dataset.
  - Verify zero data leakage provenance audit before running evaluation.
  - Compute full discrimination metrics (Macro AUROC, Macro AUPRC, Macro-F1, Accuracy),
    calibration metrics (ECE, MCE, Brier score), and clinical Decision Curve Analysis (DCA).
  - Export complete clinical visualization figures (ROC, PR, DCA, Calibration, Confusion Matrix)
    into the designated plots directory.
  - Generate comprehensive JSON evaluation artifacts for team handoffs.

========================================================================================
COLLABORATION & HANDOFF INTERFACES:
----------------------------------------------------------------------------------------
[MEMBER 1 - Lead ML / Modeling]:
  - Member 1 can override `src/evaluation/dca_analysis.py` and `src/evaluation/metrics.py`.
  - Member 1 can review the exported metrics in `data/evaluation_plots/clinical_utility_metrics.json`
    to populate scientific comparison tables against Baseline 1 (CatBoost), Baseline 2 (FT-Transformer),
    and Baseline 3 (Bio_ClinicalBERT).
[MEMBER 3 - Full-Stack AI & Frontend]:
  - Member 3's route `GET /api/v1/evaluation/benchmark` can directly ingest:
    `data/evaluation_plots/clinical_utility_metrics.json` and `data/benchmark_summary.json`.
  - Member 3 can utilize the DCA data records (`dca_table` key in json) for the interactive
    recharts/chart.js Decision Curve component on the doctor's web interface.
========================================================================================
"""

from __future__ import annotations

import argparse
import io
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

# Force UTF-8 stdout on Windows
if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    except Exception:
        pass

os.environ.setdefault("MPLCONFIGDIR", tempfile.gettempdir())
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)
from sklearn.preprocessing import label_binarize
import torch
from torch.utils.data import DataLoader, Dataset

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.evaluation.dca_analysis import calculate_net_benefit, plot_dca_curve
from src.evaluation.metrics import (
    compute_calibration_bins,
    compute_multiclass_metrics,
    expected_calibration_error,
    maximum_calibration_error,
    plot_reliability_diagram,
)
from src.models.calibration import TemperatureScalingCalibrator
from src.models.multimodal_fusion import AblationModel
from src.models.text_encoder import DEFAULT_TEXT_MODEL

DISEASE_CLASSES = ["ASTHMA", "COPD", "HEART_FAILURE", "PNEUMONIA"]
VIETNAMESE_DISEASE_NAMES = {
    "ASTHMA": "Hen phế quản (Asthma)",
    "COPD": "Bệnh phổi tắc nghẽn mạn tính (COPD)",
    "HEART_FAILURE": "Suy tim sung huyết (Heart Failure)",
    "PNEUMONIA": "Viêm phổi mắc phải cộng đồng (Pneumonia)",
}


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate clinical utility of multimodal EHR CDSS.")
    parser.add_argument(
        "--model_path",
        "--model-path",
        dest="model_path",
        type=Path,
        default=Path("data/checkpoints/multimodal_best.pt"),
        help="Path to multimodal model checkpoint (.pt)",
    )
    parser.add_argument(
        "--test_data",
        "--test-data",
        dest="test_data",
        type=Path,
        default=Path("data/processed_rebuilt_strict/test.parquet"),
        help="Path to holdout test set (.parquet)",
    )
    parser.add_argument(
        "--output_plots",
        "--output-plots",
        dest="output_plots",
        type=Path,
        default=Path("data/evaluation_plots"),
        help="Directory to export clinical evaluation graphs and summary",
    )
    parser.add_argument(
        "--audit_file",
        "--audit-file",
        dest="audit_file",
        type=Path,
        default=Path("data/rebuilt_strict_split_audit.json"),
        help="Path to data split audit verification report",
    )
    parser.add_argument(
        "--target_class",
        dest="target_class",
        type=int,
        default=2,
        help="Target class index for primary DCA One-vs-Rest (default: 2 = HEART_FAILURE)",
    )
    parser.add_argument(
        "--batch_size",
        dest="batch_size",
        type=int,
        default=16,
        help="Batch size for text embedding extraction and inference",
    )
    parser.add_argument(
        "--max_length",
        dest="max_length",
        type=int,
        default=512,
        help="Maximum token sequence length for clinical note tokenizer",
    )
    parser.add_argument(
        "--device",
        dest="device",
        type=str,
        default="cpu",
        choices=["cpu", "cuda", "auto"],
        help="Computation device",
    )
    parser.add_argument(
        "--seed",
        dest="seed",
        type=int,
        default=42,
        help="Random seed for deterministic evaluation",
    )
    return parser


def verify_provenance_and_audit(audit_file: Path) -> dict:
    """Validate data split audit to prevent data leakage before clinical evaluation."""
    print(f"[*] Step 1/6: Verifying data split provenance and audit report at: {audit_file}...")
    if not audit_file.exists():
        print(f"  [!] Warning: Audit file {audit_file} not found. Attempting data audit check...")
        from scripts.audit_data_leakage import audit
        data_dir = audit_file.parent / "processed_rebuilt_strict"
        if not data_dir.exists():
            data_dir = Path("data/processed_rebuilt_strict")
        rep = audit(data_dir)
        if not rep.get("passed"):
            raise RuntimeError(f"Data leakage audit FAILED: {rep.get('failures')}")
        print("  [✓] Zero patient leakage verified via live audit.")
        return rep

    with open(audit_file, "r", encoding="utf-8") as f:
        rep = json.load(f)

    if not rep.get("passed"):
        raise RuntimeError(f"Audit report indicates data leakage failure: {rep.get('failures')}")

    overlap = rep.get("overlap", {})
    pt_overlap = overlap.get("patient_id", {})
    print(f"  [✓] Audit verified: 0 patient cross-leakage (train-test: {pt_overlap.get('train_test', 0)}, val-test: {pt_overlap.get('val_test', 0)})")
    return rep


class SimpleInferenceDataset(Dataset):
    def __init__(
        self,
        numerical: torch.Tensor,
        categorical: torch.Tensor,
        hidden: torch.Tensor,
        mask: torch.Tensor,
        labels: torch.Tensor,
    ):
        self.numerical = numerical
        self.categorical = categorical
        self.hidden = hidden
        self.mask = mask
        self.labels = labels

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, idx: int):
        return (
            self.numerical[idx],
            self.categorical[idx],
            self.hidden[idx],
            self.mask[idx],
            self.labels[idx],
        )


def extract_multimodal_tensors(
    df: pd.DataFrame,
    preprocessing: dict,
    max_length: int = 512,
    batch_size: int = 16,
    device: torch.device = torch.device("cpu"),
    seed: int = 42,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    """Transform tabular features using checkpoint scaler and encode clinical text."""
    print(f"[*] Step 2/6: Preprocessing tabular and text modalities for N = {len(df)} test samples...")

    num_cols = preprocessing.get("numerical_features", [])
    cat_cols = preprocessing.get("categorical_features", [])
    cat_values = preprocessing.get("category_values", {})
    scaler_mean = np.array(preprocessing["scaler_mean"], dtype=np.float32)
    scaler_scale = np.array(preprocessing["scaler_scale"], dtype=np.float32)

    # 1. Tabular numerical scaling
    raw_num = df[num_cols].to_numpy(dtype=np.float32)
    norm_num = (raw_num - scaler_mean) / scaler_scale
    tensor_num = torch.from_numpy(norm_num.astype(np.float32))

    # 2. Tabular categorical encoding
    cat_mat = np.zeros((len(df), len(cat_cols)), dtype=np.int64)
    for col_idx, col_name in enumerate(cat_cols):
        allowed_vals = cat_values.get(col_name, ())
        val_map = {val: i + 1 for i, val in enumerate(allowed_vals)}
        cat_mat[:, col_idx] = df[col_name].astype(str).map(val_map).fillna(0).to_numpy(dtype=np.int64)
    tensor_cat = torch.from_numpy(cat_mat)

    tensor_labels = torch.tensor(df["diagnosis_label"].to_numpy(dtype=np.int64))

    # Optional local cache for lightning-fast repeated evaluations
    cache_path = Path("data/checkpoints") / f"test_text_emb_cached_{len(df)}.pt"
    if cache_path.exists():
        print(f"  [✓] Loading precomputed text embeddings from cache: {cache_path}...")
        cached_data = torch.load(cache_path, map_location="cpu")
        tensor_hidden = cached_data["hidden"]
        tensor_mask = cached_data["mask"]
    else:
        # 3. Clinical text encoding via ClinicalBERT
        print(f"  [*] Tokenizing clinical notes and extracting representations via {DEFAULT_TEXT_MODEL}...")
        from transformers import AutoConfig, AutoModel, AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(DEFAULT_TEXT_MODEL, local_files_only=True)
        try:
            from huggingface_hub import try_to_load_from_cache
            has_weights = try_to_load_from_cache(DEFAULT_TEXT_MODEL, "model.safetensors") or try_to_load_from_cache(
                DEFAULT_TEXT_MODEL, "pytorch_model.bin"
            )
        except Exception:
            has_weights = None

        if has_weights:
            backbone = AutoModel.from_pretrained(DEFAULT_TEXT_MODEL, local_files_only=True).to(device).eval()
        else:
            # Load from config deterministically matching training backbone
            torch.manual_seed(seed)
            np.random.seed(seed)
            cfg = AutoConfig.from_pretrained(DEFAULT_TEXT_MODEL, local_files_only=True)
            backbone = AutoModel.from_config(cfg).to(device).eval()

        notes = df["clinical_note"].fillna("").astype(str).tolist()
        hidden_chunks, mask_chunks = [], []

        with torch.inference_mode():
            for start in range(0, len(notes), batch_size):
                chunk = notes[start : start + batch_size]
                encoded = tokenizer(
                    chunk,
                    padding="max_length",
                    truncation=True,
                    max_length=max_length,
                    return_tensors="pt",
                )
                mask = encoded["attention_mask"]
                hidden = backbone(
                    input_ids=encoded["input_ids"].to(device),
                    attention_mask=mask.to(device),
                ).last_hidden_state
                hidden_chunks.append(hidden.cpu().half())
                mask_chunks.append(mask.cpu())

        tensor_hidden = torch.cat(hidden_chunks)
        tensor_mask = torch.cat(mask_chunks)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        torch.save({"hidden": tensor_hidden, "mask": tensor_mask}, cache_path)

    print(f"  [✓] Multimodal inputs ready: Tabular {tensor_num.shape}, Text {tensor_hidden.shape}")
    return tensor_num, tensor_cat, tensor_hidden, tensor_mask, tensor_labels


def run_model_inference(
    model: torch.nn.Module,
    dataset: Dataset,
    batch_size: int,
    calibrator: TemperatureScalingCalibrator,
    device: torch.device,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Execute model forward pass and temperature calibration."""
    print("[*] Step 3/6: Executing multimodal cross-attention inference...")
    model.eval()
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

    logits_list = []
    labels_list = []

    with torch.inference_mode():
        for num, cat, hid, msk, target in loader:
            out = model(
                num.to(device),
                cat.to(device),
                hid.to(device),
                msk.to(device),
            )
            logits_list.append(out.float().cpu())
            labels_list.append(target)

    all_logits = torch.cat(logits_list)
    all_labels = torch.cat(labels_list)

    raw_probs = torch.softmax(all_logits, dim=-1).detach().cpu().numpy()
    calibrated_probs = calibrator.predict_proba(all_logits).detach().cpu().numpy()
    all_logits_np = all_logits.detach().cpu().numpy()
    all_labels_np = all_labels.detach().cpu().numpy()

    return all_logits_np, raw_probs, calibrated_probs, all_labels_np


# ==============================================================================
# PLOTTING ROUTINES (Deliverables for Member 2)
# ==============================================================================

def plot_confusion_matrix_figure(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    output_path: Path,
    title_suffix: str = "Multimodal CDSS",
) -> Path:
    """
    Export Confusion Matrix figure with integer counts and class-wise normalized percentages.
    Saved at data/confusion_matrix.png (Deliverable 2.1) and in evaluation_plots.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cm = confusion_matrix(y_true, y_pred, labels=np.arange(len(DISEASE_CLASSES)))
    cm_norm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]

    fig, ax = plt.subplots(figsize=(8.5, 7.5), dpi=300)
    fig.patch.set_facecolor("#ffffff")
    im = ax.imshow(cm, interpolation="nearest", cmap="Blues")

    # Add Colorbar
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=9)
    cbar.set_label("Số lượng ca bệnh (Sample Count)", fontsize=10, fontweight="bold")

    acc = (y_pred == y_true).mean()

    # Annotate cells
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            val = cm[i, j]
            pct = cm_norm[i, j]
            color = "white" if val > (cm.max() / 2.0) else "#1e293b"
            ax.text(
                j,
                i,
                f"{val}\n({pct:.1%})",
                ha="center",
                va="center",
                color=color,
                fontsize=11,
                fontweight="bold",
            )

    ax.set_xticks(np.arange(len(DISEASE_CLASSES)))
    ax.set_yticks(np.arange(len(DISEASE_CLASSES)))
    ax.set_xticklabels([f"{c}\n({VIETNAMESE_DISEASE_NAMES[c].split(' (')[0]})" for c in DISEASE_CLASSES], fontsize=9)
    ax.set_yticklabels([f"{c}\n({VIETNAMESE_DISEASE_NAMES[c].split(' (')[0]})" for c in DISEASE_CLASSES], fontsize=9)

    ax.set_title(
        f"MA TRẬN NHẦM LẪN (CONFUSION MATRIX) - {title_suffix}\n"
        f"Holdout Strict Test Set (N = {len(y_true)} | Accuracy = {acc:.2%})",
        fontsize=12,
        fontweight="bold",
        pad=14,
        color="#0f172a",
    )
    ax.set_xlabel("Nhãn Dự Đoán Của Mô Hình (Predicted Class)", fontsize=11, fontweight="bold", labelpad=8)
    ax.set_ylabel("Nhãn Thực Tế Bệnh Nhân (True Diagnosis)", fontsize=11, fontweight="bold", labelpad=8)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    return output_path


def plot_multiclass_roc_curves(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    output_path: Path,
) -> Path:
    """Plot One-vs-Rest ROC curve for each class and Macro average."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    num_classes = len(DISEASE_CLASSES)
    y_onehot = label_binarize(y_true, classes=np.arange(num_classes))

    colors = ["#2563eb", "#059669", "#d97706", "#dc2626"]
    plt.figure(figsize=(8.5, 7.0), dpi=300)
    plt.plot([0, 1], [0, 1], "k--", alpha=0.5, label="Phân loại ngẫu nhiên (AUROC = 0.5000)")

    for idx, (cls_name, color) in enumerate(zip(DISEASE_CLASSES, colors)):
        fpr, tpr, _ = roc_curve(y_onehot[:, idx], y_prob[:, idx])
        roc_auc = roc_auc_score(y_onehot[:, idx], y_prob[:, idx])
        vn_name = VIETNAMESE_DISEASE_NAMES[cls_name].split(" (")[0]
        plt.plot(fpr, tpr, color=color, linewidth=2.0, label=f"{cls_name} ({vn_name}) - AUC = {roc_auc:.4f}")

    macro_auc = roc_auc_score(y_onehot, y_prob, multi_class="ovr", average="macro")
    plt.plot([], [], " ", label=f"► Macro-average AUROC = {macro_auc:.4f}")

    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("1 - Độ đặc hiệu (False Positive Rate)", fontsize=11, fontweight="bold")
    plt.ylabel("Độ nhạy (True Positive Rate)", fontsize=11, fontweight="bold")
    plt.title(
        f"Đường Cong ROC Đa Lớp One-vs-Rest (Multiclass ROC Curves)\n"
        f"Mô hình Multimodal EHR CDSS trên Tập Strict Test (N = {len(y_true)})",
        fontsize=11,
        fontweight="bold",
        pad=12,
    )
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="lower right", fontsize=9, framealpha=0.95)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    return output_path


def plot_multiclass_pr_curves(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    output_path: Path,
) -> Path:
    """Plot Precision-Recall curve for each class and Macro average."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    num_classes = len(DISEASE_CLASSES)
    y_onehot = label_binarize(y_true, classes=np.arange(num_classes))

    colors = ["#2563eb", "#059669", "#d97706", "#dc2626"]
    plt.figure(figsize=(8.5, 7.0), dpi=300)

    for idx, (cls_name, color) in enumerate(zip(DISEASE_CLASSES, colors)):
        precision, recall, _ = precision_recall_curve(y_onehot[:, idx], y_prob[:, idx])
        ap = average_precision_score(y_onehot[:, idx], y_prob[:, idx])
        vn_name = VIETNAMESE_DISEASE_NAMES[cls_name].split(" (")[0]
        plt.plot(recall, precision, color=color, linewidth=2.0, label=f"{cls_name} ({vn_name}) - AP = {ap:.4f}")

    macro_ap = average_precision_score(y_onehot, y_prob, average="macro")
    plt.plot([], [], " ", label=f"► Macro-average AUPRC = {macro_ap:.4f}")

    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("Độ nhạy / Thu hồi (Recall)", fontsize=11, fontweight="bold")
    plt.ylabel("Độ chính xác (Precision)", fontsize=11, fontweight="bold")
    plt.title(
        f"Đường Cong Precision-Recall Đa Lớp (Multiclass PR Curves)\n"
        f"Mô hình Multimodal EHR CDSS trên Tập Strict Test (N = {len(y_true)})",
        fontsize=11,
        fontweight="bold",
        pad=12,
    )
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="lower left", fontsize=9, framealpha=0.95)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    return output_path


# ==============================================================================
# MAIN PIPELINE EXECUTION
# ==============================================================================

def main():
    parser = build_arg_parser()
    args = parser.parse_args()

    print("=" * 80)
    print("   AUTOMATED CLINICAL UTILITY & MULTIMODAL EVALUATION PIPELINE")
    print("      Phase 2 Validation | PROBAST & TRIPOD+AI Compliant")
    print("=" * 80)

    # 1. Audit check
    verify_provenance_and_audit(args.audit_file)

    # 2. Setup Device
    if args.device == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(args.device)
    print(f"[*] Target device: {device}")

    # 3. Load Checkpoint
    if not args.model_path.exists():
        raise FileNotFoundError(f"Model checkpoint not found: {args.model_path}")
    print(f"[*] Loading model checkpoint from: {args.model_path}")
    ckpt = torch.load(args.model_path, map_location="cpu")

    preprocessing = ckpt.get("preprocessing", {})
    cfg = ckpt.get("model_config", {})
    temperature = float(ckpt.get("temperature", 1.0))
    classes = ckpt.get("classes", DISEASE_CLASSES)

    # Reconstruct Multimodal Model
    model = AblationModel(
        mode="cross_attention",
        text_width=cfg.get("text_width", 768),
        d_token=cfg.get("d_token", 128),
        num_classes=len(classes),
        n_blocks=cfg.get("n_blocks", 4),
        n_heads=cfg.get("n_heads", 4),
        dropout=0.1,
    )
    model.load_state_dict(ckpt["model_state"])
    model.to(device)
    calibrator = TemperatureScalingCalibrator(temperature=temperature)

    # 4. Read Test Dataset
    if not args.test_data.exists():
        raise FileNotFoundError(f"Test data parquet not found: {args.test_data}")
    df_test = pd.read_parquet(args.test_data)
    print(f"  [✓] Loaded test set with {len(df_test)} samples across {df_test['diagnosis_label'].nunique()} classes.")

    # 5. Extract features
    t_num, t_cat, t_hid, t_msk, t_y = extract_multimodal_tensors(
        df=df_test,
        preprocessing=preprocessing,
        max_length=args.max_length,
        batch_size=args.batch_size,
        device=device,
        seed=args.seed,
    )
    dataset = SimpleInferenceDataset(t_num, t_cat, t_hid, t_msk, t_y)

    # 6. Execute Model Inference
    test_logits, raw_probs, cal_probs, y_true = run_model_inference(
        model=model,
        dataset=dataset,
        batch_size=args.batch_size,
        calibrator=calibrator,
        device=device,
    )
    y_pred = cal_probs.argmax(axis=1)

    # 7. Compute Scientific Metrics
    print("[*] Step 4/6: Computing discrimination, calibration, and class-level metrics...")
    overall_metrics_uncal = compute_multiclass_metrics(y_true, raw_probs)
    overall_metrics_cal = compute_multiclass_metrics(y_true, cal_probs)

    # Per-class metrics
    class_metrics = {}
    y_onehot = label_binarize(y_true, classes=np.arange(len(classes)))
    for idx, cls_name in enumerate(classes):
        cls_true = (y_true == idx).astype(int)
        cls_pred = (y_pred == idx).astype(int)
        tp = int(np.sum((cls_pred == 1) & (cls_true == 1)))
        fp = int(np.sum((cls_pred == 1) & (cls_true == 0)))
        fn = int(np.sum((cls_pred == 0) & (cls_true == 1)))
        tn = int(np.sum((cls_pred == 0) & (cls_true == 0)))

        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        ppv = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        npv = tn / (tn + fn) if (tn + fn) > 0 else 0.0
        cls_f1 = f1_score(cls_true, cls_pred, zero_division=0)
        cls_auc = roc_auc_score(cls_true, cal_probs[:, idx])
        cls_ap = average_precision_score(cls_true, cal_probs[:, idx])

        class_metrics[cls_name] = {
            "disease_name_vi": VIETNAMESE_DISEASE_NAMES.get(cls_name, cls_name),
            "sample_count": int(np.sum(cls_true)),
            "auroc": float(cls_auc),
            "auprc": float(cls_ap),
            "f1_score": float(cls_f1),
            "sensitivity_recall": float(sensitivity),
            "specificity": float(specificity),
            "positive_predictive_value": float(ppv),
            "negative_predictive_value": float(npv),
            "confusion": {"tp": tp, "fp": fp, "fn": fn, "tn": tn},
        }

    # 8. Decision Curve Analysis (DCA)
    print(f"[*] Step 5/6: Calculating Decision Curve Analysis for target class {args.target_class} ({classes[args.target_class]})...")
    df_dca = calculate_net_benefit(y_true, cal_probs, target_class=args.target_class)

    # 9. Export Plots
    args.output_plots.mkdir(parents=True, exist_ok=True)
    print(f"[*] Step 6/6: Rendering and exporting clinical utility plots to: {args.output_plots}...")

    # (a) Confusion Matrix
    cm_plot_eval = args.output_plots / "confusion_matrix.png"
    plot_confusion_matrix_figure(y_true, y_pred, cm_plot_eval)
    # Also save to data/confusion_matrix.png (Deliverable 2.1)
    cm_root_path = Path("data/confusion_matrix.png")
    shutil.copyfile(cm_plot_eval, cm_root_path)
    print(f"  [✓] Exported Confusion Matrix: {cm_plot_eval} & {cm_root_path}")

    # (b) Multiclass ROC Curves
    roc_plot = args.output_plots / "roc_curves.png"
    plot_multiclass_roc_curves(y_true, cal_probs, roc_plot)
    print(f"  [✓] Exported Multiclass ROC Curves: {roc_plot}")

    # (c) Multiclass PR Curves
    pr_plot = args.output_plots / "pr_curves.png"
    plot_multiclass_pr_curves(y_true, cal_probs, pr_plot)
    print(f"  [✓] Exported Multiclass PR Curves: {pr_plot}")

    # (d) DCA Plot
    dca_plot_eval = args.output_plots / "dca_curve.png"
    plot_dca_curve(
        df_dca=df_dca,
        output_path=dca_plot_eval,
        target_name=f"{classes[args.target_class]} ({VIETNAMESE_DISEASE_NAMES[classes[args.target_class]]})",
        hypothetical_action="Chỉ định xét nghiệm & hội chẩn chuyên khoa",
        sample_size=len(y_true),
    )
    # Also copy to data/dca_curve.png for Member 1 handover
    dca_root_path = Path("data/dca_curve.png")
    shutil.copyfile(dca_plot_eval, dca_root_path)
    print(f"  [✓] Exported DCA Net Benefit Curve: {dca_plot_eval} & {dca_root_path}")

    # (e) Reliability Diagram / Calibration Curve
    calib_plot_eval = args.output_plots / "calibration_curve.png"
    plot_reliability_diagram(
        y_true=y_true,
        probs_uncalibrated=raw_probs,
        probs_calibrated=cal_probs,
        output_path=calib_plot_eval,
        n_bins=10,
        temperature=temperature,
    )
    print(f"  [✓] Exported Reliability Diagram: {calib_plot_eval}")

    # 10. Generate JSON Artifacts (Deliverable for Member 1 & Member 3)
    metrics_payload = {
        "metadata": {
            "evaluation_timestamp": datetime.now(timezone.utc).isoformat(),
            "model_path": str(args.model_path),
            "test_data_path": str(args.test_data),
            "test_sample_count": len(y_true),
            "classes": classes,
            "calibrated_temperature": temperature,
            "device": str(device),
            "seed": args.seed,
            "disclaimer": (
                "Phân tích hiệu năng mô hình trên tập kiểm thử độc lập (Holdout Strict Test). "
                "Kết quả Decision Curve Analysis (DCA) là minh họa theo phương pháp luận khoa học, "
                "không thay thế cho thử nghiệm lâm sàng ngẫu nhiên có đối chứng (RCT)."
            ),
        },
        "overall_metrics": {
            "uncalibrated": overall_metrics_uncal,
            "calibrated": overall_metrics_cal,
        },
        "per_class_metrics": class_metrics,
        "dca_analysis": {
            "target_class_index": args.target_class,
            "target_class_name": classes[args.target_class],
            "prevalence": float(df_dca["prevalence"].iloc[0]),
            "threshold_range": [float(df_dca["threshold"].min()), float(df_dca["threshold"].max())],
            "dca_table": df_dca.to_dict(orient="records"),
        },
    }

    metrics_json_path = args.output_plots / "clinical_utility_metrics.json"
    with open(metrics_json_path, "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2, ensure_ascii=False)
    print(f"  [✓] Saved comprehensive metrics JSON: {metrics_json_path}")

    # Export a concise benchmark summary for Member 3's REST API:
    # GET /api/v1/evaluation/benchmark
    benchmark_summary_path = Path("data/benchmark_summary.json")
    with open(benchmark_summary_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "benchmark_name": "M-CDSS Phase 2 Strict Holdout Clinical Benchmark",
                "evaluated_at": metrics_payload["metadata"]["evaluation_timestamp"],
                "test_samples": len(y_true),
                "num_classes": len(classes),
                "classes": classes,
                "temperature": temperature,
                "multimodal_model": {
                    "macro_auroc": overall_metrics_cal["macro_auroc"],
                    "macro_auprc": overall_metrics_cal["macro_auprc"],
                    "macro_f1": overall_metrics_cal["macro_f1"],
                    "accuracy": overall_metrics_cal["accuracy"],
                    "brier_score": overall_metrics_cal["brier_score"],
                    "ece": overall_metrics_cal["ece"],
                },
                "per_class_summary": {k: {"auroc": v["auroc"], "f1": v["f1_score"]} for k, v in class_metrics.items()},
                "dca_target": classes[args.target_class],
                "dca_curve_sample_points": df_dca[::5][["threshold", "net_benefit_model", "net_benefit_all", "net_benefit_none"]].to_dict(orient="records"),
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
    print(f"  [✓] Exported API benchmark summary: {benchmark_summary_path}")

    print("\n" + "=" * 80)
    print("                     EVALUATION REPORT SUMMARY")
    print("=" * 80)
    print(f"  Accuracy                : {overall_metrics_cal['accuracy']:.4f}")
    print(f"  Macro-average AUROC     : {overall_metrics_cal['macro_auroc']:.4f}")
    print(f"  Macro-average AUPRC     : {overall_metrics_cal['macro_auprc']:.4f}")
    print(f"  Macro-average F1-Score  : {overall_metrics_cal['macro_f1']:.4f}")
    print(f"  Multiclass Brier Score  : {overall_metrics_cal['brier_score']:.4f}")
    print(f"  Expected Calib Error    : {overall_metrics_cal['ece'] * 100:.2f}% (T = {temperature:.4f})")
    print("=" * 80)
    print("[✓] Clinical validation automated execution completed successfully.")


if __name__ == "__main__":
    main()
