"""Regression tests for the Phase 2 embedding indexer."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from app.packages.embed import indexer


def _write_segments(job_dir: Path) -> None:
    segments = {
        "job_id": job_dir.name,
        "segments": [
            {"id": "seg-1", "embedding": (np.ones(8) / np.sqrt(8)).tolist()},
            {"id": "seg-2", "embedding": (np.arange(8) / np.linalg.norm(np.arange(8))).tolist()},
        ],
        "embedding_model": "unit-test",
        "embedding_dim": 8,
    }
    (job_dir / "segments_embedded.json").write_text(json.dumps(segments), encoding="utf-8")


def test_indexer_writes_metadata(tmp_path):
    job_dir = tmp_path / "job"
    job_dir.mkdir()
    _write_segments(job_dir)

    metadata = indexer.build_and_save_index(str(job_dir))

    meta_path = job_dir / "index_metadata.json"
    assert meta_path.exists()

    payload = json.loads(meta_path.read_text(encoding="utf-8"))
    assert payload["num_vectors"] == 2
    assert payload["dimension"] == 8

    if metadata["index_type"] == "faiss":
        assert (job_dir / "index.faiss").exists()
    else:
        assert metadata["index_type"] == "numpy"
        assert (job_dir / "index.npy").exists()
