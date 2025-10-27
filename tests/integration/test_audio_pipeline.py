"""Integration tests for the deterministic audio pipeline."""

from pathlib import Path

from app.packages.tts import synthesizer
from app.packages.mastering import mixer
from app.packages.exporters import audio_exporter, notes_generator


def test_pipeline_generates_mix_and_exports(tmp_path):
    script = tmp_path / "script.md"
    script.write_text("Alex: Hello\nJordan: Welcome to the show", encoding="utf-8")

    stems_dir = tmp_path / "stems"
    generated = synthesizer.synthesize_script(script, stems_dir)
    assert len(generated) == 2

    mix_path = tmp_path / "mix.wav"
    mixer.mix_stems(stems_dir, mix_path)
    assert mix_path.exists() and mix_path.stat().st_size > 0

    export_dir = tmp_path / "export"
    audio_exporter.export_audio(mix_path, export_dir)

    mp3_path = export_dir / "output_mix.mp3"
    opus_path = export_dir / "output_mix.opus"
    chapters_path = export_dir / "chapters.json"

    assert mp3_path.exists()
    assert opus_path.exists()
    assert chapters_path.exists()
    # Copies are direct; verify byte equality for determinism
    assert mp3_path.read_bytes() == mix_path.read_bytes()
    assert opus_path.read_bytes() == mix_path.read_bytes()

    notes_path = export_dir / "notes.md"
    notes_generator.generate_notes(script, notes_path)
    assert notes_path.exists()
    content = notes_path.read_text(encoding="utf-8")
    assert "Show Notes" in content