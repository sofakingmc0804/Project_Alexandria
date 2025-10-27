"""Regression tests for the RAG indexing and auditing pipeline."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from app.packages.rag_audit import auditor, source_indexer


class FakeModel:
    name_or_path = "unit-test-encoder"

    def encode(self, texts, normalize_embeddings=True, show_progress_bar=False, convert_to_numpy=True):
        vectors = []
        for text in texts:
            tokens = text.lower().split()
            length = len(tokens)
            checksum = sum(ord(ch) for ch in text) % 1000
            unique = len(set(tokens))
            vec = np.array([length, checksum, unique, 1.0], dtype=np.float32)
            vec = vec / np.linalg.norm(vec)
            vectors.append(vec)
        result = np.stack(vectors)
        if convert_to_numpy:
            return result
        return result.tolist()


def test_rag_pipeline_with_real_embeddings(tmp_path, monkeypatch):
    sources_dir = tmp_path / "sources"
    sources_dir.mkdir()
    source_text = "Machine learning fundamentals require careful data preparation and evaluation."
    (sources_dir / "source.txt").write_text(source_text, encoding="utf-8")

    job_dir = tmp_path / "job"
    job_dir.mkdir()
    script_content = "## Chapter 1\nAlex: Machine learning fundamentals require careful data preparation."  # shares wording
    (job_dir / "script.md").write_text(script_content, encoding="utf-8")

    config = {
        "embed_model": "unit-test",
        "embed_device": "cpu",
        "db": "faiss",
        "db_path": str(tmp_path / "index_store"),
        "retrieval": {"top_k": 3, "min_score": -1.0},
        "quality": {"min_groundedness": 0.4},
    }

    monkeypatch.setattr(source_indexer, "load_config", lambda *_args, **_kwargs: config)
    monkeypatch.setattr(source_indexer, "load_embedding_model", lambda _cfg: FakeModel())

    metadata = source_indexer.index_sources(
        sources_dir=str(sources_dir),
        config_path="ignored",
        job_dir=str(job_dir),
    )
    assert metadata["num_sources"] == 1
    assert (Path(config["db_path"]) / "sources_embeddings.npy").exists()

    monkeypatch.setattr(auditor, "load_config", lambda *_args, **_kwargs: config)
    monkeypatch.setattr(auditor, "load_embedding_model", lambda _cfg: FakeModel())

    report = auditor.audit_job(str(job_dir))
    assert report["passed"], "Audit should pass with overlapping content"
    assert report["avg_groundedness"] >= config["quality"]["min_groundedness"]
