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
    Verify CORS configuration permits http://localhost:3000 and dynamic localhost ports.
    """
    # Preflight GET on /health
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"

    # Preflight POST on /api/v1/predict/baseline
    post_preflight = client.options(
        "/api/v1/predict/baseline",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert post_preflight.status_code == 200
    assert post_preflight.headers.get("access-control-allow-origin") == "http://localhost:3000"

    # Dynamic localhost port (e.g. 3001)
    port_3001_preflight = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3001",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert port_3001_preflight.status_code == 200
    assert port_3001_preflight.headers.get("access-control-allow-origin") == "http://localhost:3001"


def test_direct_options_requests(client):
    """
    Verify direct OPTIONS requests return HTTP 200.
    """
    assert client.options("/health").status_code == 200
    assert client.options("/api/v1/predict/status").status_code == 200
    assert client.options("/api/v1/predict/baseline").status_code == 200


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


def test_predict_baseline_endpoint(client):
    """
    Verify POST /api/v1/predict/baseline accepts PatientInferenceRequest
    and returns predictions for all 3 baselines (Task 3.3).
    """
    payload = {
        "patient_id": "PT-001",
        "tabular_features": {
            "age": 64,
            "systolic_bp": 135.0,
            "diastolic_bp": 85.0,
            "heart_rate": 88.0,
            "respiratory_rate": 22.0,
            "spo2": 92.0,
            "temperature": 37.2,
            "wbc_count": 8.5,
            "crp": 12.0,
            "gender": "M",
            "smoking_status": "CURRENT",
            "history_hypertension": 1,
            "history_diabetes": 0,
        },
        "clinical_notes": "Bệnh nhân nam 64 tuổi có tiền sử hút thuốc lá, khó thở tăng dần khi gắng sức.",
    }

    response = client.post("/api/v1/predict/baseline", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["patient_id"] == "PT-001"
    assert "baseline_results" in data
    results = data["baseline_results"]

    # Verify all 3 baselines are present
    assert "classical_tabular" in results
    assert "tabular_deep" in results
    assert "text_only" in results

    for key in ["classical_tabular", "tabular_deep", "text_only"]:
        assert "predicted_class" in results[key]
        assert "confidence" in results[key]
        assert 0.0 <= results[key]["confidence"] <= 1.0


def test_benchmarks_baselines_endpoint(client):
    opt_resp = client.options("/api/v1/benchmarks/baselines")
    assert opt_resp.status_code == 200

    response = client.get("/api/v1/benchmarks/baselines")
    assert response.status_code == 200
    data = response.json()
    assert "benchmark_metadata" in data
    results = data.get("results", data)
    assert "baseline_1_classical_tabular" in results
    assert "baseline_2_tabular_deep" in results
    assert "baseline_3_text_only" in results
