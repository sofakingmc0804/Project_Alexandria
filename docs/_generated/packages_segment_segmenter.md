# app.packages.segment.segmenter

packages/segment/segmenter.py

Uses silero-vad to detect speech segments and creates 20-60s chunks.
Falls back to simple silence detection if silero-vad unavailable.

## Members
- Any(*args, **kwargs)
- Path(*args, **kwargs)
- create_segments_from_transcript(transcript: Dict[str, Any], min_duration_s: float = 20.0, max_duration_s: float = 60.0, target_duration_s: float = 40.0) -> List[Dict[str, Any]]
- create_segments_from_transcript_fallback(transcript: Dict[str, Any], min_duration_s: float, max_duration_s: float, target_duration_s: float) -> List[Dict[str, Any]]
- load_transcript(transcript_json_path: str) -> Dict[str, Any]
- segment_audio(job_dir: str) -> Dict[str, Any]
- validate_segments(segments: List[Dict[str, Any]]) -> bool
