"""
Unit Tests for FastAPI REST Endpoints & Pydantic Schemas
"""

import pytest
from pydantic import ValidationError

from src.api.schemas import (
    BaselinePredictionResult,
    ClinicalNoteInput,
    TabularFeatures,
)


def test_health_check(client):
    """
    Test that the /health endpoint returns HTTP 200 and 'healthy' status.
    (Specified in Task 3.4 of MEMBER_3.md)
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_health_check_payload_structure(client):
    """
    Verify /health returns version and valid ISO timestamp.
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert data["version"] == "1.0.0-phase1"
    assert "timestamp" in data


def test_cors_preflight_and_headers(client):
    """
    Verify CORS configuration permits http://localhost:3000.
    """
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_inference_status_endpoint(client):
    """
    Verify modular router /api/v1/predict/status responds correctly.
    """
    response = client.get("/api/v1/predict/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "inference_service_ready"
    assert "classical" in data["supported_baselines"]


def test_tabular_features_schema_valid():
    """
    Verify valid tabular features conform to constraints.
    """
    valid_payload = {
        "age": 58,
        "systolic_bp": 125.0,
        "diastolic_bp": 80.0,
        "heart_rate": 72.0,
        "respiratory_rate": 16.0,
        "spo2": 97.5,
        "temperature": 36.8,
        "wbc_count": 6.8,
        "crp": 1.2,
        "gender": "F",
        "smoking_status": "NEVER",
        "history_hypertension": 0,
        "history_diabetes": 0,
    }
    features = TabularFeatures(**valid_payload)
    assert features.age == 58
    assert features.gender == "F"


def test_tabular_features_schema_invalid_bounds():
    """
    Verify physiological bounds rejection.
    """
    base = {
        "age": 58,
        "systolic_bp": 125.0,
        "diastolic_bp": 80.0,
        "heart_rate": 72.0,
        "respiratory_rate": 16.0,
        "spo2": 97.5,
        "temperature": 36.8,
        "wbc_count": 6.8,
        "crp": 1.2,
        "gender": "F",
        "smoking_status": "NEVER",
        "history_hypertension": 0,
        "history_diabetes": 0,
    }
    # Age < 18
    with pytest.raises(ValidationError):
        TabularFeatures(**{**base, "age": 16})

    # SpO2 > 100%
    with pytest.raises(ValidationError):
        TabularFeatures(**{**base, "spo2": 105.0})

    # Systolic <= Diastolic
    with pytest.raises(ValidationError):
        TabularFeatures(**{**base, "systolic_bp": 80.0, "diastolic_bp": 90.0})


def test_clinical_note_input_schema():
    """
    Verify clinical note schema rejects invalid timestamps and empty text.
    """
    valid_note = ClinicalNoteInput(
        patient_id="PT-0042",
        encounter_timestamp="2026-10-10T14:30:00",
        raw_text="Patient presents with acute productive cough and dyspnea.",
    )
    assert valid_note.patient_id == "PT-0042"

    with pytest.raises(ValidationError):
        ClinicalNoteInput(
            patient_id="PT-0042",
            encounter_timestamp="invalid-timestamp",
            raw_text="Short text",
        )


def test_baseline_prediction_result_schema():
    """
    Verify prediction result probability range [0.0, 1.0].
    """
    valid_result = BaselinePredictionResult(
        baseline_name="FT-Transformer",
        disease_name="ASTHMA",
        probability=0.78,
    )
    assert valid_result.probability == 0.78

    with pytest.raises(ValidationError):
        BaselinePredictionResult(
            baseline_name="FT-Transformer",
            disease_name="ASTHMA",
            probability=1.2,
        )

    with pytest.raises(ValidationError):
        BaselinePredictionResult(
            baseline_name="FT-Transformer",
            disease_name="UNKNOWN",
            probability=0.5,
        )
