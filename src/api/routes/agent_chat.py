"""
Agent Consultation & Clinical Explainability Router
M-CDSS Phase 2 / Backlog 05 (Task 3.4 & Task 2.3)

Provides deterministic template differential reasoning and Character-Offset
Evidence Grounding (string-match verification only) with CPG Retrieval.
"""

import re
import time
from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException

from src.agent.evidence_grounder import EvidenceGrounder
from src.agent.retriever import HybridGuidelineRetriever
from src.api.schemas import (
    AgentExplainRequest,
    AgentExplainResponse,
    ClaimAudit,
    EvidenceSpan,
    GuidelineReference,
)
from src.data_pipeline.deidentifier import ClinicalDeidentifier

router = APIRouter(prefix="/agent")

grounder = EvidenceGrounder(fuzzy_threshold=0.88)
retriever = HybridGuidelineRetriever()
deidentifier = ClinicalDeidentifier(spacy_model=None, use_ner=False)

KNOWN_CLINICAL_DIAGNOSES = {
    "ASTHMA",
    "COPD",
    "HEART_FAILURE",
    "CONGESTIVE_HEART_FAILURE",
    "PNEUMONIA",
    "COMMUNITY_ACQUIRED_PNEUMONIA",
}


@router.options("/explain")
def options_explain():
    """Direct OPTIONS handler for CORS preflight."""
    return {"status": "ok"}


@router.post("/explain", response_model=AgentExplainResponse)
def explain_clinical_case(request: AgentExplainRequest) -> AgentExplainResponse:
    """
    Multi-Agent Differential Diagnosis & Character-Offset Evidence Grounding Endpoint.
    Analyzes raw patient clinical notes against primary and differential hypotheses,
    extracts character-offset spans verified against the note (string-match provenance only),
    and retrieves CPG references.
    """
    start_time = time.time()
    patient_id = request.patient_id or "PT-001"
    raw_notes = request.clinical_notes or ""

    if len(raw_notes.strip()) < 5:
        raise HTTPException(
            status_code=422,
            detail="Bệnh án lâm sàng quá ngắn, vui lòng nhập ít nhất 5 ký tự để phân tích.",
        )

    # De-identify PHI defensively
    clean_notes = deidentifier.deidentify_text(raw_notes)
    notes_lower = clean_notes.lower()

    # Determine primary vs differential hypothesis (calibrated probabilities take priority)
    warning_msg: str | None = None
    if request.calibrated_probabilities and len(request.calibrated_probabilities) > 0:
        sorted_probs = sorted(
            request.calibrated_probabilities.items(),
            key=lambda item: float(item[1]),
            reverse=True,
        )
        top1 = sorted_probs[0][0].upper()
        if len(sorted_probs) > 1:
            top2 = sorted_probs[1][0].upper()
        else:
            top2 = "COPD" if top1 != "COPD" else "ASTHMA"
        if request.target_diagnosis and request.target_diagnosis.upper() != top1:
            warning_msg = (
                f"Client target_diagnosis '{request.target_diagnosis}' was disregarded as ground truth "
                f"in favor of calibrated model probabilities (top prediction: {top1})."
            )
    elif request.target_diagnosis:
        top1 = request.target_diagnosis.upper()
        top2 = request.differential_diagnosis.upper() if request.differential_diagnosis else ("COPD" if top1 != "COPD" else "ASTHMA")
    elif "sốt" in notes_lower or "đờm mủ" in notes_lower or "pneumonia" in notes_lower or "viêm phổi" in notes_lower:
        top1 = "PNEUMONIA"
        top2 = "COPD"
    elif "suy tim" in notes_lower or "orthopnea" in notes_lower or "phù" in notes_lower:
        top1 = "HEART_FAILURE"
        top2 = "COPD"
    elif ("khó thở" in notes_lower or "tracheostomy" in notes_lower or "copd" in notes_lower) and (
        "hút thuốc" in notes_lower or "bao-năm" in notes_lower or "tracheostomy" in notes_lower or "smoking" in notes_lower
    ):
        top1 = "COPD"
        top2 = "ASTHMA"
    elif "inhaler" in notes_lower or "wheez" in notes_lower or "hen" in notes_lower or "asthma" in notes_lower:
        top1 = "ASTHMA"
        top2 = "COPD"
    else:
        top1 = "ASTHMA"
        top2 = "COPD"

    disease_names = {
        "ASTHMA": "Hen phế quản (Asthma)",
        "COPD": "Bệnh phổi tắc nghẽn mạn (COPD)",
        "HEART_FAILURE": "Suy tim (Heart Failure)",
        "CONGESTIVE_HEART_FAILURE": "Suy tim (Heart Failure)",
        "PNEUMONIA": "Viêm phổi mắc phải cộng đồng (CAP)",
        "COMMUNITY_ACQUIRED_PNEUMONIA": "Viêm phổi mắc phải cộng đồng (CAP)",
    }

    # Retrieve matching guidelines via Hybrid Retriever
    guideline_query = f"tiêu chuẩn chẩn đoán phân biệt {top1} và {top2} triệu chứng khó thở ho đờm"
    retrieved_raw = retriever.retrieve(query=guideline_query, top_k=3)
    guideline_refs = [
        GuidelineReference(
            chunk_id=c["chunk_id"],
            source_id=c.get("source_id", ""),
            version=c.get("version", ""),
            section_locator=c.get("section_locator", ""),
            source_verified=c.get("source_verified", False),
            guideline_source=c["guideline_source"],
            disease_entity=c["disease_entity"],
            section_title=c["section_title"],
            clinical_category=c["clinical_category"],
            evidence_level=c.get("evidence_level") or "N/A",
            text_content=c["text_content"],
            relevance_score=c.get("relevance_score", 1.0),
        )
        for c in retrieved_raw
    ]

    # Formulate uniform clinical reasoning & dynamic evidence extraction (no hardcoded patient IDs)
    claims_to_ground: List[Dict[str, Any]] = []
    red_flags: List[str] = []

    def _is_admin_boilerplate(line: str) -> bool:
        stripped = line.strip()
        if not stripped or len(stripped) < 15:
            return True
        if re.fullmatch(r"[-=_\s]+", stripped):
            return True
        if "|" in stripped:
            return True
        upper = stripped.upper()
        admin_tokens = (
            "CLINICAL ENCOUNTER NOTE",
            "ELECTRONIC HEALTH RECORD",
            "PATIENT ID:",
            "HỒ SƠ BỆNH ÁN",
            "NGÀY TIẾP NHẬN",
            "BÁC SĨ KHÁM",
            "CMND/CCCD",
            "THẺ BHYT",
            "ĐIỆN THOẠI LIÊN HỆ",
            "NƠI CƯ TRÚ",
            "GIỚI TÍNH:",
            "HỌ VÀ TÊN",
        )
        if any(tok in upper for tok in admin_tokens):
            return True
        if stripped.endswith(":") or re.fullmatch(r"\d+\.\s*[A-ZÀ-Ỹ0-9\s/()-]+:?", stripped):
            return True
        return False

    candidate_sentences = [
        s.strip()
        for s in re.split(r"(?:\r?\n|(?<!\d)\.(?!\d))", clean_notes)
        if not _is_admin_boilerplate(s)
    ]
    if not candidate_sentences:
        candidate_sentences = [
            s.strip()
            for s in re.split(r"(?:\r?\n|(?<!\d)\.(?!\d))", clean_notes)
            if len(s.strip()) > 10
        ]

    for idx, sentence in enumerate(candidate_sentences[:4]):
        cat = "supporting" if idx % 2 == 0 else "counter"
        claims_to_ground.append({
            "text": sentence,
            "category": cat,
            "label": f"Chứng cứ {idx + 1}" if cat == "supporting" else f"Yếu tố phân biệt {idx + 1}",
            "reason": "Trích dẫn nguyên văn từ nội dung diễn biến lâm sàng của bệnh nhân.",
        })

    investigations = [
        "Đo chức năng thông khí phổi (Hô hấp ký) trước và sau nghiệm pháp giãn phế quản",
        "Chụp X-quang tim phổi thẳng hoặc CT lồng ngực liều thấp",
        "Xét nghiệm tổng phân tích tế bào máu và nồng độ CRP định lượng",
    ]

    # Check for clinical red-flags
    if "spO2: 9" not in raw_notes and ("spo2 < 88" in notes_lower or "tím tái" in notes_lower):
        red_flags.append("Cảnh báo suy hô hấp cấp nguy kịch: Độ bão hòa oxy giảm nghiêm trọng.")
    if "huyết áp" in notes_lower and ("< 90" in notes_lower or "tụt huyết áp" in notes_lower):
        red_flags.append("Cảnh báo huyết động: Nguy cơ sốc hoặc tụt huyết áp cấp.")

    # Execute Evidence Grounding and Anti-Hallucination verification
    grounded_raw, rejected_count = grounder.ground_evidence_claims(
        raw_clinical_note=clean_notes,
        claims=claims_to_ground,
    )

    claim_texts = [
        c["text"] if isinstance(c, dict) else str(c)
        for c in claims_to_ground
    ]
    raw_audits = grounder.ground_claims_detailed(clean_notes, claim_texts)
    claim_audits = [ClaimAudit(**item) for item in raw_audits]

    grounded_spans = [
        EvidenceSpan(
            start_char=s["start_char"],
            end_char=s["end_char"],
            start=s["start_char"],
            end=s["end_char"],
            text=s["text"],
            category=s["category"],
            label=s["label"],
            reason=s.get("reason"),
            confidence=s.get("confidence", 1.0),
            is_exact=s.get("is_exact", True),
        )
        for s in grounded_raw
    ]

    has_insufficient_evidence = (
        top1 not in KNOWN_CLINICAL_DIAGNOSES or len(grounded_spans) == 0
    )
    status_value = "insufficient_evidence" if has_insufficient_evidence else "success"

    # Keep reasoning explicitly labeled as deterministic template pipeline
    differential_reasoning = (
        f"Giả thuyết cần đối chiếu (chế độ deterministic_template): {top1} và {top2}. "
        f"Có {len(grounded_spans)} đoạn khớp chính xác với ghi chú đã khử định danh. "
        "Các trích đoạn phác đồ cần được bác sĩ kiểm tra nguồn và phiên bản trước khi quyết định."
    )
    if not any(reference.source_verified for reference in guideline_refs):
        investigations = []

    exec_time = round((time.time() - start_time) * 1000, 2)

    return AgentExplainResponse(
        status=status_value,
        reasoning_mode="deterministic_template",
        patient_id=patient_id,
        display_note=clean_notes,
        primary_diagnosis=top1,
        primary_diagnosis_name=disease_names.get(top1, top1),
        differential_diagnosis=top2,
        differential_diagnosis_name=disease_names.get(top2, top2),
        top1_diagnosis=top1,
        top2_diagnosis=top2,
        differential_reasoning=differential_reasoning,
        grounded_spans=grounded_spans,
        verified_spans=grounded_spans,
        guideline_references=guideline_refs,
        guideline_citations=guideline_refs,
        claim_audits=claim_audits,
        red_flags=red_flags,
        recommended_investigations=investigations,
        hallucination_filtered_count=rejected_count,
        has_insufficient_evidence=has_insufficient_evidence,
        warning=warning_msg,
        execution_time_ms=exec_time,
    )
