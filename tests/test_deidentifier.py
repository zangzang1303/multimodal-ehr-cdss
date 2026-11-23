"""
Unit tests for ClinicalDeidentifier (M-CDSS Backlog 08 - Task 2.2)
Verifies positive and negative regex patterns:
- Positive: Vietnamese BHYT, academic titles/degrees, uppercase hospital names, dates, phone, IDs
- Negative: Clinical abbreviations like BP, HR, SpO2, WBC, CRP, normal sentence starters
"""

import pytest
from src.data_pipeline.deidentifier import ClinicalDeidentifier


@pytest.fixture
def deid():
    return ClinicalDeidentifier(spacy_model=None, use_ner=False)


def test_bhyt_redaction_positive(deid):
    samples = [
        "Thẻ BHYT: DN485553035110",
        "Mã thẻ BHYT: GD418667188111",
        "Insurance ID: DN418667188111",
        "Số thẻ BHYT: TE123456789012",
        "BHYT: CA1234567890123",
        "Mã BHYT: DN412345678901",
    ]
    for s in samples:
        res = deid.deidentify_text(s)
        assert "[REDACTED_ID]" in res, f"Failed to redact BHYT in: {s}"
        assert "DN485553035110" not in res
        assert "GD418667188111" not in res


def test_doctor_degrees_and_titles_positive(deid):
    samples = [
        "Bác sĩ khám: BS. Nguyễn Văn Hùng",
        "Hội chẩn cùng PGS.TS. Lê Hoàng Nam",
        "Thăm khám trực tiếp bởi BS.CKII. Trần Thu Hà",
        "Bác sĩ điều trị: ThS. BS. Vũ Quốc Tuấn",
        "Phụ trách ca: BS.CKI. Đỗ Quốc Tuấn",
        "Bác sĩ chuyên khoa: BSCK. Hoàng Minh Đức",
        "Chỉ đạo chuyên môn: GS.TS. Nguyễn Gia Bình",
    ]
    for s in samples:
        res = deid.deidentify_text(s)
        assert "[REDACTED_NAME]" in res, f"Failed to redact doctor in: {s}"
        assert "Lê Hoàng Nam" not in res
        assert "Trần Thu Hà" not in res
        assert "Nguyễn Văn Hùng" not in res
        assert "Vũ Quốc Tuấn" not in res


def test_uppercase_hospital_positive(deid):
    samples = [
        "HỒ SƠ BỆNH ÁN ĐIỆN TỬ - BỆNH VIỆN BẠCH MAI",
        "Khám tại BỆNH VIỆN PHỔI TRUNG ƯƠNG ngày 10/10/2026",
        "Chuyển viện từ BỆNH VIỆN ĐẠI HỌC Y HÀ NỘI",
        "BỆNH VIỆN TRUNG ƯƠNG QUÂN ĐỘI 108",
        "Tiếp nhận tại Bệnh viện Chợ Rẫy",
    ]
    for s in samples:
        res = deid.deidentify_text(s)
        assert "[REDACTED_HOSPITAL]" in res, f"Failed to redact hospital in: {s}"
        assert "BẠCH MAI" not in res
        assert "PHỔI TRUNG ƯƠNG" not in res


def test_clinical_vitals_negative_not_masked(deid):
    clinical_text = (
        "BP: 120/80 mmHg, HR: 88 bpm, RR: 20 bpm, SpO2: 96%, Temp: 37.1 C. "
        "WBC count: 8.5 x10^9/L, CRP: 5.2 mg/L. "
        "Bệnh nhân khó thở tăng dần, không sốt, không đau ngực. "
        "Bệnh sử ghi nhận ho khạc đờm 3 ngày nay."
    )
    res = deid.deidentify_text(clinical_text)
    assert "BP: 120/80 mmHg" in res
    assert "HR: 88 bpm" in res
    assert "SpO2: 96%" in res
    assert "WBC count: 8.5" in res
    assert "CRP: 5.2" in res
    assert "Bệnh nhân khó thở" in res
    assert "Bệnh sử ghi nhận" in res
    assert "[REDACTED_NAME]" not in res
    assert "[REDACTED_HOSPITAL]" not in res


def test_structured_headers_deidentification(deid):
    header = (
        "HỒ SƠ BỆNH ÁN ĐIỆN TỬ - BỆNH VIỆN BẠCH MAI\n"
        "Ngày tiếp nhận: 21/08/2026 | Bác sĩ khám: BS. Nguyễn Văn Hùng\n"
        "Bệnh nhân: Phạm Hồng Minh | Giới tính: M | Tuổi: 69\n"
        "Số CMND/CCCD: 096821668732 | Thẻ BHYT: DN485553035110 | Điện thoại liên hệ: 0772719583\n"
        "Nơi cư trú: Hà Nội, Việt Nam\n"
    )
    res = deid.deidentify_text(header)
    assert "[REDACTED_HOSPITAL]" in res
    assert "[REDACTED_NAME]" in res
    assert "[REDACTED_ID]" in res
    assert "[REDACTED_PHONE]" in res
    assert "[REDACTED_LOC]" in res
    assert "Phạm Hồng Minh" not in res
    assert "096821668732" not in res
    assert "DN485553035110" not in res
    assert "0772719583" not in res
