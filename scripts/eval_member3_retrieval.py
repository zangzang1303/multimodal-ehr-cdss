"""Evaluate Recall@K on the small, explicitly labelled Member 3 query set."""

import json
from pathlib import Path

from src.agent.retriever import HybridGuidelineRetriever


def evaluate(queries: list[dict], k: int = 3) -> float:
    retriever = HybridGuidelineRetriever()
    hits = 0
    for item in queries:
        returned = {result["chunk_id"] for result in retriever.retrieve(item["query"], top_k=k)}
        hits += bool(returned.intersection(item["relevant_chunk_ids"]))
    return hits / len(queries) if queries else 0.0


if __name__ == "__main__":
    path = Path(__file__).resolve().parents[1] / "data/retrieval_queries_member3.json"
    queries = json.loads(path.read_text(encoding="utf-8"))
    print(f"Recall@3: {evaluate(queries):.3f} ({len(queries)} labelled queries)")
