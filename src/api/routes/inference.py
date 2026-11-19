# ==============================================================================
# [CHÚ THÍCH MOCK ENDPOINT - DÙNG PHÁT TRIỂN GIAO DIỆN TRƯỚC KHI CÓ CHECKPOINT]
# LƯU Ý: Endpoint POST /api/v1/predict/mock trong file này là endpoint giả lập
# (mock) theo nhiệm vụ của Thành viên 3 (Backlog 04 - Nhiệm vụ 3.1) để phát triển
# giao diện DiagnosticCard.tsx. Khi Thành viên 1 hoàn thành huấn luyện trọng số
# data/checkpoints/multimodal_best.pt và viết endpoint GPU thực tế
# POST /api/v1/predict/multimodal (Backlog 05 - Nhiệm vụ 1.3), hệ thống sẽ chuyển
# sang dùng suy luận mô hình thật.
# ==============================================================================
"""
Inference API Endpoints for Baselines
Multimodal EHR CDSS - Phase 1 / Backlog 02 (Task 3.3)
"""

import hashlib
import json
import math
import os
from functools import lru_cache
from pathlib import Path
from fastapi import APIRouter, HTTPException
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


def predict_checkpoint(tabular_features: dict, deidentified_note: str):
    """Lazily import PyTorch multimodal inference so lightweight deploy images can boot."""
    from src.api.multimodal_service import predict_checkpoint as _predict_checkpoint

    return _predict_checkpoint(tabular_features, deidentified_note)

router = APIRouter(prefix="/predict")

# Initialize ClinicalDeidentifier for pre-inference PHI protection
deidentifier = ClinicalDeidentifier(spacy_model=None, use_ner=False)


@lru_cache(maxsize=1)
def _load_model_card_metadata() -> dict:
    """Reads checkpoint hash, temperature, and data manifest metadata for transparency UI."""
    repo_root = Path(__file__).resolve().parents[3]
    ckpt_path = repo_root / "data" / "checkpoints" / "multimodal_best.pt"
    manifest_path = repo_root / "data" / "DATA_MANIFEST.json"
    summary_path = repo_root / "data" / "benchmark_summary.json"

    ckpt_sha = "unavailable"
    if ckpt_path.is_file():
        ckpt_sha = hashlib.sha256(ckpt_path.read_bytes()).hexdigest()[:12]

    manifest_sha = "unavailable"
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest_sha = str(manifest.get("manifest_sha256", "unavailable"))[:12]
        except Exception:
            manifest_sha = "unavailable"

    trained_at = "2026-11-05"
    temperature = 1.3541
    if summary_path.is_file():
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            temperature = float(summary.get("temperature", 1.3541))
            if summary.get("evaluated_at"):
                trained_at = str(summary["evaluated_at"])[:10]
        except Exception:
            pass

    return {
        "checkpoint_name": ckpt_path.name,
        "checkpoint_sha256_short": ckpt_sha,
        "trained_at": trained_at,
        "temperature": round(temperature, 4),
        "data_manifest_sha": manifest_sha,
    }


def _softmax_top(scores: dict[str, float]) -> tuple[str, float]:
    max_val = max(scores.values())
    exps = {k: math.exp(v - max_val) for k, v in scores.items()}
    total = sum(exps.values()) or 1.0
    best_k = max(exps, key=lambda k: exps[k])
    return best_k, round(exps[best_k] / total, 4)


@router.options("/status")
async def options_status():
    """Direct OPTIONS handler for status endpoint."""
    return {"status": "ok"}


@router.get("/status")
async def inference_status():
    """Check inference service status, reasoning mode, and model card provenance."""
    return {
        "status": "inference_service_ready",
        "supported_baselines": ["classical", "tabular_deep", "text_only"],
        "reasoning_mode": "deterministic_template",
        "model_card": _load_model_card_metadata(),
    }


@router.options("/baseline")
async def options_baseline():
    """Direct OPTIONS handler for baseline endpoint."""
    return {"status": "ok"}


@router.post("/baseline", response_model=PatientInferenceResponse)
async def predict_baseline(request: PatientInferenceRequest) -> PatientInferenceResponse:
    """
    Baseline heuristic fallback prediction endpoint across 3 unimodal baselines
    until fitted Member 1 baseline artifacts (.cbm / .pt) are registered.
    Set MCDSS_STRICT_NO_MOCK_BASELINE=1 to return 503 baseline_models_unavailable.
    """
    if os.getenv("MCDSS_STRICT_NO_MOCK_BASELINE") == "1":
        raise HTTPException(status_code=503, detail="baseline_models_unavailable")

    patient_id = request.patient_id or "PT-001"
    tf = request.tabular_features

    raw_notes = request.clinical_notes or ""
    sanitized_notes = deidentifier.deidentify_text(raw_notes) if raw_notes else ""
    notes_text = sanitized_notes.lower()

    # Uniform tabular physiological scoring (no hardcoded patient_id branches)
    tab_scores = {
        "ASTHMA": 0.4 + (0.9 if tf.age < 40 else 0.0) + (0.4 if tf.smoking_status == "NEVER" else -0.3) + (0.3 if tf.spo2 >= 94 else 0.0),
        "COPD": 0.4 + (0.9 if tf.smoking_status in ("FORMER", "CURRENT") else 0.0) + (0.6 if tf.age >= 55 else 0.0) + (0.5 if tf.spo2 <= 93.0 else 0.0) + (0.3 if tf.crp > 15.0 else 0.0),
        "CONGESTIVE_HEART_FAILURE": 0.3 + (0.8 if tf.history_hypertension == 1 else 0.0) + (0.7 if tf.systolic_bp > 140.0 else 0.0) + (0.4 if tf.age > 60 else 0.0),
        "COMMUNITY_ACQUIRED_PNEUMONIA": 0.2 + (0.9 if tf.temperature > 38.0 else 0.0) + (0.8 if tf.wbc_count > 12.0 else 0.0) + (0.7 if tf.crp > 30.0 else 0.0),
    }
    pred_tab, conf_tab = _softmax_top(tab_scores)
    deep_scores = {k: v * 0.92 for k, v in tab_scores.items()}
    pred_deep, conf_deep = _softmax_top(deep_scores)

    # Uniform text-token scoring
    txt_scores = {
        "ASTHMA": 0.4 + 0.7 * sum(w in notes_text for w in ("wheez", "inhaler", "khò khè", "hen", "asthma")),
        "COPD": 0.4 + 0.7 * sum(w in notes_text for w in ("copd", "smoking", "hút thuốc", "tracheostomy", "thở rít", "khí quản", "đờm trắng")),
        "CONGESTIVE_HEART_FAILURE": 0.4 + 0.7 * sum(w in notes_text for w in ("heart failure", "suy tim", "orthopnea", "phù", "bnp", "crackles")),
        "COMMUNITY_ACQUIRED_PNEUMONIA": 0.4 + 0.7 * sum(w in notes_text for w in ("pneumonia", "viêm phổi", "sốt", "fever", "đờm mủ", "đông đặc")),
    }
    pred_text, conf_text = _softmax_top(txt_scores)

    return PatientInferenceResponse(
        patient_id=patient_id,
        prediction_source="heuristic_baseline_fallback_pending_member1_cbm",
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
    "HEART_FAILURE": "Suy tim sung huyết (HEART_FAILURE)",
    "COMMUNITY_ACQUIRED_PNEUMONIA": "Viêm phổi mắc phải cộng đồng (PNEUMONIA)",
    "PNEUMONIA": "Viêm phổi mắc phải cộng đồng (PNEUMONIA)",
}


@router.post("/multimodal", response_model=MultimodalMockResponse)
def predict_multimodal(request: PatientInferenceRequest) -> MultimodalMockResponse:
    """Run the fitted research checkpoint; return 503 when local assets are missing."""
    if not request.clinical_notes or len(request.clinical_notes.strip()) < 10:
        raise HTTPException(status_code=422, detail="Clinical notes require at least 10 characters")
    clean_note = deidentifier.deidentify_text(request.clinical_notes)
    try:
        checkpoint, probabilities = predict_checkpoint(
            request.tabular_features.model_dump(), clean_note
        )
    except (ImportError, FileNotFoundError, OSError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    classes = list(checkpoint["classes"])
    ordered = sorted(zip(classes, probabilities), key=lambda pair: pair[1], reverse=True)
    top_k = [
        TopKPrediction(
            disease=disease,
            disease_name=DISEASE_DISPLAY_NAMES.get(disease, disease),
            probability=probability,
            percentage=round(probability * 100, 1),
            risk_level=_determine_risk_level(probability),
        )
        for disease, probability in ordered
    ]
    top_disease, confidence = ordered[0]
    metrics = checkpoint.get("training_metadata", {}).get("calibrated_test_metrics", {})
    return MultimodalMockResponse(
        patient_id=request.patient_id,
        prediction_source="checkpoint",
        model_version=checkpoint.get("training_metadata", {}).get("trained_at"),
        predicted_disease=top_disease,
        predicted_disease_name=DISEASE_DISPLAY_NAMES.get(top_disease, top_disease),
        confidence=confidence,
        calibrated=True,
        temperature=float(checkpoint["temperature"]),
        ece_score=metrics.get("ece"),
        top_k_predictions=top_k,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


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
