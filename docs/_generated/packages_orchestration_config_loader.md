# app.packages.orchestration.config_loader

Load orchestration configuration for Celery and FastAPI.

## Members
- ApiRouteSpec(name: 'str', path: 'str', method: 'str', task: 'str') -> None
- OrchestrationConfig(tasks: 'Dict[str, TaskSpec]', routes: 'Iterable[ApiRouteSpec]') -> None
- Path(*args, **kwargs)
- TaskSpec(name: 'str', module: 'str', callable: 'str', queue: 'str' = 'default', description: 'Optional[str]' = None) -> None
- dataclass(cls=None, /, *, init=True, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False, match_args=True, kw_only=False, slots=False, weakref_slot=False)
- load_orchestration_config(path: 'Path | None' = None) -> 'OrchestrationConfig'
