"""
Clinical Evaluation & Decision Curve Analysis (DCA) Router
M-CDSS Phase 2 / Backlog 06 (Task 3.1)

Provides quantitative benchmarks comparing Baselines vs Multimodal Core,
and computes clinical Decision Curve Analysis (DCA) Net Benefit metrics.
"""

import json
from pathlib import Path
from typing import Any, Dict
from fastapi import APIRouter, HTTPException
from src.api.routes.benchmarks import get_ablation_benchmarks
from src.evaluation.dca_analysis import evaluate_holdout_dca

router = APIRouter(prefix="/evaluation")

@router.options("/benchmark")
async def options_benchmark():
    """Direct OPTIONS handler for CORS preflight."""
    return {"status": "ok"}


@router.get("/benchmark")
async def get_clinical_evaluation_benchmark() -> Dict[str, Any]:
    """
    Returns full quantitative validation matrix and Decision Curve Analysis (DCA)
    data for M-CDSS compared against 3 single-modality baselines.
    """
    result = {
        "evaluation_metadata": {
            "evaluation_cohort": "Hold-out Strict Test Cohort (0% patient overlap)",
            "test_samples": 302,
            "classes": ["ASTHMA", "COPD", "HEART_FAILURE", "PNEUMONIA"],
            "prevalence_per_class": 0.25,
            "validation_standard": "TRIPOD-AI reporting framework; PROBAST not independently assessed",
        },
        # Filled exclusively from results/registry.json and data/ablation_results.json below;
        # no metric is hard-coded in source (Phase 3 rule: one source of truth).
        "model_benchmarks": {},
        "decision_curve_analysis": {
            "threshold_points": [],
            "analysis_threshold_range": [0.10, 0.45],
            "dca_conclusion": "DCA is computed dynamically from the available hold-out prediction source.",
        },
        "probast_compliance_summary": {
            "participants_risk": "Low Risk (Stratified Group Split, không rò rỉ bệnh nhân)",
            "predictors_risk": "Low Risk (Chuẩn hóa sinh lý học, không đưa tiêu chuẩn vàng vào input)",
            "outcome_risk": "Low Risk (Đối chiếu ICD-10 và phác đồ quốc tế GINA/GOLD/ESC)",
            "analysis_risk": "Low Risk (Hiệu chuẩn ECE < 0.05, kiểm soát overfitting bằng Dropout/Early Stopping)",
            "overall_bias_risk": "Low Risk of Bias (Đạt chuẩn 20/20 tiêu chí PROBAST)",
        },
    }

    ablation = await get_ablation_benchmarks()
    models = ablation["models"]
    result["evaluation_metadata"]["test_samples"] = ablation["experiment_metadata"]["test_samples"]
    dca = evaluate_holdout_dca()
    is_empirical = dca["prediction_source"] == "empirical_holdout_artifact"
    result["evaluation_metadata"]["test_samples"] = dca["n_samples"]
    result["evaluation_metadata"]["dca_status"] = (
        "empirical_holdout_predictions" if is_empirical
        else "illustrative_simulation_pending_patient_level_predictions"
    )
    result["evaluation_metadata"]["dca_prediction_source"] = dca["prediction_source"]
    result["evaluation_metadata"]["prevalence_per_class"] = dca["class_prevalence"]
    result["evaluation_metadata"]["probast_status"] = "not_independently_assessed"
    for target, source in (
        ("tabular_deep", "tabular_only"),
        ("text_only", "text_only"),
        ("mcdss_multimodal_core", "cross_attention_fusion"),
    ):
        result["model_benchmarks"][target] = models[source]
    result["model_benchmarks"]["mcdss_multimodal_core"]["net_gain_auroc_over_tabular"] = (
        models["cross_attention_fusion"]["macro_auroc"] - models["tabular_only"]["macro_auroc"]
    )
    registry_path = Path(__file__).resolve().parents[3] / "results" / "registry.json"
    if registry_path.exists():
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        for row in registry.get("rq1_multiseed_comparison", {}).get("models", []):
            if row["model"] == "catboost":
                result["model_benchmarks"]["classical_tabular"] = {
                    "name": "CatBoost (Tabular)", "modality": "Structured Tabular Only",
                    "macro_auroc": row["auroc_mean"], "macro_auprc": row["auprc_mean"], "macro_f1": row["f1_mean"],
                    "accuracy": row["accuracy_mean"], "brier_score": row["brier_score_mean"], "ece": row["ece_mean"],
                    "aggregation": f"mean of {row['n_seeds']} seeds",
                }
    result["decision_curve_analysis"]["dca_conclusion"] = (
        "Computed from patient-level hold-out predictions; this is a research analysis, not evidence of clinical utility."
        if is_empirical else
        "Illustrative simulation only; patient-level predictions are required before clinical interpretation."
    )
    result["decision_curve_analysis"]["threshold_points"] = dca["threshold_points"]
    result["probast_compliance_summary"] = {
        key: "Not independently assessed" for key in result["probast_compliance_summary"]
    }
    return result


@router.options("/registry")
async def options_registry():
    """Direct OPTIONS handler for evaluation registry endpoint."""
    return {"status": "ok"}


@router.get("/registry")
async def get_results_registry() -> Dict[str, Any]:
    """
    Returns Phase 3 central results registry (results/registry.json) combining
    real measured RAG/Latency benchmarks (Member 3) and pending multi-seed placeholders.
    """
    registry_path = Path(__file__).resolve().parents[3] / "results" / "registry.json"
    if not registry_path.exists():
        raise HTTPException(status_code=404, detail="results/registry.json not found")
    return json.loads(registry_path.read_text(encoding="utf-8"))
