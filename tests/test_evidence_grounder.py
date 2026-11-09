"""
Unit Tests for EvidenceGrounder
M-CDSS Backlog 05 - Member 2 Verification
"""

import pytest
from src.agent.evidence_grounder import EvidenceGrounder


@pytest.fixture
def sample_deidentified_note():
    return (
        "BỆNH ÁN TIỀN PHẪU VÀ HỘI CHẨN:\n"
        "Bệnh nhân nam, 67 tuổi, vào viện vì khó thở tiến triển dai dẳng và ho khạc đờm mạn tính.\n"
        "Tiền sử hút thuốc lá 35 bao-năm, khó thở tăng dần khi gắng sức trong 6 tháng qua.\n"
        "Khám lâm sàng: lồng ngực hình thùng, rì rào phế nang giảm hai phế trường, rale rít rải rác.\n"
        "SpO2: 89% khí trời, mạch 94 lần/phút, huyết áp 135/85 mmHg.\n"
        "Không có dấu hiệu đau ngực kiểu bóp nghẹt hay khó thở kịch phát về đêm.\n"
        "Chức năng thông khí phổi sau giãn phế quản: FEV1/FVC = 0.58."
    )


def test_exact_grounding(sample_deidentified_note):
    grounder = EvidenceGrounder()
    claims = [
        "Tiền sử hút thuốc lá 35 bao-năm",
        "SpO2: 89% khí trời",
        "FEV1/FVC = 0.58"
    ]

    spans = grounder.ground_evidence(sample_deidentified_note, claims)
    assert len(spans) == 3

    for span in spans:
        # Strict Invariant Test: S[start:end] == text
        s, e, text = span["start"], span["end"], span["text"]
        assert sample_deidentified_note[s:e] == text
        assert span["confidence"] == 1.0


def test_case_insensitive_grounding(sample_deidentified_note):
    grounder = EvidenceGrounder()
    claims = ["tiền sử hút thuốc lá 35 bao-năm"]

    spans = grounder.ground_evidence(sample_deidentified_note, claims)
    assert len(spans) == 1
    span = spans[0]
    # S[start:end] should match note exactly
    assert sample_deidentified_note[span["start"]:span["end"]] == span["text"]
    assert span["text"] == "Tiền sử hút thuốc lá 35 bao-năm"
    assert span["confidence"] >= 0.95


def test_normalized_whitespace_grounding(sample_deidentified_note):
    grounder = EvidenceGrounder()
    # Claim with extra spaces
    claims = ["lồng ngực   hình    thùng"]

    spans = grounder.ground_evidence(sample_deidentified_note, claims)
    assert len(spans) == 1
    span = spans[0]
    assert sample_deidentified_note[span["start"]:span["end"]] == "lồng ngực hình thùng"
    assert span["text"] == "lồng ngực hình thùng"


def test_hallucination_rejection(sample_deidentified_note):
    grounder = EvidenceGrounder()
    # Claims completely absent from note
    hallucinated_claims = [
        "Bệnh nhân có tiền sử đái tháo đường type 2 điều trị insulin",
        "Chụp CT ngực phát hiện tổn thương đông đặc hình chêm phân thùy dưới",
        "Điện tâm đồ ST chênh lên ở V1-V4"
    ]

    spans = grounder.ground_evidence(sample_deidentified_note, hallucinated_claims)
    # Zero hallucination guarantee: Must be empty
    assert len(spans) == 0


def test_detailed_claims_audit(sample_deidentified_note):
    grounder = EvidenceGrounder()
    claims = [
        "Tiền sử hút thuốc lá 35 bao-năm",  # verified
        "Bệnh nhân sốt cao 39.5 độ C",      # unverified hallucination
    ]

    audit = grounder.ground_claims_detailed(sample_deidentified_note, claims)
    assert len(audit) == 2

    assert audit[0]["status"] == "verified"
    assert len(audit[0]["spans"]) == 1
    assert "clinical_interpretation_note" in audit[0]

    assert audit[1]["status"] == "unverified"
    assert len(audit[1]["spans"]) == 0
    assert audit[1]["confidence"] == 0.0


def test_overlapping_spans_resolution():
    spans = [
        {"text": "hút thuốc lá", "start": 10, "end": 22, "confidence": 0.9},
        {"text": "Tiền sử hút thuốc lá 35 bao-năm", "start": 2, "end": 35, "confidence": 1.0},
        {"text": "khó thở", "start": 50, "end": 57, "confidence": 1.0},
    ]

    resolved = EvidenceGrounder.resolve_overlapping_spans(spans)
    assert len(resolved) == 2
    # The higher confidence span covering 2:35 should be kept, and 10:22 dropped
    assert resolved[0]["start"] == 2
    assert resolved[0]["end"] == 35
    assert resolved[1]["start"] == 50

