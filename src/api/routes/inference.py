"""
Inference API Endpoints for Baselines
Multimodal EHR CDSS - Phase 1 / Backlog 02 (Task 3.3)
"""

from fastapi import APIRouter
from datetime import datetime, timezone
from src.api.schemas import (
    BaselineModelResult,
    ModalityStreamResult,
    MultimodalMockResponse,
    PatientInferenceRequest,
    PatientInferenceResponse,
    TopKPrediction,
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


@router.options("/mock")
async def options_mock():
    """Direct OPTIONS handler for mock prediction endpoint."""
    return {"status": "ok"}


DISEASE_DISPLAY_NAMES = {
    "ASTHMA": "Hen phế quản (ASTHMA)",
    "COPD": "Bệnh phổi tắc nghẽn mạn tính (COPD)",
    "CONGESTIVE_HEART_FAILURE": "Suy tim sung huyết (HEART_FAILURE)",
    "COMMUNITY_ACQUIRED_PNEUMONIA": "Viêm phổi mắc phải cộng đồng (PNEUMONIA)",
}


def _determine_risk_level(prob: float) -> str:
    """Group simulated scores for display; these are not clinical risk thresholds."""
    if prob >= 0.70:
        return "high"
    elif prob >= 0.30:
        return "moderate"
    return "low"


@router.post("/mock", response_model=MultimodalMockResponse)
async def predict_multimodal_mock(request: PatientInferenceRequest) -> MultimodalMockResponse:
    """
    Mock multimodal prediction endpoint for Phase 2 Multimodal Core.
    Combines tabular features and clinical notes via simulated Cross-Attention Late Fusion
    without a fitted clinical model or validation calibration.
    """
    patient_id = request.patient_id or "PT-001"
    tf = request.tabular_features
    raw_notes = request.clinical_notes or ""
    sanitized_notes = deidentifier.deidentify_text(raw_notes) if raw_notes else ""
    notes_text = sanitized_notes.lower()

    timestamp_str = datetime.now(timezone.utc).isoformat()

    # Case 1: PT-0044 (Ground Truth ASTHMA) - Tabular misclassified as COPD, Text correct as ASTHMA
    if patient_id == "PT-0044" or (tf.age == 18 and tf.crp > 20.0):
        top_disease = "ASTHMA"
        top_confidence = 0.8940
        probs = {
            "ASTHMA": 0.8940,
            "COPD": 0.0780,
            "COMMUNITY_ACQUIRED_PNEUMONIA": 0.0180,
            "CONGESTIVE_HEART_FAILURE": 0.0100,
        }
        streams = {
            "tabular_stream": ModalityStreamResult(
                stream_name="CatBoost (Dữ liệu bảng)",
                predicted_disease="COPD",
                confidence=0.7882,
            ),
            "text_stream": ModalityStreamResult(
                stream_name="Bio_ClinicalBERT (Ghi chú lâm sàng)",
                predicted_disease="ASTHMA",
                confidence=0.8580,
            ),
            "multimodal_fusion": ModalityStreamResult(
                stream_name="Cross-Attention Late Fusion (Đa phương thức)",
                predicted_disease="ASTHMA",
                confidence=0.8940,
            ),
        }
        gate_weights = {"g_tabular": 0.35, "g_text": 0.65}

    # Case 2: PT-0254 (Ground Truth COPD) - Text misclassified as HEART_FAILURE, Tabular correct as COPD
    elif patient_id == "PT-0254" or (tf.age == 65 and ("tracheostomy" in notes_text or "khí quản" in notes_text)):
        top_disease = "COPD"
        top_confidence = 0.8450
        probs = {
            "COPD": 0.8450,
            "CONGESTIVE_HEART_FAILURE": 0.1020,
            "COMMUNITY_ACQUIRED_PNEUMONIA": 0.0380,
            "ASTHMA": 0.0150,
        }
        streams = {
            "tabular_stream": ModalityStreamResult(
                stream_name="CatBoost (Dữ liệu bảng)",
                predicted_disease="COPD",
                confidence=0.7522,
            ),
            "text_stream": ModalityStreamResult(
                stream_name="Bio_ClinicalBERT (Ghi chú lâm sàng)",
                predicted_disease="CONGESTIVE_HEART_FAILURE",
                confidence=0.5899,
            ),
            "multimodal_fusion": ModalityStreamResult(
                stream_name="Cross-Attention Late Fusion (Đa phương thức)",
                predicted_disease="COPD",
                confidence=0.8450,
            ),
        }
        gate_weights = {"g_tabular": 0.68, "g_text": 0.32}

    # General Case - Dynamic Multimodal Inference
    elif (
        tf.wbc_count > 12.0
        or tf.crp > 30.0
        or tf.temperature > 38.0
        or "sốt" in notes_text
        or "đờm" in notes_text
        or "thâm nhiễm" in notes_text
    ):
        top_disease = "COMMUNITY_ACQUIRED_PNEUMONIA"
        top_confidence = 0.8820
        probs = {
            "COMMUNITY_ACQUIRED_PNEUMONIA": 0.8820,
            "ASTHMA": 0.0540,
            "COPD": 0.0410,
            "CONGESTIVE_HEART_FAILURE": 0.0230,
        }
        streams = {
            "tabular_stream": ModalityStreamResult(
                stream_name="CatBoost (Dữ liệu bảng)",
                predicted_disease="COMMUNITY_ACQUIRED_PNEUMONIA",
                confidence=0.7600,
            ),
            "text_stream": ModalityStreamResult(
                stream_name="Bio_ClinicalBERT (Ghi chú lâm sàng)",
                predicted_disease="COMMUNITY_ACQUIRED_PNEUMONIA",
                confidence=0.7100,
            ),
            "multimodal_fusion": ModalityStreamResult(
                stream_name="Cross-Attention Late Fusion (Đa phương thức)",
                predicted_disease="COMMUNITY_ACQUIRED_PNEUMONIA",
                confidence=0.8820,
            ),
        }
        gate_weights = {"g_tabular": 0.52, "g_text": 0.48}

    elif tf.history_hypertension == 1 and (tf.systolic_bp > 140.0 or "suy tim" in notes_text or "phù" in notes_text):
        top_disease = "CONGESTIVE_HEART_FAILURE"
        top_confidence = 0.8650
        probs = {
            "CONGESTIVE_HEART_FAILURE": 0.8650,
            "COPD": 0.0650,
            "COMMUNITY_ACQUIRED_PNEUMONIA": 0.0450,
            "ASTHMA": 0.0250,
        }
        streams = {
            "tabular_stream": ModalityStreamResult(
                stream_name="CatBoost (Dữ liệu bảng)",
                predicted_disease="CONGESTIVE_HEART_FAILURE",
                confidence=0.7000,
            ),
            "text_stream": ModalityStreamResult(
                stream_name="Bio_ClinicalBERT (Ghi chú lâm sàng)",
                predicted_disease="CONGESTIVE_HEART_FAILURE",
                confidence=0.6400,
            ),
            "multimodal_fusion": ModalityStreamResult(
                stream_name="Cross-Attention Late Fusion (Đa phương thức)",
                predicted_disease="CONGESTIVE_HEART_FAILURE",
                confidence=0.8650,
            ),
        }
        gate_weights = {"g_tabular": 0.55, "g_text": 0.45}

    elif tf.smoking_status in ("FORMER", "CURRENT") and (tf.age >= 50 or tf.spo2 <= 94.0):
        top_disease = "COPD"
        top_confidence = 0.8120
        probs = {
            "COPD": 0.8120,
            "ASTHMA": 0.1180,
            "COMMUNITY_ACQUIRED_PNEUMONIA": 0.0450,
            "CONGESTIVE_HEART_FAILURE": 0.0250,
        }
        streams = {
            "tabular_stream": ModalityStreamResult(
                stream_name="CatBoost (Dữ liệu bảng)",
                predicted_disease="COPD",
                confidence=0.7200,
            ),
            "text_stream": ModalityStreamResult(
                stream_name="Bio_ClinicalBERT (Ghi chú lâm sàng)",
                predicted_disease="COPD",
                confidence=0.6500,
            ),
            "multimodal_fusion": ModalityStreamResult(
                stream_name="Cross-Attention Late Fusion (Đa phương thức)",
                predicted_disease="COPD",
                confidence=0.8120,
            ),
        }
        gate_weights = {"g_tabular": 0.50, "g_text": 0.50}

    else:
        top_disease = "ASTHMA"
        top_confidence = 0.8250
        probs = {
            "ASTHMA": 0.8250,
            "COPD": 0.0950,
            "COMMUNITY_ACQUIRED_PNEUMONIA": 0.0500,
            "CONGESTIVE_HEART_FAILURE": 0.0300,
        }
        streams = {
            "tabular_stream": ModalityStreamResult(
                stream_name="CatBoost (Dữ liệu bảng)",
                predicted_disease="ASTHMA",
                confidence=0.7100,
            ),
            "text_stream": ModalityStreamResult(
                stream_name="Bio_ClinicalBERT (Ghi chú lâm sàng)",
                predicted_disease="ASTHMA",
                confidence=0.6500,
            ),
            "multimodal_fusion": ModalityStreamResult(
                stream_name="Cross-Attention Late Fusion (Đa phương thức)",
                predicted_disease="ASTHMA",
                confidence=0.8250,
            ),
        }
        gate_weights = {"g_tabular": 0.40, "g_text": 0.60}

    # Build Top-K sorted list
    top_k_list = []
    for dis, p in sorted(probs.items(), key=lambda item: item[1], reverse=True):
        top_k_list.append(
            TopKPrediction(
                disease=dis,
                disease_name=DISEASE_DISPLAY_NAMES.get(dis, dis),
                probability=p,
                percentage=round(p * 100.0, 1),
                risk_level=_determine_risk_level(p),
            )
        )

    return MultimodalMockResponse(
        patient_id=patient_id,
        predicted_disease=top_disease,
        predicted_disease_name=DISEASE_DISPLAY_NAMES.get(top_disease, top_disease),
        confidence=top_confidence,
        calibrated=False,
        temperature=None,
        ece_score=None,
        top_k_predictions=top_k_list,
        modality_streams=streams,
        fusion_gate_weights=gate_weights,
        timestamp=timestamp_str,
    )
