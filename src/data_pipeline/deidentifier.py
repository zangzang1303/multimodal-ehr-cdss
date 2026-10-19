"""
MOCK FILE - DO THÀNH VIÊN 3 TẠO MOCK ĐỂ PHỤC VỤ TEST / PHÁT TRIỂN
CẦN THAY THẾ (TODO: REPLACE WITH MEMBER 2'S ACTUAL IMPLEMENTATION IN SPRINT)
Mô tả: Module khử định danh PHI/PII (Regex + Biomedical NER / Rule-based)
Tuân thủ: HIPAA 18 Safe Harbor Identifiers
"""

import re
from typing import Optional


class ClinicalDeidentifier:
    """
    Mock implementation of ClinicalDeidentifier for testing and system development.
    Replaces sensitive clinical entities (CCCD, phone, email, dates, hospitals, doctor/patient names)
    with standardized surrogate tokens:
    [REDACTED_NAME], [REDACTED_DATE], [REDACTED_HOSPITAL], [REDACTED_PHONE], [REDACTED_ID].
    """

    def __init__(self, spacy_model: Optional[str] = "en_core_web_sm"):
        self.spacy_model_name = spacy_model
        self.nlp = None

        if spacy_model:
            try:
                import spacy
                self.nlp = spacy.load(spacy_model)
            except Exception:
                # Fallback to rule engine if model is not downloaded
                self.nlp = None

        # Regex patterns for clinical de-identification
        self.phone_pattern = re.compile(
            r'(?:\+84|0)(?:3[2-9]|5[689]|7[06-9]|8[1-9]|9[0-9])\d{7}\b|\b(?:\+84|0)\d{9,10}\b'
        )
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
        )
        # CCCD / CMND / National ID (9 - 12 digits)
        self.id_pattern = re.compile(
            r'\b\d{12}\b|\b\d{9}\b'
        )
        # Date patterns (DD/MM/YYYY, YYYY-MM-DD, DD-MM-YYYY)
        self.date_pattern = re.compile(
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b'
        )
        # Hospital & healthcare facility patterns in Vietnamese
        self.hospital_pattern = re.compile(
            r'(?:Bệnh viện|BV|Phòng khám|Trạm y tế)\s+([A-ZÀ-Ỹ][a-zà-ỹ0-9]+(?:\s+[A-ZÀ-Ỹ][a-zà-ỹ0-9]+)*)',
            re.UNICODE,
        )
        # Doctor / Patient naming patterns in Vietnamese
        self.doctor_pattern = re.compile(
            r'(?:Bác sĩ|Bác sỹ|BS\.?|bác sĩ|bác sỹ)\s+([A-ZÀ-Ỹ][a-zà-ỹ]+(?:\s+[A-ZÀ-Ỹ][a-zà-ỹ]+){1,3})',
            re.UNICODE,
        )
        self.patient_pattern = re.compile(
            r'(?:Bệnh nhân|bệnh nhân|BN\.?)\s+([A-ZÀ-Ỹ][a-zà-ỹ]+(?:\s+[A-ZÀ-Ỹ][a-zà-ỹ]+){1,3})',
            re.UNICODE,
        )

    def deidentify_text(self, text: str) -> str:
        """
        De-identify unstructured clinical notes by replacing PHI with surrogate tokens.
        """
        if not text:
            return ""

        redacted = text

        # 1. Redact Email & Phone
        redacted = self.email_pattern.sub("[REDACTED_ID]", redacted)
        redacted = self.phone_pattern.sub("[REDACTED_PHONE]", redacted)

        # 2. Redact Date
        redacted = self.date_pattern.sub("[REDACTED_DATE]", redacted)

        # 3. Redact National ID / CCCD (12 or 9 digits)
        redacted = self.id_pattern.sub("[REDACTED_ID]", redacted)

        # 4. Redact Doctor and Patient names
        redacted = self.doctor_pattern.sub(r"Bác sĩ [REDACTED_NAME]", redacted)
        redacted = self.patient_pattern.sub(r"bệnh nhân [REDACTED_NAME]", redacted)

        # 5. Redact Hospital / Facility
        redacted = self.hospital_pattern.sub(r"[REDACTED_HOSPITAL]", redacted)

        # 6. Fallback spaCy NER if available for any remaining entities
        if self.nlp:
            try:
                doc = self.nlp(redacted)
                for ent in doc.ents:
                    if ent.label_ in ("PERSON", "PER"):
                        redacted = redacted.replace(ent.text, "[REDACTED_NAME]")
                    elif ent.label_ in ("ORG", "FACILITY") and "[REDACTED" not in ent.text:
                        redacted = redacted.replace(ent.text, "[REDACTED_HOSPITAL]")
            except Exception:
                pass

        return redacted
