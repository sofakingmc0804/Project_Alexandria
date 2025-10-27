"""Integration tests covering the planner → writer → continuity chain."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.packages.continuity import checker
from app.packages.planner import outliner, selector
from app.packages.writer import scripter


@pytest.fixture()
def planner_job(tmp_path) -> Path:
    job_dir = tmp_path / "job"
    job_dir.mkdir()

    segments = {
        "job_id": job_dir.name,
        "segments": [
            {"id": "s1", "start_ms": 0.0, "end_ms": 40000.0, "text": "Intro block."},
            {"id": "s2", "start_ms": 40000.0, "end_ms": 85000.0, "text": "Deep dive material."},
            {"id": "s3", "start_ms": 85000.0, "end_ms": 120000.0, "text": "Closing remarks."},
        ],
    }
    (job_dir / "segments.json").write_text(json.dumps(segments), encoding="utf-8")

    graph = {
        "duplicates": [],
    }
    (job_dir / "graph.json").write_text(json.dumps(graph), encoding="utf-8")

    return job_dir


def test_planner_pipeline_generates_script(planner_job, monkeypatch):
    job_dir = planner_job

    monkeypatch.setattr(outliner, "load_config", lambda _path='': {"target_duration_minutes": 6, "length_mode": "condensed"})
    outline = outliner.generate_outline(str(job_dir))
    assert outline["validation"]["passed"]
    assert outline["chapters"], "Chapters should be created"

    selection = selector.select_segments(str(job_dir))
    assert selection["num_selected"] == 3

    # Patch persona + hosts so the writer uses a predictable setup.
    monkeypatch.setattr(scripter, "load_hosts", lambda: {"hosts": [{"name": "Alex"}, {"name": "Jordan"}]})
    monkeypatch.setattr(scripter, "load_output_menu", lambda: {"persona": "conversational_educator"})
    monkeypatch.setattr(scripter, "load_persona_cards", lambda: {})

    script_info = scripter.generate_script(job_dir)
    script_path = Path(script_info["script_path"])
    content = script_path.read_text(encoding="utf-8")
    assert "Alex" in content and "Jordan" in content

    report = checker.check_continuity(job_dir)
    assert report["passed"]
    assert Path(job_dir / "continuity_report.json").is_file()
