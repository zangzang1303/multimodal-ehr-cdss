"""
Comprehensive RAG, Evidence Grounding & Anti-Hallucination Unit Tests
Backlog 05 Definition of Done (DoD) Verification
"""

import pytest
from src.agent.evidence_grounder import EvidenceGrounder
from src.api.routes.agent_chat import explain_clinical_case
from src.api.schemas import AgentExplainRequest


@pytest.fixture
def sample_deidentified_note():
    return (
        "BỆNH ÁN HỘI CHẨN:\n"
        "Bệnh nhân nam 68 tuổi, tiền sử hút thuốc lá 40 bao-năm, khó thở tăng dần khi gắng sức.\n"
        "Khám lâm sàng: lồng ngực hình thùng, rì rào phế nang giảm đều hai phế trường.\n"
        "Đo chức năng hô hấp sau giãn phế quản: FEV1/FVC = 0.54, FEV1 = 45% dự đoán.\n"
        "SpO2: 87% khí trời, thở nhanh 32 lần/phút, có co kéo cơ hô hấp phụ.\n"
        "Không có sốt, không có đờm mủ đục, không có ran nổ khu trú.\n"
        "Điện tâm đồ: nhịp xoang nhanh 105 lần/phút, không có ST chênh lên."
    )


def test_grounded_spans_strict_offset_matching(sample_deidentified_note):
    """
    DoD 1: Verify all returned spans strictly match character index
    in the active de-identified clinical note: note[start:end] == span.text.
    """
    grounder = EvidenceGrounder()
    claims = [
        "tiền sử hút thuốc lá 40 bao-năm",
        "lồng ngực hình thùng",
        "FEV1/FVC = 0.54",
        "SpO2: 87% khí trời",
    ]

    spans = grounder.ground_evidence(sample_deidentified_note, claims)
    assert len(spans) == 4

    for span in spans:
        s, e, text = span["start"], span["end"], span["text"]
        # Invariant check
        assert sample_deidentified_note[s:e] == text
        assert span["confidence"] >= 0.95


def test_rejection_of_unreferenced_claims(sample_deidentified_note):
    """
    DoD 2: Claims lacking source passages in note must be rejected / flagged as unverified.
    """
    grounder = EvidenceGrounder()
    unreferenced_claims = [
        "Bệnh nhân có ran ẩm mịn hai đáy phổi và phản hồi gan - tĩnh mạch cổ dương tính",
        "Đo khí máu động mạch thấy pH 7.25, PaCO2 65 mmHg",
        "Chụp X-quang phổi có tổn thương đông đặc phân thùy giữa phổi phải",
    ]

    audit = grounder.ground_claims_detailed(sample_deidentified_note, unreferenced_claims)
    assert len(audit) == 3

    for item in audit:
        assert item["status"] == "unverified"
        assert len(item["spans"]) == 0
        assert item["confidence"] == 0.0


def test_guideline_citations_provenance(sample_deidentified_note):
    """
    DoD 3: Guidelines citations must have valid source_id, version, and section/page.
    """
    req = AgentExplainRequest(
        patient_id="PT-DOD-01",
        clinical_note=sample_deidentified_note,
        calibrated_probabilities={"COPD": 0.88, "ASTHMA": 0.08},
    )

    response = explain_clinical_case(req)
    assert response.status == "success"
    assert len(response.guideline_citations) > 0

    for cit in response.guideline_citations:
        assert cit.source_id in ["GOLD_2024", "GINA_2024", "ESC_2023", "BYT_VN_CAP_2020"]
        assert cit.version != ""
        assert cit.section_title != ""
        assert cit.page_or_section != ""
        assert cit.text_content != ""


def test_overlapping_and_modified_spans():
    """
    DoD 4: Test overlapping spans resolution and span ordering.
    """
    note = "Bệnh nhân có tiền sử hút thuốc lá nặng 30 bao-năm."
    grounder = EvidenceGrounder()
    # Overlapping claims
    claims = [
        "hút thuốc lá",
        "tiền sử hút thuốc lá nặng",
        "30 bao-năm",
    ]
    spans = grounder.ground_evidence(note, claims)
    # The overlapping span "hút thuốc lá" should be subsumed or resolved cleanly
    for i in range(len(spans) - 1):
        assert spans[i]["end"] <= spans[i + 1]["start"], "Spans must not overlap in resolved output"

