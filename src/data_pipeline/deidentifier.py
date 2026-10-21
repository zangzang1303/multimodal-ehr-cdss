from __future__ import annotations

import logging
import re
from typing import Iterable, List, Optional, Tuple

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )


class ClinicalDeidentifier:

    DEFAULT_SPACY_MODEL = "en_core_web_sm"

    def __init__(
        self,
        spacy_model: Optional[str] = "en_core_web_sm",
        use_ner: bool = True,
        email_token: str = "[REDACTED_EMAIL]",
        id_token: str = "[REDACTED_ID]",
        phone_token: str = "[REDACTED_PHONE]",
        date_token: str = "[REDACTED_DATE]",
        name_token: str = "[REDACTED_NAME]",
        hospital_token: str = "[REDACTED_HOSPITAL]",
        loc_token: str = "[REDACTED_LOC]",
    ) -> None:

        self.spacy_model_name = spacy_model
        self.use_ner = use_ner

        self.EMAIL_TOKEN = email_token
        self.ID_TOKEN = id_token
        self.PHONE_TOKEN = phone_token
        self.DATE_TOKEN = date_token
        self.NAME_TOKEN = name_token
        self.HOSPITAL_TOKEN = hospital_token
        self.LOC_TOKEN = loc_token

        self.nlp = None
        if self.use_ner and self.spacy_model_name:
            self._init_spacy_model(self.spacy_model_name)

        self._compile_patterns()

    def _init_spacy_model(self, model_name: str) -> None:

        try:
            import spacy

            try:
                self.nlp = spacy.load(model_name)
                logger.info("ClinicalDeidentifier: Loaded spaCy model '%s'.", model_name)
            except OSError:
                logger.warning(
                    "spaCy model '%s' not found locally. Attempting to download...",
                    model_name,
                )
                try:
                    spacy.cli.download(model_name)
                    self.nlp = spacy.load(model_name)
                    logger.info(
                        "ClinicalDeidentifier: Successfully downloaded and loaded '%s'.", model_name
                    )
                except Exception as dl_err:
                    logger.warning(
                        "Unable to auto-download '%s' (%s). Falling back to blank model.",
                        model_name,
                        dl_err,
                    )
                    self.nlp = spacy.blank("en")
        except ImportError:
            logger.warning("spaCy is not installed. NER-based masking will be disabled.")
            self.nlp = None

    def _compile_patterns(self) -> None:

        # Structured EHR exports often carry PHI in labelled header fields. These
        # rules are language-aware and do not depend on an English NER model.
        self.structured_name_pattern = re.compile(
            r"(?i)((?:Patient Name|Tên bệnh nhân|Họ và tên|Doctor Name|Tên bác sĩ|Attending Physician)\s*:\s*)"
            r"[^\r\n|]+"
        )
        self.structured_facility_pattern = re.compile(
            r"(?im)^(\s*(?:Facility|Hospital|Cơ sở|Bệnh viện)\s*:\s*)[^\r\n|]+"
        )
        self.structured_id_pattern = re.compile(
            r"(?i)\b((?:(?:Patient|Encounter|Medical Record|MRN)\s+ID|"
            r"Citizen ID/SSN|Insurance ID(?:\s*\(BHYT\))?)\s*:\s*)[A-Za-z0-9_-]+"
        )
        self.structured_location_pattern = re.compile(
            r"(?im)^(\s*(?:Residential Address|Home Address|Địa chỉ)\s*:\s*)[^\r\n|]+"
        )

        self.email_pattern = re.compile(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}\b",
            re.IGNORECASE,
        )

        self.phone_pattern = re.compile(r"(?:\+84|\b0)(?:[\s.-]?)(?:3|5|7|8|9)(?:[\s.-]?\d){8}\b")

        self.labeled_id_pattern = re.compile(
            r"\b(?:CCCD|CMND|BHYT|MRN|HSBA|Mã thẻ|Số thẻ|Mã định danh|Định danh|SSN)[:\s]+([A-Za-z0-9\-_]{6,16})\b",
            re.IGNORECASE,
        )

        self.bhyt_pattern = re.compile(
            r"\b(?:DN|GD|TE|CA|QN|HC|XK|HT|TB|NO|CT|XB|TN|CS|XN|MS|HD|TQ|TA|TY|HG|LS|PV|CN|HS|SV|GB|CB|CF|CH|KC|HN|DT|DK|XD|BT|TS|TC|TV)\d{13}\b"
        )

        self.standalone_id_pattern = re.compile(r"\b\d{9}\b|\b\d{12}\b")

        self.date_patterns = [
            re.compile(r"\bngày\s+\d{1,2}\s+tháng\s+\d{1,2}\s+năm\s+\d{4}\b", re.IGNORECASE),
            re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"),
            re.compile(r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b"),
            re.compile(r"\b\d{1,2}\.\d{1,2}\.\d{2,4}\b"),
        ]

        self.doctor_context_pattern = re.compile(
            r"(?:\b(?i:bác sĩ|bác sỹ|bs\.|bs|y sĩ|điều dưỡng|dr\.|doctor)\s+)"
            r"([A-ZÀ-ỸĐ][a-zà-ỹđ]*(?:\s+[A-ZÀ-ỸĐ][a-zà-ỹđ]*){1,5})\b"
        )

        self.patient_context_pattern = re.compile(
            r"(?:\b(?i:bệnh nhân|bn\.|bn|patient|pt\.)\s+)"
            r"([A-ZÀ-ỸĐ][a-zà-ỹđ]*(?:\s+[A-ZÀ-ỸĐ][a-zà-ỹđ]*){1,5})\b"
        )

        self.contact_context_pattern = re.compile(
            r"(?:\b(?i:người nhà|thân nhân|liên hệ|người giám hộ|family|contact)\s*(?::|-)?\s*)"
            r"([A-ZÀ-ỸĐ][a-zà-ỹđ]*(?:\s+[A-ZÀ-ỸĐ][a-zà-ỹđ]*){1,5})\b"
        )

        self.hospital_context_pattern = re.compile(
            r"\b(?i:bệnh viện|bv|phòng khám|trạm y tế|trung tâm y tế)\s+([A-ZÀ-ỸĐ][a-zà-ỹđ0-9]*(?:\s+[A-ZÀ-ỸĐ][a-zà-ỹđ0-9]*)*)\b"
        )
        self.hospital_en_pattern = re.compile(
            r"\b([A-Z][a-zA-Z0-9]*(?:\s+[A-Z][a-zA-Z0-9]*)*\s+(?i:hospital|clinic|health center|medical center|infirmary))\b"
        )

    def deidentify_text(self, text: str) -> str:

        if not isinstance(text, str) or not text.strip():
            return "" if text is None else text

        result = text

        result = self.structured_name_pattern.sub(
            lambda m: m.group(1) + self.NAME_TOKEN, result
        )
        result = self.structured_facility_pattern.sub(
            lambda m: m.group(1) + self.HOSPITAL_TOKEN, result
        )
        result = self.structured_id_pattern.sub(
            lambda m: m.group(1) + self.ID_TOKEN, result
        )
        result = self.structured_location_pattern.sub(
            lambda m: m.group(1) + self.LOC_TOKEN, result
        )

        result = self.doctor_context_pattern.sub(
            lambda m: m.group(0).replace(m.group(1), self.NAME_TOKEN),
            result,
        )

        result = self.patient_context_pattern.sub(
            lambda m: m.group(0).replace(m.group(1), self.NAME_TOKEN),
            result,
        )

        result = self.contact_context_pattern.sub(
            lambda m: m.group(0).replace(m.group(1), self.NAME_TOKEN),
            result,
        )

        result = self.hospital_context_pattern.sub(self.HOSPITAL_TOKEN, result)
        result = self.hospital_en_pattern.sub(self.HOSPITAL_TOKEN, result)

        result = self.email_pattern.sub(self.EMAIL_TOKEN, result)

        result = self.phone_pattern.sub(self.PHONE_TOKEN, result)

        for date_pat in self.date_patterns:
            result = date_pat.sub(self.DATE_TOKEN, result)

        result = self.labeled_id_pattern.sub(
            lambda m: m.group(0).replace(m.group(1), self.ID_TOKEN),
            result,
        )

        result = self.bhyt_pattern.sub(self.ID_TOKEN, result)

        result = self.standalone_id_pattern.sub(self.ID_TOKEN, result)

        if self.nlp is not None:
            doc = self.nlp(result)
            entities_to_replace: List[Tuple[int, int, str]] = []
            hospital_keywords = {
                "hospital",
                "clinic",
                "bệnh viện",
                "phòng khám",
                "center",
                "centre",
            }

            for ent in doc.ents:
                ent_text = ent.text.strip()
                if ent_text.startswith("[REDACTED_"):
                    continue

                token_to_use = None
                if ent.label_ in ["PERSON", "PER"]:
                    token_to_use = self.NAME_TOKEN
                elif ent.label_ in ["FAC", "FACILITY", "ORG"]:
                    if any(kw in ent_text.lower() for kw in hospital_keywords):
                        token_to_use = self.HOSPITAL_TOKEN
                elif ent.label_ in ["GPE", "LOC"]:
                    token_to_use = self.LOC_TOKEN
                elif ent.label_ in ["DATE", "TIME"]:
                    token_to_use = self.DATE_TOKEN

                if token_to_use:
                    entities_to_replace.append((ent.start_char, ent.end_char, token_to_use))

            for start, end, token in sorted(entities_to_replace, key=lambda x: x[0], reverse=True):
                result = result[:start] + token + result[end:]

        return result

    def anonymize(self, text: str) -> str:
        return self.deidentify_text(text)

    def deidentify(self, text: str) -> str:
        return self.deidentify_text(text)

    def deidentify_batch(self, texts: Iterable[str]) -> List[str]:
        return [self.deidentify_text(t) for t in texts]
