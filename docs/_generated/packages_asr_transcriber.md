# app.packages.asr.transcriber

ASR transcriber using faster-whisper.

Transcribes normalized audio to text with word-level timestamps.
Outputs both SRT and JSON formats.

## Members
- Path(*args, **kwargs)
- format_timestamp_srt(seconds: float) -> str
- process_job(job_dir: pathlib._local.Path, model_name: str = 'large-v3') -> bool
- timedelta()
- transcribe_audio(audio_path: pathlib._local.Path, model_name: str = 'large-v3', device: str = 'cpu') -> tuple[typing.List[typing.Dict], typing.List[typing.Dict]]
- write_srt(segments: List[Dict], output_path: pathlib._local.Path) -> None
