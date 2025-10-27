"""Celery task handlers that bridge to pipeline orchestrators."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Mapping

from app.packages.worker.orchestrator import run_full_pipeline


async def _run_phase5_async(payload: Mapping[str, Any]) -> Any:
    script_path = Path(payload["script_path"]).resolve()
    stems_dir = Path(payload["stems_dir"]).resolve()
    mix_path = Path(payload["mix_path"]).resolve()
    export_dir = Path(payload["export_dir"]).resolve()
    notes_path = Path(payload["notes_path"]).resolve()
    config_path = Path(payload.get("config_path", "configs/hosts.yaml")).resolve()

    return await run_full_pipeline(
        script_path=script_path,
        stems_dir=stems_dir,
        mix_path=mix_path,
        export_dir=export_dir,
        notes_path=notes_path,
        config_path=config_path,
    )


def handle_phase5_pipeline(**payload: Any) -> Any:
    """Celery task entry point for the Phase 5 pipeline."""

    return asyncio.run(_run_phase5_async(payload))


__all__ = ["handle_phase5_pipeline"]