"""Tests for the async Phase 5 orchestrator utilities."""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from typer.testing import CliRunner

from app.packages.cli.cli_generated import app
from app.packages.worker import Phase5OrchestrationError, run_full_pipeline


REPO_ROOT = Path(__file__).resolve().parents[2]
HOSTS_CONFIG = REPO_ROOT / "configs" / "hosts.yaml"


@pytest.mark.asyncio
async def test_run_full_pipeline_generates_artifacts(tmp_path):
    script = tmp_path / "script.md"
    script.write_text("Alex: Hello world\nJordan: Another line", encoding="utf-8")

    stems_dir = tmp_path / "stems"
    mix_path = tmp_path / "mix.wav"
    export_dir = tmp_path / "export"
    notes_path = export_dir / "notes.md"

    segments = [
        {"id": "seg1", "start_ms": 0, "end_ms": 20000, "text": "Hello", "lang": "en"},
        {"id": "seg2", "start_ms": 20000, "end_ms": 40000, "text": "World", "lang": "en"},
    ]
    chapters = [
        {"id": "ch1", "title": "Intro", "start_ms": 0, "end_ms": 40000},
    ]

    artifacts = await run_full_pipeline(
        script_path=script,
        stems_dir=stems_dir,
        mix_path=mix_path,
        export_dir=export_dir,
        notes_path=notes_path,
        config_path=HOSTS_CONFIG,
        segments=segments,
        chapters=chapters,
    )

    assert len(artifacts.stems) == 2
    assert artifacts.mix_path.exists()
    assert (artifacts.export_dir / "output_mix.mp3").exists()
    assert (artifacts.export_dir / "output_mix.opus").exists()
    assert artifacts.notes_path.exists()
    assert artifacts.summary["segment_count"] == 2.0
    assert artifacts.summary["chapter_count"] == 1.0


@pytest.mark.asyncio
async def test_run_full_pipeline_invalid_segment_raises(tmp_path):
    script = tmp_path / "script.md"
    script.write_text("Alex: Hello world", encoding="utf-8")

    with pytest.raises(Phase5OrchestrationError):
        await run_full_pipeline(
            script_path=script,
            stems_dir=tmp_path / "stems",
            mix_path=tmp_path / "mix.wav",
            export_dir=tmp_path / "export",
            notes_path=tmp_path / "export" / "notes.md",
            config_path=HOSTS_CONFIG,
            segments=[{"id": "seg", "start_ms": 0, "end_ms": 1000, "text": "bad", "lang": "en"}],
        )


def test_cli_pipeline_command(tmp_path):
    script = tmp_path / "script.md"
    script.write_text("Alex: Hello world", encoding="utf-8")

    work_dir = tmp_path / "work"
    export_dir = tmp_path / "export"

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "pipeline",
            str(script),
            "--work-dir",
            str(work_dir),
            "--export-dir",
            str(export_dir),
            "--config",
            str(HOSTS_CONFIG),
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Phase 5 pipeline completed" in result.stdout
    assert (export_dir / "output_mix.mp3").exists()