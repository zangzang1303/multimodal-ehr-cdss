

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status

from src.api.schemas import (
    AgentExplainRequest,
    AgentExplainResponse,
    EvidenceSpan,
    ClaimAudit,
    GuidelineCitation,
)
from src.agent.evidence_grounder import EvidenceGrounder
from src.agent.diagnostic_agent import DiagnosticAgent

logger = logging.getLogger("AgentExplainRoute")

router = APIRouter(prefix="/agent", tags=["Agentic RAG & Explainability"])


_grounder: Optional[EvidenceGrounder] = None
_diagnostic_agent: Optional[DiagnosticAgent] = None


def get_grounder() -> EvidenceGrounder:
    global _grounder
    if _grounder is None:
        _grounder = EvidenceGrounder()
    return _grounder


def get_diagnostic_agent() -> DiagnosticAgent:
    """
    Singleton provider for DiagnosticAgent.
    [TODO - MEMBER_1 / MEMBER_3]:
    - Member 1: Khởi tạo và truyền LLM Client (Gemini/OpenAI/Local LLM) vào đây.
    - Member 3: Truyền instance HybridGuidelineRetriever (src/agent/retriever.py) vào đây.
      Ví dụ:
      return DiagnosticAgent(
          llm_client=GeminiClient(api_key=os.getenv("GEMINI_API_KEY")),
          retriever=HybridGuidelineRetriever()
      )
    """
    global _diagnostic_agent
    if _diagnostic_agent is None:
        _diagnostic_agent = DiagnosticAgent()
    return _diagnostic_agent


@router.post(
    "/explain",
    response_model=AgentExplainResponse,
    status_code=status.HTTP_200_OK,
    summary="Clinical Differential Explainability with Grounded Evidence",
    description="Analyzes de-identified clinical notes, performs differential reasoning between Top-1 and Top-2 pathologies, grounds citations with exact character offsets, and cross-references official clinical guidelines.",
)
def explain_clinical_case(request: AgentExplainRequest) -> AgentExplainResponse:
    """
    POST /api/v1/agent/explain
    
    [GHI CHÚ DÀNH CHO MEMBER 3 (FRONTEND / FULL-STACK)]:
    - Endpoint này được gọi từ `frontend/src/lib/api.ts` (Nhiệm vụ 3.4).
    - Dữ liệu trả về gồm:
      1. `verified_spans`: Danh sách tọa độ [start, end] để đưa vào `EvidenceViewer.tsx` (Nhiệm vụ 3.2).
      2. `guideline_citations`: Danh sách phác đồ để trượt mở trong `GuidelineDrawer.tsx`.
      3. `claim_audits`: Trạng thái xác thực từng câu claim (loại bỏ ảo giác).
    """
    clinical_note = request.clinical_note.strip()
    if not clinical_note:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Clinical note cannot be empty.",
        )

   
    warning_notes = []
    if request.target_diagnosis:
        warning_notes.append(
            f"Notice: Client-supplied target_diagnosis '{request.target_diagnosis}' was disregarded as ground truth and subjected to objective differential audit."
        )

    agent = get_diagnostic_agent()
    grounder = get_grounder()

    try:
        
        analysis = agent.run_differential_analysis(
            clinical_note=clinical_note,
            calibrated_probs=request.calibrated_probabilities,
        )
    except Exception as e:
        logger.error(f"DiagnosticAgent error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Diagnostic agent reasoning failed: {str(e)}",
        )

    top1 = analysis.get("top1_diagnosis", "COPD")
    top2 = analysis.get("top2_diagnosis")
    reasoning = analysis.get("differential_reasoning", "")
    pro_claims = analysis.get("pro_evidence_claims", [])
    counter_claims = analysis.get("counter_evidence_claims", [])
    red_flags = analysis.get("red_flags", [])
    raw_guidelines = analysis.get("guideline_sources", [])

   
    all_claims = pro_claims + counter_claims + red_flags
    claim_audits_raw = grounder.ground_claims_detailed(clinical_note, all_claims)

    verified_spans: List[EvidenceSpan] = []
    claim_audits: List[ClaimAudit] = []

    for item in claim_audits_raw:
        item_spans = [
            EvidenceSpan(
                text=s["text"],
                start=s["start"],
                end=s["end"],
                confidence=s.get("confidence", 1.0),
                match_type=s.get("match_type", "exact"),
            )
            for s in item.get("spans", [])
        ]
        # Invariant check: verify that note[start:end] == span.text
        for sp in item_spans:
            if clinical_note[sp.start : sp.end] != sp.text:
                logger.warning(f"Span invariant failed for text '{sp.text}', adjusting.")
                continue
            verified_spans.append(sp)

        claim_audits.append(
            ClaimAudit(
                claim=item["claim"],
                status=item["status"],
                spans=item_spans,
                confidence=item["confidence"],
                match_type=item["match_type"],
                clinical_interpretation_note=item.get("clinical_interpretation_note"),
                reason=item.get("reason"),
            )
        )

   
    resolved_raw = grounder.resolve_overlapping_spans([s.model_dump() for s in verified_spans])
    final_spans = [EvidenceSpan(**s) for s in resolved_raw]

    # Step 3: Format Guideline Citations
    guideline_citations: List[GuidelineCitation] = []
    for g in raw_guidelines:
        guideline_citations.append(
            GuidelineCitation(
                chunk_id=g.get("chunk_id", "UNKNOWN"),
                source_id=g.get("source_id", "UNKNOWN"),
                version=g.get("version", "2024"),
                target_disease=g.get("target_disease", top1),
                section_title=g.get("section_title", "Clinical Recommendation"),
                page_or_section=g.get("page_or_section", "Official Text"),
                clinical_category=g.get("clinical_category", "DIAGNOSTIC_CRITERIA"),
                evidence_level=g.get("evidence_level"),
                text_content=g.get("text_content", ""),
            )
        )

    # Step 4: Evaluate sufficiency of evidence
    has_insufficient_evidence = len(guideline_citations) == 0 or (len(all_claims) > 0 and len(final_spans) == 0)
    response_status = "insufficient_evidence" if has_insufficient_evidence else "success"

    if has_insufficient_evidence:
        warning_notes.append(
            "Warning: Insufficient verifiable evidence. Missing matching clinical guidelines or all claims failed string-level grounding."
        )

    patient_identifier = request.patient_id or "ANON_PATIENT"

    return AgentExplainResponse(
        status=response_status,
        patient_id=patient_identifier,
        top1_diagnosis=top1,
        top2_diagnosis=top2,
        differential_reasoning=reasoning,
        pro_evidence_claims=pro_claims,
        counter_evidence_claims=counter_claims,
        red_flags=red_flags,
        verified_spans=final_spans,
        claim_audits=claim_audits,
        guideline_citations=guideline_citations,
        has_insufficient_evidence=has_insufficient_evidence,
        warning=" | ".join(warning_notes) if warning_notes else None,
    )
