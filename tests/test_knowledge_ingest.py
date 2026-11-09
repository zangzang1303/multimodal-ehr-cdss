"""
Unit Tests for ClinicalKnowledgeIngestor and Qdrant Vector Store
M-CDSS Backlog 05 - Member 2 Verification
"""

import pytest
from qdrant_client import QdrantClient
from src.agent.knowledge_ingest import ClinicalKnowledgeIngestor, ClinicalChunk


def test_chunk_evidence_level_integrity():
    """Verify strictly no guessing/invention of evidence_level when source does not state it."""
    chunk_with_level = ClinicalChunk(
        chunk_id="TEST_01",
        source_id="TEST",
        version="2024",
        target_disease="COPD",
        section_title="Test Section",
        page_or_section="Page 1",
        clinical_category="DIAGNOSTIC_CRITERIA",
        text_content="Some clinical text",
        evidence_level="Evidence A",
    )
    assert chunk_with_level.evidence_level == "Evidence A"

    chunk_without_level = ClinicalChunk(
        chunk_id="TEST_02",
        source_id="TEST",
        version="2024",
        target_disease="COPD",
        section_title="Test Section 2",
        page_or_section="Page 2",
        clinical_category="RISK_FACTORS",
        text_content="Some risk factors",
        evidence_level=None,
    )
    assert chunk_without_level.evidence_level is None
    payload = chunk_without_level.to_payload()
    assert payload["evidence_level"] is None


def test_load_guidelines_from_dir():
    """Verify loading from real data/guidelines folder."""
    ingestor = ClinicalKnowledgeIngestor(qdrant_client=QdrantClient(":memory:"))
    chunks = ingestor.load_guidelines_from_dir("data/guidelines")

    assert len(chunks) >= 14
    sources = {c.source_id for c in chunks}
    assert "GINA_2024" in sources
    assert "GOLD_2024" in sources
    assert "ESC_2023" in sources
    assert "BYT_VN_CAP_2020" in sources

    # Check evidence_level is None for BYT (Vietnamese official guidelines don't have GRADE Evidence A/B)
    byt_chunks = [c for c in chunks if c.source_id == "BYT_VN_CAP_2020"]
    for bc in byt_chunks:
        assert bc.evidence_level is None


def test_qdrant_storage_and_query():
    """Test Qdrant collection query on persisted vector store."""
    from src.agent.knowledge_ingest import get_qdrant_client
    client = get_qdrant_client("data/vector_store/qdrant")
    cols = [c.name for c in client.get_collections().collections]
    assert "clinical_guidelines" in cols

    info = client.get_collection("clinical_guidelines")
    assert info.points_count >= 14
    assert info.config.params.vectors.size == 768

    # Query directly by payload filter
    results, _ = client.scroll(
        collection_name="clinical_guidelines",
        limit=5,
        with_payload=True,
    )
    assert len(results) > 0
    payload = results[0].payload
    assert "source_id" in payload
    assert "version" in payload
    assert "section_title" in payload
    assert "text_content" in payload

