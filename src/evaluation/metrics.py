"""Validated multiclass metrics for the Phase 1 baseline benchmark."""

from __future__ import annotations

import numpy as np
from sklearn.metrics import accuracy_score, average_precision_score, f1_score, roc_auc_score
from sklearn.preprocessing import label_binarize


def expected_calibration_error(
    y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10
) -> float:
    """Compute top-label ECE using equal-width confidence bins."""
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


def compute_multiclass_metrics(
    y_true: np.ndarray, y_prob: np.ndarray, *, n_bins: int = 10
) -> dict[str, float]:
    """Return discrimination, classification and calibration metrics."""
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
    if not np.allclose(probabilities.sum(axis=1), 1.0, atol=1e-6):
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
    }
