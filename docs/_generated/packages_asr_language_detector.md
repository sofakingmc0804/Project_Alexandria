# app.packages.asr.language_detector

Language detector for transcripts.

Detects language from transcript text using langdetect.
Updates manifest with detected language.

## Members
- Path(*args, **kwargs)
- detect_language(text: str) -> tuple[str, float]
- process_job(job_dir: pathlib._local.Path) -> bool
