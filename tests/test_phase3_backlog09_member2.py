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


def test_task_2_1_dca_results():
    """Verify Task 2.1 Decision Curve Analysis results and artifacts."""
    reg_path = ROOT_DIR / "results" / "registry.json"
    with open(reg_path, "r", encoding="utf-8") as f:
        dca_data = json.load(f)["dca"]

    assert dca_data["target_disease"] == "HEART_FAILURE"
    assert dca_data["target_class"] == 2
    assert dca_data["test_sample_size"] == 302
    assert abs(dca_data["heart_failure_test_prevalence"] - 0.350993) < 1e-4

    # Thresholds 0.10 and 0.20
    m_10 = dca_data["metrics_at_pt_0_10"]["cross_attention"]
    assert "net_benefit" in m_10
    assert "delta_nb_vs_treat_all" in m_10
    assert m_10["delta_nb_vs_treat_all"] > 0
    assert m_10["avoided_interventions_per_100_vs_all"] > 0

    m_20 = dca_data["metrics_at_pt_0_20"]["cross_attention"]
    assert "net_benefit" in m_20
    assert "delta_nb_vs_treat_all" in m_20
    assert m_20["delta_nb_vs_treat_all"] > 0
    assert m_20["avoided_interventions_per_100_vs_all"] > 0

    # Verify plots
    pdf_path = ROOT_DIR / "data" / "evaluation_plots" / "fig_dca_curve.pdf"
    png_path = ROOT_DIR / "data" / "evaluation_plots" / "dca_curve.png"
    assert pdf_path.exists(), f"DCA PDF plot missing: {pdf_path}"
    assert png_path.exists(), f"DCA PNG plot missing: {png_path}"


def test_task_2_2_missing_modality_robustness():
    """Verify Task 2.2 Missing Modality & Noise Robustness results."""
    reg_path = ROOT_DIR / "results" / "registry.json"
    with open(reg_path, "r", encoding="utf-8") as f:
        rob_data = json.load(f)["robustness"]

    required_conditions = [
        "full_multimodal",
        "drop_10pct_tabular",
        "drop_30pct_tabular",
        "drop_50pct_tabular",
        "complete_tabular_loss",
        "complete_text_loss",
    ]
    for cond in required_conditions:
        assert cond in rob_data["results"], f"Condition '{cond}' missing in robustness results"

    # Multimodal fusion under missing text maintains high performance while text model drops to random (~0.50)
    fusion_missing_text = rob_data["results"]["complete_text_loss"]["fusion"]
    bert_missing_text = rob_data["results"]["complete_text_loss"]["bert"]
    assert fusion_missing_text > 0.90, "Fusion should preserve tabular performance when text is missing"
    assert bert_missing_text < 0.60, "BERT should degrade to near random when text is empty"

    # Verify plot files
    pdf_path = ROOT_DIR / "data" / "evaluation_plots" / "fig_missing_modality.pdf"
    png_path = ROOT_DIR / "data" / "evaluation_plots" / "fig_missing_modality.png"
    assert pdf_path.exists(), f"Missing modality PDF missing: {pdf_path}"
    assert png_path.exists(), f"Missing modality PNG missing: {png_path}"


def test_task_2_3_internal_generalization():
    """Verify Task 2.3 Temporal Split generalization reporting and disclaimers."""
    reg_path = ROOT_DIR / "results" / "registry.json"
    with open(reg_path, "r", encoding="utf-8") as f:
        gen_data = json.load(f)["generalization"]

    assert "Temporal split" in gen_data["split_method"]
    assert gen_data["train_samples"] == 1400
    assert gen_data["test_samples"] == 600
    assert "delta_macro_auroc" in gen_data["metrics"]
    assert "validation_nature" in gen_data
    assert "NOT external hospital validation" in gen_data["validation_nature"]


def test_task_2_4_fairness_and_error_analysis():
    """Verify Task 2.4 Subgroup Fairness and 30-case Error Analysis."""
    reg_path = ROOT_DIR / "results" / "registry.json"
    with open(reg_path, "r", encoding="utf-8") as f:
        fair_data = json.load(f)["fairness"]

    required_subgroups = [
        "gender_M",
        "gender_F",
        "age_under_65",
        "age_65_and_older",
        "smoking_NEVER",
        "smoking_FORMER",
        "smoking_CURRENT",
    ]
    for sg in required_subgroups:
        assert sg in fair_data["subgroups"], f"Subgroup '{sg}' missing in fairness report"
        res = fair_data["subgroups"][sg]
        assert "sample_size" in res
        assert "macro_auroc" in res
        assert "macro_auroc_ci95" in res
        assert "macro_f1" in res
        assert "macro_f1_ci95" in res
        assert len(res["macro_auroc_ci95"]) == 2
        assert len(res["macro_f1_ci95"]) == 2

    # Check 30 error cases
    err_path = ROOT_DIR / "data" / "error_analysis_30cases.json"
    assert err_path.exists(), f"Error analysis JSON missing: {err_path}"

    with open(err_path, "r", encoding="utf-8") as f:
        err_data = json.load(f)

    assert "top_3_confusion_pairs" in err_data
    pairs = err_data["top_3_confusion_pairs"]
    assert len(pairs) == 3
    total_cases = sum(len(cases) for cases in pairs.values())
    assert total_cases == 30, f"Expected 30 cases across top 3 pairs, got {total_cases}"

    for pair_name, cases in pairs.items():
        assert len(cases) == 10, f"Pair {pair_name} does not have 10 cases"
        for case in cases:
            assert "patient_id" in case
            assert "true_disease" in case
            assert "predicted_disease" in case
            assert "confidence" in case
            assert "vitals_summary" in case
            assert "root_cause_code" in case


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
    """Verify docs/06_ERROR_ANALYSIS_AND_CLINICAL_DISCREPANCIES.md contains all required clinical analyses."""
    doc_path = ROOT_DIR / "docs" / "06_ERROR_ANALYSIS_AND_CLINICAL_DISCREPANCIES.md"
    assert doc_path.exists(), f"Error analysis doc missing: {doc_path}"

    content = doc_path.read_text(encoding="utf-8")
    assert "302" in content
    assert "OVERLAPPING_VITALS" in content or "Overlapping Vitals" in content or "Sinh hiệu chồng lấn" in content
    assert "NOISY_TEXT" in content or "Noisy Text" in content or "Văn bản nhiễu" in content
    assert "SYNTHETIC_LABEL_DISCREPANCY" in content or "Synthetic Label Discrepancy" in content or "Đặc trưng nhãn mô phỏng" in content
    assert "PT-00044" in content or "PT-0044" in content
    assert "PT-00254" in content or "PT-0254" in content
    assert "PT-01997" in content
    assert "PT-01946" in content
