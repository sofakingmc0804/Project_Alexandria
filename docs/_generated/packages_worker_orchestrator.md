# app.packages.worker.orchestrator

Async orchestration utilities for the Phase 5 audio pipeline.

## Members
- Chapter(*, id: str, title: Annotated[str, MinLen(min_length=1)], start_ms: Annotated[int, Ge(ge=0)], end_ms: Annotated[int, Ge(ge=0)]) -> None
- Path(*args, **kwargs)
- Phase5Artifacts(stems: 'List[Path]', mix_path: 'Path', export_dir: 'Path', notes_path: 'Path', qc_report: 'Optional[QCReport]' = None, summary: 'dict[str, float]' = <factory>) -> None
- Phase5OrchestrationError()
- QCReport(*, job_id: str, timestamp: datetime.datetime, passed: bool, metrics: app.packages.models_generated.qc_model.QCMetric, issues: List[app.packages.models_generated.qc_model.QCIssue] = <factory>, recommendations: List[str] = <factory>) -> None
- Segment(*, id: str, start_ms: Annotated[float, Ge(ge=0)], end_ms: Annotated[float, Ge(ge=0)], text: Annotated[str, MinLen(min_length=1)], lang: Annotated[str, _PydanticGeneralMetadata(pattern='^[a-z]{2}(-[A-Z]{2})?$')], source_file: Optional[str] = None, speaker_id: Optional[str] = None, embedding_vector_ref: Optional[str] = None, confidence: Annotated[Optional[float], Ge(ge=0), Le(le=1)] = None) -> None
- ValidationError(title, line_errors, input_type='python', hide_input=False)
- dataclass(cls=None, /, *, init=True, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False, match_args=True, kw_only=False, slots=False, weakref_slot=False)
- export_derivatives(mix_path: 'Path', export_dir: 'Path') -> 'Path'
- field(*, default=<dataclasses._MISSING_TYPE object at 0x000001C6AC9F9FD0>, default_factory=<dataclasses._MISSING_TYPE object at 0x000001C6AC9F9FD0>, init=True, repr=True, hash=None, compare=True, metadata=None, kw_only=<dataclasses._MISSING_TYPE object at 0x000001C6AC9F9FD0>)
- generate_notes(script_path: 'Path', notes_path: 'Path') -> 'Path'
- generate_stems(script_path: 'Path', stems_dir: 'Path', config_path: 'Path') -> 'List[Path]'
- mix_audio(stems_dir: 'Path', output_mix: 'Path') -> 'Path'
- run_full_pipeline(script_path: 'Path', stems_dir: 'Path', mix_path: 'Path', export_dir: 'Path', notes_path: 'Path', *, config_path: 'Path' = WindowsPath('configs/hosts.yaml'), segments: 'Optional[Sequence[Segment | dict]]' = None, chapters: 'Optional[Sequence[Chapter | dict]]' = None, existing_qc_report: 'Optional[QCReport | dict]' = None) -> 'Phase5Artifacts'
