"""Tests for the writer scripter persona integration."""

from __future__ import annotations

import json
from pathlib import Path

from app.packages.writer import scripter
from app.packages.writer.persona_loader import PersonaCard


def _persona() -> PersonaCard:
    return PersonaCard(
        id="test_persona",
        display_name="Test Persona",
        voice_id="voice.primary",
        fallback_voice_id="voice.fallback",
        lexical_favor=("delightful",),
        lexical_avoid=("boring",),
        tone_traits=("friendly",),
        style_notes=None,
    )


def test_generate_script_applies_persona_rewrite(tmp_path, monkeypatch):
    job_dir = tmp_path / "job"
    job_dir.mkdir()
    selection = {
        "selection": [
            {
                "title": "Chapter",
                "segments": [
                    {"text": "This is a boring topic."},
                ],
            }
        ]
    }
    (job_dir / "selection.json").write_text(json.dumps(selection), encoding="utf-8")

    monkeypatch.setattr(scripter, "load_hosts", lambda: {"hosts": [{"name": "Alex"}], "persona_id": "test_persona"})
    monkeypatch.setattr(scripter, "load_persona_cards", lambda: {"test_persona": _persona()})
    monkeypatch.setattr(scripter, "load_output_menu", lambda: {"persona": "test_persona"})

    result = scripter.generate_script(job_dir)
    contents = (job_dir / "script.md").read_text(encoding="utf-8")

    assert "delightful topic" in contents
    assert result["job_id"] == job_dir.name


def test_generate_script_handles_missing_persona(tmp_path, monkeypatch):
    job_dir = tmp_path / "job"
    job_dir.mkdir()
    selection = {
        "selection": [
            {
                "title": "Chapter",
                "segments": [
                    {"text": "Nothing special."},
                ],
            }
        ]
    }
    (job_dir / "selection.json").write_text(json.dumps(selection), encoding="utf-8")

    monkeypatch.setattr(scripter, "load_hosts", lambda: {"hosts": [{"name": "Alex"}], "persona_id": "missing"})
    monkeypatch.setattr(scripter, "load_persona_cards", lambda: {})
    monkeypatch.setattr(scripter, "load_output_menu", lambda: {"persona": "missing"})

    scripter.generate_script(job_dir)
    contents = (job_dir / "script.md").read_text(encoding="utf-8")

    assert "Nothing special" in contents
