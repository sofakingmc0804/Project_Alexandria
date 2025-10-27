# app.packages.exporters.notes_generator

Notes generator implemented with the shared pipeline base classes.

## Members
- NotesGeneratorStep()
- Path(*args, **kwargs)
- PipelineContext(job_id: 'str', work_dir: 'Path', config: 'ConfigT', params: 'MutableMapping[str, Any]' = <factory>) -> None
- PipelineStep()
- generate_notes(script_path: 'str | Path', notes_path: 'str | Path') -> 'Path'
