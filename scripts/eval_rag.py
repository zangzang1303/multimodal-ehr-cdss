"""
Empirical Evaluation Script for Agentic RAG & Evidence Grounding (RQ5)
M-CDSS Phase 3 / Backlog 09 - Task 3.1 (Member 3)

Strictly READ-ONLY when connected to a remote Qdrant server via QDRANT_URL / --qdrant-url:
1. Verifies Qdrant collection vector dim (768), exact chunk_id set alignment, and
   exact text_content SHA-256 parity against data/guidelines/*.json (raises if out of sync).
2. Evaluates Cohen's kappa and Retrieval metrics (Recall@1/3/5, MRR, nDCG@5) over 60 queries.
3. Audits explain_clinical_case() character-offset grounding and out-of-note string probe
   rejection over 50 hold-out notes, recording exact dataset provenance and exporting
   20 real pipeline spans for manual human semantic audit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from qdrant_client import QdrantClient

from src.agent.evidence_grounder import EvidenceGrounder
from src.agent.knowledge_ingest import ClinicalKnowledgeIngestor
from src.agent.retriever import HybridGuidelineRetriever, _hashed_dense_fallback, load_extended_guideline_corpus
from src.api.routes.agent_chat import explain_clinical_case
from src.api.schemas import AgentExplainRequest


REPO_ROOT = Path(__file__).resolve().parents[1]

FABRICATED_PROBES = [
    "Hồ sơ ghi nhận tiền sử phẫu thuật bắc cầu mạch vành và xơ gan cổ trướng mức độ 4.",
    "CT sọ não cấp cứu phát hiện khối u nguyên bào thần kinh đệm vùng trán phải.",
    "Bệnh nhân đang lọc máu chu kỳ 3 lần/tuần do bệnh thận mạn giai đoạn cuối và tăng kali máu.",
    "Xét nghiệm Troponin I siêu nhạy tăng gấp 20 lần kèm ST chênh lên ở chuyển đạo trước ngực.",
    "Chẩn đoán sản giật nặng trên thai phụ 36 tuần kèm hội chứng HELLP và suy gan cấp.",
]


CHECKED_METADATA_FIELDS = [
    "source_id",
    "version",
    "target_disease",
    "section_title",
    "page_or_section",
    "clinical_category",
    "evidence_level",
    "source_verified",
]


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def verify_qdrant_collection_sync(
    qdrant_client: QdrantClient,
    collection_name: str,
    corpus: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Read-only verification of collection dim (768), chunk_id set parity,
    text_content SHA-256 parity, and 8 provenance metadata fields against data/guidelines/*.json.
    Does NOT verify semantic embedding quality when deterministic hashed fallback vectors are active.
    """
    info = qdrant_client.get_collection(collection_name)
    vec_dim = getattr(getattr(getattr(info, "config", None), "params", None), "vectors", None)
    actual_dim = getattr(vec_dim, "size", None)
    if actual_dim != 768:
        raise RuntimeError(
            f"Qdrant collection '{collection_name}' has vector size {actual_dim} != 768. "
            "Run `python src/agent/knowledge_ingest.py` explicitly to rebuild."
        )

    qdrant_by_id: Dict[str, str] = {}
    qdrant_payloads: Dict[str, Dict[str, Any]] = {}
    next_offset = None
    while True:
        records, next_offset = qdrant_client.scroll(
            collection_name=collection_name,
            limit=100,
            offset=next_offset,
            with_payload=True,
            with_vectors=False,
        )
        for rec in records:
            payload = rec.payload or {}
            cid = payload.get("chunk_id")
            if cid is not None:
                cid_str = str(cid)
                qdrant_by_id[cid_str] = _sha256_text(str(payload.get("text_content", "")))
                qdrant_payloads[cid_str] = payload
        if next_offset is None:
            break

    ingestor = ClinicalKnowledgeIngestor(qdrant_client=qdrant_client)
    disk_payloads = {
        str(c.chunk_id): c.to_payload()
        for c in ingestor.load_guidelines_from_dir(str(REPO_ROOT / "data" / "guidelines"))
    }
    disk_by_id = {
        str(c["chunk_id"]): _sha256_text(str(c.get("text_content", "")))
        for c in corpus
    }
    missing_in_qdrant = sorted(set(disk_by_id) - set(qdrant_by_id))
    extra_in_qdrant = sorted(set(qdrant_by_id) - set(disk_by_id))
    content_mismatches = sorted(
        cid for cid in set(disk_by_id).intersection(qdrant_by_id)
        if disk_by_id[cid] != qdrant_by_id[cid]
    )
    metadata_mismatches = [
        (cid, field, disk_payloads[cid].get(field), qdrant_payloads[cid].get(field))
        for cid in sorted(set(disk_payloads).intersection(qdrant_payloads))
        for field in CHECKED_METADATA_FIELDS
        if disk_payloads[cid].get(field) != qdrant_payloads[cid].get(field)
    ]

    if (
        (info.points_count or 0) != len(disk_by_id)
        or missing_in_qdrant
        or extra_in_qdrant
        or content_mismatches
        or metadata_mismatches
    ):
        raise RuntimeError(
            f"Qdrant collection '{collection_name}' is NOT synchronized with data/guidelines/*.json "
            f"(qdrant_points={info.points_count}, disk_chunks={len(disk_by_id)}, "
            f"missing={missing_in_qdrant[:5]}, extra={extra_in_qdrant[:5]}, "
            f"content_hash_mismatches={content_mismatches[:5]}, "
            f"metadata_mismatches={metadata_mismatches[:5]}). "
            "eval_rag.py is strictly read-only on remote Qdrant; run `python src/agent/knowledge_ingest.py` explicitly."
        )

    metadata_matched_chunks = len(set(disk_payloads).intersection(qdrant_payloads))
    return {
        "qdrant_points_count": info.points_count,
        "qdrant_vector_dim": actual_dim,
        "qdrant_vector_dim_verified": actual_dim,
        "qdrant_corpus_sync_verified": True,
        "qdrant_chunk_id_match_count": len(disk_by_id),
        "qdrant_content_sha256_match_count": len(disk_by_id) - len(content_mismatches),
        "qdrant_metadata_match_count": metadata_matched_chunks,
        "qdrant_checked_metadata_fields": CHECKED_METADATA_FIELDS,
        "qdrant_vector_semantics_verified": False,
        "qdrant_sync_scope_note": (
            "Read-only check verified 768-D vector dimension, chunk_id set, text_content SHA-256, "
            "and 8 provenance metadata fields against data/guidelines/*.json; it does NOT verify "
            "semantic embedding quality because offline deterministic 768-D hashed fallback vectors "
            "are active instead of all-mpnet-base-v2."
        ),
    }


def compute_cohens_kappa(queries: List[Dict[str, Any]], all_chunk_ids: List[str]) -> float:
    """Computes binary relevance Cohen's kappa across all (query, chunk) pairs."""
    n_pos_1 = n_pos_2 = n_both = n_neither = 0
    total = 0
    for q in queries:
        a1 = set(q.get("annotator_1_chunk_ids", q["relevant_chunk_ids"]))
        a2 = set(q.get("annotator_2_chunk_ids", q["relevant_chunk_ids"]))
        for cid in all_chunk_ids:
            in1 = cid in a1
            in2 = cid in a2
            if in1:
                n_pos_1 += 1
            if in2:
                n_pos_2 += 1
            if in1 and in2:
                n_both += 1
            elif not in1 and not in2:
                n_neither += 1
            total += 1
    if total == 0:
        return 1.0
    p0 = (n_both + n_neither) / total
    pe = ((n_pos_1 / total) * (n_pos_2 / total)) + (
        ((total - n_pos_1) / total) * ((total - n_pos_2) / total)
    )
    if abs(1.0 - pe) < 1e-12:
        return 1.0
    return round((p0 - pe) / (1.0 - pe), 4)


def compute_ranking_metrics(
    ranked_lists: List[List[str]],
    ground_truth_sets: List[set[str]],
) -> Dict[str, float]:
    n = len(ranked_lists)
    r1 = r3 = r5 = mrr = ndcg5 = 0.0
    for ranked, gt in zip(ranked_lists, ground_truth_sets):
        top1 = set(ranked[:1])
        top3 = set(ranked[:3])
        top5 = set(ranked[:5])
        if top1.intersection(gt):
            r1 += 1.0
        if top3.intersection(gt):
            r3 += 1.0
        if top5.intersection(gt):
            r5 += 1.0
        for rank_idx, cid in enumerate(ranked, start=1):
            if cid in gt:
                mrr += 1.0 / rank_idx
                break
        dcg = 0.0
        for rank_idx, cid in enumerate(ranked[:5], start=1):
            if cid in gt:
                dcg += 1.0 / math.log2(rank_idx + 1)
        ideal_hits = min(len(gt), 5)
        idcg = sum(1.0 / math.log2(i + 1) for i in range(1, ideal_hits + 1))
        ndcg5 += (dcg / idcg) if idcg > 0 else 0.0

    denom = max(n, 1)
    return {
        "recall_at_1": round(r1 / denom, 4),
        "recall_at_3": round(r3 / denom, 4),
        "recall_at_5": round(r5 / denom, 4),
        "mrr": round(mrr / denom, 4),
        "ndcg_at_5": round(ndcg5 / denom, 4),
    }


def dense_only_retrieve(
    client: QdrantClient,
    collection_name: str,
    query: str,
    embedding_fn: Any,
    top_k: int = 10,
) -> List[str]:
    resp = client.query_points(
        collection_name=collection_name,
        query=embedding_fn(query),
        limit=top_k,
        with_payload=True,
    )
    return [pt.payload["chunk_id"] for pt in resp.points if pt.payload and "chunk_id" in pt.payload]


def evaluate_grounding_on_test_notes(
    n_cases: int = 50,
    allow_synthetic_note_fallback: bool = False,
) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Checks substring/character-offset invariants of explain_clinical_case() and out-of-note
    string probe rejection via EvidenceGrounder. Records exact hold-out dataset provenance and
    never silently pads with synthetic template notes unless --allow-synthetic-note-fallback is set.
    """
    grounder = EvidenceGrounder(fuzzy_threshold=0.88)
    strict_parquet = REPO_ROOT / "data" / "processed_rebuilt_strict" / "test.parquet"
    legacy_parquet = REPO_ROOT / "data" / "processed" / "test.parquet"

    if strict_parquet.exists():
        notes_path = strict_parquet
        is_canonical_strict = True
    elif legacy_parquet.exists():
        notes_path = legacy_parquet
        is_canonical_strict = False
    else:
        raise FileNotFoundError("Neither data/processed_rebuilt_strict/test.parquet nor data/processed/test.parquet found.")

    df = pd.read_parquet(notes_path)
    dataset_total_rows = int(len(df))
    note_col = next(
        (c for c in ("clinical_note", "note_text", "raw_text", "text") if c in df.columns),
        None,
    )
    if note_col is None:
        raise KeyError(f"No clinical note column found in {notes_path}")

    dataset_notes = [str(val) for val in df[note_col].dropna().tolist()[:n_cases]]
    notes_from_dataset_count = len(dataset_notes)
    notes_from_fallback_template_count = 0

    if len(dataset_notes) < n_cases:
        if not allow_synthetic_note_fallback:
            raise RuntimeError(
                f"{notes_path} yielded only {len(dataset_notes)} non-null notes (< {n_cases}). "
                "Pass --allow-synthetic-note-fallback explicitly if synthetic padding is intended."
            )
        base_template = (
            "CHIEF COMPLAINT: Patient {idx} presents with acute dyspnea and wheezing.\n"
            "HISTORY OF PRESENT ILLNESS: Cough and shortness of breath worsening over 4 days.\n"
            "PHYSICAL EXAMINATION: BP: 124/78 mmHg, HR: 84 bpm, SpO2: 94%. Auscultation reveals expiratory wheezes.\n"
            "MEDICATIONS: Albuterol inhaler PRN and corticosteroid taper."
        )
        while len(dataset_notes) < n_cases:
            dataset_notes.append(base_template.format(idx=len(dataset_notes) + 1))
            notes_from_fallback_template_count += 1

    total_pipeline_claims = 0
    grounded_pipeline_claims = 0
    invariant_matches = 0
    total_fabricated_probes = 0
    rejected_fabricated_probes = 0
    manual_audit_samples: List[Dict[str, Any]] = []

    for idx, note in enumerate(dataset_notes[:n_cases]):
        req = AgentExplainRequest(
            patient_id=f"PT-AUDIT-{idx + 1:03d}",
            clinical_notes=note,
        )
        resp = explain_clinical_case(req)

        total_pipeline_claims += len(resp.claim_audits)
        grounded_pipeline_claims += len(resp.verified_spans)
        for sp in resp.verified_spans:
            if resp.display_note[sp.start_char : sp.end_char] == sp.text:
                invariant_matches += 1
            if len(manual_audit_samples) < 20:
                manual_audit_samples.append(
                    {
                        "sample_id": len(manual_audit_samples) + 1,
                        "patient_id": resp.patient_id,
                        "primary_diagnosis": resp.primary_diagnosis,
                        "reasoning_mode": resp.reasoning_mode,
                        "span_text": sp.text,
                        "start_char": sp.start_char,
                        "end_char": sp.end_char,
                        "note_excerpt": resp.display_note[
                            max(0, sp.start_char - 40) : min(len(resp.display_note), sp.end_char + 40)
                        ],
                        "human_verified": None,
                        "auditor_comment": "",
                    }
                )

        # Out-of-note string probe check (does NOT measure semantic/negation hallucination)
        probe = FABRICATED_PROBES[idx % len(FABRICATED_PROBES)]
        probe_claims = [{"text": probe, "category": "counter", "label": "Out-of-note string probe"}]
        if resp.verified_spans:
            probe_claims.append(
                {"text": resp.verified_spans[0].text, "category": "supporting", "label": "Baseline note clause"}
            )
        spans, rejected_count = grounder.ground_evidence_claims(resp.display_note, probe_claims)
        total_fabricated_probes += 1
        if not any(s["text"] == probe for s in spans) and rejected_count >= 1:
            rejected_fabricated_probes += 1

    is_strict_302 = is_canonical_strict and dataset_total_rows == 302
    audit_status = "canonical_strict_holdout" if is_strict_302 else "preliminary_non_strict_holdout"
    scope_dataset_note = (
        "Evaluated on canonical strict N=302 hold-out split."
        if is_strict_302
        else (
            f"PRELIMINARY non-strict hold-out audit only: sourced from data/processed/test.parquet "
            f"(N={dataset_total_rows}), NOT an official evaluation on the pending canonical strict N=302 split."
        )
    )

    audit_summary = {
        "audit_status": audit_status,
        "audit_method": "pipeline_offset_invariant_and_out_of_note_string_rejection_only",
        "audit_scope_limitation": (
            "Automatic metrics verify character-offset substring matching on display_note and rejection "
            "of out-of-note probe strings only; they do NOT establish semantic correctness, negation "
            f"fidelity, or clinical validity. {scope_dataset_note}"
        ),
        "notes_source_path": str(notes_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "notes_source_is_canonical_strict_302": is_strict_302,
        "dataset_total_rows": dataset_total_rows,
        "cases_tested": n_cases,
        "notes_from_dataset_count": notes_from_dataset_count,
        "notes_from_fallback_template_count": notes_from_fallback_template_count,
        "total_genuine_claims": total_pipeline_claims,
        "grounded_claims": grounded_pipeline_claims,
        "genuine_claim_grounding_rate": round(grounded_pipeline_claims / max(total_pipeline_claims, 1), 4),
        "injected_out_of_note_probes": total_fabricated_probes,
        "rejected_out_of_note_probes": rejected_fabricated_probes,
        "out_of_note_probe_rejection_rate": round(rejected_fabricated_probes / max(total_fabricated_probes, 1), 4),
        "span_substring_match_rate": round(invariant_matches / max(grounded_pipeline_claims, 1), 4),
        "manual_semantic_precision_20_spans": None,
        "manual_semantic_audit_status": "pending_human_review",
        "manual_audit_sample_file": "results/grounding_manual_audit_20_samples.json",
        "sampled_20_spans_checked": 0,
        "exported_samples_for_review": len(manual_audit_samples),
    }
    return audit_summary, manual_audit_samples


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only evaluation of Agentic RAG & Grounding (RQ5).")
    parser.add_argument("--qdrant-url", default=None, help="Live Qdrant HTTP URL (defaults to QDRANT_URL env).")
    parser.add_argument(
        "--allow-synthetic-note-fallback",
        action="store_true",
        help="Explicit opt-in if dataset parquet has fewer than 50 notes.",
    )
    args = parser.parse_args()

    os.environ.pop("MCDSS_USE_ST_ENCODER", None)
    queries_path = REPO_ROOT / "data" / "retrieval_queries_member3.json"
    queries = json.loads(queries_path.read_text(encoding="utf-8"))

    corpus = load_extended_guideline_corpus()
    all_chunk_ids = [c["chunk_id"] for c in corpus]

    resolved_url = args.qdrant_url or os.getenv("QDRANT_URL")
    if resolved_url:
        qdrant_client = QdrantClient(url=resolved_url, timeout=5)
        qdrant_target = resolved_url
        sync_info = verify_qdrant_collection_sync(qdrant_client, "clinical_guidelines", corpus)
    else:
        qdrant_client = QdrantClient(":memory:")
        qdrant_target = "in_memory_ephemeral"
        ingestor = ClinicalKnowledgeIngestor(qdrant_client=qdrant_client)
        ingestor.ingest(guidelines_dir="data/guidelines", recreate_collection=True)
        sync_info = verify_qdrant_collection_sync(qdrant_client, "clinical_guidelines", corpus)

    dense_fn = lambda txt: _hashed_dense_fallback(txt, dim=768)
    dense_lists = [
        dense_only_retrieve(qdrant_client, "clinical_guidelines", q["query"], dense_fn, top_k=10)
        for q in queries
    ]

    sparse_retriever = HybridGuidelineRetriever(corpus=corpus, qdrant_client=None)
    bm25_lists = [
        [r["chunk_id"] for r in sparse_retriever.retrieve(q["query"], top_k=10)]
        for q in queries
    ]

    hybrid_retriever = HybridGuidelineRetriever(
        corpus=corpus,
        qdrant_client=qdrant_client,
        embedding_fn=dense_fn,
        strict_qdrant=True,
    )
    hybrid_lists = []
    for q in queries:
        rows = hybrid_retriever.retrieve(q["query"], top_k=10)
        meta = hybrid_retriever.last_retrieval_metadata
        if meta.get("dense_hit_count", 0) <= 0:
            raise RuntimeError(f"Hybrid Qdrant returned 0 dense hits for {q['query_id']}: {meta}")
        hybrid_lists.append([r["chunk_id"] for r in rows])

    gt_sets = [set(q["relevant_chunk_ids"]) for q in queries]
    kappa = compute_cohens_kappa(queries, all_chunk_ids)
    grounding_audit, manual_samples = evaluate_grounding_on_test_notes(
        n_cases=50,
        allow_synthetic_note_fallback=args.allow_synthetic_note_fallback,
    )

    results_dir = REPO_ROOT / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    manual_audit_path = results_dir / "grounding_manual_audit_20_samples.json"
    manual_audit_path.write_text(
        json.dumps(
            {
                "instructions": (
                    "Review each grounded span from explain_clinical_case() against note_excerpt and "
                    "set human_verified=true/false manually before reporting manual semantic precision."
                ),
                "samples": manual_samples,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    rag_report = {
        "is_mock": False,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "qdrant_target": qdrant_target,
        "qdrant_points_count": sync_info["qdrant_points_count"],
        "qdrant_vector_dim_verified": sync_info["qdrant_vector_dim_verified"],
        "qdrant_corpus_sync_verified": sync_info["qdrant_corpus_sync_verified"],
        "qdrant_chunk_id_match_count": sync_info["qdrant_chunk_id_match_count"],
        "qdrant_content_sha256_match_count": sync_info["qdrant_content_sha256_match_count"],
        "qdrant_metadata_match_count": sync_info["qdrant_metadata_match_count"],
        "qdrant_checked_metadata_fields": sync_info["qdrant_checked_metadata_fields"],
        "qdrant_vector_semantics_verified": sync_info["qdrant_vector_semantics_verified"],
        "qdrant_sync_scope_note": sync_info["qdrant_sync_scope_note"],
        "corpus_size_chunks": len(corpus),
        "ingested_guideline_json_chunks": sync_info["qdrant_points_count"],
        "dense_encoder": "768d_hashed_deterministic_cpu_fallback (all-mpnet-base-v2 offline unavailable)",
        "dense_encoder_is_semantic_model": False,
        "retrieval_scope_note": (
            "Recall/MRR/nDCG metrics reflect live Qdrant RRF using deterministic 768-D hashed "
            "fallback vectors (all-mpnet-base-v2 offline unavailable), NOT a real semantic encoder."
        ),
        "query_count": len(queries),
        "cohens_kappa": kappa,
        "modes": {
            "dense_only": compute_ranking_metrics(dense_lists, gt_sets),
            "bm25_only": compute_ranking_metrics(bm25_lists, gt_sets),
            "hybrid_rrf": compute_ranking_metrics(hybrid_lists, gt_sets),
        },
        "grounding_audit_50_cases": grounding_audit,
    }

    report_path = results_dir / "rag_evaluation_report.json"
    report_path.write_text(json.dumps(rag_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    registry_path = results_dir / "registry.json"
    if registry_path.exists():
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry["rag"] = rag_report
        registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(rag_report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
