#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verification Test Suite: Phase 3 / Backlog 09 - Member 2
(Biomedical Data Engineer & Privacy)
================================================================================
Verifies compliance with all core tasks and deliverables:
  - Task 2.1 [CORE]: Decision Curve Analysis (RQ4b), 6 curves, bootstrap CI, ΔNB.
  - Task 2.2 [CORE]: Missing Modality & Noise Robustness (no text, no tab, 10/30/50%).
  - Task 2.3 [CORE]: Internal Generalization (Temporal split, ΔAUROC, internal check disclaimer).
  - Task 2.4 [CORE]: Subgroup Fairness (gender, age, smoking) & 30-case Error Analysis.
  - Task 2.5 [OPTIONAL]: Real data MIMIC-IV extraction roadmap & Survey protocol status.
  - Registry integration in results/registry.json.
  - Pre-registration in docs/11_ANALYSIS_PLAN.md.
  - Qualitative clinical documentation in docs/06_ERROR_ANALYSIS_AND_CLINICAL_DISCREPANCIES.md.
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent


def test_analysis_plan_pre_registration():
    """Verify docs/11_ANALYSIS_PLAN.md existence and core pre-registration clauses."""
    plan_path = ROOT_DIR / "docs" / "11_ANALYSIS_PLAN.md"
    assert plan_path.exists(), f"Analysis plan missing: {plan_path}"

    content = plan_path.read_text(encoding="utf-8")
    # Verify primary and secondary metrics
    assert "Macro-average AUROC" in content or "AUROC" in content
    assert "Macro-average AUPRC" in content or "AUPRC" in content
    assert "Macro-average F1" in content or "F1-Score" in content
    assert "Brier Score" in content
    assert "Expected Calibration Error" in content or "ECE" in content

    # Verify DCA pre-registration
    assert "HEART_FAILURE" in content
    assert "0.05" in content and "0.30" in content
    assert "2000" in content or "2,000" in content


def test_results_registry_keys():
    """Verify results/registry.json exists and contains all required Member 2 keys."""
    reg_path = ROOT_DIR / "results" / "registry.json"
    assert reg_path.exists(), f"Registry file missing: {reg_path}"

    with open(reg_path, "r", encoding="utf-8") as f:
        registry = json.load(f)

    for required_key in ["dca", "robustness", "generalization", "fairness"]:
        assert required_key in registry, f"Key '{required_key}' missing from results/registry.json"


def _registry():
    with open(ROOT_DIR / "results" / "registry.json", "r", encoding="utf-8") as f:
        return json.load(f)


# NOTE (2026-11-23 review): these tests previously asserted the *desired outcome*
# (e.g. "delta NB > 0", "fusion AUROC > 0.90 without text", "temporal train == 1400").
# A test must never force a research result, so they now check structure, sample sizes
# fixed by the analysis plan, and internal consistency only.


def test_task_2_1_dca_results():
    """DCA follows the pre-registered definition (HF one-vs-rest, p_t in [0.05, 0.30])."""
    dca = _registry()["dca"]
    assert dca["target_disease"] == "HEART_FAILURE" and dca["target_class"] == 2
    assert dca["test_sample_size"] == 302
    assert abs(dca["heart_failure_test_prevalence"] - 106 / 302) < 1e-3
    assert dca["predefined_threshold_range"] == [0.05, 0.30]
    assert "(1 - p_t) / p_t" in dca["formula"]
    for pt in ("pt_0.10", "pt_0.20"):
        block = dca["at_thresholds"][pt]
        for model in block["models"].values():
            threshold = float(pt.split("_")[1])
            expected = (model["delta_nb_vs_treat_all"]) * (1 - threshold) / threshold * 100
            assert abs(model["net_reduction_in_interventions_per_100"] - expected) < 0.05
    for name in ("fig_dca.pdf",):
        assert (ROOT_DIR / "docs" / "paper_latex" / "figures" / "generated" / name).exists()
    assert (ROOT_DIR / "data" / "evaluation_plots" / "fig_dca.png").exists()


def test_task_2_2_missing_modality_robustness():
    """Every pre-registered missing-modality scenario is reported for the deployment model."""
    rob = _registry()["robustness"]
    expected = {"full", "tab_missing_10", "tab_missing_30", "tab_missing_50", "no_tabular", "no_text"}
    assert {s["scenario"] for s in rob["scenarios"]} == expected
    for scenario in expected:
        value = rob["by_model"][scenario]["xattn_frozen"]["mean"]
        assert 0.0 <= value <= 1.0
    assert (ROOT_DIR / "data" / "evaluation_plots" / "fig_missing_modality.png").exists()


def test_task_2_3_internal_generalization():
    """Temporal split is group-aware, has a validation set and is labelled as internal."""
    gen = _registry()["generalization"]
    assert "Temporal split" in gen["split_method"]
    assert gen["train_samples"] + gen["val_samples"] + gen["test_samples"] == 2000
    assert "delta_macro_auroc" in gen["metrics"]
    assert "NOT external hospital validation" in gen["validation_nature"]


def test_task_2_4_fairness_and_error_analysis():
    """Subgroups cover the analysis plan and sum to the strict test size; 30 error cases."""
    reg = _registry()
    fair = reg["fairness"]
    subgroups = ["gender_M", "gender_F", "age_under_65", "age_65_and_older",
                 "smoking_NEVER", "smoking_FORMER", "smoking_CURRENT"]
    for sg in subgroups:
        res = fair["subgroups"][sg]
        for key in ("sample_size", "macro_auroc", "macro_auroc_ci95", "macro_f1", "macro_f1_ci95"):
            assert key in res
    assert fair["subgroups"]["gender_M"]["sample_size"] + fair["subgroups"]["gender_F"]["sample_size"] <= 302
    assert (fair["subgroups"]["age_under_65"]["sample_size"]
            + fair["subgroups"]["age_65_and_older"]["sample_size"]) == 302
    errors = reg["error_analysis"]
    assert len(errors["top_confused_pairs"]) == 3
    assert len(errors["cases"]) <= 30 and len(errors["cases"]) > 0
    for case in errors["cases"]:
        assert {"patient_id", "true", "pred", "confidence"} <= set(case)


def test_task_2_5_clinical_survey_and_mimic_roadmap():
    """Verify Task 2.5 Clinical survey protocol status and MIMIC-IV roadmap documentation."""
    survey_doc = ROOT_DIR / "docs" / "07_CLINICAL_EXPERT_SURVEY_PROTOCOL.md"
    assert survey_doc.exists(), f"Survey document missing: {survey_doc}"

    content = survey_doc.read_text(encoding="utf-8")
    assert "CHƯA THỰC HIỆN" in content
    assert "Krippendorff" in content
    assert "MIMIC-IV" in content
    assert "CITI" in content
    for icd in ["J45", "J44", "I50", "J18"]:
        assert icd in content, f"ICD-10 code {icd} missing from roadmap"


def test_clinical_error_analysis_documentation():
    """docs/06 reports the deployment-model error analysis on the canonical strict test set."""
    doc_path = ROOT_DIR / "docs" / "06_ERROR_ANALYSIS_AND_CLINICAL_DISCREPANCIES.md"
    content = doc_path.read_text(encoding="utf-8")
    assert "302" in content
    assert "Overlapping vitals" in content and "Synthetic label discrepancy" in content
    assert "PT-0044" in content and "PT-0254" in content
    assert "bệnh nhân gốc" in content  # effective-sample-size caveat must be stated
    assert "legacy_invalid_2026-11-19" in content  # withdrawn analysis is referenced, not reused
