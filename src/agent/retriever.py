"""
Hybrid Clinical Knowledge Retriever
M-CDSS Phase 2 / Backlog 05 (Task 3.1)

Combines Dense Semantic Vector retrieval with Sparse Lexical BM25 keyword filtering
to retrieve authoritative Clinical Practice Guidelines (CPGs) from GINA 2024, GOLD 2024,
ESC 2023, and Vietnam Ministry of Health (BYT).
Supports both live Qdrant Vector DB connection and local In-Memory Fallback.
"""

import math
import os
import re
from collections import Counter
from typing import Any, Dict, List, Optional


# Authoritative Clinical Practice Guideline Chunks with deep clinical metadata
STANDARD_GUIDELINE_CORPUS: List[Dict[str, Any]] = [
    {
        "chunk_id": "GOLD_2024_DIAG_CRITERIA_01",
        "guideline_source": "GOLD_2024",
        "disease_entity": "COPD",
        "section_title": "Tiêu Chuẩn Chẩn Đoán & Yếu Tố Nguy Cơ COPD",
        "clinical_category": "DIAGNOSTIC_CRITERIA",
        "evidence_level": "Level_A",
        "text_content": (
            "Chẩn đoán COPD cần được xem xét ở bất kỳ bệnh nhân nào có các triệu chứng: "
            "Khó thở tiến triển theo thời gian, nặng hơn khi gắng sức, dai dẳng; "
            "Ho mạn tính kèm khạc đờm trắng đục; "
            "Tiền sử tiếp xúc yếu tố nguy cơ: Hút thuốc lá chủ động hoặc thụ động (> 10-20 bao-năm), khói bụi nghề nghiệp. "
            "Tiêu chuẩn vàng xác định: Đo chức năng thông khí phổi sau nghiệm pháp giãn phế quản có chỉ số FEV1/FVC < 0.70."
        ),
        "keywords": ["copd", "khó thở", "hút thuốc", "bao-năm", "fev1/fvc", "đờm", "mạn tính"],
    },
    {
        "chunk_id": "GOLD_GINA_DIFFERENTIAL_02",
        "guideline_source": "GOLD_2024_GINA_2024",
        "disease_entity": "COPD_VS_ASTHMA",
        "section_title": "Chẩn Đoán Phân Biệt Lâm Sàng Giữa COPD & Hen Phế Quản",
        "clinical_category": "DIFFERENTIAL_DIAGNOSIS",
        "evidence_level": "Level_A",
        "text_content": (
            "Phân biệt Hen phế quản và COPD: "
            "1. Tuổi khởi phát: Hen thường khởi phát sớm (<40 tuổi), COPD thường sau 40-50 tuổi. "
            "2. Bệnh sử hút thuốc: COPD hầu như luôn có tiền sử hút thuốc lá nặng (>10 bao-năm); Hen có thể xảy ra ở người không hút thuốc. "
            "3. Biến thiên triệu chứng: Hen thay đổi từng ngày, nặng về đêm hoặc gần sáng, hồi phục hoàn toàn giữa các cơn; COPD khó thở tiến triển liên tục, ít biến thiên ngày-đêm. "
            "4. Đáp ứng giãn phế quản: Hen có khả năng hồi phục luồng khí hoàn toàn hoặc rõ rệt (FEV1 tăng > 12% và > 200ml); COPD tắc nghẽn cố định không hồi phục hoàn toàn."
        ),
        "keywords": ["phân biệt", "hen", "copd", "hút thuốc", "biến thiên", "đêm", "hồi phục", "tuổi"],
    },
    {
        "chunk_id": "GINA_2024_ASTHMA_CRITERIA_01",
        "guideline_source": "GINA_2024",
        "disease_entity": "ASTHMA",
        "section_title": "Tiêu Chuẩn Chẩn Đoán & Đặc Trưng Hen Phế Quản",
        "clinical_category": "DIAGNOSTIC_CRITERIA",
        "evidence_level": "Level_A",
        "text_content": (
            "Hen là bệnh lý viêm mạn tính đường thở đặc trưng bởi: "
            "Các triệu chứng hô hấp thay đổi theo thời gian và cường độ: thở rít (wheezing), khó thở, nặng ngực, ho khan hoặc ho có đờm trong; "
            "Các triệu chứng thường khởi phát hoặc nặng lên khi tiếp xúc dị nguyên, nhiễm virus đường hô hấp, gắng sức hoặc thay đổi thời tiết; "
            "Tiền sử cá nhân hoặc gia đình mắc các bệnh dị ứng (viêm mũi dị ứng, chàm, viêm kết mạc dị ứng)."
        ),
        "keywords": ["hen", "asthma", "thở rít", "wheezing", "dị ứng", "gắng sức", "thời tiết", "ho"],
    },
    {
        "chunk_id": "ESC_2023_HEART_FAILURE_01",
        "guideline_source": "ESC_2023",
        "disease_entity": "HEART_FAILURE",
        "section_title": "Tiêu Chuẩn Lâm Sàng Chẩn Đoán Suy Tim Cấp & Mạn",
        "clinical_category": "DIAGNOSTIC_CRITERIA",
        "evidence_level": "Level_A",
        "text_content": (
            "Chẩn đoán Suy tim (Heart Failure) theo khuyến cáo ESC 2023: "
            "Triệu chứng điển hình: Khó thở khi nằm đầu thấp (orthopnea), khó thở kịch phát về đêm (PND), giảm khả năng gắng sức, mệt mỏi; "
            "Dấu hiệu ứ trệ dịch: Phù hai chi dưới đối xứng, tĩnh mạch cổ nổi, phản hồi gan - tĩnh mạch cổ (+), ran ẩm ở hai đáy phổi; "
            "Xét nghiệm cận lâm sàng: Tăng peptide lợi niệu NT-proBNP (> 125 pg/mL ở ca mạn, > 300 pg/mL ở đợt cấp) hoặc BNP (> 35 pg/mL)."
        ),
        "keywords": ["suy tim", "heart failure", "khó thở khi nằm", "orthopnea", "phù", "nt-probnp", "ran ẩm"],
    },
    {
        "chunk_id": "BYT_2020_COMMUNITY_PNEUMONIA_01",
        "guideline_source": "BYT_2020",
        "disease_entity": "PNEUMONIA",
        "section_title": "Hướng Dẫn Chẩn Đoán Viêm Phổi Mắc Phải Cộng Đồng (CAP)",
        "clinical_category": "DIAGNOSTIC_CRITERIA",
        "evidence_level": "Level_B",
        "text_content": (
            "Chẩn đoán Viêm phổi mắc phải cộng đồng (Bộ Y tế): "
            "Hội chứng nhiễm trùng cấp tính: Sốt cao (> 38°C), ớn lạnh, môi khô lưỡi bẩn; "
            "Triệu chứng hô hấp: Ho khạc đờm mủ đục hoặc đờm màu gỉ sắt, đau ngực kiểu màng phổi tăng lên khi hít sâu; "
            "Khám phổi: Hội chứng đông đặc (rì rào phế nang giảm, rung thanh tăng, gõ đục), ran ẩm, ran nổ khu trú; "
            "Chỉ số xét nghiệm: Bạch cầu máu tăng (> 10.0 G/L) hoặc tỷ lệ bạch cầu đa nhân trung tính tăng > 85%, chỉ số CRP tăng cao (> 20 mg/L)."
        ),
        "keywords": ["viêm phổi", "pneumonia", "sốt", "đờm mủ", "bạch cầu", "crp", "ran nổ", "đông đặc"],
    },
    {
        "chunk_id": "GLOBAL_RED_FLAG_EMERGENCY_01",
        "guideline_source": "GINA_GOLD_ESC_BYT",
        "disease_entity": "ALL_RESPIRATORY_CARDIAC",
        "section_title": "Dấu Hiệu Cờ Đỏ Cấp Cứu Suy Hô Hấp & Tim Mạch Đe Dọa Tính Mạng",
        "clinical_category": "RED_FLAG",
        "evidence_level": "Level_A",
        "text_content": (
            "Dấu hiệu cảnh báo nguy kịch cần can thiệp cấp cứu ngay lập tức: "
            "1. Suy hô hấp cấp nặng: SpO2 < 88% khi thở khí phòng, tần số thở > 30 lần/phút hoặc < 10 lần/phút, thở nghịch thường ngực - bụng, co kéo cơ hô hấp phụ; "
            "2. Rối loạn huyết động: Huyết áp tâm thu < 90 mmHg kèm vã mồ hôi, đầu chi lạnh ẩm, mạch nhanh nhỏ > 120 bpm; "
            "3. Rối loạn ý thức: Li bì, lơ mơ, kích động hoặc hôn mê do ứ CO2 hoặc thiếu oxy não cấp."
        ),
        "keywords": ["cờ đỏ", "red flag", "cấp cứu", "spo2 < 88", "suy hô hấp", "co kéo", "huyết áp thấp"],
    },
]


class HybridGuidelineRetriever:
    """
    Hybrid retriever that searches authoritative medical guidelines.
    Uses BM25 keyword matching and term frequency overlap over the guideline corpus.
    Can also connect to a live Qdrant client when host/port are provided.
    """

    def __init__(
        self,
        corpus: Optional[List[Dict[str, Any]]] = None,
        qdrant_client: Optional[Any] = None,
        collection_name: str = "clinical_guidelines",
        embedding_fn: Optional[Any] = None,
    ):
        self.corpus = corpus or STANDARD_GUIDELINE_CORPUS
        self.qdrant_client = qdrant_client
        self.collection_name = collection_name
        self.embedding_fn = embedding_fn
        if self.qdrant_client is None and os.getenv("QDRANT_URL"):
            from qdrant_client import QdrantClient

            self.qdrant_client = QdrantClient(url=os.environ["QDRANT_URL"], timeout=2)
        if self.embedding_fn is None and os.getenv("MCDSS_DENSE_MODEL"):
            from sentence_transformers import SentenceTransformer

            encoder = SentenceTransformer(os.environ["MCDSS_DENSE_MODEL"], local_files_only=True)
            self.embedding_fn = lambda text: encoder.encode(text).tolist()

    def _tokenize(self, text: str) -> List[str]:
        """Simple lower-case word tokenizer."""
        return re.findall(r"\w+", text.lower())

    def _bm25_rank(self, query: str, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank exact corpus text with BM25; scores are local ranking values."""
        documents = [
            self._tokenize(" ".join([c.get("text_content", ""), c.get("section_title", ""),
                                     " ".join(c.get("keywords", []))]))
            for c in chunks
        ]
        frequencies = [Counter(tokens) for tokens in documents]
        avg_length = sum(map(len, documents)) / max(len(documents), 1)
        terms = set(self._tokenize(query))
        scores = []
        for chunk, counts, tokens in zip(chunks, frequencies, documents):
            score = 0.0
            for term in terms:
                frequency = counts[term]
                if not frequency:
                    continue
                document_frequency = sum(term in item for item in frequencies)
                idf = math.log(1 + (len(chunks) - document_frequency + 0.5) / (document_frequency + 0.5))
                score += idf * frequency * 2.2 / (
                    frequency + 1.2 * (0.25 + 0.75 * len(tokens) / max(avg_length, 1))
                )
            item = dict(chunk)
            item["relevance_score"] = round(score, 6)
            scores.append(item)
        return sorted(scores, key=lambda item: item["relevance_score"], reverse=True)

    @staticmethod
    def _with_provenance(chunk: Dict[str, Any]) -> Dict[str, Any]:
        item = dict(chunk)
        item.setdefault("source_id", item.get("guideline_source", ""))
        item.setdefault("version", item.get("guideline_source", "").rsplit("_", 1)[-1])
        item.setdefault("section_locator", item.get("section_title", ""))
        item.setdefault("source_verified", False)
        return item

    def retrieve(
        self,
        query: str,
        disease_filter: Optional[str] = None,
        top_k: int = 4,
    ) -> List[Dict[str, Any]]:
        """
        Retrieves top_k most relevant guideline chunks for a clinical query.
        """
        if top_k < 1:
            raise ValueError("top_k must be positive")
        target = disease_filter.upper() if disease_filter else None
        candidates = [
            self._with_provenance(chunk) for chunk in self.corpus
            if not target or target in chunk.get("disease_entity", "").upper()
            or chunk.get("disease_entity") == "ALL_RESPIRATORY_CARDIAC"
        ]
        sparse = self._bm25_rank(query, candidates)
        dense = []
        if self.qdrant_client is not None and self.embedding_fn is not None:
            try:
                response = self.qdrant_client.query_points(
                    collection_name=self.collection_name,
                    query=self.embedding_fn(query),
                    limit=max(top_k * 4, 10),
                    with_payload=True,
                )
                for point in response.points:
                    payload = self._with_provenance(point.payload or {})
                    if not all(payload.get(key) for key in ("chunk_id", "source_id", "version", "section_locator", "text_content")):
                        continue
                    if target and target not in payload.get("disease_entity", "").upper() and payload.get("disease_entity") != "ALL_RESPIRATORY_CARDIAC":
                        continue
                    dense.append(payload)
            except Exception:
                # A failed vector store does not make the local research corpus authoritative.
                dense = []

        merged = {}
        for ranking in (sparse, dense):
            for rank, item in enumerate(ranking):
                key = item["chunk_id"]
                merged.setdefault(key, {**item, "fusion_score": 0.0})
                merged[key]["fusion_score"] += 1 / (60 + rank + 1)
                if item.get("source_verified"):
                    merged[key].update(item)
        results = sorted(merged.values(), key=lambda item: item["fusion_score"], reverse=True)
        return results[:top_k]
