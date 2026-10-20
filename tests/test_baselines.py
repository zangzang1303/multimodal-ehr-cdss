"""Acceptance tests for backlog 2 member 1 deliverables."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import torch

from src.evaluation.metrics import compute_multiclass_metrics
from src.models.baselines import (
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
    ClassicalTabularBaseline,
    DummyTextBackbone,
    TabularDeepBaseline,
    TextOnlyBaseline,
)

ROOT = Path(__file__).resolve().parents[1]


def sample_frame(size: int = 32) -> tuple[pd.DataFrame, np.ndarray]:
    rng = np.random.default_rng(42)
    frame = pd.DataFrame(rng.normal(size=(size, 9)), columns=NUMERICAL_FEATURES)
    frame["age"] = rng.integers(18, 90, size=size)
    frame["gender"] = rng.choice(["M", "F", "OTHER"], size=size)
    frame["smoking_status"] = rng.choice(["NEVER", "FORMER", "CURRENT"], size=size)
    frame["history_hypertension"] = rng.integers(0, 2, size=size)
    frame["history_diabetes"] = rng.integers(0, 2, size=size)
    return frame, np.resize(np.arange(4), size)


def test_classical_baseline_fit_predict_probability():
    frame, labels = sample_frame()
    model = ClassicalTabularBaseline(
        estimator="random_forest", estimator_params={"n_estimators": 12, "max_depth": 4}
    ).fit(frame, labels)
    assert model.predict(frame.iloc[:5]).shape == (5,)
    probabilities = model.predict_proba(frame.iloc[:5])
    assert probabilities.shape == (5, 4)
    assert np.allclose(probabilities.sum(axis=1), 1.0)
    assert set(NUMERICAL_FEATURES + CATEGORICAL_FEATURES).issubset(frame.columns)


def test_deep_and_text_forward_shapes():
    assert TabularDeepBaseline()(torch.randn(2, 9)).shape == (2, 4)
    text = TextOnlyBaseline(backbone=DummyTextBackbone(hidden_size=12))
    logits = text(torch.randint(0, 32, (2, 16)), torch.ones(2, 16, dtype=torch.long))
    assert logits.shape == (2, 4)


def test_compute_multiclass_metrics_contract():
    labels = np.tile(np.arange(4), 3)
    probabilities = np.full((12, 4), 0.1)
    probabilities[np.arange(12), labels] = 0.7
    metrics = compute_multiclass_metrics(labels, probabilities)
    assert set(metrics) == {
        "macro_auroc",
        "macro_auprc",
        "macro_f1",
        "accuracy",
        "brier_score",
        "ece",
    }
    assert all(np.isfinite(value) for value in metrics.values())
    assert metrics["accuracy"] == 1.0

    with pytest.raises(ValueError, match="sum to 1"):
        compute_multiclass_metrics(labels, probabilities * 2)


def test_run_baselines_cli_help_and_smoke_test():
    help_result = subprocess.run(
        [sys.executable, "scripts/run_baselines.py", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert help_result.returncode == 0
    for option in ("--data_dir", "--config", "--output_file", "--baseline"):
        assert option in help_result.stdout

    smoke_result = subprocess.run(
        [sys.executable, "scripts/run_baselines.py", "--smoke-test"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert smoke_result.returncode == 0, smoke_result.stderr
    assert '"text_only_logits_shape": [\n    3,\n    4\n  ]' in smoke_result.stdout
