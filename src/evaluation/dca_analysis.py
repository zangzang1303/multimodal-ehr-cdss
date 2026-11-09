# ==============================================================================
# [MOCK / STAND-IN FILE - CHỜ MA TRẬN DỰ ĐOÁN THẬT TỪ THÀNH VIÊN 1 & 2]
# LƯU Ý QUAN TRỌNG:
# 1. Theo phân công Backlog 06 (Nhiệm vụ 1.2), module src/evaluation/dca_analysis.py
#    thuộc phạm vi của Thành viên 1 và script xuất dự đoán trên tập test.parquet từ
#    checkpoint multimodal_best.pt (scripts/evaluate_clinical_utility.py) thuộc
#    phạm vi của Thành viên 2 (Backlog 06 - Nhiệm vụ 2.2).
# 2. File này được Thành viên 3 tạo trước để phục vụ API /api/v1/evaluation/benchmark
#    và biểu đồ DCACurveChart.tsx (Backlog 06 - Nhiệm vụ 3.1 & 3.2).
# 3. Hàm _build_deterministic_test_predictions() bên dưới CHỈ LÀ DỮ LIỆU GIẢ LẬP
#    (mock fallback) khi chưa có tệp dự đoán thật data/holdout_predictions.npz
#    (hoặc .json) từ checkpoint của Thành viên 1 & 2. Tuyệt đối không dùng số liệu
#    từ hàm giả lập này làm kết quả thực nghiệm chính thức trong bài báo.
# ==============================================================================
"""
Decision Curve Analysis (DCA) Module for Multiclass Clinical Evaluation
M-CDSS Phase 2 / Backlog 06

Implements Vickers & Elkin (Medical Decision Making / BMJ, 2006) Net Benefit
formulation over One-vs-Rest (OvR) multiclass probability predictions on the
strict hold-out test cohort (N=302).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import numpy as np


DEFAULT_DCA_THRESHOLDS: List[float] = [
    round(0.05 * i, 2) for i in range(1, 13)
]  # 0.05 to 0.60


def compute_ovr_net_benefit(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float,
) -> float:
    """
    Computes macro-averaged One-vs-Rest (OvR) Net Benefit at threshold probability pt:
        NB_c(pt) = (TP_c / N) - (FP_c / N) * (pt / (1 - pt))
        NB_macro(pt) = (1 / C) * sum_{c=1..C} NB_c(pt)
    """
    if not (0.0 < threshold < 1.0):
        raise ValueError(f"threshold must be in (0, 1), got {threshold}")

    labels = np.asarray(y_true, dtype=int)
    probs = np.asarray(y_prob, dtype=float)
    n_samples, n_classes = probs.shape
    if n_samples == 0:
        raise ValueError("Empty sample array")

    exchange_weight = threshold / (1.0 - threshold)
    nb_per_class: List[float] = []

    for c in range(n_classes):
        is_pos = labels == c
        pred_pos = probs[:, c] >= threshold
        tp = float(np.sum(pred_pos & is_pos))
        fp = float(np.sum(pred_pos & (~is_pos)))
        nb_c = (tp / n_samples) - (fp / n_samples) * exchange_weight
        nb_per_class.append(nb_c)

    return float(np.mean(nb_per_class))


def compute_treat_all_net_benefit(
    y_true: np.ndarray,
    n_classes: int,
    threshold: float,
) -> float:
    """
    Computes macro-averaged One-vs-Rest Net Benefit of the 'Treat All' strategy:
        NB_all_c(pt) = prev_c - (1 - prev_c) * (pt / (1 - pt))
    """
    labels = np.asarray(y_true, dtype=int)
    n_samples = len(labels)
    exchange_weight = threshold / (1.0 - threshold)

    nb_all_list: List[float] = []
    for c in range(n_classes):
        prev_c = float(np.sum(labels == c)) / max(n_samples, 1)
        nb_all_c = prev_c - (1.0 - prev_c) * exchange_weight
        nb_all_list.append(nb_all_c)

    return float(np.mean(nb_all_list))


def compute_dca_curve_from_predictions(
    y_true: np.ndarray,
    prob_mcdss: np.ndarray,
    prob_tabular: np.ndarray,
    prob_text: np.ndarray,
    thresholds: Optional[Sequence[float]] = None,
) -> List[Dict[str, float]]:
    """
    Computes Decision Curve Analysis (DCA) table across threshold probabilities pt
    directly from true labels and model probability matrices [N, C].

    Returns for each threshold pt:
      - net_benefit_mcdss
      - net_benefit_tabular
      - net_benefit_text
      - net_benefit_treat_all
      - net_benefit_treat_none (always 0.0)
      - net_tp_gained_per_100:
            100 * max(0, NB_mcdss(pt) - max(NB_treat_all(pt), 0))
      - net_interventions_avoided_per_100:
            100 * max(0, (NB_mcdss(pt) - NB_treat_all(pt)) / (pt / (1 - pt)))
    """
    pts = list(thresholds) if thresholds is not None else DEFAULT_DCA_THRESHOLDS
    n_classes = prob_mcdss.shape[1]
    curve_points: List[Dict[str, float]] = []

    for pt in pts:
        nb_mcdss = compute_ovr_net_benefit(y_true, prob_mcdss, pt)
        nb_tab = compute_ovr_net_benefit(y_true, prob_tabular, pt)
        nb_txt = compute_ovr_net_benefit(y_true, prob_text, pt)
        nb_all = compute_treat_all_net_benefit(y_true, n_classes, pt)
        nb_none = 0.0

        best_default = max(nb_all, nb_none)
        net_tp_per_100 = 100.0 * max(0.0, nb_mcdss - best_default)

        odds = pt / (1.0 - pt)
        net_avoided_per_100 = (
            100.0 * max(0.0, (nb_mcdss - nb_all) / odds) if odds > 1e-8 else 0.0
        )

        curve_points.append(
            {
                "threshold": round(float(pt), 2),
                "net_benefit_mcdss": round(nb_mcdss, 3),
                "net_benefit_tabular": round(nb_tab, 3),
                "net_benefit_text": round(nb_txt, 3),
                "net_benefit_treat_all": round(nb_all, 3),
                "net_benefit_treat_none": round(nb_none, 3),
                "net_tp_gained_per_100": round(net_tp_per_100, 1),
                "net_interventions_avoided_per_100": round(net_avoided_per_100, 1),
            }
        )

    return curve_points


def _build_deterministic_test_predictions(
    y_true: np.ndarray,
    seed: int = 42,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Fallback calibrated simulation of probability matrices [N, 4] over the strict
    hold-out test labels (N=302) used ONLY when Member 1/2's per-sample hold-out
    prediction artifact (data/holdout_predictions.npz or .json from multimodal_best.pt)
    is not yet present on disk.
    """
    rng = np.random.default_rng(seed)
    n_samples = len(y_true)
    n_classes = 4

    def _simulate_model_probs(
        target_acc: float, true_alpha: float, noise_alpha: float
    ) -> np.ndarray:
        probs = np.zeros((n_samples, n_classes), dtype=float)
        for i, y in enumerate(y_true):
            is_correct = rng.random() < target_acc
            alpha = np.full(n_classes, noise_alpha, dtype=float)
            if is_correct:
                alpha[int(y)] = true_alpha
            else:
                wrong_cls = (int(y) + int(rng.integers(1, n_classes))) % n_classes
                alpha[wrong_cls] = true_alpha * 0.75
                alpha[int(y)] = true_alpha * 0.45
            sample_p = rng.dirichlet(alpha)
            probs[i] = sample_p
        return probs

    prob_tabular = _simulate_model_probs(
        target_acc=0.6589, true_alpha=5.2, noise_alpha=1.1
    )
    prob_text = _simulate_model_probs(
        target_acc=0.8543, true_alpha=8.5, noise_alpha=0.75
    )
    prob_mcdss = _simulate_model_probs(
        target_acc=0.8940, true_alpha=11.0, noise_alpha=0.55
    )
    return prob_mcdss, prob_tabular, prob_text


def evaluate_holdout_dca(
    audit_json_path: Optional[Path] = None,
    predictions_path: Optional[Path] = None,
    thresholds: Optional[Sequence[float]] = None,
) -> Dict[str, Any]:
    """
    Computes the Decision Curve Analysis trajectory on the strict hold-out test cohort (N=302).
    1. If a per-sample prediction artifact exported from Member 1/2's checkpoint evaluation
       exists (`data/holdout_predictions.npz` or `data/holdout_predictions.json`), loads
       the empirical `y_true`, `prob_mcdss`, `prob_tabular`, and `prob_text` directly.
    2. Otherwise, falls back to calibrated simulation over the strict test label distribution
       from `data/rebuilt_strict_split_audit.json` and marks `prediction_source` as
       `"calibrated_simulation_pending_checkpoint"`.
    """
    repo_root = Path(__file__).resolve().parents[2]
    npz_path = predictions_path or (repo_root / "data" / "holdout_predictions.npz")
    json_pred_path = repo_root / "data" / "holdout_predictions.json"

    if npz_path.exists() and npz_path.suffix == ".npz":
        loaded = np.load(npz_path)
        y_true = np.asarray(loaded["y_true"], dtype=int)
        prob_mcdss = np.asarray(loaded["prob_mcdss"], dtype=float)
        prob_tabular = np.asarray(loaded["prob_tabular"], dtype=float)
        prob_text = np.asarray(loaded["prob_text"], dtype=float)
        prediction_source = "empirical_holdout_artifact"
    elif json_pred_path.exists():
        raw = json.loads(json_pred_path.read_text(encoding="utf-8"))
        y_true = np.asarray(raw["y_true"], dtype=int)
        prob_mcdss = np.asarray(raw["prob_mcdss"], dtype=float)
        prob_tabular = np.asarray(raw["prob_tabular"], dtype=float)
        prob_text = np.asarray(raw["prob_text"], dtype=float)
        prediction_source = "empirical_holdout_artifact"
    else:
        audit_path = audit_json_path or (
            repo_root / "data" / "rebuilt_strict_split_audit.json"
        )
        y_true_opt: Optional[np.ndarray] = None
        if audit_path.exists():
            try:
                audit = json.loads(audit_path.read_text(encoding="utf-8"))
                test_counts = audit.get("class_counts", {}).get("test", {})
                if test_counts:
                    labels_list: List[int] = []
                    for cls_key in sorted(test_counts.keys(), key=lambda x: int(x)):
                        labels_list.extend([int(cls_key)] * int(test_counts[cls_key]))
                    y_true_opt = np.asarray(labels_list, dtype=int)
            except Exception:
                y_true_opt = None

        if y_true_opt is None or len(y_true_opt) == 0:
            y_true = np.array(
                [0] * 71 + [1] * 71 + [2] * 106 + [3] * 54, dtype=int
            )
        else:
            y_true = y_true_opt

        prob_mcdss, prob_tabular, prob_text = _build_deterministic_test_predictions(
            y_true, seed=42
        )
        prediction_source = "calibrated_simulation_pending_checkpoint"

    points = compute_dca_curve_from_predictions(
        y_true=y_true,
        prob_mcdss=prob_mcdss,
        prob_tabular=prob_tabular,
        prob_text=prob_text,
        thresholds=thresholds,
    )

    return {
        "n_samples": int(len(y_true)),
        "prediction_source": prediction_source,
        "threshold_points": points,
    }
