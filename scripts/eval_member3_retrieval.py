"""Evaluate Recall@K on the explicitly labelled Member 3 query set (supports live Qdrant Hybrid or BM25)."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, List

from src.agent.retriever import HybridGuidelineRetriever


def evaluate(
    queries: List[Dict[str, Any]],
    k: int = 3,
    qdrant_url: str | None = None,
    require_qdrant: bool = False,
) -> Dict[str, Any]:
    resolved_url = qdrant_url or os.getenv("QDRANT_URL")
    qdrant_client = None
    qdrant_points = None
    if resolved_url:
        from qdrant_client import QdrantClient

        qdrant_client = QdrantClient(url=resolved_url, timeout=5)
        info = qdrant_client.get_collection("clinical_guidelines")
        qdrant_points = info.points_count
    elif require_qdrant:
        raise RuntimeError("QDRANT_URL must be set when require_qdrant=True")

    retriever = HybridGuidelineRetriever(
        qdrant_client=qdrant_client,
        strict_qdrant=bool(resolved_url or require_qdrant),
    )

    hits = 0
    dense_hits = 0
    modes_seen = set()
    for item in queries:
        returned = {result["chunk_id"] for result in retriever.retrieve(item["query"], top_k=k)}
        hits += bool(returned.intersection(item["relevant_chunk_ids"]))
        meta = retriever.last_retrieval_metadata
        modes_seen.add(meta.get("mode", "unknown"))
        if resolved_url and meta.get("dense_hit_count", 0) <= 0:
            raise RuntimeError(f"Qdrant returned 0 dense hits for query {item.get('query_id')}: {meta}")
        if meta.get("dense_hit_count", 0) > 0:
            dense_hits += 1

    recall = hits / len(queries) if queries else 0.0
    mode_label = ", ".join(sorted(modes_seen)) if modes_seen else "bm25_only"
    dense_encoder = (
        (os.getenv("MCDSS_DENSE_MODEL") or "768d_hashed_fallback_not_mpnet")
        if resolved_url
        else "none_bm25_only"
    )
    return {
        "recall_at_k": recall,
        "query_count": len(queries),
        "corpus_size": len(retriever.corpus),
        "mode": mode_label,
        "qdrant_url": resolved_url or "disabled",
        "qdrant_points_count": qdrant_points,
        "queries_with_qdrant_hits": dense_hits,
        "dense_encoder": dense_encoder,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate Member 3 guideline retrieval.")
    parser.add_argument("--qdrant-url", default=None, help="Live Qdrant HTTP URL (defaults to QDRANT_URL env).")
    parser.add_argument("--require-qdrant", action="store_true", help="Fail if QDRANT_URL is unset or returns 0 hits.")
    parser.add_argument("--k", type=int, default=3)
    args = parser.parse_args()

    path = Path(__file__).resolve().parents[1] / "data/retrieval_queries_member3.json"
    queries = json.loads(path.read_text(encoding="utf-8"))
    summary = evaluate(queries, k=args.k, qdrant_url=args.qdrant_url, require_qdrant=args.require_qdrant)
    print(
        f"Recall@{args.k}: {summary['recall_at_k']:.3f} ({summary['query_count']} labelled queries) | "
        f"mode={summary['mode']} | corpus={summary['corpus_size']} | "
        f"qdrant_points={summary['qdrant_points_count']} | dense_queries={summary['queries_with_qdrant_hits']} | "
        f"encoder={summary['dense_encoder']}"
    )
