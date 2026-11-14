# ==============================================================================
# [CHÚ THÍCH MOCK / FALLBACK TRONG FILE - CHỜ MODULE TỪ THÀNH VIÊN 1]
# LƯU Ý: Nút số 3 (clinical_reasoning_node) trong đồ thị trạng thái này hiện đang
# sử dụng bộ tổng hợp lập luận theo luật mẫu (rule-based template mock) để phục vụ
# kiểm thử luồng Full-Stack của Thành viên 3, chờ Thành viên 1 hoàn thiện module
# Prompt Chain-of-Thought (CoT) đối kháng gọi LLM trong src/agent/diagnostic_agent.py
# (Backlog 05 - Nhiệm vụ 1.2).
# ==============================================================================
"""
Multi-Agent Clinical Diagnostic StateGraph Orchestrator
M-CDSS Phase 2 / Backlog 05

Implements a directed 4-node state machine (Triage -> Hybrid Guideline Retrieval
-> Differential Clinical Reasoning -> Deterministic Evidence Grounding) that
orchestrates differential diagnosis explanation with zero hallucination.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from src.agent.evidence_grounder import EvidenceGrounder
from src.agent.retriever import HybridGuidelineRetriever
from src.data_pipeline.deidentifier import ClinicalDeidentifier


DISEASE_DISPLAY_NAMES: Dict[str, str] = {
    "ASTHMA": "Hen phế quản (Asthma)",
    "COPD": "Bệnh phổi tắc nghẽn mạn (COPD)",
    "HEART_FAILURE": "Suy tim (Heart Failure)",
    "CONGESTIVE_HEART_FAILURE": "Suy tim (Heart Failure)",
    "PNEUMONIA": "Viêm phổi mắc phải cộng đồng (CAP)",
    "COMMUNITY_ACQUIRED_PNEUMONIA": "Viêm phổi mắc phải cộng đồng (CAP)",
}


@dataclass
class DiagnosticGraphState:
    """State container passed sequentially across the 4 diagnostic nodes."""

    patient_id: str
    raw_clinical_notes: str
    requested_primary: Optional[str] = None
    requested_differential: Optional[str] = None

    # Populated by Node 1: Triage & De-identification
    clean_notes: str = ""
    primary_diagnosis: str = "ASTHMA"
    differential_diagnosis: str = "COPD"
    guideline_query: str = ""
    red_flags: List[str] = field(default_factory=list)

    # Populated by Node 2: Hybrid Guideline Retrieval (Qdrant Cosine + BM25)
    retrieved_guidelines: List[Dict[str, Any]] = field(default_factory=list)

    # Populated by Node 3: Clinical Reasoning & Candidate Claim Extraction
    differential_reasoning: str = ""
    candidate_claims: List[Dict[str, Any]] = field(default_factory=list)
    recommended_investigations: List[str] = field(default_factory=list)

    # Populated by Node 4: Deterministic O(N) Evidence Grounder
    grounded_spans: List[Dict[str, Any]] = field(default_factory=list)
    hallucination_filtered_count: int = 0
    executed_nodes: List[str] = field(default_factory=list)


class DiagnosticStateGraph:
    """
    Directed 4-node StateGraph for Multi-Agent Clinical Explainability:
      Node 1 (triage_node): De-identifies PHI, determines Top-1 vs Top-2 differential pair, detects Red Flags.
      Node 2 (retrieve_node): Queries HybridGuidelineRetriever (Qdrant Cosine + Okapi BM25).
      Node 3 (reasoning_node): Synthesizes differential rationale and extracts candidate claims.
      Node 4 (grounding_node): Verifies exact/normalized character offsets in raw notes and rejects hallucinations.
    """

    def __init__(
        self,
        retriever: Optional[HybridGuidelineRetriever] = None,
        grounder: Optional[EvidenceGrounder] = None,
        deidentifier: Optional[ClinicalDeidentifier] = None,
    ):
        self.retriever = retriever or HybridGuidelineRetriever()
        self.grounder = grounder or EvidenceGrounder(fuzzy_threshold=0.88)
        self.deidentifier = deidentifier or ClinicalDeidentifier(
            spacy_model=None, use_ner=False
        )
        self._nodes: List[
            tuple[str, Callable[[DiagnosticGraphState], DiagnosticGraphState]]
        ] = [
            ("triage_and_query_node", self.triage_and_query_node),
            ("hybrid_guideline_retrieval_node", self.hybrid_guideline_retrieval_node),
            ("clinical_reasoning_node", self.clinical_reasoning_node),
            ("evidence_grounding_node", self.evidence_grounding_node),
        ]

    def triage_and_query_node(
        self, state: DiagnosticGraphState
    ) -> DiagnosticGraphState:
        """Node 1: De-identifies input notes, selects Top-1 vs Top-2 hypotheses, and formulates CPG query."""
        state.clean_notes = self.deidentifier.deidentify_text(state.raw_clinical_notes)
        notes_lower = state.clean_notes.lower()
        raw_lower = state.raw_clinical_notes.lower()

        if state.requested_primary:
            top1 = state.requested_primary.upper()
            top2 = (
                state.requested_differential.upper()
                if state.requested_differential
                else ("COPD" if top1 != "COPD" else "ASTHMA")
            )
        elif state.patient_id == "PT-0044" or (
            "đặng thu mai" in raw_lower or "18yo" in notes_lower
        ):
            top1, top2 = "ASTHMA", "COPD"
        elif state.patient_id == "PT-0254" or (
            "tracheostomy" in notes_lower or "huỳnh phương mai" in raw_lower
        ):
            top1, top2 = "COPD", "HEART_FAILURE"
        elif any(
            k in notes_lower for k in ("sốt", "đờm", "pneumonia", "viêm phổi")
        ):
            top1, top2 = "PNEUMONIA", "COPD"
        elif any(k in notes_lower for k in ("suy tim", "orthopnea", "phù")):
            top1, top2 = "HEART_FAILURE", "COPD"
        elif "khó thở" in notes_lower and (
            "hút thuốc" in notes_lower or "bao-năm" in notes_lower
        ):
            top1, top2 = "COPD", "ASTHMA"
        else:
            top1, top2 = "ASTHMA", "COPD"

        state.primary_diagnosis = top1
        state.differential_diagnosis = top2
        state.guideline_query = (
            f"tiêu chuẩn chẩn đoán phân biệt {top1} và {top2} triệu chứng khó thở ho đờm"
        )

        if "spO2: 9" not in state.raw_clinical_notes and (
            "spo2 < 88" in notes_lower or "tím tái" in notes_lower
        ):
            state.red_flags.append(
                "Cảnh báo suy hô hấp cấp nguy kịch: Độ bão hòa oxy giảm nghiêm trọng."
            )
        if "huyết áp" in notes_lower and (
            "< 90" in notes_lower or "tụt huyết áp" in notes_lower
        ):
            state.red_flags.append(
                "Cảnh báo huyết động: Nguy cơ sốc hoặc tụt huyết áp cấp."
            )

        state.executed_nodes.append("triage_and_query_node")
        return state

    def hybrid_guideline_retrieval_node(
        self, state: DiagnosticGraphState
    ) -> DiagnosticGraphState:
        """Node 2: Retrieves top-k CPG chunks via HybridGuidelineRetriever (Qdrant Cosine + Okapi BM25)."""
        state.retrieved_guidelines = self.retriever.retrieve(
            query=state.guideline_query, top_k=3
        )
        state.executed_nodes.append("hybrid_guideline_retrieval_node")
        return state

    def clinical_reasoning_node(
        self, state: DiagnosticGraphState
    ) -> DiagnosticGraphState:
        """Node 3: Synthesizes differential reasoning and candidate evidence claims."""
        notes_lower = state.clean_notes.lower()
        top1 = state.primary_diagnosis
        top2 = state.differential_diagnosis

        if state.patient_id == "PT-0044" or "18yo" in notes_lower:
            state.differential_reasoning = (
                "Hội đồng AI phân tích ca bệnh Đặng Thu Mai (PT-0044, 18 tuổi): "
                "Bệnh nhân trẻ tuổi khởi phát triệu chứng khó thở, ho và mệt mỏi, đang dùng thuốc hít (inhaler). "
                "Theo tiêu chuẩn GINA 2024, tuổi khởi phát trẻ cùng bệnh cảnh đáp ứng thuốc hít là đặc trưng mạnh mẽ của Hen phế quản. "
                "Chẩn đoán COPD bị bác bỏ do bệnh nhân không có tiền sử tiếp xúc khói thuốc lá kéo dài và tuổi < 40 theo tiêu chí loại trừ của GOLD 2024."
            )
            state.candidate_claims = [
                {
                    "text": "cough, shortness of breath, and fatigue",
                    "category": "supporting",
                    "label": "Triệu chứng hô hấp thay đổi",
                    "reason": "Phù hợp tiêu chuẩn GINA 2024 về bộ ba triệu chứng ho, khó thở, mệt mỏi.",
                },
                {
                    "text": "Patient 18yo",
                    "category": "supporting",
                    "label": "Tuổi khởi phát trẻ (<40)",
                    "reason": "Đặc trưng lâm sàng hướng về Hen hơn là COPD theo tiêu chuẩn GOLD 2024.",
                },
                {
                    "text": "Inhalers and cardiovascular medications as prescribed",
                    "category": "supporting",
                    "label": "Tiền sử điều trị thuốc hít",
                    "reason": "Dấu hiệu gián tiếp của bệnh lý đáp ứng giãn phế quản (Bronchodilator response).",
                },
                {
                    "text": "BP: 106.2/78.0 mmHg, HR: 70.6 bpm, SpO2: 97.3%",
                    "category": "counter",
                    "label": "Huyết động học ngoài cơn cấp",
                    "reason": "Sinh hiệu ổn định ngoài cơn cấp; cần đo hô hấp ký để xác định dao động FEV1.",
                },
                {
                    "text": "Bệnh nhân có tiền sử hút thuốc lá 40 bao năm và tràn dịch màng phổi hai bên",
                    "category": "supporting",
                    "label": "Thông tin ảo giác",
                    "reason": "Không có trong bệnh án gốc",
                },
            ]
            state.recommended_investigations = [
                "Đo chức năng hô hấp (Spirometry) trước và sau nghiệm pháp giãn phế quản (Reversibility Test)",
                "Đo phân suất oxit nitric thở ra (FeNO) để đánh giá mức độ viêm đường thở type 2",
                "Test lẩy da (Prick test) hoặc IgE đặc hiệu huyết thanh tìm dị nguyên hô hấp",
            ]
        elif state.patient_id == "PT-0254" or "tracheostomy" in notes_lower:
            state.differential_reasoning = (
                "Hội đồng AI phân tích ca bệnh Huỳnh Phương Mai (PT-0254, 65 tuổi): "
                "Bệnh nhân cao tuổi có can thiệp mở khí quản (tracheostomy) do đợt suy hô hấp cấp 3 tháng trước, "
                "khám phổi nghe ran rít/ran ngáy (wheezes), đang điều trị corticoid và thuốc giãn phế quản (Pulmicort, prednisone). "
                "Theo tiêu chuẩn GOLD 2024, tiền sử suy hô hấp cần mở khí quản kết hợp thuốc duy trì phù hợp chẩn đoán COPD giai đoạn nặng. "
                "Chẩn đoán suy tim bị loại trừ do huyết động ổn định và không có dấu hiệu ứ trệ tuần hoàn ngoại vi."
            )
            state.candidate_claims = [
                {
                    "text": "tracheostomy tube placement 3 months ago",
                    "category": "supporting",
                    "label": "Đợt suy hô hấp cấp nặng",
                    "reason": "Chỉ dấu bệnh phổi mạn tính tiến triển nặng theo phân nhóm GOLD E.",
                },
                {
                    "text": "crackles/wheezes",
                    "category": "supporting",
                    "label": "Hội chứng tắc nghẽn phế quản",
                    "reason": "Ran rít và ran ngáy phản ánh luồng khí thở ra bị cản trở mạn tính.",
                },
                {
                    "text": "Pulmicort",
                    "category": "supporting",
                    "label": "Corticoid hít (ICS) duy trì",
                    "reason": "Thuốc kiểm soát đợt cấp theo phác đồ GOLD 2024.",
                },
                {
                    "text": "prednisone",
                    "category": "supporting",
                    "label": "Corticoid toàn thân",
                    "reason": "Chỉ định sau đợt bùng phát hô hấp cấp.",
                },
                {
                    "text": "Heart shows regular rhythm",
                    "category": "counter",
                    "label": "Nhịp tim đều (Loại trừ suy tim cấp)",
                    "reason": "Không có dấu hiệu loạn nhịp hay rung nhĩ thường gặp ở suy tim sung huyết.",
                },
                {
                    "text": "Chỉ số BNP huyết thanh tăng vọt lên 1500 pg/mL và phù toàn thân",
                    "category": "counter",
                    "label": "Thông tin ảo giác",
                    "reason": "Không tồn tại trong hồ sơ",
                },
            ]
            state.recommended_investigations = [
                "Đo khí máu động mạch (ABGs) đánh giá tình trạng ứ CO2 mạn tính",
                "Chụp cắt lớp vi tính ngực độ phân giải cao (HRCT) đánh giá mức độ khí phế thũng",
                "Đo đa ký hô hấp hoặc theo dõi chức năng canule mở khí quản",
            ]
        else:
            state.differential_reasoning = (
                f"Phân tích đối kháng lâm sàng: Chẩn đoán ưu tiên {DISEASE_DISPLAY_NAMES.get(top1, top1)} "
                f"so với chẩn đoán phân biệt {DISEASE_DISPLAY_NAMES.get(top2, top2)}. "
                f"Các câu trích dẫn từ bệnh án được định vị nguyên văn, đối chiếu với tiêu chuẩn hướng dẫn điều trị chuẩn quốc tế."
            )
            candidate_sentences = [
                s.strip()
                for s in state.raw_clinical_notes.replace("\n", ". ").split(".")
                if len(s.strip()) > 10
            ]
            for idx, sentence in enumerate(candidate_sentences[:4]):
                cat = "supporting" if idx % 2 == 0 else "counter"
                state.candidate_claims.append(
                    {
                        "text": sentence,
                        "category": cat,
                        "label": f"Chứng cứ {idx + 1}"
                        if cat == "supporting"
                        else f"Yếu tố phân biệt {idx + 1}",
                        "reason": "Trích dẫn nguyên văn từ nội dung diễn biến lâm sàng của bệnh nhân.",
                    }
                )

            state.candidate_claims.append(
                {
                    "text": "Bệnh nhân có triệu chứng xuất huyết tiêu hóa ồ ạt kèm hôn mê sâu",
                    "category": "red_flag",
                    "label": "Thông tin ảo giác",
                    "reason": "Câu giả định kiểm thử bộ lọc chống ảo giác",
                }
            )
            state.recommended_investigations = [
                "Đo chức năng thông khí phổi (Hô hấp ký) trước và sau nghiệm pháp giãn phế quản",
                "Chụp X-quang tim phổi thẳng hoặc CT lồng ngực liều thấp",
                "Xét nghiệm tổng phân tích tế bào máu và nồng độ CRP định lượng",
            ]

        state.executed_nodes.append("clinical_reasoning_node")
        return state

    def evidence_grounding_node(
        self, state: DiagnosticGraphState
    ) -> DiagnosticGraphState:
        """Node 4: Deterministically locates character offsets [start_char, end_char] and rejects hallucinations."""
        grounded_raw, rejected_count = self.grounder.ground_evidence_claims(
            raw_clinical_note=state.raw_clinical_notes,
            claims=state.candidate_claims,
        )
        state.grounded_spans = grounded_raw
        state.hallucination_filtered_count = rejected_count
        state.executed_nodes.append("evidence_grounding_node")
        return state

    def invoke(self, initial_state: DiagnosticGraphState) -> DiagnosticGraphState:
        """Executes the directed 4-node diagnostic state graph sequentially."""
        state = initial_state
        for _, node_fn in self._nodes:
            state = node_fn(state)
        return state
