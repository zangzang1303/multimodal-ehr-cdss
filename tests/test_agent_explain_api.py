"""
Tests for POST /api/v1/agent/explain Endpoint
M-CDSS Backlog 05 - Member 2 Deliverable
"""

import pytest
from fastapi import HTTPException
from src.api.routes.agent_chat import explain_clinical_case
from src.api.schemas import AgentExplainRequest, AgentExplainResponse


@pytest.fixture
def sample_explain_request():
    return AgentExplainRequest(
        patient_id="PT-TEST-001",
        clinical_note=(
            "BỆNH ÁN:\n"
            "Bệnh nhân nam 65 tuổi vào viện vì khó thở tiến triển dai dẳng.\n"
            "Tiền sử hút thuốc lá 35 bao-năm.\n"
            "Chức năng thông khí phổi: FEV1/FVC = 0.58 sau thử thuốc giãn phế quản.\n"
            "SpO2: 89% khí trời, nhịp thở 28 lần/phút."
        ),
        calibrated_probabilities={
            "COPD": 0.82,
            "ASTHMA": 0.12,
            "CONGESTIVE_HEART_FAILURE": 0.04,
            "COMMUNITY_ACQUIRED_PNEUMONIA": 0.02,
        },
        target_diagnosis="ASTHMA",  # Client suggests ASTHMA, but model indicates COPD
    )


def test_agent_explain_logic_success(sample_explain_request):
    """
    Direct endpoint logic test: verifies differential reasoning, grounding,
    guidelines citations, and untrusted label audit.
    """
    response: AgentExplainResponse = explain_clinical_case(sample_explain_request)

    assert response.status == "success"
    assert response.patient_id == "PT-TEST-001"
    # Primary hypothesis must be COPD based on calibrated probability, not ASTHMA from client
    assert response.top1_diagnosis == "COPD"
    assert response.top2_diagnosis == "ASTHMA"
    assert "COPD" in response.differential_reasoning

    # Guideline citations integrity
    assert len(response.guideline_citations) > 0
    for g in response.guideline_citations:
        assert g.source_id in ["GOLD_2024", "GINA_2024", "ESC_2023", "BYT_VN_CAP_2020"]
        assert g.version is not None
        assert g.section_title != ""
        assert g.text_content != ""

    # Spans integrity: invariant check note[start:end] == span.text
    note = sample_explain_request.clinical_note
    assert len(response.verified_spans) > 0
    for span in response.verified_spans:
        assert note[span.start : span.end] == span.text
        assert span.confidence >= 0.90

    # Warning regarding client target_diagnosis
    assert response.warning is not None
    assert "disregarded as ground truth" in response.warning


def test_agent_explain_empty_note_validation():
    """Verify empty clinical note raises HTTP 422."""
    with pytest.raises((HTTPException, ValueError)):
        req = AgentExplainRequest(
            patient_id="PT-EMPTY",
            clinical_note="   ",
        )
        explain_clinical_case(req)


def test_agent_explain_insufficient_evidence():
    """Verify ungrounded / out-of-domain case triggers insufficient_evidence status."""
    req = AgentExplainRequest(
        patient_id="PT-IRRELEVANT",
        clinical_note=(
            "Bệnh nhân vào khám mắt định kỳ, thị lực hai mắt 10/10, không có triệu chứng hô hấp tim mạch nào."
        ),
        calibrated_probabilities={
            "UNKNOWN_DISEASE": 0.99,
        },
    )
    response = explain_clinical_case(req)
    assert response.has_insufficient_evidence is True or response.status == "insufficient_evidence"


def test_agent_explain_claim_audits(sample_explain_request):
    """Verify each claim has separate span location from clinical interpretation."""
    response = explain_clinical_case(sample_explain_request)
    assert len(response.claim_audits) > 0
    for audit in response.claim_audits:
        assert audit.status in ["verified", "candidate", "unverified"]
        if audit.status == "verified":
            assert audit.clinical_interpretation_note is not None
            assert "Clinical interpretation must be validated independently" in audit.clinical_interpretation_note
