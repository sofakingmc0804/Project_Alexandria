# app.packages.ingest.watcher

Input file watcher and manifest generator.

Scans /inputs directory for audio/video files, validates formats,
and creates initial manifest.json for processing pipeline.

## Members
- Path(*args, **kwargs)
- compute_checksum(file_path: pathlib._local.Path) -> str
- create_manifest(input_file: pathlib._local.Path, job_id: str, output_dir: pathlib._local.Path) -> Dict
- datetime()
- scan_inputs(inputs_dir: pathlib._local.Path = None, tmp_dir: pathlib._local.Path = None) -> List[Dict]
- validate_file(file_path: pathlib._local.Path) -> tuple[bool, typing.Optional[str]]
