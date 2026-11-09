

import os
import json
import logging
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
import yaml

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("KnowledgeIngest")


os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

# Process-level singleton QdrantClient for local embedded storage concurrency
_shared_qdrant_client: Optional[QdrantClient] = None


def get_qdrant_client(storage_path: str = "data/vector_store/qdrant") -> QdrantClient:
    """
    Returns a shared singleton QdrantClient to prevent concurrent lock collisions
    on local embedded directory storage within the same process.
    """
    global _shared_qdrant_client
    if _shared_qdrant_client is None:
        try:
            if os.path.exists(storage_path):
                _shared_qdrant_client = QdrantClient(path=storage_path)
            else:
                _shared_qdrant_client = QdrantClient(":memory:")
        except Exception:
            _shared_qdrant_client = QdrantClient(":memory:")
    return _shared_qdrant_client


@dataclass
class ClinicalChunk:
    chunk_id: str
    source_id: str
    version: str
    target_disease: str
    section_title: str
    page_or_section: str
    clinical_category: str
    text_content: str
    evidence_level: Optional[str] = None
    extra_metadata: Optional[Dict[str, Any]] = None

    def to_payload(self) -> Dict[str, Any]:
        data = asdict(self)
        if self.extra_metadata:
            data.update(self.extra_metadata)
        data.pop("extra_metadata", None)
        return data


class ClinicalKnowledgeIngestor:
    """
    Ingestor pipeline to parse guideline documents, compute embeddings,
    and persist structured chunks into Qdrant collection 'clinical_guidelines'.

    GHI CHÚ DÀNH CHO CÁC THÀNH VIÊN KHÁC:
    - [MEMBER 1 - Task 1.1]: Cấu hình mô hình embedding và threshold được load từ
      `configs/rag_config.yaml`. Nếu Member 1 đánh giá chọn model embedding khác (ví dụ: mô hình y khoa),
      chỉ cần cập nhật trường `embedding_model` trong `configs/rag_config.yaml` và chạy lại `python src/agent/knowledge_ingest.py`.
    - [MEMBER 3 - Task 3.1]: Collection Qdrant tạo bởi class này tên là 'clinical_guidelines'.
      Lớp `HybridGuidelineRetriever` (src/agent/retriever.py) của Member 3 sẽ truy vấn trực tiếp
      trên collection này (kết hợp Dense search trên vector 768-dim và BM25 trên trường `text_content`).
    """

    DEFAULT_CONFIG_PATH = "configs/rag_config.yaml"

    def __init__(
        self,
        config_path: Optional[str] = None,
        qdrant_client: Optional[QdrantClient] = None,
        storage_path: Optional[str] = None,
        collection_name: Optional[str] = None,
        embedding_model_name: Optional[str] = None,
    ):
        self.config = self._load_config(config_path or self.DEFAULT_CONFIG_PATH)

        self.collection_name = collection_name or self.config.get("collection_name", "clinical_guidelines")
        self.model_name = embedding_model_name or self.config.get(
            "embedding_model", "sentence-transformers/all-mpnet-base-v2"
        )
        self.vector_dim = self.config.get("vector_dim", 768)

       
        if qdrant_client is not None:
            self.client = qdrant_client
        else:
            final_storage_path = storage_path or self.config.get("qdrant_storage_path", "data/vector_store/qdrant")
            os.makedirs(final_storage_path, exist_ok=True)
            self.client = get_qdrant_client(final_storage_path)

        self._encoder = None

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    @property
    def encoder(self):
    
        if self._encoder is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            from sentence_transformers import SentenceTransformer
            try:
                self._encoder = SentenceTransformer(self.model_name, local_files_only=True)
            except TypeError:
                self._encoder = SentenceTransformer(self.model_name)
        return self._encoder

    def load_guidelines_from_dir(self, guidelines_dir: str = "data/guidelines") -> List[ClinicalChunk]:
        
        chunks: List[ClinicalChunk] = []
        if not os.path.exists(guidelines_dir):
            raise FileNotFoundError(f"Guidelines directory '{guidelines_dir}' not found.")

        for fname in os.listdir(guidelines_dir):
            if fname.endswith(".json") and not fname.startswith("catalog"):
                fpath = os.path.join(guidelines_dir, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    try:
                        raw_items = json.load(f)
                    except Exception as e:
                        logger.error(f"Failed to read {fpath}: {e}")
                        continue

                    for item in raw_items:
                        
                        chunk = ClinicalChunk(
                            chunk_id=item["chunk_id"],
                            source_id=item["source_id"],
                            version=item.get("version", "2024"),
                            target_disease=item.get("target_disease", "GENERAL"),
                            section_title=item.get("section_title", ""),
                            page_or_section=item.get("page_or_section", ""),
                            clinical_category=item.get("clinical_category", "DIAGNOSTIC_CRITERIA"),
                            text_content=item["text_content"],
                        
                            evidence_level=item.get("evidence_level") if item.get("evidence_level") else None,
                            extra_metadata=item.get("metadata", {}),
                        )
                        chunks.append(chunk)

        logger.info(f"Loaded {len(chunks)} clinical chunks from {guidelines_dir}")
        return chunks

    def initialize_collection(self, recreate_if_exists: bool = False):
        """Creates or resets the Qdrant collection with 768-dim Cosine configuration."""
        existing_cols = [c.name for c in self.client.get_collections().collections]

        if self.collection_name in existing_cols:
            if recreate_if_exists:
                logger.info(f"Recreating existing collection '{self.collection_name}'...")
                self.client.delete_collection(self.collection_name)
            else:
                logger.info(f"Collection '{self.collection_name}' already exists.")
                return

        logger.info(f"Creating collection '{self.collection_name}' (dim={self.vector_dim}, metric=Cosine)...")
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=qmodels.VectorParams(
                size=self.vector_dim,
                distance=qmodels.Distance.COSINE,
            ),
        )

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
      
        embeddings = self.encoder.encode(
            texts,
            show_progress_bar=True,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return embeddings.tolist()

    def ingest(self, guidelines_dir: str = "data/guidelines", recreate_collection: bool = True) -> Dict[str, Any]:
        
        chunks = self.load_guidelines_from_dir(guidelines_dir)
        if not chunks:
            raise ValueError(f"No clinical chunks found to ingest in {guidelines_dir}")

        self.initialize_collection(recreate_if_exists=recreate_collection)

        texts = [c.text_content for c in chunks]
        logger.info(f"Computing embeddings for {len(texts)} chunks...")
        vectors = self.generate_embeddings(texts)

        points = []
        source_counts: Dict[str, int] = {}
        disease_counts: Dict[str, int] = {}

        for idx, (chunk, vector) in enumerate(zip(chunks, vectors)):
            payload = chunk.to_payload()
            points.append(
                qmodels.PointStruct(
                    id=idx + 1,
                    vector=vector,
                    payload=payload,
                )
            )
       
            source_counts[chunk.source_id] = source_counts.get(chunk.source_id, 0) + 1
            disease_counts[chunk.target_disease] = disease_counts.get(chunk.target_disease, 0) + 1

        logger.info(f"Upserting {len(points)} points into Qdrant collection '{self.collection_name}'...")
        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

        collection_info = self.client.get_collection(self.collection_name)
        total_points = collection_info.points_count

        logger.info(f"Ingestion complete! Total stored chunks: {total_points}")
        return {
            "status": "success",
            "collection_name": self.collection_name,
            "total_chunks": total_points,
            "source_distribution": source_counts,
            "disease_distribution": disease_counts,
        }


def run_ingest():
  
    ingestor = ClinicalKnowledgeIngestor()
    result = ingestor.ingest(guidelines_dir="data/guidelines", recreate_collection=True)
    print("\n" + "=" * 60)
    print("CLINICAL KNOWLEDGE INGESTION SUMMARY:")
    print(f"Collection Name:     {result['collection_name']}")
    print(f"Total Stored Chunks: {result['total_chunks']}")
    print(f"Sources:             {result['source_distribution']}")
    print(f"Diseases:            {result['disease_distribution']}")
    print("=" * 60 + "\n")
    return result


if __name__ == "__main__":
    run_ingest()
