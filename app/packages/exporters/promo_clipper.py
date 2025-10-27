"""
Promo Clipper - Extracts highlight segments (30-90s) for promotional use
Selects segments based on length, text density, and position diversity
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any

def load_segments(job_dir: Path) -> List[Dict[str, Any]]:
    """Load segments from job directory"""
    seg_path = job_dir / 'segments.json'
    if not seg_path.exists():
        return []
    with open(seg_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('segments', [])

def score_segment_for_promo(seg: Dict[str, Any], position: int, total: int) -> float:
    """
    Score a segment for promo worthiness based on:
    - Duration (prefer 30-90s range)
    - Text density (more engaging content)
    - Position (favor intro, middle, conclusion)
    """
    duration_ms = seg['end_ms'] - seg['start_ms']
    duration_s = duration_ms / 1000.0

    # Duration score (prefer 30-90s)
    if 30 <= duration_s <= 90:
        dur_score = 1.0
    elif duration_s < 30:
        dur_score = duration_s / 30.0
    else:
        dur_score = max(0.3, 1.0 - (duration_s - 90) / 120.0)

    # Text density score (words per second)
    text = seg.get('text', '')
    word_count = len(text.split())
    wps = word_count / max(1, duration_s)
    text_score = min(1.0, wps / 3.0)  # Normalize to 3 wps = full score

    # Position score (favor intro 0-20%, middle 40-60%, end 80-100%)
    pos_ratio = position / max(1, total - 1)
    if pos_ratio < 0.2 or pos_ratio > 0.8:  # Intro or conclusion
        pos_score = 1.0
    elif 0.4 <= pos_ratio <= 0.6:  # Middle
        pos_score = 0.9
    else:
        pos_score = 0.6

    # Weighted combination
    return (dur_score * 0.4) + (text_score * 0.4) + (pos_score * 0.2)

def select_promo_segments(segments: List[Dict[str, Any]], count: int = 3) -> List[Dict[str, Any]]:
    """Select the best segments for promos, ensuring diversity"""
    if not segments:
        return []

    # Score all segments
    scored = []
    for i, seg in enumerate(segments):
        score = score_segment_for_promo(seg, i, len(segments))
        scored.append((score, i, seg))

    # Sort by score descending
    scored.sort(reverse=True, key=lambda x: x[0])

    # Select top N with position diversity
    selected = []
    selected_positions = []

    for score, pos, seg in scored:
        if len(selected) >= count:
            break

        # Ensure minimum 10 segments separation (if possible)
        if not selected_positions or all(abs(pos - p) >= 10 for p in selected_positions):
            selected.append(seg)
            selected_positions.append(pos)
        elif len(segments) < count * 10:
            # If dataset is small, be less strict
            selected.append(seg)
            selected_positions.append(pos)

    # If we couldn't get enough, just take top N
    while len(selected) < min(count, len(segments)):
        for score, pos, seg in scored:
            if seg not in selected:
                selected.append(seg)
                break

    return selected

def extract_promo_clips(job_dir: str, promo_count: int = 3):
    """Extract promo clips from job segments"""
    job_path = Path(job_dir)
    if not job_path.exists():
        print(f"Error: Job directory {job_dir} not found")
        sys.exit(1)

    segments = load_segments(job_path)
    if not segments:
        print("Warning: No segments found")
        return

    # Select best promo segments
    promo_segments = select_promo_segments(segments, promo_count)

    # Create promos directory
    promo_dir = job_path / 'promos'
    promo_dir.mkdir(parents=True, exist_ok=True)

    # Save promo metadata
    promos = []
    for i, seg in enumerate(promo_segments, 1):
        duration_s = (seg['end_ms'] - seg['start_ms']) / 1000.0
        promo_data = {
            'promo_id': f'promo_{i:02d}',
            'segment_id': seg['id'],
            'start_ms': seg['start_ms'],
            'end_ms': seg['end_ms'],
            'duration_seconds': round(duration_s, 2),
            'text': seg.get('text', ''),
            'transcript_file': f'promo_{i:02d}.txt',
            'audio_file': f'promo_{i:02d}.wav'
        }
        promos.append(promo_data)

        # Save transcript
        transcript_path = promo_dir / f'promo_{i:02d}.txt'
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(seg.get('text', ''))

        # Mock: Create placeholder audio (would normally extract from mix)
        audio_path = promo_dir / f'promo_{i:02d}.wav'
        audio_path.touch()
        print(f"Created promo {i}: {duration_s:.1f}s - {seg.get('text', '')[:60]}...")

    # Save promo manifest
    manifest = {
        'job_id': job_path.name,
        'promo_count': len(promos),
        'promos': promos
    }
    manifest_path = promo_dir / 'promo_manifest.json'
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    print(f"\nGenerated {len(promos)} promo clips in {promo_dir}")
    print(f"Manifest: {manifest_path}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python promo_clipper.py <job_dir> [promo_count]")
        print("Example: python promo_clipper.py tmp/test_job 3")
        sys.exit(1)

    job_dir = sys.argv[1]
    promo_count = int(sys.argv[2]) if len(sys.argv) > 2 else 3

    extract_promo_clips(job_dir, promo_count)
