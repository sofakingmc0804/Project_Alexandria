"""REM-020 tests covering Phase 1 ingestion mocks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from app.packages.asr import language_detector, transcriber
from app.packages.ingest import normalizer, watcher


def _write_dummy_audio(path: Path) -> None:
    """Write a tiny WAV-like payload just to create a non-empty file."""

    path.write_bytes(b"RIFF\x00\x00\x00\x00WAVEfmt ")


def _load_manifest(job_dir: Path) -> dict[str, Any]:
    return json.loads((job_dir / "manifest.json").read_text(encoding="utf-8"))


def _save_manifest(job_dir: Path, manifest: dict[str, Any]) -> None:
    (job_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def test_scan_inputs_creates_manifest(tmp_path, monkeypatch):
    inputs_dir = tmp_path / "inputs"
    tmp_dir = tmp_path / "tmp"
    inputs_dir.mkdir()

    audio_file = inputs_dir / "lesson.wav"
    _write_dummy_audio(audio_file)

    manifests = watcher.scan_inputs(inputs_dir, tmp_dir)

    assert len(manifests) == 1
    manifest = manifests[0]
    job_id = manifest["job_id"]

    manifest_path = tmp_dir / job_id / "manifest.json"
    assert manifest_path.is_file()

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert data["pipeline_stage"] == "ingest"
    assert data["input_file"]["filename"] == "lesson.wav"
    assert data["input_file"]["format"] == "wav"


def test_normalizer_process_job_updates_manifest(tmp_path, monkeypatch):
    input_file = tmp_path / "lesson.mp3"
    _write_dummy_audio(input_file)
    job_dir = tmp_path / "job-001"
    watcher.create_manifest(input_file, "job-001", job_dir)

    monkeypatch.setattr(normalizer, "USE_WSL", False)

    def fake_run(cmd, capture_output, text, check):
        output_path = Path(cmd[-2])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        _write_dummy_audio(output_path)

        class _Result:
            returncode = 0
            stderr = ""
            stdout = ""

        return _Result()

    monkeypatch.setattr(normalizer.subprocess, "run", fake_run)

    assert normalizer.process_job(job_dir)

    manifest = _load_manifest(job_dir)
    assert manifest["pipeline_stage"] == "normalized"
    normalized = Path(manifest["normalized_audio"]["path"])
    assert normalized.is_file()
    assert normalized.suffix == ".wav"


def test_transcriber_writes_outputs_and_updates_manifest(tmp_path, monkeypatch):
    job_dir = tmp_path / "job-002"
    job_dir.mkdir()
    input_file = tmp_path / "lesson.wav"
    _write_dummy_audio(input_file)
    watcher.create_manifest(input_file, "job-002", job_dir)

    normalized_dir = job_dir / "normalized"
    normalized_dir.mkdir()
    normalized_path = normalized_dir / "lesson_normalized.wav"
    _write_dummy_audio(normalized_path)

    manifest = _load_manifest(job_dir)
    manifest["pipeline_stage"] = "normalized"
    manifest["normalized_audio"] = {
        "path": str(normalized_path),
        "sample_rate": 16000,
        "channels": 1,
        "format": "wav",
        "size_bytes": normalized_path.stat().st_size,
    }
    _save_manifest(job_dir, manifest)

    monkeypatch.setattr(transcriber, "WHISPER_AVAILABLE", False)

    assert transcriber.process_job(job_dir)

    manifest = _load_manifest(job_dir)
    transcript_meta = manifest["transcript"]
    transcript_dir = Path(transcript_meta["json_path"]).parent

    assert manifest["pipeline_stage"] == "transcribed"
    assert (transcript_dir / "transcript.srt").is_file()
    transcript_json = json.loads((transcript_dir / "transcript.json").read_text(encoding="utf-8"))
    assert transcript_json["segments"]
    assert transcript_json["language"] == "en"


def test_language_detector_updates_manifest(tmp_path, monkeypatch):
    job_dir = tmp_path / "job-003"
    job_dir.mkdir()
    input_file = tmp_path / "lesson.wav"
    _write_dummy_audio(input_file)
    watcher.create_manifest(input_file, "job-003", job_dir)

    transcript_dir = job_dir / "transcript"
    transcript_dir.mkdir()
    transcript_json = {
        "segments": [{"text": "This is a mock transcript"}],
        "words": [],
        "language": "unknown",
        "duration": 5.0,
    }
    (transcript_dir / "transcript.json").write_text(json.dumps(transcript_json), encoding="utf-8")

    manifest = _load_manifest(job_dir)
    manifest["transcript"] = {
        "json_path": str(transcript_dir / "transcript.json"),
        "srt_path": str(transcript_dir / "transcript.srt"),
        "segments_count": 1,
        "words_count": 0,
        "duration": 5.0,
    }
    manifest["pipeline_stage"] = "transcribed"
    _save_manifest(job_dir, manifest)

    monkeypatch.setattr(language_detector, "LANGDETECT_AVAILABLE", False)

    assert language_detector.process_job(job_dir)

    manifest = _load_manifest(job_dir)
    assert manifest["metadata"]["language"] == "en"
    assert manifest["language_detection"]["language"] == "en"

