

"""
Diagnostic Agent - Clinical Differential Reasoning & Hypothesis Engine
M-CDSS Backlog 05 - Multi-Agent Layer

LƯU Ý PHÂN CÔNG (TASK ASSIGNMENT NOTE):
- Module này thuộc trách nhiệm chính của THÀNH VIÊN 1 (Task 1.2 - MEMBER_1.md).
- Hiện tại file chứa cấu trúc khung (Scaffolding / Deterministic Fallback) do Thành viên 2 
  tạo để chạy tích hợp và kiểm thử API / Evidence Grounding.
- Các vị trí đánh dấu [TODO - MEMBER_1] và [TODO - MEMBER_3] dưới đây là những chỗ người sau
  cần bổ sung, kết nối LLM Prompting, hoặc thay thế bằng Hybrid Retriever.
"""

import os
import atexit
from typing import Dict, List, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from src.agent.knowledge_ingest import get_qdrant_client


class DiagnosticAgent:
    """
    Diagnostic Agent orchestrating differential diagnosis between Top 1 and Top 2 pathologies.
    """

    def __init__(
        self,
        qdrant_client: Optional[QdrantClient] = None,
        collection_name: str = "clinical_guidelines",
        storage_path: str = "data/vector_store/qdrant",
        # -----------------------------------------------------------------------------------------
        # [TODO - MEMBER_1] BỔ SUNG / GHI ĐÈ:
        # Nhận thêm llm_client (Gemini / OpenAI / Local VLLM) và model_name để phục vụ suy luận LLM:
        # e.g.: llm_client: Optional[Any] = None, llm_model: str = "gemini-1.5-flash"
        # -----------------------------------------------------------------------------------------
        # [TODO - MEMBER_3] TÍCH HỢP HYBRID RETRIEVER:
        # Nhận thêm hybrid_retriever từ `src/agent/retriever.py` thay vì chỉ dùng client Qdrant thô.
        # e.g.: retriever: Optional[HybridGuidelineRetriever] = None
        # -----------------------------------------------------------------------------------------
        llm_client: Optional[Any] = None,
        retriever: Optional[Any] = None,
    ):
        self.collection_name = collection_name
        self.llm_client = llm_client
        self.retriever = retriever

        if qdrant_client is not None:
            self.client = qdrant_client
        else:
            self.client = get_qdrant_client(storage_path)

        if hasattr(self.client, "close"):
            atexit.register(self.close)

    def close(self):
        """Explicitly close QdrantClient connection."""
        try:
            if hasattr(self, "client") and self.client is not None:
                self.client.close()
        except Exception:
            pass

    def select_hypotheses(
        self,
        calibrated_probs: Optional[Dict[str, float]],
        clinical_note: str,
    ) -> tuple[str, Optional[str]]:
        """
        Selects primary hypothesis H1 and secondary differential H2.
        Does NOT rely on untrusted client labels.
        """
        # Ưu tiên xác suất đã hiệu chuẩn từ mạng Multimodal (Inference Engine)
        if calibrated_probs and len(calibrated_probs) > 0:
            sorted_diseases = sorted(calibrated_probs.items(), key=lambda x: x[1], reverse=True)
            top1 = sorted_diseases[0][0]
            top2 = sorted_diseases[1][0] if len(sorted_diseases) > 1 and sorted_diseases[1][1] >= 0.05 else None
            return top1, top2

        # -----------------------------------------------------------------------------------------
        # [TODO - MEMBER_1] BỔ SUNG:
        # Nếu calibrated_probs bị thiếu, có thể cho LLM trích xuất bệnh nghi ngờ từ bệnh án
        # thay cho bộ đếm từ khóa fallback dưới đây.
        # -----------------------------------------------------------------------------------------
        note_lower = clinical_note.lower()
        scores = {
            "COPD": sum(w in note_lower for w in ["copd", "thuốc lá", "bao-năm", "fev1/fvc", "lồng ngực hình thùng"]),
            "ASTHMA": sum(w in note_lower for w in ["hen", "khò khè", "dị ứng", "pef", "cơn hen", "hồi phục phế quản"]),
            "CONGESTIVE_HEART_FAILURE": sum(w in note_lower for w in ["suy tim", "bnp", "nt-probnp", "tĩnh mạch cổ", "phù chân", "gallop"]),
            "COMMUNITY_ACQUIRED_PNEUMONIA": sum(w in note_lower for w in ["viêm phổi", "sốt", "đờm mủ", "đông đặc", "ran nổ", "curb-65"]),
        }
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top1 = sorted_scores[0][0] if sorted_scores[0][1] > 0 else "COPD"
        top2 = sorted_scores[1][0] if len(sorted_scores) > 1 and sorted_scores[1][1] > 0 else None
        return top1, top2

    def retrieve_guidelines(
        self,
        disease_h1: str,
        disease_h2: Optional[str] = None,
        limit: int = 4,
    ) -> List[Dict[str, Any]]:
        """
        Retrieves relevant guideline chunks from Qdrant vector store.
        """
        # -----------------------------------------------------------------------------------------
        # [TODO - MEMBER_3] GHI ĐÈ BẰNG HYBRID GUIDELINE RETRIEVER:
        # Nếu self.retriever (từ src/agent/retriever.py) có sẵn, dùng hybrid search (Dense + BM25)
        # thay cho việc scroll/filter đơn thuần:
        #
        # if self.retriever:
        #     query = f"Tiêu chuẩn chẩn đoán phân biệt giữa {disease_h1} và {disease_h2 or ''}"
        #     return self.retriever.retrieve(query=query, top_k=limit)
        # -----------------------------------------------------------------------------------------
        if self.retriever and hasattr(self.retriever, "retrieve"):
            query = f"Tiêu chuẩn chẩn đoán phân biệt giữa {disease_h1} và {disease_h2 or ''}"
            return self.retriever.retrieve(query=query, top_k=limit)

        guidelines = []
        try:
            must_conditions = [
                qmodels.FieldCondition(
                    key="target_disease",
                    match=qmodels.MatchAny(any=[disease_h1] + ([disease_h2] if disease_h2 else [])),
                )
            ]
            filter_query = qmodels.Filter(must=must_conditions)

            results, _ = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=filter_query,
                limit=limit,
                with_payload=True,
            )
            for r in results:
                guidelines.append(r.payload)
        except Exception:
            pass

        return guidelines

    def run_differential_analysis(
        self,
        clinical_note: str,
        calibrated_probs: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Runs clinical differential logic, extracting pro/counter evidence claims
        and red flags.
        """
        h1, h2 = self.select_hypotheses(calibrated_probs, clinical_note)
        guidelines = self.retrieve_guidelines(h1, h2, limit=4)

        # =========================================================================================
        # [TODO - MEMBER_1] CHỖ CẦN THAY THẾ CHÍNH: LLM STRUCTURED REASONER (TASK 1.2)
        # -----------------------------------------------------------------------------------------
        # Thay thế khối if/else bên dưới bằng lời gọi LLM Prompting có cấu trúc (JSON Mode).
        # Tham khảo mục 5 trong `docs/04_AGENTIC_RAG_AND_EXPLAINABILITY.md`:
        #
        # if self.llm_client:
        #     context_str = "\n\n".join([f"[{g.get('source_id')} - {g.get('section_title')}]: {g.get('text_content')}" for g in guidelines])
        #     prompt = f\"\"\"
        #     Bạn là Bác sĩ Chuyên khoa Hội chẩn cấp cao.
        #     BỆNH ÁN: \"\"\"{clinical_note}\"\"\"
        #     XÁC SUẤT: H1: {h1}, H2: {h2}
        #     PHÁC ĐỒ CHUẨN: {context_str}
        #     YÊU CẦU:
        #     1. Trích nguyên văn các câu trong bệnh án ủng hộ H1 (pro_evidence_claims).
        #     2. Trích nguyên văn các câu trong bệnh án ủng hộ H2 / phản bác H1 (counter_evidence_claims).
        #     3. Liệt kê dấu hiệu cờ đỏ nguy kịch (red_flags).
        #     Trả về định dạng JSON nghiêm ngặt...
        #     \"\"\"
        #     response_json = self.llm_client.generate_json(prompt)
        #     return {
        #         "top1_diagnosis": h1,
        #         "top2_diagnosis": h2,
        #         "differential_reasoning": response_json.get("differential_reasoning", ""),
        #         "pro_evidence_claims": response_json.get("pro_evidence_claims", []),
        #         "counter_evidence_claims": response_json.get("counter_evidence_claims", []),
        #         "red_flags": response_json.get("red_flags", []),
        #         "guideline_sources": guidelines,
        #     }
        #
        # LƯU Ý BẮT BUỘC ĐỐI VỚI MEMBER 1:
        # Giữ nguyên cấu trúc key trong dictionary trả về để tương thích 100% với
        # EvidenceGrounder và Endpoint POST /api/v1/agent/explain.
        # =========================================================================================

        # -----------------------------------------------------------------------------------------
        # DETERMINISTIC RULE-BASED FALLBACK:
        # Giữ lại đoạn bên dưới làm fallback khi không có LLM client hoặc offline / test CI/CD.
        # -----------------------------------------------------------------------------------------
        pro_claims: List[str] = []
        counter_claims: List[str] = []
        red_flags: List[str] = []

        note_lines = [line.strip() for line in clinical_note.split("\n") if line.strip()]

        for line in note_lines:
            lower = line.lower()
            if any(k in lower for k in ["spo2 <", "spo2: 8", "lồng ngực im lặng", "khạc bọt hồng", "choáng", "lú lẫn"]):
                red_flags.append(line)

            if h1 == "COPD" and any(k in lower for k in ["thuốc lá", "khó thở tiến triển", "fev1/fvc < 0.70", "fev1/fvc ="]):
                pro_claims.append(line)
            elif h1 == "ASTHMA" and any(k in lower for k in ["khò khè", "dao động", "dị ứng", "ban đêm", "sáng sớm"]):
                pro_claims.append(line)
            elif h1 == "CONGESTIVE_HEART_FAILURE" and any(k in lower for k in ["khó thở khi nằm", "kịch phát về đêm", "phù", "tĩnh mạch cổ"]):
                pro_claims.append(line)
            elif h1 == "COMMUNITY_ACQUIRED_PNEUMONIA" and any(k in lower for k in ["sốt", "đờm mủ", "đông đặc", "ran nổ"]):
                pro_claims.append(line)

            if h2:
                if any(k in lower for k in ["không có dấu hiệu", "loại trừ", "không sốt", "không phù"]):
                    counter_claims.append(line)

        reasoning = (
            f"Hội chẩn phân biệt ưu tiên chẩn đoán sơ bộ H1: {h1}"
            + (f" đối kháng với H2: {h2}." if h2 else ".")
            + f" Đối chiếu phác đồ đã trích xuất {len(guidelines)} phân mảnh y khoa liên quan."
        )

        return {
            "top1_diagnosis": h1,
            "top2_diagnosis": h2,
            "differential_reasoning": reasoning,
            "pro_evidence_claims": pro_claims,
            "counter_evidence_claims": counter_claims,
            "red_flags": red_flags,
            "guideline_sources": guidelines,
        }

