"""
Inference API Endpoints for Baselines
Multimodal EHR CDSS - Phase 1 / Backlog 02 (Task 3.3)
"""

from fastapi import APIRouter
from src.api.schemas import (
    BaselineModelResult,
    PatientInferenceRequest,
    PatientInferenceResponse,
)
from src.data_pipeline.deidentifier import ClinicalDeidentifier

router = APIRouter(prefix="/predict")

# Initialize ClinicalDeidentifier for pre-inference PHI protection
deidentifier = ClinicalDeidentifier(spacy_model=None, use_ner=False)


@router.options("/status")
async def options_status():
    """Direct OPTIONS handler for status endpoint."""
    return {"status": "ok"}


@router.get("/status")
async def inference_status():
    """Check inference service status."""
    return {
        "status": "inference_service_ready",
        "supported_baselines": ["classical", "tabular_deep", "text_only"],
    }


@router.options("/baseline")
async def options_baseline():
    """Direct OPTIONS handler for baseline endpoint."""
    return {"status": "ok"}


@router.post("/baseline", response_model=PatientInferenceResponse)
async def predict_baseline(request: PatientInferenceRequest) -> PatientInferenceResponse:
    """
    Mock baseline prediction endpoint returning probability predictions for 3 baseline models:
    - classical_tabular (e.g. XGBoost)
    - tabular_deep (e.g. FT-Transformer)
    - text_only (e.g. Bio_ClinicalBERT)
    """
    patient_id = request.patient_id or "PT-001"
    tf = request.tabular_features

    # Sanitize clinical notes using Member 2's De-identification pipeline
    raw_notes = request.clinical_notes or ""
    sanitized_notes = deidentifier.deidentify_text(raw_notes) if raw_notes else ""
    notes_text = sanitized_notes.lower()

    # Case Study exact ground truth / error analysis mapping
    if patient_id == "PT-0044" or (tf.age == 18 and tf.crp > 20.0):
        pred_tab = "COPD"
        conf_tab = 0.7882
        pred_deep = "COPD"
        conf_deep = 0.7410
        pred_text = "ASTHMA"
        conf_text = 0.8580
    elif patient_id == "PT-0254" or (tf.age == 65 and ("tracheostomy" in notes_text or "khí quản" in notes_text)):
        pred_tab = "COPD"
        conf_tab = 0.7522
        pred_deep = "COPD"
        conf_deep = 0.7130
        pred_text = "HEART_FAILURE"
        conf_text = 0.5899
    # Rule-assisted mock prediction matching clinical indications
    elif (
        tf.wbc_count > 12.0
        or tf.crp > 30.0
        or tf.temperature > 38.0
        or "sốt" in notes_text
        or "đờm" in notes_text
    ):
        pred_tab = "COMMUNITY_ACQUIRED_PNEUMONIA"
        conf_tab = 0.76
        pred_deep = "COMMUNITY_ACQUIRED_PNEUMONIA"
        conf_deep = 0.74
        pred_text = "COMMUNITY_ACQUIRED_PNEUMONIA"
        conf_text = 0.71
    elif tf.smoking_status in ("FORMER", "CURRENT") and (tf.age >= 50 or tf.spo2 <= 94.0):
        pred_tab = "COPD"
        conf_tab = 0.72
        pred_deep = "COPD"
        conf_deep = 0.68
        pred_text = "COPD" if ("khó thở" in notes_text or "copd" in notes_text) else "ASTHMA"
        conf_text = 0.65
    elif tf.history_hypertension == 1 and tf.systolic_bp > 140.0 and tf.age > 60:
        pred_tab = "CONGESTIVE_HEART_FAILURE"
        conf_tab = 0.70
        pred_deep = "CONGESTIVE_HEART_FAILURE"
        conf_deep = 0.69
        pred_text = "CONGESTIVE_HEART_FAILURE"
        conf_text = 0.64
    else:
        pred_tab = "ASTHMA"
        conf_tab = 0.71
        pred_deep = "ASTHMA"
        conf_deep = 0.67
        pred_text = "ASTHMA"
        conf_text = 0.65

    return PatientInferenceResponse(
        patient_id=patient_id,
        baseline_results={
            "classical_tabular": BaselineModelResult(
                predicted_class=pred_tab,
                confidence=conf_tab,
            ),
            "tabular_deep": BaselineModelResult(
                predicted_class=pred_deep,
                confidence=conf_deep,
            ),
            "text_only": BaselineModelResult(
                predicted_class=pred_text,
                confidence=conf_text,
            ),
        },
    )
