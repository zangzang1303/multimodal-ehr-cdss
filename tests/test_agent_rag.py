"""
Unit Tests for Agentic RAG, Evidence Grounding & Clinical Explainability
M-CDSS Phase 2 / Backlog 05 & 06
"""

import pytest
from fastapi.testclient import TestClient

from src.agent.diagnostic_graph import DiagnosticGraphState, DiagnosticStateGraph
from src.agent.evidence_grounder import EvidenceGrounder
from src.agent.retriever import HybridGuidelineRetriever, STANDARD_GUIDELINE_CORPUS
from src.api.main import app
from src.evaluation.dca_analysis import evaluate_holdout_dca

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


def test_hybrid_retriever_qdrant_indexing_and_hybrid_scores():
    """
    Verify HybridGuidelineRetriever indexes vectors into Qdrant and computes true
    hybrid combination of Okapi BM25 + Cosine Similarity:
        S_hybrid = alpha * S_bm25_norm + (1 - alpha) * S_cosine
    """
    retriever = HybridGuidelineRetriever(alpha=0.65)
    assert retriever._qdrant_ready is True
    assert retriever.qdrant_client is not None

    col_info = retriever.qdrant_client.get_collection(retriever.collection_name)
    assert col_info.points_count == len(STANDARD_GUIDELINE_CORPUS)

    results = retriever.retrieve(
        query="suy tim khó thở khi nằm orthopnea phù hai chi dưới NT-proBNP",
        top_k=3,
    )
    assert len(results) == 3
    top_hit = results[0]
    assert top_hit["disease_entity"] == "HEART_FAILURE"
    assert "bm25_score" in top_hit
    assert "cosine_score" in top_hit
    assert top_hit["bm25_score"] > 0.0
    assert top_hit["cosine_score"] > 0.0

    expected_hybrid = round(
        0.65 * top_hit["bm25_score"] + 0.35 * top_hit["cosine_score"], 4
    )
    assert abs(top_hit["relevance_score"] - expected_hybrid) <= 1e-3


def test_diagnostic_state_graph_four_node_execution():
    """Verify DiagnosticStateGraph executes all 4 nodes in order."""
    graph = DiagnosticStateGraph()
    init_state = DiagnosticGraphState(
        patient_id="PT-0044",
        raw_clinical_notes=SAMPLE_PT0044_NOTE,
    )
    final_state = graph.invoke(init_state)

    assert final_state.executed_nodes == [
        "triage_and_query_node",
        "hybrid_guideline_retrieval_node",
        "clinical_reasoning_node",
        "evidence_grounding_node",
    ]
    assert final_state.primary_diagnosis == "ASTHMA"
    assert final_state.differential_diagnosis == "COPD"
    assert len(final_state.retrieved_guidelines) >= 1
    assert len(final_state.grounded_spans) >= 3
    assert final_state.hallucination_filtered_count >= 1


def test_dca_analysis_mathematical_consistency():
    """
    Verify Decision Curve Analysis (DCA) computation on N=302 hold-out test set
    and ensure net_tp_gained_per_100 and net_interventions_avoided_per_100 match
    the exact formulas in the paper.
    """
    dca_res = evaluate_holdout_dca()
    assert dca_res["n_samples"] == 302
    points = dca_res["threshold_points"]
    assert len(points) == 12

    for pt_obj in points:
        pt = pt_obj["threshold"]
        nb_m = pt_obj["net_benefit_mcdss"]
        nb_all = pt_obj["net_benefit_treat_all"]
        nb_none = pt_obj["net_benefit_treat_none"]
        assert nb_none == 0.0

        # Formula 1: ΔTP_net/100 = 100 * max(0, NB_mcdss - max(NB_all, 0))
        expected_tp = round(100.0 * max(0.0, nb_m - max(nb_all, 0.0)), 1)
        assert abs(pt_obj["net_tp_gained_per_100"] - expected_tp) <= 0.2

        # Formula 2: ΔFP_avoided/100 = 100 * max(0, (NB_mcdss - NB_all) / (pt / (1 - pt)))
        odds = pt / (1.0 - pt)
        expected_avoided = round(100.0 * max(0.0, (nb_m - nb_all) / odds), 1)
        assert abs(pt_obj["net_interventions_avoided_per_100"] - expected_avoided) <= 0.5


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
    assert data["hallucination_filtered_count"] >= 1

    # Verify zero-hallucination property on all returned spans
    for span in data["grounded_spans"]:
        start = span["start_char"]
        end = span["end_char"]
        assert SAMPLE_PT0044_NOTE[start:end] == span["text"]


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
