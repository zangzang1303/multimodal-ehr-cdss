"""
Unit tests for data manifest generation & verification (Backlog 08 - Task 2.1)
"""

import json
from pathlib import Path
import pytest
import pandas as pd

from src.data_pipeline.manifest import (
    compute_sha256,
    generate_manifest,
    verify_manifest,
)

ROOT_DIR = Path(__file__).resolve().parents[1]


def test_compute_sha256(tmp_path):
    f = tmp_path / "sample.txt"
    f.write_text("hello world", encoding="utf-8")
    h1 = compute_sha256(f)
    assert len(h1) == 64
    assert h1 == compute_sha256(f)

    f2 = tmp_path / "sample2.txt"
    f2.write_text("hello world 2", encoding="utf-8")
    assert compute_sha256(f2) != h1


def test_verify_manifest_raises_on_missing_file(tmp_path):
    fake_manifest = tmp_path / "DATA_MANIFEST.json"
    fake_manifest.write_text(json.dumps({
        "splits": {
            "test": {"path": "data/processed_rebuilt_strict/test.parquet", "sha256": "dummy", "row_count": 100, "class_distribution": {}}
        }
    }), encoding="utf-8")

    empty_dir = tmp_path / "empty_dir"
    empty_dir.mkdir()

    with pytest.raises(RuntimeError) as exc_info:
        verify_manifest(data_dir=empty_dir, manifest_path=fake_manifest)
    assert "Split file missing" in str(exc_info.value)


def test_verify_manifest_raises_on_hash_mismatch(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    df = pd.DataFrame({"diagnosis_label": [0, 1, 2, 3]})
    df.to_parquet(data_dir / "test.parquet", index=False)

    fake_manifest = tmp_path / "DATA_MANIFEST.json"
    fake_manifest.write_text(json.dumps({
        "splits": {
            "test": {"path": "test.parquet", "sha256": "bad_hash_12345", "row_count": 4, "class_distribution": {"0": 1, "1": 1, "2": 1, "3": 1}}
        }
    }), encoding="utf-8")

    with pytest.raises(RuntimeError) as exc_info:
        verify_manifest(data_dir=data_dir, manifest_path=fake_manifest)
    assert "Checksum mismatch" in str(exc_info.value)
