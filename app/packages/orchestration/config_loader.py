"""Load orchestration configuration for Celery and FastAPI."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Mapping, Optional

import yaml


@dataclass(frozen=True)
class TaskSpec:
    name: str
    module: str
    callable: str
    queue: str = "default"
    description: Optional[str] = None


@dataclass(frozen=True)
class ApiRouteSpec:
    name: str
    path: str
    method: str
    task: str


@dataclass(frozen=True)
class OrchestrationConfig:
    tasks: Dict[str, TaskSpec]
    routes: Iterable[ApiRouteSpec]


def load_orchestration_config(path: Path | None = None) -> OrchestrationConfig:
    config_path = path or Path("configs/orchestration.yaml")
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}

    task_specs: Dict[str, TaskSpec] = {}
    for task_name, task_payload in (data.get("tasks") or {}).items():
        task_specs[task_name] = TaskSpec(
            name=task_name,
            module=task_payload["module"],
            callable=task_payload["callable"],
            queue=task_payload.get("queue", "default"),
            description=task_payload.get("description"),
        )

    routes = [
        ApiRouteSpec(
            name=route_payload.get("name", route_payload["task"]),
            path=route_payload["path"],
            method=route_payload.get("method", "POST").upper(),
            task=route_payload["task"],
        )
        for route_payload in (data.get("api", {}).get("routes") or [])
    ]

    return OrchestrationConfig(tasks=task_specs, routes=routes)


__all__ = ["TaskSpec", "ApiRouteSpec", "OrchestrationConfig", "load_orchestration_config"]