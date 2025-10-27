"""Celery application configured from orchestration YAML."""

from __future__ import annotations

import asyncio
import os
from importlib import import_module
from typing import Any, Callable

try:
    from celery import Celery  # type: ignore[import-not-found]
except ModuleNotFoundError:  # pragma: no cover - triggered in minimal test envs
    class _EagerResult:
        """Minimal stand-in for Celery AsyncResult when Celery is unavailable."""

        def __init__(self, result: Any):
            self.id = "eager"
            self.status = "SUCCESS"
            self.result = result

    class _TaskWrapper:
        def __init__(self, func: Callable[..., Any]):
            self.run = func

        def apply(self, args: tuple[Any, ...] | None = None, kwargs: dict[str, Any] | None = None) -> _EagerResult:
            args = args or ()
            kwargs = kwargs or {}
            return _EagerResult(self.run(*args, **kwargs))

    class Celery:  # type: ignore[override]
        """Very small subset of Celery interface used in tests."""

        def __init__(self, name: str):
            self.main = name
            self.conf: dict[str, Any] = {}
            self.tasks: dict[str, _TaskWrapper] = {}

        def task(self, name: str | None = None, queue: str | None = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
            def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
                _ = queue  # retain signature parity with real Celery
                task_name = name or func.__name__
                wrapper = _TaskWrapper(func)
                self.tasks[task_name] = wrapper
                return wrapper.run

            return decorator

        def send_task(
            self, name: str, args: tuple[Any, ...] | None = None, kwargs: dict[str, Any] | None = None
        ) -> _EagerResult:
            if name not in self.tasks:
                raise KeyError(f"Task {name} not registered")
            return self.tasks[name].apply(args=args, kwargs=kwargs)


from app.packages.orchestration import TaskSpec, load_orchestration_config


celery_app = Celery("alexandria")
celery_app.conf.update(
    broker_url=os.getenv("CELERY_BROKER_URL", "memory://"),
    result_backend=os.getenv("CELERY_RESULT_BACKEND", "cache+memory://"),
    task_always_eager=os.getenv("ALEXANDRIA_CELERY_EAGER", "1") == "1",
    task_eager_propagates=True,
)

config = load_orchestration_config()
REGISTERED_TASKS: dict[str, str] = {}


def _resolve_call(target_spec: TaskSpec) -> Callable[..., Any]:
    module = import_module(target_spec.module)
    target = getattr(module, target_spec.callable)
    if asyncio.iscoroutinefunction(target):

        def runner(**kwargs: Any) -> Any:
            return asyncio.run(target(**kwargs))

        return runner
    return target


for task_name, spec in config.tasks.items():
    runner = _resolve_call(spec)
    celery_task_name = f"alexandria.{task_name}"
    celery_app.task(name=celery_task_name, queue=spec.queue)(runner)
    REGISTERED_TASKS[task_name] = celery_task_name


__all__ = ["celery_app", "REGISTERED_TASKS"]