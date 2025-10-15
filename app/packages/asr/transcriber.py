#!/usr/bin/env python3
"""ASR transcriber using faster-whisper.

Transcribes normalized audio to text with word-level timestamps.
Outputs both SRT and JSON formats.
"""

import json
import sys
from datetime import timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Try to import faster-whisper, gracefully degrade if not available
try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print(" faster-whisper not installed, using mock transcription", file=sys.stderr)


def format_timestamp_srt(seconds: float) -> str:
    """Format timestamp for SRT format (HH:MM:SS,mmm)."""
    td = timedelta(seconds=seconds)
    hours = int(td.total_seconds() // 3600)
    minutes = int((td.total_seconds() % 3600) // 60)
    secs = int(td.total_seconds() % 60)
    millis = int((td.total_seconds() % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def write_srt(segments: List[Dict], output_path: Path) -> None:
    """Write segments to SRT file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, seg in enumerate(segments, 1):
            f.write(f"{i}\n")
            f.write(f"{format_timestamp_srt(seg['start'])} --> {format_timestamp_srt(seg['end'])}\n")
            f.write(f"{seg['text'].strip()}\n")
            f.write("\n")


def transcribe_audio(audio_path: Path, model_name: str = "large-v3", 
                     device: str = "cpu") -> tuple[List[Dict], List[Dict]]:
    """Transcribe audio using faster-whisper.
    
    Args:
        audio_path: Path to audio file (WAV 16kHz mono)
        model_name: Whisper model size
        device: Device to use (cpu, cuda)
        
    Returns:
        (segments, words) - Lists of segment and word dictionaries
    """
    if not WHISPER_AVAILABLE:
        # Mock transcription for testing
        return (
            [{
                'id': 0,
                'start': 0.0,
                'end': 5.0,
                'text': 'Mock transcription - install faster-whisper for real ASR',
                'words': []
            }],
            [{
                'word': 'Mock',
                'start': 0.0,
                'end': 0.5,
                'probability': 1.0
            }]
        )
    
    print(f"Loading Whisper model: {model_name}")
    model = WhisperModel(model_name, device=device, compute_type="int8")
    
    print(f"Transcribing: {audio_path.name}")
    segments_result, info = model.transcribe(
        str(audio_path),
        beam_size=5,
        word_timestamps=True,
        vad_filter=True
    )
    
    print(f"Detected language: {info.language} (probability: {info.language_probability:.2f})")
    
    segments = []
    all_words = []
    
    for seg in segments_result:
        seg_dict = {
            'id': seg.id,
            'start': seg.start,
            'end': seg.end,
            'text': seg.text,
            'words': []
        }
        
        if seg.words:
            for word in seg.words:
                word_dict = {
                    'word': word.word,
                    'start': word.start,
                    'end': word.end,
                    'probability': word.probability
                }
                seg_dict['words'].append(word_dict)
                all_words.append(word_dict)
        
        segments.append(seg_dict)
    
    return segments, all_words


def process_job(job_dir: Path, model_name: str = "large-v3") -> bool:
    """Transcribe audio from a job directory.
    
    Args:
        job_dir: Job directory containing manifest.json and normalized audio
        model_name: Whisper model to use
        
    Returns:
        True if successful
    """
    manifest_path = job_dir / "manifest.json"
    
    if not manifest_path.exists():
        print(f" Manifest not found: {manifest_path}", file=sys.stderr)
        return False
    
    # Load manifest
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    # Get normalized audio path
    if 'normalized_audio' not in manifest:
        print(f" No normalized audio in manifest. Run normalizer first.", file=sys.stderr)
        return False
    
    audio_path = Path(manifest['normalized_audio']['path'])
    
    if not audio_path.exists():
        print(f" Normalized audio not found: {audio_path}", file=sys.stderr)
        return False
    
    # Transcribe
    segments, words = transcribe_audio(audio_path, model_name)
    
    # Write outputs
    transcript_dir = job_dir / "transcript"
    transcript_dir.mkdir(parents=True, exist_ok=True)
    
    srt_path = transcript_dir / "transcript.srt"
    json_path = transcript_dir / "transcript.json"
    
    # Write SRT
    write_srt(segments, srt_path)
    print(f" Wrote SRT: {srt_path}")
    
    # Write JSON with word timestamps
    transcript_data = {
        'segments': segments,
        'words': words,
        'language': 'en',  # TODO: Extract from whisper info
        'duration': segments[-1]['end'] if segments else 0.0
    }
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(transcript_data, f, indent=2)
    print(f" Wrote JSON: {json_path}")
    
    # Update manifest
    manifest['pipeline_stage'] = 'transcribed'
    manifest['transcript'] = {
        'srt_path': str(srt_path),
        'json_path': str(json_path),
        'segments_count': len(segments),
        'words_count': len(words),
        'duration': transcript_data['duration']
    }
    
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    print(f" Transcribed {len(segments)} segments, {len(words)} words")
    
    return True


if __name__ == "__main__":
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description="Transcribe audio using faster-whisper")
    parser.add_argument("--job", type=Path,
                       help="Job directory containing manifest.json")
    parser.add_argument("--audio", type=Path,
                       help="Audio file to transcribe (direct mode)")
    parser.add_argument("--output", type=Path,
                       help="Output directory (direct mode)")
    parser.add_argument("--model", type=str,
                       default=os.environ.get('WHISPER_MODEL', 'large-v3'),
                       help="Whisper model (default: large-v3)")
    
    args = parser.parse_args()
    
    if args.job:
        # Process job mode
        success = process_job(args.job, args.model)
        sys.exit(0 if success else 1)
    elif args.audio and args.output:
        # Direct mode
        segments, words = transcribe_audio(args.audio, args.model)
        
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        srt_path = output_dir / "transcript.srt"
        json_path = output_dir / "transcript.json"
        
        write_srt(segments, srt_path)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({'segments': segments, 'words': words}, f, indent=2)
        
        print(f" Transcription complete: {len(segments)} segments")
        sys.exit(0)
    else:
        parser.print_help()
        print("\nError: Must specify either --job or both --audio and --output", file=sys.stderr)
        sys.exit(1)
