"""
Unit Tests for FastAPI REST Endpoints & Pydantic Schemas
"""

import tempfile
from pathlib import Path

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
    assert "data_manifest_is_mock" in data["model_card"]
    assert isinstance(data["model_card"]["data_manifest_is_mock"], bool)


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


def test_predict_baseline_endpoint(client, monkeypatch):
    """
    Verify POST /api/v1/predict/baseline defaults to HTTP 503 baseline_models_unavailable
    when fitted Member 1 artifacts are absent, and supports explicit heuristic fallback
    only when MCDSS_ALLOW_HEURISTIC_BASELINE=1 is set.
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

    from src.api import baseline_service

    real_dir = baseline_service.BASELINE_DIR
    # 1) No fitted artifacts -> 503 (never heuristic numbers by default)
    monkeypatch.setattr(baseline_service, "BASELINE_DIR", Path(tempfile.mkdtemp()))
    monkeypatch.delenv("MCDSS_ALLOW_HEURISTIC_BASELINE", raising=False)
    strict_response = client.post("/api/v1/predict/baseline", json=payload)
    assert strict_response.status_code == 503
    assert strict_response.json()["detail"] == "baseline_models_unavailable"

    # 2) Heuristic fallback only when explicitly enabled (UI testing)
    monkeypatch.setenv("MCDSS_ALLOW_HEURISTIC_BASELINE", "1")
    response = client.post("/api/v1/predict/baseline", json=payload)
    assert response.status_code == 200
    assert response.json()["prediction_source"].startswith("heuristic")

    # 3) Fitted artifacts (scripts/export_baseline_artifacts.py) -> real model predictions
    monkeypatch.delenv("MCDSS_ALLOW_HEURISTIC_BASELINE", raising=False)
    monkeypatch.setattr(baseline_service, "BASELINE_DIR", real_dir)
    if not (real_dir / "manifest.json").is_file():
        pytest.skip("fitted baseline artifacts not exported on this machine")
    response = client.post("/api/v1/predict/baseline", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["prediction_source"] == "fitted_baseline_artifacts_seed42"

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


def test_predict_mock_endpoint(client):
    """
    Test POST /api/v1/predict/mock (Backlog 04 Member 3 Task 3.1).
    Verifies that the mock endpoint returns calibrated Top-K predictions and modality streams.
    """
    # Preflight check
    opt_resp = client.options("/api/v1/predict/mock")
    assert opt_resp.status_code == 200

    payload = {
        "patient_id": "PT-TEST-01",
        "tabular_features": {
            "age": 60,
            "systolic_bp": 130.0,
            "diastolic_bp": 80.0,
            "heart_rate": 75.0,
            "respiratory_rate": 18.0,
            "spo2": 96.0,
            "temperature": 37.0,
            "wbc_count": 6.5,
            "crp": 5.0,
            "gender": "M",
            "smoking_status": "NEVER",
            "history_hypertension": 0,
            "history_diabetes": 0,
        },
        "clinical_notes": "Patient presents for routine follow-up with mild intermittent wheezing.",
    }

    response = client.post("/api/v1/predict/mock", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["patient_id"] == "PT-TEST-01"
    assert "predicted_disease" in data
    assert "confidence" in data
    assert 0.0 <= data["confidence"] <= 1.0
    assert data["calibrated"] is False
    assert data["temperature"] is None
    assert data["ece_score"] is None
    assert "top_k_predictions" in data
    assert len(data["top_k_predictions"]) == 4

    # Verify probability ordering and fields
    probs = [item["probability"] for item in data["top_k_predictions"]]
    assert probs == sorted(probs, reverse=True)
    assert sum(probs) == pytest.approx(1.0, abs=1e-3)

    for item in data["top_k_predictions"]:
        assert "disease" in item
        assert "disease_name" in item
        assert "risk_level" in item
        assert item["risk_level"] in ("low", "moderate", "high")

    # Verify modality streams
    assert "modality_streams" in data
    assert "tabular_stream" in data["modality_streams"]
    assert "text_stream" in data["modality_streams"]
    assert "multimodal_fusion" in data["modality_streams"]


def test_predict_mock_case_study_pt0044(client):
    """
    Verify exact case study mapping for PT-0044 (ASTHMA) where text resolves tabular error.
    """
    payload = {
        "patient_id": "PT-0044",
        "tabular_features": {
            "age": 18,
            "systolic_bp": 106.2,
            "diastolic_bp": 78.0,
            "heart_rate": 70.6,
            "respiratory_rate": 12.8,
            "spo2": 97.3,
            "temperature": 37.7,
            "wbc_count": 4.78,
            "crp": 24.28,
            "gender": "F",
            "smoking_status": "NEVER",
            "history_hypertension": 1,
            "history_diabetes": 0,
        },
        "clinical_notes": "Patient 18yo presents with cough, shortness of breath. Medications: Inhalers.",
    }

    response = client.post("/api/v1/predict/mock", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["predicted_disease"] == "ASTHMA"
    assert data["confidence"] > 0.80
    assert data["top_k_predictions"][0]["disease"] == "ASTHMA"
    assert data["modality_streams"]["tabular_stream"]["predicted_disease"] == "COPD"
    assert data["modality_streams"]["text_stream"]["predicted_disease"] == "ASTHMA"
    assert data["modality_streams"]["multimodal_fusion"]["predicted_disease"] == "ASTHMA"


def test_benchmarks_ablation_endpoint(client):
    """
    Test GET /api/v1/benchmarks/ablation (Backlog 04 Member 3 Task 3.3).
    """
    opt_resp = client.options("/api/v1/benchmarks/ablation")
    assert opt_resp.status_code == 200

    response = client.get("/api/v1/benchmarks/ablation")
    assert response.status_code == 200
    data = response.json()

    assert "experiment_metadata" in data
    assert "models" in data
    models = data["models"]
    assert "tabular_only" in models
    assert "text_only" in models
    assert "concat_fusion" in models
    assert "cross_attention_fusion" in models

    # The dashboard must report the canonical training artifact, not fixture values.
    import json
    from pathlib import Path

    artifact = json.loads((Path(__file__).resolve().parents[1] / "data" / "ablation_results.json").read_text(encoding="utf-8"))
    tab_auroc = models["tabular_only"]["macro_auroc"]
    ca_auroc = models["cross_attention_fusion"]["macro_auroc"]
    assert tab_auroc == artifact["variants"]["tabular"]["test"]["macro_auroc"]
    assert ca_auroc == artifact["variants"]["cross_attention"]["test"]["macro_auroc"]
    assert models["cross_attention_fusion"]["ece"] == artifact["variants"]["cross_attention"]["test"]["ece"]


def test_multimodal_checkpoint_contract_and_unavailable_assets(client, monkeypatch):
    from src.api.routes import inference

    payload = {
        "patient_id": "PT-TEST",
        "tabular_features": {
            "age": 60, "systolic_bp": 130, "diastolic_bp": 80, "heart_rate": 75,
            "respiratory_rate": 18, "spo2": 96, "temperature": 37,
            "wbc_count": 6.5, "crp": 5, "gender": "M",
            "smoking_status": "NEVER", "history_hypertension": 0,
            "history_diabetes": 0,
        },
        "clinical_notes": "Patient reports intermittent wheezing and cough.",
    }
    checkpoint = {
        "classes": ["ASTHMA", "COPD", "HEART_FAILURE", "PNEUMONIA"],
        "temperature": 1.3,
        "training_metadata": {"trained_at": "2026-11-05", "calibrated_test_metrics": {"ece": 0.12}},
    }
    monkeypatch.setattr(inference, "predict_checkpoint", lambda *_: (checkpoint, [0.4, 0.3, 0.2, 0.1]))
    response = client.post("/api/v1/predict/multimodal", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["prediction_source"] == "checkpoint"
    assert data["calibrated"] is True
    assert sum(item["probability"] for item in data["top_k_predictions"]) == pytest.approx(1)
    assert data["ece_score"] == 0.12

    payload["clinical_notes"] = " "
    assert client.post("/api/v1/predict/multimodal", json=payload).status_code == 422
    payload["clinical_notes"] = "Patient reports intermittent wheezing and cough."
    monkeypatch.setattr(inference, "predict_checkpoint", lambda *_: (_ for _ in ()).throw(FileNotFoundError("missing weights")))
    assert client.post("/api/v1/predict/multimodal", json=payload).status_code == 503



def test_evaluation_benchmark_endpoint(client):
    """
    Test GET /api/v1/evaluation/benchmark (Backlog 06 Member 3 Task 3.1).
    Validates comprehensive benchmark matrix, Decision Curve Analysis (DCA),
    and PROBAST compliance summary.
    """
    # Preflight OPTIONS
    opt_resp = client.options("/api/v1/evaluation/benchmark")
    assert opt_resp.status_code == 200

    response = client.get("/api/v1/evaluation/benchmark")
    assert response.status_code == 200
    data = response.json()

    assert "evaluation_metadata" in data
    assert data["evaluation_metadata"]["test_samples"] == 302

    # Verify model benchmarks
    assert "model_benchmarks" in data
    benchmarks = data["model_benchmarks"]
    assert "mcdss_multimodal_core" in benchmarks
    import json
    ablation = json.loads((Path(__file__).resolve().parents[1] / "data" / "ablation_results.json").read_text())
    expected = ablation["variants"]["cross_attention"]["test"]
    assert benchmarks["mcdss_multimodal_core"]["macro_auroc"] == pytest.approx(expected["macro_auroc"])
    assert benchmarks["mcdss_multimodal_core"]["ece"] == pytest.approx(expected["ece"])
    assert data["evaluation_metadata"]["dca_status"] in (
        "illustrative_simulation_pending_patient_level_predictions",
        "empirical_holdout_predictions",
    )

    # Verify Decision Curve Analysis (DCA) points
    assert "decision_curve_analysis" in data
    dca = data["decision_curve_analysis"]
    assert "threshold_points" in dca
    points = dca["threshold_points"]
    assert len(points) >= 10

    # Verify Net Benefit superiority of M-CDSS on clinical thresholds [0.10, 0.45]
    for pt in points:
        t = pt["threshold"]
        if 0.10 <= t <= 0.45:
            assert pt["net_benefit_mcdss"] > pt["net_benefit_treat_all"], f"M-CDSS must beat Treat All at threshold {t}"
            assert pt["net_benefit_mcdss"] > pt["net_benefit_treat_none"], f"M-CDSS must beat Treat None at threshold {t}"

    # Verify PROBAST compliance summary
    assert "probast_compliance_summary" in data
    probast = data["probast_compliance_summary"]
    assert "overall_bias_risk" in probast
    assert probast["overall_bias_risk"] == "Not independently assessed"


def test_agent_explain_in_api_endpoints(client):
    """
    Verify /api/v1/agent/explain endpoint integration in test_api_endpoints suite.
    """
    payload = {
        "patient_id": "PT-0044",
        "clinical_notes": "Patient 18yo presents with cough, shortness of breath, and fatigue. Medications: Inhalers.",
        "target_diagnosis": "ASTHMA",
    }
    response = client.post("/api/v1/agent/explain", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["patient_id"] == "PT-0044"
    assert data["primary_diagnosis"] == "ASTHMA"
    assert len(data["grounded_spans"]) >= 1
    assert len(data["guideline_references"]) >= 1


def test_agent_explain_rejects_empty_and_short_payloads(client):
    """Verify invalid or too-short notes do not return HTTP 200."""
    bad_short = client.post("/api/v1/agent/explain", json={"patient_id": "PT-BAD", "clinical_notes": "abc"})
    assert bad_short.status_code in (400, 422)
    bad_blank = client.post("/api/v1/agent/explain", json={"patient_id": "PT-BAD", "clinical_notes": "     "})
    assert bad_blank.status_code in (400, 422)


def test_evaluation_benchmark_handles_missing_holdout_artifact(client, monkeypatch):
    """Verify /evaluation/benchmark handles missing hold-out prediction file gracefully."""
    from src.api.routes import evaluation_routes

    monkeypatch.setattr(
        evaluation_routes,
        "evaluate_holdout_dca",
        lambda: {
            "n_samples": 302,
            "class_prevalence": {"0": 0.235, "1": 0.235, "2": 0.351, "3": 0.179},
            "prediction_source": "calibrated_simulation_pending_checkpoint",
            "threshold_points": [
                {
                    "threshold": 0.20,
                    "net_benefit_mcdss": 0.23,
                    "net_benefit_tabular": 0.17,
                    "net_benefit_text": 0.22,
                    "net_benefit_treat_all": 0.06,
                    "net_benefit_treat_none": 0.0,
                    "net_tp_gained_per_100": 17.0,
                    "net_interventions_avoided_per_100": 68.0,
                }
            ],
        },
    )
    resp = client.get("/api/v1/evaluation/benchmark")
    assert resp.status_code == 200
    body = resp.json()
    assert body["evaluation_metadata"]["dca_prediction_source"] == "calibrated_simulation_pending_checkpoint"
    assert body["evaluation_metadata"]["dca_status"] == "illustrative_simulation_pending_patient_level_predictions"
