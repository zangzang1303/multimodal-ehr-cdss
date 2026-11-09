# ==============================================================================
# [CHÚ THÍCH MOCK / FALLBACK TRONG FILE - CHỜ DỮ LIỆU TỪ THÀNH VIÊN 1 & 2]
# LƯU Ý:
# 1. Bộ dữ liệu STANDARD_GUIDELINE_CORPUS (6 chunks mẫu) trong file này chỉ là
#    dữ liệu mồi (seed/mock) tạm thời để Thành viên 3 kiểm thử Qdrant + BM25,
#    chờ Thành viên 2 hoàn thiện src/agent/knowledge_ingest.py nạp >= 100 chunks
#    phác đồ chuẩn vào Qdrant (Backlog 05 - Nhiệm vụ 2.1 & Backlog 07 - Nhiệm vụ 2.1).
# 2. Hàm _encode_text() (vector đặc trưng 64 chiều từ cụm khái niệm + băm n-gram)
#    là bộ mã hóa fallback tạm thời trên CPU, chờ Thành viên 1 hoàn thiện cấu hình
#    configs/rag_config.yaml với sentence-transformers/all-mpnet-base-v2 (768 chiều)
#    (Backlog 05 - Nhiệm vụ 1.1).
# ==============================================================================
"""
Hybrid Clinical Knowledge Retriever
M-CDSS Phase 2 / Backlog 05 (Task 3.1)

Combines Dense Semantic Vector retrieval (via Qdrant Vector DB with Cosine Similarity)
and Sparse Lexical Okapi BM25 scoring to retrieve authoritative Clinical Practice
Guidelines (CPGs) from GINA 2024, GOLD 2024, ESC 2023, and Vietnam Ministry of Health (BYT).
"""

from __future__ import annotations

import hashlib
import math
import os
import re
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, PointStruct, VectorParams

    HAS_QDRANT = True
except ImportError:
    HAS_QDRANT = False


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

# Bilingual clinical concept clusters used for semantic dense vector construction
CLINICAL_CONCEPT_CLUSTERS: List[List[str]] = [
    ["asthma", "hen", "wheezing", "thở rít", "khò khè", "inhaler", "albuterol", "dị ứng", "gina", "hồi phục"],
    ["copd", "tắc nghẽn", "hút thuốc", "smoking", "bao-năm", "fev1", "fvc", "mạn tính", "gold", "khí phế thũng"],
    ["heart", "failure", "suy tim", "orthopnea", "pnd", "phù", "edema", "bnp", "nt-probnp", "tĩnh mạch cổ", "esc"],
    ["pneumonia", "viêm phổi", "sốt", "fever", "đờm mủ", "bạch cầu", "wbc", "crp", "đông đặc", "ran nổ", "cap"],
    ["khó thở", "dyspnea", "shortness", "breath", "ho", "cough", "đờm", "sputum", "ran ẩm", "crackles"],
    ["cờ đỏ", "red flag", "cấp cứu", "emergency", "spo2", "huyết áp", "hypotension", "hôn mê", "suy hô hấp"],
    ["phân biệt", "differential", "tuổi", "age", "biến thiên", "đêm", "gắng sức", "tiêu chuẩn", "chẩn đoán"],
]


class HybridGuidelineRetriever:
    """
    Hybrid retriever that combines:
      1. Dense Semantic Vector Cosine Similarity (via Qdrant Vector DB or in-memory vector index)
      2. Sparse Lexical Okapi BM25 scoring (k1=1.5, b=0.75) with medical keyword boosting.

    Final hybrid score:
        S_hybrid(q, d) = alpha * S_bm25_norm(q, d) + (1 - alpha) * S_cosine(q, d)
    """

    def __init__(
        self,
        corpus: Optional[List[Dict[str, Any]]] = None,
        qdrant_client: Optional[Any] = None,
        collection_name: str = "clinical_guidelines",
        alpha: float = 0.65,
        k1: float = 1.5,
        b: float = 0.75,
        vector_dim: int = 64,
        embedding_fn: Optional[Callable[[str], np.ndarray]] = None,
    ):
        self.corpus = corpus or STANDARD_GUIDELINE_CORPUS
        self.collection_name = collection_name
        self.alpha = float(np.clip(alpha, 0.0, 1.0))
        self.k1 = k1
        self.b = b
        self.vector_dim = vector_dim
        self.embedding_fn = embedding_fn

        # Build BM25 inverted index & corpus statistics
        self._doc_tokens: List[List[str]] = []
        self._doc_freqs: Dict[str, int] = {}
        self._avgdl: float = 1.0
        self._build_bm25_index()

        # Precompute dense embeddings for corpus
        self._corpus_embeddings: np.ndarray = np.vstack(
            [self._encode_text(self._chunk_full_text(c)) for c in self.corpus]
        )

        # Initialize Qdrant client (external URL if configured & reachable, else in-memory Qdrant)
        self.qdrant_client = qdrant_client
        self._qdrant_ready = False
        self._init_qdrant_index()

    def _chunk_full_text(self, chunk: Dict[str, Any]) -> str:
        return (
            f"{chunk.get('section_title', '')} "
            f"{chunk.get('disease_entity', '')} "
            f"{chunk.get('text_content', '')} "
            f"{' '.join(chunk.get('keywords', []))}"
        )

    def _tokenize(self, text: str) -> List[str]:
        """Lower-case word and medical symbol tokenizer."""
        return [t for t in re.findall(r"\w+", text.lower()) if len(t) >= 2]

    def _build_bm25_index(self) -> None:
        """Precomputes document token lists, document frequencies, and average document length."""
        self._doc_tokens = []
        self._doc_freqs = {}
        total_len = 0

        for chunk in self.corpus:
            tokens = self._tokenize(self._chunk_full_text(chunk))
            self._doc_tokens.append(tokens)
            total_len += len(tokens)
            for unique_tok in set(tokens):
                self._doc_freqs[unique_tok] = self._doc_freqs.get(unique_tok, 0) + 1

        n_docs = max(len(self.corpus), 1)
        self._avgdl = max(total_len / n_docs, 1.0)

    def _encode_text(self, text: str) -> np.ndarray:
        """
        Computes an L2-normalized dense semantic embedding vector for clinical text.
        Uses custom embedding_fn if provided; otherwise combines bilingual clinical
        concept activation dimensions with hashed character/word n-gram projections.
        """
        if self.embedding_fn is not None:
            vec = np.asarray(self.embedding_fn(text), dtype=np.float32).reshape(-1)
            norm = float(np.linalg.norm(vec))
            return vec / norm if norm > 1e-8 else vec

        vec = np.zeros(self.vector_dim, dtype=np.float32)
        text_lower = text.lower()
        tokens = self._tokenize(text_lower)

        # 1. Clinical concept cluster activations (first len(CLINICAL_CONCEPT_CLUSTERS) dims)
        for cluster_idx, cluster_terms in enumerate(CLINICAL_CONCEPT_CLUSTERS):
            if cluster_idx >= self.vector_dim:
                break
            hits = sum(1.0 for term in cluster_terms if term in text_lower)
            if hits > 0:
                vec[cluster_idx] = math.log1p(hits) * 2.0

        # 2. Hashed word & bigram semantic projection across remaining dimensions
        offset = len(CLINICAL_CONCEPT_CLUSTERS)
        rem_dim = max(self.vector_dim - offset, 1)
        ngrams = list(tokens) + [
            f"{tokens[i]}_{tokens[i + 1]}" for i in range(len(tokens) - 1)
        ]
        for ng in ngrams:
            digest = hashlib.md5(ng.encode("utf-8")).digest()
            idx = offset + (int.from_bytes(digest[:4], "little") % rem_dim)
            sign = 1.0 if (digest[4] & 1) == 0 else -1.0
            vec[idx] += sign * 0.5

        norm = float(np.linalg.norm(vec))
        if norm > 1e-8:
            vec = vec / norm
        else:
            vec[0] = 1.0
        return vec

    def _init_qdrant_index(self) -> None:
        """Initializes Qdrant collection and indexes the guideline corpus vectors."""
        if not HAS_QDRANT:
            return

        try:
            if self.qdrant_client is None:
                qdrant_url = os.getenv("QDRANT_URL")
                if qdrant_url:
                    try:
                        client = QdrantClient(url=qdrant_url, timeout=1.5)
                        client.get_collections()
                        self.qdrant_client = client
                    except Exception:
                        self.qdrant_client = QdrantClient(":memory:")
                else:
                    self.qdrant_client = QdrantClient(":memory:")

            collections = [
                c.name for c in self.qdrant_client.get_collections().collections
            ]
            if self.collection_name not in collections:
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_dim,
                        distance=Distance.COSINE,
                    ),
                )

            points = [
                PointStruct(
                    id=idx,
                    vector=self._corpus_embeddings[idx].tolist(),
                    payload=dict(chunk),
                )
                for idx, chunk in enumerate(self.corpus)
            ]
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=points,
            )
            self._qdrant_ready = True
        except Exception:
            self._qdrant_ready = False

    def _compute_bm25_score(
        self, query_tokens: List[str], doc_idx: int, chunk: Dict[str, Any]
    ) -> float:
        """
        Computes Okapi BM25 lexical relevance score for document doc_idx,
        plus authoritative keyword tag bonus.
        """
        if not query_tokens:
            return 0.0

        doc_tokens = self._doc_tokens[doc_idx]
        doc_len = len(doc_tokens)
        if doc_len == 0:
            return 0.0

        n_docs = len(self.corpus)
        tf_map: Dict[str, int] = {}
        for t in doc_tokens:
            tf_map[t] = tf_map.get(t, 0) + 1

        bm25 = 0.0
        chunk_keywords = [k.lower() for k in chunk.get("keywords", [])]
        chunk_text_lower = self._chunk_full_text(chunk).lower()

        for q_tok in query_tokens:
            tf = tf_map.get(q_tok, 0)
            if tf == 0 and q_tok in chunk_text_lower:
                tf = 1
            if tf > 0:
                df = self._doc_freqs.get(q_tok, 1)
                idf = math.log(1.0 + (n_docs - df + 0.5) / (df + 0.5))
                denom = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / self._avgdl))
                bm25 += idf * ((tf * (self.k1 + 1.0)) / denom)

                if any(q_tok in kw for kw in chunk_keywords):
                    bm25 += 0.75

        return float(bm25)

    def _query_dense_cosine_scores(self, query_vec: np.ndarray) -> Dict[int, float]:
        """
        Queries Qdrant Vector DB (when available) or in-memory cosine matrix
        to obtain dense semantic cosine similarity in [0, 1] for each corpus chunk.
        """
        cosine_map: Dict[int, float] = {}

        if self._qdrant_ready and self.qdrant_client is not None:
            try:
                response = self.qdrant_client.query_points(
                    collection_name=self.collection_name,
                    query=query_vec.tolist(),
                    limit=len(self.corpus),
                )
                for pt in response.points:
                    cosine_map[int(pt.id)] = float(np.clip((pt.score + 1.0) / 2.0 if pt.score < 0 else pt.score, 0.0, 1.0))
                if cosine_map:
                    return cosine_map
            except Exception:
                pass

        # Fallback: direct matrix-vector cosine similarity
        sims = np.dot(self._corpus_embeddings, query_vec)
        for idx, val in enumerate(sims):
            cosine_map[idx] = float(np.clip(max(val, 0.0), 0.0, 1.0))
        return cosine_map

    def retrieve(
        self,
        query: str,
        disease_filter: Optional[str] = None,
        top_k: int = 4,
    ) -> List[Dict[str, Any]]:
        """
        Retrieves top_k most relevant guideline chunks by combining normalized
        Okapi BM25 lexical score and Qdrant Dense Cosine Similarity score:
            S_hybrid = alpha * S_bm25_norm + (1 - alpha) * S_cosine
        """
        query_tokens = self._tokenize(query)
        query_vec = self._encode_text(query)

        # 1. Dense Cosine similarity scores from Qdrant / embedding index
        cosine_scores = self._query_dense_cosine_scores(query_vec)

        # 2. Sparse Okapi BM25 lexical scores
        raw_bm25_scores: Dict[int, float] = {}
        for idx, chunk in enumerate(self.corpus):
            raw_bm25_scores[idx] = self._compute_bm25_score(query_tokens, idx, chunk)

        max_bm25 = max(raw_bm25_scores.values()) if raw_bm25_scores else 0.0

        # 3. Filter and compute combined hybrid score
        scored_chunks: List[Tuple[float, float, float, Dict[str, Any]]] = []
        for idx, chunk in enumerate(self.corpus):
            if disease_filter:
                entity = chunk.get("disease_entity", "").upper()
                target = disease_filter.upper()
                if target not in entity and entity != "ALL_RESPIRATORY_CARDIAC":
                    continue

            raw_bm25 = raw_bm25_scores[idx]
            bm25_norm = (raw_bm25 / max_bm25) if max_bm25 > 1e-8 else 0.0
            cos_sim = cosine_scores.get(idx, 0.0)

            hybrid_score = self.alpha * bm25_norm + (1.0 - self.alpha) * cos_sim

            # Only include candidates with positive lexical or semantic signal when disease_filter is set
            if raw_bm25 > 0 or cos_sim > 0.05 or not disease_filter:
                scored_chunks.append((hybrid_score, bm25_norm, cos_sim, chunk))

        # Sort descending by hybrid score
        scored_chunks.sort(key=lambda x: x[0], reverse=True)

        results: List[Dict[str, Any]] = []
        for hybrid_score, bm25_norm, cos_sim, chunk in scored_chunks[:top_k]:
            item = dict(chunk)
            item["bm25_score"] = round(float(bm25_norm), 4)
            item["cosine_score"] = round(float(cos_sim), 4)
            item["relevance_score"] = round(float(hybrid_score), 4)
            results.append(item)

        if not results:
            for idx, c in enumerate(self.corpus[:top_k]):
                item = dict(c)
                item["bm25_score"] = 0.0
                item["cosine_score"] = round(float(cosine_scores.get(idx, 0.0)), 4)
                item["relevance_score"] = item["cosine_score"]
                results.append(item)

        return results
