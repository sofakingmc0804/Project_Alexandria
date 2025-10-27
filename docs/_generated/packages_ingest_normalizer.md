# app.packages.ingest.normalizer

Audio normalizer using ffmpeg.

Converts input audio/video to WAV 16kHz mono for pipeline processing.
Uses WSL ffmpeg on Windows for better compatibility.

## Members
- Path(*args, **kwargs)
- get_ffmpeg_command() -> str
- normalize_audio(input_path: pathlib._local.Path, output_path: pathlib._local.Path, sample_rate: int = 16000) -> bool
- process_job(job_dir: pathlib._local.Path, sample_rate: int = 16000) -> bool
