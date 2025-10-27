"""Shared pipeline base classes for code-generated modules."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Generic, Mapping, MutableMapping, Optional, TypeVar

import yaml


ConfigT = TypeVar("ConfigT", bound=Mapping[str, Any])
InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")
FinalT = TypeVar("FinalT")


@dataclass(slots=True)
class PipelineContext(Generic[ConfigT]):
    """Execution context passed to pipeline steps."""

    job_id: str
    work_dir: Path
    config: ConfigT
    params: MutableMapping[str, Any] = field(default_factory=dict)


class PipelineStep(Generic[InputT, OutputT, FinalT]):
    """Template method base-class for structured pipeline steps."""

    config_path: Optional[Path] = None

    def load_config(self) -> Mapping[str, Any]:
        if self.config_path is None:
            return {}
        with self.config_path.expanduser().resolve().open("r", encoding="utf-8") as handle:
            loaded = yaml.safe_load(handle) or {}
        if not isinstance(loaded, Mapping):
            raise TypeError(f"Configuration at {self.config_path} must be a mapping, got {type(loaded)!r}")
        return loaded

    def init_context(
        self,
        *,
        job_id: str,
        work_dir: Optional[Path] = None,
        params: Optional[Mapping[str, Any]] = None,
    ) -> PipelineContext[Mapping[str, Any]]:
        resolved_work_dir = (work_dir or Path("tmp") / job_id).resolve()
        resolved_work_dir.mkdir(parents=True, exist_ok=True)
        context = PipelineContext(
            job_id=job_id,
            work_dir=resolved_work_dir,
            config=self.load_config(),
            params=dict(params or {}),
        )
        return context

    def run(
        self,
        *,
        job_id: str,
        input_data: InputT,
        work_dir: Optional[Path] = None,
        params: Optional[Mapping[str, Any]] = None,
    ) -> FinalT:
        context = self.init_context(job_id=job_id, work_dir=work_dir, params=params)
        processed = self.process(context, input_data)
        final = self.after_process(context, processed)
        return processed if final is None else final

    def process(self, context: PipelineContext[Mapping[str, Any]], input_data: InputT) -> OutputT:
        raise NotImplementedError

    def after_process(
        self,
        context: PipelineContext[Mapping[str, Any]],
        processed: OutputT,
    ) -> Optional[FinalT]:
        return None


__all__ = ["PipelineContext", "PipelineStep"]