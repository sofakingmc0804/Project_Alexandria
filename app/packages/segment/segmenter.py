"""Segment creation utilities with Silero VAD support."""

from __future__ import annotations

import json
import uuid
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Dict, Any

import numpy as np

from app.packages.segment.vad import SileroVadAdapter, VadWindow


@dataclass
class TranscriptSegment:
    id: str
    start_ms: float
    end_ms: float
    text: str
    lang: str
    confidence: float


def load_transcript(transcript_json_path: str) -> Dict[str, Any]:
    """Load transcript JSON produced by the ASR step."""
    with open(transcript_json_path, 'r', encoding='utf-8') as handle:
        return json.load(handle)


def _transcript_segments(transcript: Dict[str, Any]) -> List[TranscriptSegment]:
    entries: List[TranscriptSegment] = []
    for raw in transcript.get('segments', []):
        entries.append(
            TranscriptSegment(
                id=str(raw.get('id') or uuid.uuid4()),
                start_ms=float(raw.get('start', 0.0) * 1000.0),
                end_ms=float(raw.get('end', 0.0) * 1000.0),
                text=raw.get('text', '').strip(),
                lang=transcript.get('language', raw.get('lang', 'en')),
                confidence=float(raw.get('confidence', 1.0)),
            )
        )
    return entries


def _load_normalized_audio(path: Path) -> tuple[np.ndarray, int]:
    with wave.open(str(path), 'rb') as wav:
        sample_rate = wav.getframerate()
        frames = wav.readframes(wav.getnframes())
        array = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
    return array, sample_rate


def _merge_transcript_into_windows(
    windows: Iterable[VadWindow],
    transcript_segments: List[TranscriptSegment],
    min_duration_s: float,
    max_duration_s: float,
    target_duration_s: float,
) -> List[Dict[str, Any]]:
    merged: List[Dict[str, Any]] = []

    for window in windows:
        candidates = [
            seg for seg in transcript_segments
            if seg.start_ms < window.end_ms and seg.end_ms > window.start_ms
        ]

        if not candidates:
            continue

        start_ms = min(seg.start_ms for seg in candidates)
        end_ms = max(seg.end_ms for seg in candidates)
        duration = (end_ms - start_ms) / 1000.0

        if duration < min_duration_s:
            end_ms = start_ms + min_duration_s * 1000.0
            duration = min_duration_s
        elif duration > max_duration_s:
            end_ms = start_ms + target_duration_s * 1000.0
            duration = target_duration_s

        text = ' '.join(seg.text for seg in candidates if seg.text)
        lang = candidates[0].lang
        confidence = min(seg.confidence for seg in candidates)

        merged.append({
            'id': str(uuid.uuid4()),
            'start_ms': start_ms,
            'end_ms': end_ms,
            'text': text.strip(),
            'lang': lang,
            'confidence': confidence,
        })

    return merged


def _group_transcript_segments(
    transcript_segments: List[TranscriptSegment],
    min_duration_s: float,
    max_duration_s: float,
    target_duration_s: float,
) -> List[Dict[str, Any]]:
    if not transcript_segments:
        return []

    output: List[Dict[str, Any]] = []
    current: List[TranscriptSegment] = []

    def flush() -> None:
        if not current:
            return
        start_ms = current[0].start_ms
        end_ms = current[-1].end_ms
        text = ' '.join(seg.text for seg in current if seg.text)
        duration_s = (end_ms - start_ms) / 1000.0
        if duration_s < min_duration_s and output:
            # Merge with previous segment if this one is too short.
            prev = output[-1]
            prev['end_ms'] = end_ms
            prev['text'] = (prev['text'] + ' ' + text).strip()
            prev['confidence'] = min(prev['confidence'], min(seg.confidence for seg in current))
        else:
            output.append({
                'id': str(uuid.uuid4()),
                'start_ms': start_ms,
                'end_ms': end_ms,
                'text': text.strip(),
                'lang': current[0].lang,
                'confidence': min(seg.confidence for seg in current),
            })
        current.clear()

    for seg in transcript_segments:
        if not current:
            current.append(seg)
            continue

        tentative_duration = (seg.end_ms - current[0].start_ms) / 1000.0
        if tentative_duration > max_duration_s:
            flush()
            current.append(seg)
        else:
            current.append(seg)

        # When we reach the target duration, emit and start a new one.
        if current:
            duration = (current[-1].end_ms - current[0].start_ms) / 1000.0
            if duration >= target_duration_s:
                flush()

    flush()
    return output


def create_segments_with_vad(
    transcript: Dict[str, Any],
    normalized_audio_path: Path | None,
    min_duration_s: float = 20.0,
    max_duration_s: float = 60.0,
    target_duration_s: float = 40.0,
) -> List[Dict[str, Any]]:
    transcript_segments = _transcript_segments(transcript)

    if normalized_audio_path is None or not normalized_audio_path.exists():
        return _group_transcript_segments(transcript_segments, min_duration_s, max_duration_s, target_duration_s)

    vad = SileroVadAdapter()
    if not vad.enabled:
        return _group_transcript_segments(transcript_segments, min_duration_s, max_duration_s, target_duration_s)

    audio, sample_rate = _load_normalized_audio(normalized_audio_path)
    windows = vad.detect(audio, sample_rate)
    if not windows:
        return _group_transcript_segments(transcript_segments, min_duration_s, max_duration_s, target_duration_s)

    merged = _merge_transcript_into_windows(
        windows,
        transcript_segments,
        min_duration_s,
        max_duration_s,
        target_duration_s,
    )

    if not merged:
        return _group_transcript_segments(transcript_segments, min_duration_s, max_duration_s, target_duration_s)

    return merged


def create_segments_from_transcript_fallback(
    transcript: Dict[str, Any],
    min_duration_s: float,
    max_duration_s: float,
    target_duration_s: float,
) -> List[Dict[str, Any]]:
    transcript_segments = _transcript_segments(transcript)
    return _group_transcript_segments(transcript_segments, min_duration_s, max_duration_s, target_duration_s)


def validate_segments(segments: List[Dict[str, Any]]) -> bool:
    """
    Validate that all segments meet duration requirements.
    
    Returns:
        True if all segments are valid, False otherwise
    """
    for seg in segments:
        duration_s = (seg['end_ms'] - seg['start_ms']) / 1000
        if duration_s < 15 or duration_s > 65:
            print(f"Warning: Segment {seg['id']} duration {duration_s:.1f}s outside 15-65s range")
            return False
    return True


def segment_audio(job_dir: str) -> Dict[str, Any]:
    """
    Main segmentation function.
    
    Args:
        job_dir: Path to job directory (e.g., tmp/input_sample_30s_20251015_041747)
    
    Returns:
        Dictionary with segments data and metadata
    """
    job_path = Path(job_dir)
    
    # Load manifest
    manifest_path = job_path / 'manifest.json'
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    # Load transcript
    transcript_path = job_path / 'transcript' / 'transcript.json'
    if not transcript_path.exists():
        raise FileNotFoundError(f"Transcript not found: {transcript_path}")
    
    transcript = load_transcript(str(transcript_path))

    normalized_audio_path = None
    normalized = manifest.get('normalized_audio')
    if normalized:
        normalized_audio_path = Path(normalized.get('path', ''))

    segments = create_segments_with_vad(
        transcript,
        normalized_audio_path,
        min_duration_s=20.0,
        max_duration_s=60.0,
        target_duration_s=40.0,
    )
    
    # Validate segments
    is_valid = validate_segments(segments)
    
    # Prepare output
    output = {
        'job_id': manifest['job_id'],
        'segments': segments,
        'segment_count': len(segments),
        'validation': {
            'passed': is_valid,
            'min_duration_s': 15,
            'max_duration_s': 65
        },
        'language': transcript.get('language', 'en')
    }
    
    # Save segments.json
    output_path = job_path / 'segments.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f" Created {len(segments)} segments")
    print(f" Saved to: {output_path}")
    print(f" Validation: {'PASSED' if is_valid else 'FAILED'}")
    
    return output


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python segmenter.py <job_dir>")
        print("Example: python segmenter.py tmp/input_sample_30s_20251015_041747")
        sys.exit(1)
    
    job_dir = sys.argv[1]
    result = segment_audio(job_dir)
    
    if not result['validation']['passed']:
        sys.exit(1)
