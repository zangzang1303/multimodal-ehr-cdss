# ==============================================================================
# [MOCK / STAND-IN FILE - DÙNG TẠM THỜI CHO THÀNH VIÊN 3 KẾT NỐI FRONTEND]
# Route POST /api/v1/agent/explain này được Thành viên 3 dựng trước để nối thông
# luồng giao diện Web (frontend/src/lib/api.ts, Backlog 05 - Nhiệm vụ 3.4) trong
# lúc chờ Thành viên 2 hoàn thiện route chính thức (Backlog 05 - Nhiệm vụ 2.3)
# và Thành viên 1 hoàn thiện DiagnosticAgent (Backlog 05 - Nhiệm vụ 1.2).
# ==============================================================================
"""
Agent Consultation & Clinical Explainability Router
M-CDSS Phase 2 / Backlog 05 (Task 3.4 & Task 2.3)

Provides Multi-Agent Differential Diagnosis Reasoning and Zero-Hallucination
Evidence Grounding with Authoritative CPG Retrieval via DiagnosticStateGraph.
"""

import time
from fastapi import APIRouter, HTTPException

from src.agent.diagnostic_graph import (
    DISEASE_DISPLAY_NAMES,
    DiagnosticGraphState,
    DiagnosticStateGraph,
)
from src.agent.evidence_grounder import EvidenceGrounder
from src.agent.retriever import HybridGuidelineRetriever
from src.api.schemas import (
    AgentExplainRequest,
    AgentExplainResponse,
    EvidenceSpan,
    GuidelineReference,
)
from src.data_pipeline.deidentifier import ClinicalDeidentifier

router = APIRouter(prefix="/agent")

grounder = EvidenceGrounder(fuzzy_threshold=0.88)
retriever = HybridGuidelineRetriever()
deidentifier = ClinicalDeidentifier(spacy_model=None, use_ner=False)
diagnostic_graph = DiagnosticStateGraph(
    retriever=retriever,
    grounder=grounder,
    deidentifier=deidentifier,
)


@router.options("/explain")
async def options_explain():
    """Direct OPTIONS handler for CORS preflight."""
    return {"status": "ok"}


@router.post("/explain", response_model=AgentExplainResponse)
async def explain_clinical_case(request: AgentExplainRequest) -> AgentExplainResponse:
    """
    Multi-Agent Differential Diagnosis & Evidence Grounding Endpoint.
    Executes the 4-node DiagnosticStateGraph (Triage -> Hybrid Qdrant+BM25 Retrieval
    -> Clinical Reasoning -> O(N) Evidence Grounding) on raw clinical notes.
    """
    start_time = time.time()
    patient_id = request.patient_id or "PT-001"
    raw_notes = request.clinical_notes or ""

    if len(raw_notes.strip()) < 5:
        raise HTTPException(
            status_code=400,
            detail="Bệnh án lâm sàng quá ngắn, vui lòng nhập ít nhất 5 ký tự để phân tích.",
        )

    initial_state = DiagnosticGraphState(
        patient_id=patient_id,
        raw_clinical_notes=raw_notes,
        requested_primary=request.target_diagnosis,
        requested_differential=request.differential_diagnosis,
    )
    final_state = diagnostic_graph.invoke(initial_state)

    guideline_refs = [
        GuidelineReference(
            chunk_id=c["chunk_id"],
            guideline_source=c["guideline_source"],
            disease_entity=c["disease_entity"],
            section_title=c["section_title"],
            clinical_category=c["clinical_category"],
            evidence_level=c.get("evidence_level", "Level_A"),
            text_content=c["text_content"],
            relevance_score=c.get("relevance_score", 1.0),
        )
        for c in final_state.retrieved_guidelines
    ]

    grounded_spans = [
        EvidenceSpan(
            start_char=s["start_char"],
            end_char=s["end_char"],
            text=s["text"],
            category=s["category"],
            label=s["label"],
            reason=s.get("reason"),
            confidence=s.get("confidence", 1.0),
            is_exact=s.get("is_exact", True),
        )
        for s in final_state.grounded_spans
    ]

    exec_time = round((time.time() - start_time) * 1000, 2)
    top1 = final_state.primary_diagnosis
    top2 = final_state.differential_diagnosis

    return AgentExplainResponse(
        patient_id=patient_id,
        primary_diagnosis=top1,
        primary_diagnosis_name=DISEASE_DISPLAY_NAMES.get(top1, top1),
        differential_diagnosis=top2,
        differential_diagnosis_name=DISEASE_DISPLAY_NAMES.get(top2, top2),
        differential_reasoning=final_state.differential_reasoning,
        grounded_spans=grounded_spans,
        guideline_references=guideline_refs,
        red_flags=final_state.red_flags,
        recommended_investigations=final_state.recommended_investigations,
        hallucination_filtered_count=final_state.hallucination_filtered_count,
        execution_time_ms=exec_time,
    )
