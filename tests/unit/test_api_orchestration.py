"""Tests for FastAPI orchestration endpoints."""

from __future__ import annotations

from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.apps.api import main as api_main


def test_phase5_route_dispatch(monkeypatch):
    called = {}

    def fake_send_task(name, kwargs=None, **extra):
        called["name"] = name
        called["kwargs"] = kwargs
        return SimpleNamespace(id="task-123", status="SUCCESS")

    monkeypatch.setattr(api_main, "celery_app", SimpleNamespace(send_task=fake_send_task))
    monkeypatch.setattr(api_main, "REGISTERED_TASKS", {"phase5_pipeline": "alexandria.phase5_pipeline"})

    client = TestClient(api_main.app)
    response = client.post("/jobs/phase5", json={"script_path": "s"})

    assert response.status_code == 200
    assert called["name"] == "alexandria.phase5_pipeline"
    assert called["kwargs"] == {"script_path": "s"}