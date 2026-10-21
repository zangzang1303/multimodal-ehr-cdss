"""
Unit Tests for Baselines Benchmark Results Integrity
Multimodal EHR CDSS - Phase 1 / Backlog 03 (Task 3.1)
Verifies:
1. Existence and valid JSON structure of data/baseline_results.json.
2. Presence of all 3 baseline model keys:
   - baseline_1_classical_tabular
   - baseline_2_tabular_deep
   - baseline_3_text_only
3. Mathematical metric bounds:
   - 0.5 < macro_auroc <= 1.0
   - 0.0 <= macro_f1 <= 1.0
   - 0.0 <= brier_score <= 1.0
   - 0.0 <= ece <= 1.0
   - Absence of NaN, Inf, or null values in numerical fields.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


BENCHMARK_FILE = Path("data/baseline_results.json")
REQUIRED_BASELINE_KEYS = [
    "baseline_1_classical_tabular",
    "baseline_2_tabular_deep",
    "baseline_3_text_only",
]


def test_baseline_results_file_exists():
    """Verify data/baseline_results.json exists on disk."""
    assert BENCHMARK_FILE.exists(), f"Benchmark file {BENCHMARK_FILE} does not exist!"
    assert BENCHMARK_FILE.stat().st_size > 0, f"Benchmark file {BENCHMARK_FILE} is empty!"


def test_baseline_results_contains_all_models():
    """Verify presence of all 3 required baseline keys in the benchmark results."""
    with open(BENCHMARK_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "_mock_status" not in data
    assert data["benchmark_metadata"]["patient_level_split"] is True

    # Check either in top-level or in 'results' dict
    source_dict = data.get("results", data)
    for model_key in REQUIRED_BASELINE_KEYS:
        assert (
            model_key in source_dict or model_key in data
        ), f"Required baseline '{model_key}' missing from benchmark results!"


def test_baseline_metric_mathematical_bounds():
    """
    Verify numerical metrics conform to valid mathematical ranges:
    - 0.5 < macro_auroc <= 1.0 (better than random guess)
    - 0.0 <= macro_f1 <= 1.0
    - 0.0 <= brier_score <= 1.0
    - 0.0 <= ece <= 1.0
    - No NaN, Inf, or null values.
    """
    with open(BENCHMARK_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    source_dict = data.get("results", data)

    for model_key in REQUIRED_BASELINE_KEYS:
        model_results = source_dict.get(model_key, data.get(model_key))
        assert model_results is not None, f"Results for '{model_key}' is None!"

        # Extract metrics
        auroc = model_results.get("macro_auroc")
        f1 = model_results.get("macro_f1")
        brier = model_results.get("brier_score")
        ece = model_results.get("ece")

        for name, val in [
            ("macro_auroc", auroc),
            ("macro_f1", f1),
            ("brier_score", brier),
            ("ece", ece),
        ]:
            assert val is not None, f"Field '{name}' in '{model_key}' is null/None!"
            assert isinstance(val, (int, float)), f"Field '{name}' in '{model_key}' is not numeric!"
            assert not math.isnan(val), f"Field '{name}' in '{model_key}' is NaN!"
            assert not math.isinf(val), f"Field '{name}' in '{model_key}' is Inf!"

        # Verify mathematical constraints
        assert (
            0.5 < auroc <= 1.0
        ), f"{model_key} macro_auroc ({auroc}) must be in (0.5, 1.0]"
        assert 0.0 <= f1 <= 1.0, f"{model_key} macro_f1 ({f1}) must be in [0.0, 1.0]"
        assert (
            0.0 <= brier <= 1.0
        ), f"{model_key} brier_score ({brier}) must be in [0.0, 1.0]"
        assert 0.0 <= ece <= 1.0, f"{model_key} ece ({ece}) must be in [0.0, 1.0]"
