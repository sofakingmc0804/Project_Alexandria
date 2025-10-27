"""FastAPI entrypoint exposing orchestration routes."""

from __future__ import annotations

from typing import Any, Dict

from fastapi import Body, FastAPI, HTTPException, status

from app.apps.worker.celery_app import REGISTERED_TASKS, celery_app
from app.packages.orchestration import load_orchestration_config


app = FastAPI(title="Alexandria Orchestration API", version="0.1.0")
config = load_orchestration_config()


def _register_route(path: str, method: str, task_name: str, endpoint_name: str) -> None:
    async def handler(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
        if task_name not in REGISTERED_TASKS:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Task '{task_name}' is not registered")

        celery_task_name = REGISTERED_TASKS[task_name]
        result = celery_app.send_task(celery_task_name, kwargs=payload or {})
        return {"task_id": result.id, "status": getattr(result, "status", "SENT")}

    method_lower = method.lower()
    if method_lower == "post":
        app.post(path, name=endpoint_name)(handler)
    elif method_lower == "get":
        app.get(path, name=endpoint_name)(handler)
    else:
        raise ValueError(f"Unsupported method '{method}' for route '{path}'")


for route_spec in config.routes:
    _register_route(route_spec.path, route_spec.method, route_spec.task, route_spec.name)


__all__ = ["app"]