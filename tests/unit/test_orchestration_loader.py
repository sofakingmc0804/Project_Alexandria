"""Tests for the orchestration configuration loader."""

from __future__ import annotations

from pathlib import Path

import yaml

from app.packages.orchestration import load_orchestration_config


def test_load_orchestration_config(tmp_path):
    config_path = tmp_path / "orchestration.yaml"
    data = {
        "tasks": {
            "task_a": {"module": "pkg.mod", "callable": "fn", "queue": "alpha"}
        },
        "api": {
            "routes": [
                {"name": "route_a", "path": "/a", "method": "POST", "task": "task_a"}
            ]
        },
    }
    config_path.write_text(yaml.safe_dump(data), encoding="utf-8")

    config = load_orchestration_config(config_path)

    assert "task_a" in config.tasks
    spec = config.tasks["task_a"]
    assert spec.module == "pkg.mod"
    assert spec.callable == "fn"
    assert spec.queue == "alpha"

    route = next(iter(config.routes))
    assert route.path == "/a"
    assert route.method == "POST"
    assert route.task == "task_a"