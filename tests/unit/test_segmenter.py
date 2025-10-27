"""Unit tests for the Phase 2 segmenter with Silero integration."""

from __future__ import annotations

import json
import math
import wave
from pathlib import Path
from typing import List

import numpy as np
import pytest

from app.packages.segment import segmenter
from app.packages.segment.vad import VadWindow


def _write_wave(path: Path, seconds: float = 2.0, freq: float = 220.0) -> None:
    sample_rate = 16000
    total_samples = int(sample_rate * seconds)
    t = np.linspace(0, seconds, total_samples, endpoint=False)
    data = (0.3 * np.sin(2 * math.pi * freq * t)).astype(np.float32)
    pcm = (data * 32767).astype(np.int16)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(pcm.tobytes())


def _write_transcript(job_dir: Path) -> None:
    transcript_dir = job_dir / "transcript"
    transcript_dir.mkdir(parents=True, exist_ok=True)
    segments: List[dict] = [
        {"id": "seg-1", "start": 0.0, "end": 50.0, "text": "Intro section."},
        {"id": "seg-2", "start": 50.0, "end": 110.0, "text": "Main topic continues."},
        {"id": "seg-3", "start": 110.0, "end": 150.0, "text": "Closing thoughts."},
    ]
    payload = {"segments": segments, "language": "en"}
    (transcript_dir / "transcript.json").write_text(json.dumps(payload), encoding="utf-8")


def _write_manifest(job_dir: Path, normalized_path: Path) -> None:
    manifest = {
        "job_id": job_dir.name,
        "pipeline_stage": "normalized",
        "normalized_audio": {
            "path": str(normalized_path),
            "sample_rate": 16000,
            "channels": 1,
            "format": "wav",
        },
    }
    (job_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


def test_segmenter_uses_vad_when_available(tmp_path, monkeypatch):
    job_dir = tmp_path / "job"
    job_dir.mkdir()
    audio_path = job_dir / "normalized" / "audio.wav"
    _write_wave(audio_path, seconds=3.0)
    _write_manifest(job_dir, audio_path)
    _write_transcript(job_dir)

    class FakeAdapter:
        def __init__(self):
            self.enabled = True

        def detect(self, audio, sample_rate):
            assert sample_rate == 16000
            assert len(audio) > 0
            return [
                VadWindow(start_ms=0.0, end_ms=60000.0),
                VadWindow(start_ms=60000.0, end_ms=130000.0),
            ]

    monkeypatch.setattr(segmenter, "SileroVadAdapter", lambda: FakeAdapter())

    result = segmenter.segment_audio(str(job_dir))
    segments = result["segments"]
    assert len(segments) == 2
    assert segments[0]["text"].startswith("Intro section")
    assert result["validation"]["passed"]


def test_segmenter_falls_back_without_vad(tmp_path, monkeypatch):
    job_dir = tmp_path / "job"
    job_dir.mkdir()
    audio_path = job_dir / "normalized" / "audio.wav"
    _write_wave(audio_path, seconds=3.0)
    _write_manifest(job_dir, audio_path)
    _write_transcript(job_dir)

    class DisabledAdapter:
        def __init__(self):
            self.enabled = False

    monkeypatch.setattr(segmenter, "SileroVadAdapter", lambda: DisabledAdapter())

    result = segmenter.segment_audio(str(job_dir))
    segments = result["segments"]
    # Fallback groups into at least one segment and keeps language metadata.
    assert segments
    assert all(seg["lang"] == "en" for seg in segments)
    assert result["validation"]["passed"]
