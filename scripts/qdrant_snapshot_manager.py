"""
Qdrant Offline Snapshot Manager & Restore Utility
M-CDSS Phase 2 / Backlog 07 - Task 2.1 (Member 2: Data Engineer & Privacy)

Provides offline snapshot creation, checksum verification, and restore automation
for Qdrant vector database hosting clinical practice guidelines (GINA, GOLD, ESC, BYT).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import shutil
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("QdrantSnapshotManager")

ROOT_DIR = Path(__file__).resolve().parents[1]
VECTOR_STORE_DIR = ROOT_DIR / "data" / "vector_store"
QDRANT_STORAGE_DIR = VECTOR_STORE_DIR / "qdrant"
GUIDELINES_DIR = ROOT_DIR / "data" / "guidelines"
SNAPSHOT_ARCHIVE = VECTOR_STORE_DIR / "qdrant_snapshot.tar.gz"
MANIFEST_FILE = VECTOR_STORE_DIR / "manifest.json"


def compute_sha256(file_path: Path) -> str:
    """Computes SHA-256 checksum of a given file."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest().upper()


def get_guideline_manifest_items() -> List[Dict[str, Any]]:
    """Calculates metadata and checksums for all guidelines in data/guidelines."""
    items = []
    if not GUIDELINES_DIR.exists():
        return items

    for file_path in sorted(GUIDELINES_DIR.glob("*.*")):
        if file_path.name.startswith("."):
            continue
        items.append({
            "filename": file_path.name,
            "relative_path": str(file_path.relative_to(ROOT_DIR)).replace("\\", "/"),
            "size_bytes": file_path.stat().st_size,
            "sha256": compute_sha256(file_path),
        })
    return items


def create_snapshot() -> Dict[str, Any]:
    """
    Creates a compressed tar.gz snapshot of the Qdrant local storage directory
    and writes the manifest.json file.
    """
    if not QDRANT_STORAGE_DIR.exists():
        logger.info(f"Qdrant storage directory {QDRANT_STORAGE_DIR} does not exist. Triggering ingestion...")
        from src.agent.knowledge_ingest import run_ingest
        run_ingest()

    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Archive qdrant directory
    logger.info(f"Creating snapshot archive at {SNAPSHOT_ARCHIVE}...")
    with tarfile.open(SNAPSHOT_ARCHIVE, "w:gz") as tar:
        # Exclude lock files if present
        def filter_lock(tarinfo):
            if tarinfo.name.endswith(".lock"):
                return None
            return tarinfo

        tar.add(QDRANT_STORAGE_DIR, arcname="qdrant", filter=filter_lock)

    snapshot_sha256 = compute_sha256(SNAPSHOT_ARCHIVE)
    snapshot_size = SNAPSHOT_ARCHIVE.stat().st_size

    # 2. Build manifest
    guideline_items = get_guideline_manifest_items()
    manifest_data = {
        "manifest_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "database": {
            "engine": "Qdrant",
            "qdrant_client_version": "1.20.0",
            "docker_image": "qdrant/qdrant:latest",
            "collection_name": "clinical_guidelines",
            "vector_dim": 768,
            "distance_metric": "Cosine",
            "total_points": 14,
        },
        "embedding": {
            "model_name": "sentence-transformers/all-mpnet-base-v2",
            "normalize_embeddings": True,
        },
        "snapshot": {
            "filename": SNAPSHOT_ARCHIVE.name,
            "relative_path": str(SNAPSHOT_ARCHIVE.relative_to(ROOT_DIR)).replace("\\", "/"),
            "size_bytes": snapshot_size,
            "sha256": snapshot_sha256,
        },
        "source_guidelines": guideline_items,
        "licensing_and_distribution": {
            "policy": "Non-commercial clinical decision support and educational research use",
            "permitted_distribution": "Pre-indexed vector embeddings derived under fair academic research terms",
            "copyright_notice": "Original guidelines copyright belongs to GINA, GOLD, ESC, and Vietnam Ministry of Health (BYT).",
        },
    }

    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2, ensure_ascii=False)

    logger.info(f"Snapshot created successfully. Manifest written to {MANIFEST_FILE}")
    logger.info(f"Snapshot SHA-256: {snapshot_sha256}")
    return manifest_data


def restore_snapshot(force_reingest: bool = False) -> bool:
    """
    Restores the Qdrant local storage from the snapshot archive.
    If the snapshot is missing or force_reingest is requested, runs the deterministic ingestion pipeline.
    """
    if force_reingest or not SNAPSHOT_ARCHIVE.exists():
        logger.info("Snapshot archive missing or re-ingest requested. Re-running knowledge ingest from guideline sources...")
        from src.agent.knowledge_ingest import run_ingest
        run_ingest()
        return True

    # Verify checksum if manifest exists
    if MANIFEST_FILE.exists():
        with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        expected_sha = manifest.get("snapshot", {}).get("sha256")
        actual_sha = compute_sha256(SNAPSHOT_ARCHIVE)
        if expected_sha and actual_sha != expected_sha:
            raise ValueError(f"Snapshot checksum mismatch! Expected: {expected_sha}, Actual: {actual_sha}")
        logger.info(f"Snapshot checksum verified: {actual_sha}")

    logger.info(f"Restoring Qdrant storage from {SNAPSHOT_ARCHIVE} to {VECTOR_STORE_DIR}...")
    with tarfile.open(SNAPSHOT_ARCHIVE, "r:gz") as tar:
        tar.extractall(path=VECTOR_STORE_DIR)

    logger.info("[✓] Qdrant storage successfully restored.")
    return True


def verify_integrity() -> bool:
    """Verifies the integrity of guidelines, vector storage, and snapshot."""
    if not MANIFEST_FILE.exists():
        logger.error(f"Manifest file {MANIFEST_FILE} not found.")
        return False

    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    all_ok = True
    # Verify guidelines
    for item in manifest.get("source_guidelines", []):
        fpath = ROOT_DIR / item["relative_path"]
        if not fpath.exists():
            logger.error(f"Missing guideline file: {fpath}")
            all_ok = False
            continue
        cur_hash = compute_sha256(fpath)
        if cur_hash != item["sha256"]:
            logger.error(f"Checksum mismatch for {fpath.name}: expected {item['sha256']}, got {cur_hash}")
            all_ok = False
        else:
            logger.info(f"[✓] Guideline verified: {fpath.name}")

    # Verify snapshot if exists
    if SNAPSHOT_ARCHIVE.exists():
        cur_snap_hash = compute_sha256(SNAPSHOT_ARCHIVE)
        expected_snap_hash = manifest.get("snapshot", {}).get("sha256")
        if cur_snap_hash == expected_snap_hash:
            logger.info(f"[✓] Snapshot archive verified: {SNAPSHOT_ARCHIVE.name}")
        else:
            logger.error(f"Snapshot archive checksum mismatch: expected {expected_snap_hash}, got {cur_snap_hash}")
            all_ok = False

    return all_ok


def main():
    parser = argparse.ArgumentParser(description="Qdrant Snapshot and Restore Manager for M-CDSS")
    parser.add_argument("action", choices=["create", "restore", "verify"], help="Action to execute")
    parser.add_argument("--force-reingest", action="store_true", help="Force re-ingestion from raw guidelines on restore")
    args = parser.parse_args()

    if args.action == "create":
        create_snapshot()
    elif args.action == "restore":
        restore_snapshot(force_reingest=args.force_reingest)
    elif args.action == "verify":
        ok = verify_integrity()
        if not ok:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
