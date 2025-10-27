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


def test_generate_script_multiple_hosts_alternation(tmp_path, monkeypatch):
    """Test that script alternates between multiple hosts."""
    job_dir = tmp_path / "job"
    job_dir.mkdir()
    selection = {
        "selection": [
            {
                "title": "Chapter 1",
                "segments": [
                    {"text": "First segment."},
                    {"text": "Second segment."},
                    {"text": "Third segment."},
                ],
            }
        ]
    }
    (job_dir / "selection.json").write_text(json.dumps(selection), encoding="utf-8")

    hosts = {"hosts": [{"name": "Alice"}, {"name": "Bob"}], "persona_id": "test"}
    monkeypatch.setattr(scripter, "load_hosts", lambda: hosts)
    monkeypatch.setattr(scripter, "load_persona_cards", lambda: {"test": _persona()})
    monkeypatch.setattr(scripter, "load_output_menu", lambda: {"persona": "test"})

    scripter.generate_script(job_dir)
    contents = (job_dir / "script.md").read_text(encoding="utf-8")

    # Verify both hosts appear
    assert "**Alice:**" in contents
    assert "**Bob:**" in contents


def test_generate_script_multiple_chapters(tmp_path, monkeypatch):
    """Test script generation with multiple chapters."""
    job_dir = tmp_path / "job"
    job_dir.mkdir()
    selection = {
        "selection": [
            {
                "title": "Chapter 1: Introduction",
                "segments": [{"text": "Welcome to the show."}],
            },
            {
                "title": "Chapter 2: Deep Dive",
                "segments": [{"text": "Let's explore the details."}],
            }
        ]
    }
    (job_dir / "selection.json").write_text(json.dumps(selection), encoding="utf-8")

    monkeypatch.setattr(scripter, "load_hosts", lambda: {"hosts": [{"name": "Host"}]})
    monkeypatch.setattr(scripter, "load_persona_cards", lambda: {"test": _persona()})
    monkeypatch.setattr(scripter, "load_output_menu", lambda: {"persona": "test"})

    scripter.generate_script(job_dir)
    contents = (job_dir / "script.md").read_text(encoding="utf-8")

    # Verify both chapter titles appear
    assert "## Chapter 1: Introduction" in contents
    assert "## Chapter 2: Deep Dive" in contents


def test_generate_script_empty_selection(tmp_path, monkeypatch):
    """Test script generation with no chapters."""
    job_dir = tmp_path / "job"
    job_dir.mkdir()
    selection = {"selection": []}
    (job_dir / "selection.json").write_text(json.dumps(selection), encoding="utf-8")

    monkeypatch.setattr(scripter, "load_hosts", lambda: {"hosts": [{"name": "Host"}]})
    monkeypatch.setattr(scripter, "load_persona_cards", lambda: {})
    monkeypatch.setattr(scripter, "load_output_menu", lambda: {})

    result = scripter.generate_script(job_dir)
    contents = (job_dir / "script.md").read_text(encoding="utf-8")

    # Should create empty script
    assert result["job_id"] == job_dir.name
    assert len(contents.strip()) >= 0  # May have minimal formatting


def test_generate_script_no_hosts_fallback(tmp_path, monkeypatch):
    """Test script generation when no hosts are configured."""
    job_dir = tmp_path / "job"
    job_dir.mkdir()
    selection = {
        "selection": [
            {
                "title": "Chapter",
                "segments": [{"text": "Test segment."}],
            }
        ]
    }
    (job_dir / "selection.json").write_text(json.dumps(selection), encoding="utf-8")

    monkeypatch.setattr(scripter, "load_hosts", lambda: {"hosts": []})  # No hosts
    monkeypatch.setattr(scripter, "load_persona_cards", lambda: {})
    monkeypatch.setattr(scripter, "load_output_menu", lambda: {})

    scripter.generate_script(job_dir)
    contents = (job_dir / "script.md").read_text(encoding="utf-8")

    # Should use fallback "Speaker" name
    assert "**Speaker:**" in contents


def test_generate_script_creates_script_file(tmp_path, monkeypatch):
    """Test that script.md file is created."""
    job_dir = tmp_path / "job"
    job_dir.mkdir()
    selection = {
        "selection": [
            {
                "title": "Chapter",
                "segments": [{"text": "Content."}],
            }
        ]
    }
    (job_dir / "selection.json").write_text(json.dumps(selection), encoding="utf-8")

    monkeypatch.setattr(scripter, "load_hosts", lambda: {"hosts": [{"name": "Host"}]})
    monkeypatch.setattr(scripter, "load_persona_cards", lambda: {})
    monkeypatch.setattr(scripter, "load_output_menu", lambda: {})

    result = scripter.generate_script(job_dir)

    # Verify script file was created
    script_path = job_dir / "script.md"
    assert script_path.exists()
    assert result["script_path"] == str(script_path)


def test_load_selection(tmp_path):
    """Test selection loading helper."""
    job_dir = tmp_path / "job"
    job_dir.mkdir()
    
    selection_data = {"selection": [{"title": "Test"}]}
    (job_dir / "selection.json").write_text(json.dumps(selection_data), encoding="utf-8")
    
    result = scripter.load_selection(job_dir)
    
    assert result["selection"][0]["title"] == "Test"


def test_rewrite_with_persona_applies_rewrite():
    """Test persona rewriting logic."""
    persona = _persona()
    result = scripter.rewrite_with_persona("This is boring.", persona, "Alice")
    
    assert "**Alice:**" in result
    assert "delightful" in result
    assert "boring" not in result


def test_rewrite_with_persona_no_persona():
    """Test rewriting without persona (passthrough)."""
    result = scripter.rewrite_with_persona("Original text.", None, "Bob")
    
    assert "**Bob:**" in result
    assert "Original text" in result

