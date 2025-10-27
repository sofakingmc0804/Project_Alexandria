# app.packages.knowledge.curator

Knowledge Curator - Manages source document ingestion
Copies files to sources_raw/, computes SHA256, detects language, updates catalog

## Members
- Path(*args, **kwargs)
- add_to_catalog(file_path: pathlib._local.Path, sha256: str, file_size: int, language: str, topic: str, status: str = 'raw') -> None
- compute_sha256(file_path: pathlib._local.Path) -> str
- curate_file(source_path: pathlib._local.Path, topic: str) -> bool
- datetime()
- detect_language_from_file(file_path: pathlib._local.Path) -> str
- main()
