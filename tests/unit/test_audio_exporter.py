"""Tests ensuring audio exporter produces expected artifacts."""

import json

from app.packages.exporters import audio_exporter
from app.packages.mastering import mixer
from app.packages.tts import synthesizer


def _prepare_mix(tmp_path):
    stems_dir = tmp_path / "stems"
    stems_dir.mkdir()
    host = synthesizer.load_hosts_config()[0]
    synthesizer.synthesize_text("Hello", host, stems_dir / "stem0.wav")
    synthesizer.synthesize_text("World", host, stems_dir / "stem1.wav")

    mix_path = tmp_path / "mix.wav"
    mixer.mix_stems(stems_dir, mix_path)
    return mix_path


def test_export_audio_creates_expected_files(tmp_path):
    mix_path = _prepare_mix(tmp_path)
    export_dir = tmp_path / "export"

    audio_exporter.export_audio(mix_path, export_dir)

    mp3 = export_dir / "output_mix.mp3"
    opus = export_dir / "output_mix.opus"
    chapters_path = export_dir / "chapters.json"

    assert mp3.exists() and mp3.stat().st_size > 0
    assert opus.exists() and opus.stat().st_size > 0
    assert chapters_path.exists()

    chapters = json.loads(chapters_path.read_text(encoding="utf-8"))
    assert any(chapter["title"] == "Intro" for chapter in chapters)