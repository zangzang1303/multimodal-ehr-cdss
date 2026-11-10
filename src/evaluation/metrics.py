

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Sequence

os.environ.setdefault("MPLCONFIGDIR", tempfile.gettempdir())
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, average_precision_score, f1_score, roc_auc_score
from sklearn.preprocessing import label_binarize


def expected_calibration_error(
    y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10
) -> float:
    
    if n_bins < 1:
        raise ValueError("n_bins must be positive")
    confidence = y_prob.max(axis=1)
    prediction = y_prob.argmax(axis=1)
    correct = prediction == y_true
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    for index in range(n_bins):
        lower, upper = edges[index], edges[index + 1]
        in_bin = (confidence > lower) & (confidence <= upper)
        if index == 0:
            in_bin |= confidence == 0.0
        if in_bin.any():
            ece += float(in_bin.mean()) * abs(
                float(correct[in_bin].mean()) - float(confidence[in_bin].mean())
            )
    return float(ece)


def maximum_calibration_error(
    y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10
) -> float:
    if n_bins < 1:
        raise ValueError("n_bins must be positive")
    confidence = y_prob.max(axis=1)
    prediction = y_prob.argmax(axis=1)
    correct = prediction == y_true
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    mce = 0.0
    for index in range(n_bins):
        lower, upper = edges[index], edges[index + 1]
        in_bin = (confidence > lower) & (confidence <= upper)
        if index == 0:
            in_bin |= confidence == 0.0
        if in_bin.any():
            calibration_gap = abs(
                float(correct[in_bin].mean()) - float(confidence[in_bin].mean())
            )
            if calibration_gap > mce:
                mce = calibration_gap
    return float(mce)


def compute_calibration_bins(
    y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10
) -> dict[str, np.ndarray]:
    
    confidence = y_prob.max(axis=1)
    prediction = y_prob.argmax(axis=1)
    correct = prediction == y_true
    edges = np.linspace(0.0, 1.0, n_bins + 1)

    bin_acc = np.zeros(n_bins)
    bin_conf = np.zeros(n_bins)
    bin_counts = np.zeros(n_bins, dtype=int)

    for index in range(n_bins):
        lower, upper = edges[index], edges[index + 1]
        in_bin = (confidence > lower) & (confidence <= upper)
        if index == 0:
            in_bin |= confidence == 0.0
        bin_counts[index] = int(in_bin.sum())
        if in_bin.any():
            bin_acc[index] = float(correct[in_bin].mean())
            bin_conf[index] = float(confidence[in_bin].mean())
        else:
            bin_acc[index] = np.nan
            bin_conf[index] = (lower + upper) / 2.0

    return {
        "bin_acc": bin_acc,
        "bin_conf": bin_conf,
        "bin_counts": bin_counts,
        "edges": edges,
    }


def compute_multiclass_metrics(
    y_true: np.ndarray, y_prob: np.ndarray, *, n_bins: int = 10
) -> dict[str, float]:
   
    labels = np.asarray(y_true)
    probabilities = np.asarray(y_prob, dtype=float)
    if labels.ndim != 1:
        raise ValueError("y_true must be a one-dimensional label vector")
    if probabilities.ndim != 2 or probabilities.shape[0] != labels.shape[0]:
        raise ValueError("y_prob must have shape [n_samples, n_classes]")
    if labels.size == 0 or probabilities.shape[1] < 2:
        raise ValueError("At least one sample and two classes are required")
    if not np.isfinite(probabilities).all() or (probabilities < 0).any():
        raise ValueError("y_prob must contain finite, non-negative probabilities")
    if not np.allclose(probabilities.sum(axis=1), 1.0, atol=1e-5):
        raise ValueError("Each y_prob row must sum to 1")

    num_classes = probabilities.shape[1]
    expected_labels = np.arange(num_classes)
    if not np.isin(labels, expected_labels).all():
        raise ValueError(f"y_true labels must be integers in [0, {num_classes - 1}]")
    present = np.unique(labels)
    if len(present) != num_classes:
        raise ValueError("AUROC/AUPRC require at least one true sample from every class")

    one_hot = label_binarize(labels, classes=expected_labels)
    prediction = probabilities.argmax(axis=1)
    brier = np.mean(np.sum((probabilities - one_hot) ** 2, axis=1))
    return {
        "macro_auroc": float(
            roc_auc_score(labels, probabilities, multi_class="ovr", average="macro")
        ),
        "macro_auprc": float(average_precision_score(one_hot, probabilities, average="macro")),
        "macro_f1": float(f1_score(labels, prediction, average="macro")),
        "accuracy": float(accuracy_score(labels, prediction)),
        "brier_score": float(brier),
        "ece": expected_calibration_error(labels, probabilities, n_bins=n_bins),
        "mce": maximum_calibration_error(labels, probabilities, n_bins=n_bins),
    }


def plot_reliability_diagram(
    y_true: np.ndarray,
    probs_uncalibrated: np.ndarray,
    probs_calibrated: np.ndarray,
    output_path: str | Path = "data/calibration_curve.png",
    n_bins: int = 10,
    temperature: float = 1.0,
) -> Path:
   
    labels = np.asarray(y_true)
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    uncal = compute_calibration_bins(labels, probs_uncalibrated, n_bins=n_bins)
    cal = compute_calibration_bins(labels, probs_calibrated, n_bins=n_bins)

    uncal_ece = expected_calibration_error(labels, probs_uncalibrated, n_bins=n_bins)
    uncal_mce = maximum_calibration_error(labels, probs_uncalibrated, n_bins=n_bins)
    cal_ece = expected_calibration_error(labels, probs_calibrated, n_bins=n_bins)
    cal_mce = maximum_calibration_error(labels, probs_calibrated, n_bins=n_bins)

    one_hot = label_binarize(labels, classes=np.arange(probs_calibrated.shape[1]))
    brier_uncal = float(np.mean(np.sum((probs_uncalibrated - one_hot) ** 2, axis=1)))
    brier_cal = float(np.mean(np.sum((probs_calibrated - one_hot) ** 2, axis=1)))

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(8, 9), gridspec_kw={"height_ratios": [3, 1]}, dpi=150
    )

    ax1.plot([0, 1], [0, 1], "k--", label="Perfect Calibration (Ideal)", linewidth=1.5, alpha=0.7)

    uncal_valid = ~np.isnan(uncal["bin_acc"])
    cal_valid = ~np.isnan(cal["bin_acc"])

    ax1.plot(
        uncal["bin_conf"][uncal_valid],
        uncal["bin_acc"][uncal_valid],
        "s-",
        color="#d9534f",
        label=f"Uncalibrated (ECE={uncal_ece*100:.2f}%, MCE={uncal_mce*100:.2f}%, Brier={brier_uncal:.4f})",
        linewidth=2,
        markersize=6,
    )
    ax1.plot(
        cal["bin_conf"][cal_valid],
        cal["bin_acc"][cal_valid],
        "o-",
        color="#2b7bba",
        label=f"Calibrated (T={temperature:.3f}, ECE={cal_ece*100:.2f}%, MCE={cal_mce*100:.2f}%, Brier={brier_cal:.4f})",
        linewidth=2,
        markersize=6,
    )

    ax1.set_xlim([0.0, 1.0])
    ax1.set_ylim([0.0, 1.0])
    ax1.set_ylabel("Empirical Accuracy", fontsize=11, fontweight="bold")
    ax1.set_title(
        "Multimodal CDSS Reliability Diagram (10 Confidence Bins)\nStrict Holdout Test Set",
        fontsize=13,
        fontweight="bold",
        pad=12,
    )
    ax1.grid(True, linestyle=":", alpha=0.6)
    ax1.legend(loc="upper left", fontsize=9, framealpha=0.95)

    bin_centers = (uncal["edges"][:-1] + uncal["edges"][1:]) / 2.0
    width = 0.035
    ax2.bar(
        bin_centers - width / 2,
        uncal["bin_counts"],
        width=width,
        color="#d9534f",
        alpha=0.6,
        label="Uncalibrated",
    )
    ax2.bar(
        bin_centers + width / 2,
        cal["bin_counts"],
        width=width,
        color="#2b7bba",
        alpha=0.6,
        label="Calibrated",
    )
    ax2.set_xlim([0.0, 1.0])
    ax2.set_xlabel("Mean Confidence Score", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Sample Count", fontsize=11, fontweight="bold")
    ax2.grid(True, linestyle=":", alpha=0.5)
    ax2.legend(loc="upper left", fontsize=8)

    plt.tight_layout()
    fig.savefig(out_file, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_file


def compute_subgroup_fairness(
    df: pd.DataFrame,
    y_prob: np.ndarray,
    target_col: str = "diagnosis_label",
    n_bootstrap: int = 500,
    seed: int = 42,
    output_path: str | Path | None = "data/fairness_report.json",
) -> dict[str, Any]:
  
    rng = np.random.RandomState(seed)
    y_true = df[target_col].to_numpy(dtype=int)
    predictions = y_prob.argmax(axis=1)

    subgroups: dict[str, dict[str, Any]] = {}

    slices: dict[str, np.ndarray] = {}

    if "gender" in df.columns:
        for g_val in df["gender"].dropna().unique():
            slices[f"gender_{g_val}"] = (df["gender"] == g_val).to_numpy()

    if "age" in df.columns:
        slices["age_under_65"] = (df["age"] < 65).to_numpy()
        slices["age_65_and_above"] = (df["age"] >= 65).to_numpy()

    for group_name, mask in slices.items():
        n_samples = int(mask.sum())
        if n_samples == 0:
            continue

        grp_true = y_true[mask]
        grp_prob = y_prob[mask]
        grp_pred = predictions[mask]

        acc = float(accuracy_score(grp_true, grp_pred))
        f1 = float(f1_score(grp_true, grp_pred, average="macro", zero_division=0))

        num_classes_in_group = len(np.unique(grp_true))
        auroc = None
        if num_classes_in_group == y_prob.shape[1]:
            try:
                auroc = float(roc_auc_score(grp_true, grp_prob, multi_class="ovr", average="macro"))
            except Exception:
                auroc = None

        boot_f1s = []
        boot_accs = []
        boot_aurocs = []
        for _ in range(n_bootstrap):
            idx = rng.choice(n_samples, size=n_samples, replace=True)
            b_true = grp_true[idx]
            b_pred = grp_pred[idx]
            boot_f1s.append(f1_score(b_true, b_pred, average="macro", zero_division=0))
            boot_accs.append(accuracy_score(b_true, b_pred))
            if len(np.unique(b_true)) == y_prob.shape[1]:
                try:
                    boot_aurocs.append(
                        roc_auc_score(b_true, grp_prob[idx], multi_class="ovr", average="macro")
                    )
                except Exception:
                    pass

        f1_ci95 = [float(np.percentile(boot_f1s, 2.5)), float(np.percentile(boot_f1s, 97.5))]
        acc_ci95 = [float(np.percentile(boot_accs, 2.5)), float(np.percentile(boot_accs, 97.5))]
        auroc_ci95 = (
            [float(np.percentile(boot_aurocs, 2.5)), float(np.percentile(boot_aurocs, 97.5))]
            if len(boot_aurocs) > 30
            else None
        )

        subgroups[group_name] = {
            "sample_size": n_samples,
            "sample_ratio": float(n_samples / len(df)),
            "accuracy": acc,
            "accuracy_ci95": acc_ci95,
            "macro_f1": f1,
            "macro_f1_ci95": f1_ci95,
            "macro_auroc": auroc,
            "macro_auroc_ci95": auroc_ci95,
        }

    gender_f1_gap = None
    if "gender_M" in subgroups and "gender_F" in subgroups:
        gender_f1_gap = abs(subgroups["gender_M"]["macro_f1"] - subgroups["gender_F"]["macro_f1"])

    age_f1_gap = None
    if "age_under_65" in subgroups and "age_65_and_above" in subgroups:
        age_f1_gap = abs(
            subgroups["age_under_65"]["macro_f1"] - subgroups["age_65_and_above"]["macro_f1"]
        )

    report = {
        "metadata": {
            "total_test_samples": len(df),
            "n_bootstrap": n_bootstrap,
            "seed": seed,
            "disclaimer": (
                "Phân tích công bằng phân nhóm trên dữ liệu tổng hợp (Synthea/MTSamples) "
                "không chứng minh hoặc đảm bảo tính công bằng trên bệnh nhân lâm sàng thực tế."
            ),
        },
        "disparities": {
            "gender_max_f1_disparity": gender_f1_gap,
            "age_senior_f1_disparity": age_f1_gap,
        },
        "subgroups": subgroups,
    }

    if output_path:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    return report
