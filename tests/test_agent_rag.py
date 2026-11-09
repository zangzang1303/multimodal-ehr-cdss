"""
Unit Tests for Agentic RAG, Evidence Grounding & Clinical Explainability
M-CDSS Phase 2 / Backlog 05 (Task 3.3)
"""

import pytest
from fastapi.testclient import TestClient

from src.agent.evidence_grounder import EvidenceGrounder
from src.agent.retriever import HybridGuidelineRetriever, STANDARD_GUIDELINE_CORPUS
from src.api.main import app

client = TestClient(app)

SAMPLE_PT0044_NOTE = (
    "CLINICAL ENCOUNTER NOTE - BỆNH VIỆN THỐNG NHẤT\n"
    "Patient ID: PT-0044 | Encounter ID: ENC-0044 | Name: Đặng Thu Mai | Age: 18 | Gender: F\n"
    "----------------------------------------------------------------------\n"
    "CHIEF COMPLAINT:\n"
    "Patient Đặng Thu Mai presents for evaluation of acute/subacute respiratory condition.\n\n"
    "HISTORY OF PRESENT ILLNESS:\n"
    "Patient 18yo presents on 12/05/1984 with cough, shortness of breath, and fatigue.\n\n"
    "PHYSICAL EXAMINATION:\n"
    "BP: 106.2/78.0 mmHg, HR: 70.6 bpm, SpO2: 97.3%. Auscultation of lungs reveals bilateral breath sounds.\n\n"
    "MEDICATIONS:\n"
    "Inhalers and cardiovascular medications as prescribed."
)

SAMPLE_PT0254_NOTE = (
    "ELECTRONIC HEALTH RECORD - BỆNH VIỆN CHỢ RẪY\n"
    "Patient ID: PT-0254 | Encounter ID: ENC-0254 | Name: Huỳnh Phương Mai | Age: 65 | Gender: F\n"
    "----------------------------------------------------------------------\n"
    "CHIEF COMPLAINT:\n"
    "Patient referred for evaluation of tracheostomy tube placement and treatment recommendations.\n\n"
    "HISTORY OF PRESENT ILLNESS:\n"
    "Suffering from end-stage [REDACTED_DIAGNOSIS], required tracheostomy tube placement 3 months ago when being treated for acute exacerbation. Resides in extended care facility with a capped tracheostomy tube.\n\n"
    "PHYSICAL EXAMINATION:\n"
    "Vital signs recorded. Auscultation of lungs reveals bilateral breath sounds with intermittent crackles/wheezes. Heart shows regular rhythm.\n\n"
    "MEDICATIONS:\n"
    "Prevacid, folic acid, aspirin, morphine sulfate, Pulmicort, Risperdal, Colace, clonazepam, prednisone."
)


def test_evidence_grounder_exact_match():
    """Verify exact string matching returns accurate start/end character offsets."""
    grounder = EvidenceGrounder()
    claim = "cough, shortness of breath, and fatigue"
    span = grounder.ground_single_claim(SAMPLE_PT0044_NOTE, claim, category="supporting")

    assert span is not None
    assert span["is_exact"] is True
    assert span["start_char"] >= 0
    assert span["end_char"] > span["start_char"]
    # Exact slice assertion
    assert SAMPLE_PT0044_NOTE[span["start_char"]:span["end_char"]] == claim


def test_evidence_grounder_case_insensitive_and_whitespace():
    """Verify matcher handles minor casing and whitespace variations."""
    grounder = EvidenceGrounder()
    claim_variant = "PATIENT  18yo   presents"
    span = grounder.ground_single_claim(SAMPLE_PT0044_NOTE, claim_variant, category="supporting")

    assert span is not None
    assert span["start_char"] >= 0
    matched_substring = SAMPLE_PT0044_NOTE[span["start_char"]:span["end_char"]]
    assert "patient 18yo presents" in matched_substring.lower()


def test_evidence_grounder_anti_hallucination_rejection():
    """
    Zero-Hallucination Guarantee:
    Claims fabricated by LLM that do NOT exist in the clinical note MUST be rejected.
    """
    grounder = EvidenceGrounder()
    fabricated_claim = "Bệnh nhân có tiền sử hút thuốc 50 bao năm và tràn khí màng phổi"
    span = grounder.ground_single_claim(SAMPLE_PT0044_NOTE, fabricated_claim, category="supporting")
    assert span is None, "Fabricated claim must be rejected and return None"

    # Batch test
    claims = [
        {"text": "Patient 18yo", "category": "supporting"},
        {"text": "Bệnh nhân hôn mê sâu glasgow 3 điểm", "category": "red_flag"},
        {"text": "Inhalers and cardiovascular medications as prescribed.", "category": "supporting"},
        {"text": "Chỉ số men tim troponin T tăng gấp 10 lần", "category": "counter"},
    ]
    grounded, rejected_count = grounder.ground_evidence_claims(SAMPLE_PT0044_NOTE, claims)

    assert len(grounded) == 2, "Only the 2 genuine claims should be grounded"
    assert rejected_count == 2, "The 2 fabricated claims must be flagged and rejected"
    for s in grounded:
        assert SAMPLE_PT0044_NOTE[s["start_char"]:s["end_char"]] == s["text"]


def test_evidence_grounder_span_bounds_validity():
    """Verify that all span indices are strictly within [0, len(note)]."""
    grounder = EvidenceGrounder()
    claims = [
        "CLINICAL ENCOUNTER NOTE",
        "cough, shortness of breath, and fatigue.",
        "BP: 106.2/78.0 mmHg",
    ]
    grounded, _ = grounder.ground_evidence_claims(SAMPLE_PT0044_NOTE, claims)

    note_len = len(SAMPLE_PT0044_NOTE)
    for s in grounded:
        assert 0 <= s["start_char"] < s["end_char"] <= note_len
        assert s["end_char"] - s["start_char"] == len(s["text"])


def test_hybrid_retriever_query_and_disease_filtering():
    """Verify HybridGuidelineRetriever finds relevant chunks and respects disease filters."""
    retriever = HybridGuidelineRetriever()

    # Query COPD & smoking
    copd_results = retriever.retrieve(query="COPD khó thở kéo dài hút thuốc lá FEV1", top_k=2)
    assert len(copd_results) >= 1
    assert any("GOLD" in r["guideline_source"] for r in copd_results)

    # Filter for Asthma
    asthma_results = retriever.retrieve(query="khó thở rít về đêm", disease_filter="ASTHMA", top_k=2)
    assert len(asthma_results) >= 1
    for r in asthma_results:
        assert "ASTHMA" in r["disease_entity"] or r["disease_entity"] == "ALL_RESPIRATORY_CARDIAC"


def test_hybrid_retriever_uses_qdrant_and_requires_source_metadata():
    from types import SimpleNamespace

    class FakeQdrant:
        def __init__(self):
            self.queries = []

        def query_points(self, **kwargs):
            self.queries.append(kwargs)
            return SimpleNamespace(points=[
                SimpleNamespace(payload={
                    "chunk_id": "VERIFIED_1", "source_id": "GOLD-DOC",
                    "version": "2024", "section_locator": "Section 2.1",
                    "text_content": "COPD diagnostic criteria", "disease_entity": "COPD",
                    "guideline_source": "GOLD_2024", "section_title": "Diagnosis",
                    "clinical_category": "DIAGNOSTIC_CRITERIA", "source_verified": True,
                }),
                SimpleNamespace(payload={"chunk_id": "NO_SOURCE", "text_content": "Untraceable"}),
            ])

    client = FakeQdrant()
    retriever = HybridGuidelineRetriever(qdrant_client=client, embedding_fn=lambda query: [0.1, 0.2])
    results = retriever.retrieve("COPD", top_k=10)
    assert client.queries[0]["query"] == [0.1, 0.2]
    assert any(item["chunk_id"] == "VERIFIED_1" and item["source_verified"] for item in results)
    assert all(item["chunk_id"] != "NO_SOURCE" for item in results)


def test_agent_explain_endpoint_pt0044():
    """Verify POST /api/v1/agent/explain endpoint for Case PT-0044."""
    payload = {
        "patient_id": "PT-0044",
        "clinical_notes": SAMPLE_PT0044_NOTE,
        "target_diagnosis": "ASTHMA",
        "differential_diagnosis": "COPD",
    }
    response = client.post("/api/v1/agent/explain", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["patient_id"] == "PT-0044"
    assert data["primary_diagnosis"] == "ASTHMA"
    assert data["differential_diagnosis"] == "COPD"
    assert "Hen phế quản" in data["primary_diagnosis_name"]
    assert len(data["grounded_spans"]) >= 3
    assert len(data["guideline_references"]) >= 1
    assert data["hallucination_filtered_count"] >= 0

    # Verify zero-hallucination property on all returned spans
    for span in data["grounded_spans"]:
        start = span["start_char"]
        end = span["end_char"]
        assert data["display_note"][start:end] == span["text"]


def test_grounder_rejects_partial_and_overlapping_claims():
    note = "Patient reports cough and fatigue."
    grounder = EvidenceGrounder()
    assert grounder.ground_single_claim(note, "Patient reports cough and fever") is None
    spans, rejected = grounder.ground_evidence_claims(
        note,
        ["Patient reports cough", "reports cough", "fatigue"],
    )
    assert rejected == 1
    assert len(spans) == 2
    assert all(note[s["start_char"] : s["end_char"]] == s["text"] for s in spans)


def test_agent_explain_endpoint_pt0254():
    """Verify POST /api/v1/agent/explain endpoint for Case PT-0254."""
    payload = {
        "patient_id": "PT-0254",
        "clinical_notes": SAMPLE_PT0254_NOTE,
        "target_diagnosis": "COPD",
        "differential_diagnosis": "HEART_FAILURE",
    }
    response = client.post("/api/v1/agent/explain", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["patient_id"] == "PT-0254"
    assert data["primary_diagnosis"] == "COPD"
    assert "COPD" in data["primary_diagnosis_name"]
    assert len(data["grounded_spans"]) >= 3

    # Check that tracheostomy span is present
    span_texts = [s["text"] for s in data["grounded_spans"]]
    assert any("tracheostomy" in t.lower() for t in span_texts)


def test_agent_explain_endpoint_invalid_short_note():
    """Verify endpoint rejects clinical notes shorter than 5 characters."""
    payload = {
        "patient_id": "PT-999",
        "clinical_notes": "Hi",
    }
    response = client.post("/api/v1/agent/explain", json=payload)
    assert response.status_code == 422 or response.status_code == 400
