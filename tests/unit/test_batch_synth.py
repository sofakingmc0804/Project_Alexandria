"""Tests for the batch synthesizer orchestration module."""

import runpy
import sys

import pytest

from app.packages.tts import batch_synth


def test_synthesize_batch_generates_expected_files(tmp_path, capsys):
    script = tmp_path / "script.md"
    script.write_text("Alex: Hello world\nJordan: Another line", encoding="utf-8")

    stems_dir = tmp_path / "stems"
    result = batch_synth.synthesize_batch(str(script), str(stems_dir))

    captured = capsys.readouterr()
    assert "Batch synthesis complete" in captured.out
    assert len(result) == 2
    for path in result:
        assert path.exists()
        assert path.parent == stems_dir


def test_cli_missing_args_exits(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["batch_synth.py"])
    sys.modules.pop("app.packages.tts.batch_synth", None)
    with pytest.raises(SystemExit):
        runpy.run_module("app.packages.tts.batch_synth", run_name="__main__", alter_sys=True)

    captured = capsys.readouterr()
    assert "Usage:" in captured.out


def test_cli_invocation_generates_stems(tmp_path, monkeypatch):
    script = tmp_path / "script.md"
    script.write_text("Alex: Hi", encoding="utf-8")
    stems_dir = tmp_path / "stems"

    monkeypatch.setattr(sys, "argv", ["batch_synth.py", str(script), str(stems_dir)])
    sys.modules.pop("app.packages.tts.batch_synth", None)

    runpy.run_module("app.packages.tts.batch_synth", run_name="__main__", alter_sys=True)

    generated = list(stems_dir.glob("*.wav"))
    assert generated