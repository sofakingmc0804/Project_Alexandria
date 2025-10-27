"""Tests for Celery app orchestration."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.apps.worker import celery_app as celery_module


def test_phase5_task_registration(monkeypatch):
    task_name = celery_module.REGISTERED_TASKS["phase5_pipeline"]
    task = celery_module.celery_app.tasks[task_name]

    captured = {}

    def fake_run(**kwargs):
        captured.update(kwargs)
        return {"received": kwargs}

    task.run = fake_run

    result = task.apply(kwargs={"script_path": "a", "stems_dir": "b", "mix_path": "c", "export_dir": "d", "notes_path": "e"})

    assert result.result == {"received": captured}


def test_register_missing_task(monkeypatch):
    with pytest.raises(KeyError):
        celery_module.REGISTERED_TASKS["not_there"]