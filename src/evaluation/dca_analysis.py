"""
Decision Curve Analysis (DCA) for Multimodal EHR Clinical Decision Support System.
Calculates clinical net benefit across decision threshold probabilities:
    Net Benefit(p_t) = (TP / N) - (FP / N) * (p_t / (1 - p_t))

========================================================================================
COLLABORATION & HANDOFF NOTES:
----------------------------------------------------------------------------------------
[MEMBER 1 - Lead ML / Modeling]:
  - Member 1 owns task 1.2 and can override or refine this module.
  - Member 1 can customize the default target disease (e.g., HEART_FAILURE vs ASTHMA/COPD),
    add bootstrap 95% confidence intervals (Net Benefit CI), or include unimodal baseline curves.
[MEMBER 3 - Full-Stack AI & Frontend]:
  - Member 3 should use the JSON output from `calculate_net_benefit` / `scripts/evaluate_clinical_utility.py`
    to feed the interactive DCA Recharts/Chart.js component in the doctor's web UI.
========================================================================================
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Sequence

os.environ.setdefault("MPLCONFIGDIR", tempfile.gettempdir())
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# Default clinical disease targets & hypothetical interventions
DEFAULT_TARGET_ACTIONS = {
    0: ("ASTHMA", "Chỉ định Phế dung ký giãn phế quản (Bronchodilator Reversibility Test)"),
    1: ("COPD", "Chỉ định Hô hấp ký xác định giới hạn luồng khí cố định & Tối ưu phác đồ LAMA/LABA"),
    2: ("HEART_FAILURE", "Chỉ định Siêu âm tim Doppler màu cấp cứu & Định lượng NT-proBNP"),
    3: ("PNEUMONIA", "Chỉ định Chụp X-quang ngực thẳng & Kháng sinh theo kinh nghiệm"),
}


def calculate_net_benefit(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    target_class: int = 2,
    thresholds: np.ndarray | None = None,
) -> pd.DataFrame:
    """
    Calculate Net Benefit across decision threshold probabilities (p_t) for One-vs-Rest decision.

    Formula:
        Net Benefit(p_t) = (TP / N) - (FP / N) * (p_t / (1 - p_t))
        Treat All(p_t)   = Prevalence - (1 - Prevalence) * (p_t / (1 - p_t))
        Treat None(p_t)  = 0.0

    Args:
        y_true: 1D array of ground truth class integer labels [0 .. K-1].
        y_prob: 2D array of predicted class probabilities [N, K].
        target_class: Index of the target class to evaluate.
        thresholds: 1D array of decision thresholds (default 0.05 to 0.70).

    Returns:
        pd.DataFrame with columns:
            ['threshold', 'net_benefit_model', 'net_benefit_all', 'net_benefit_none',
             'tp', 'fp', 'fn', 'tn', 'prevalence', 'exchange_rate']
    """
    labels = np.asarray(y_true, dtype=int)
    probs = np.asarray(y_prob, dtype=float)

    if labels.ndim != 1:
        raise ValueError("y_true must be a 1D vector of class indices")
    if probs.ndim != 2 or probs.shape[0] != labels.shape[0]:
        raise ValueError("y_prob must be a 2D matrix matching y_true sample count")
    if target_class < 0 or target_class >= probs.shape[1]:
        raise ValueError(f"target_class={target_class} is out of bounds for {probs.shape[1]} classes")

    if thresholds is None:
        thresholds = np.linspace(0.05, 0.70, 50)

    n_samples = len(labels)
    is_disease = (labels == target_class).astype(int)
    prevalence = float(np.mean(is_disease))
    prob_target = probs[:, target_class]

    records = []
    for pt in thresholds:
        # Avoid division by zero when threshold is 1.0
        if pt >= 0.999:
            continue

        pred_positive = (prob_target >= pt).astype(int)
        tp = int(np.sum((pred_positive == 1) & (is_disease == 1)))
        fp = int(np.sum((pred_positive == 1) & (is_disease == 0)))
        fn = int(np.sum((pred_positive == 0) & (is_disease == 1)))
        tn = int(np.sum((pred_positive == 0) & (is_disease == 0)))

        exchange_rate = float(pt / (1.0 - pt))
        nb_model = (tp / n_samples) - (fp / n_samples) * exchange_rate
        nb_all = prevalence - (1.0 - prevalence) * exchange_rate
        nb_none = 0.0

        records.append({
            "threshold": float(pt),
            "net_benefit_model": float(nb_model),
            "net_benefit_all": float(nb_all),
            "net_benefit_none": float(nb_none),
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "tn": tn,
            "prevalence": prevalence,
            "exchange_rate": exchange_rate,
        })

    return pd.DataFrame(records)


def plot_dca_curve(
    df_dca: pd.DataFrame,
    output_path: str | Path = "data/dca_curve.png",
    target_name: str = "HEART_FAILURE (Suy tim)",
    hypothetical_action: str = "Siêu âm tim cấp & định lượng NT-proBNP",
    sample_size: int = 286,
    prevalence: float | None = None,
) -> Path:
    """
    Render and save a high-resolution Decision Curve Analysis (Net Benefit) figure.

    NOTE FOR MEMBER 1:
        Member 1 can override styling or provide comparative baseline curves here.
    """
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    prev_val = prevalence if prevalence is not None else float(df_dca["prevalence"].iloc[0])

    plt.figure(figsize=(9, 6.5), dpi=300)
    ax = plt.subplot(1, 1, 1)

    # Plot Treat None (Zero line)
    ax.axhline(0.0, color="#64748b", linestyle=":", linewidth=1.5, label="Chiến lược: Không can thiệp (Treat None)")

    # Plot Treat All
    ax.plot(
        df_dca["threshold"],
        df_dca["net_benefit_all"],
        color="#94a3b8",
        linestyle="--",
        linewidth=1.8,
        label=f"Chiến lược: Can thiệp tất cả (Treat All | Prev={prev_val:.1%})",
    )

    # Plot Multimodal M-CDSS
    ax.plot(
        df_dca["threshold"],
        df_dca["net_benefit_model"],
        color="#2563eb",
        linestyle="-",
        linewidth=2.4,
        label="Mô hình Multimodal CDSS (Cross-Attention)",
    )

    # Format Axes and Labels
    ax.set_xlim([0.05, 0.65])
    y_min = max(-0.15, float(df_dca["net_benefit_model"].min()) - 0.05)
    y_max = max(prev_val + 0.08, float(df_dca["net_benefit_model"].max()) + 0.05)
    ax.set_ylim([y_min, y_max])

    ax.set_xlabel("Ngưỡng xác suất can thiệp lâm sàng ($p_t$)", fontsize=11, fontweight="bold", labelpad=8)
    ax.set_ylabel("Lợi ích ròng (Clinical Net Benefit)", fontsize=11, fontweight="bold", labelpad=8)
    ax.set_title(
        f"Phân Tích Đường Cong Quyết Định (Decision Curve Analysis - DCA)\n"
        f"Bệnh đích: {target_name} | Hành động: {hypothetical_action}\n"
        f"[Holdout Strict Test Set: N = {sample_size} | Nghiên cứu minh họa, không thay thế thử nghiệm lâm sàng]",
        fontsize=11,
        fontweight="bold",
        pad=12,
        color="#0f172a",
    )

    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="upper right", fontsize=9, framealpha=0.95)

    # Highlight clinical reasonable threshold window [0.10, 0.50]
    ax.axvspan(0.10, 0.50, color="#3b82f6", alpha=0.08, label="Dải ngưỡng lâm sàng khuyến nghị (10% - 50%)")

    plt.tight_layout()
    plt.savefig(out_file, dpi=300, bbox_inches="tight")
    plt.close()

    return out_file

