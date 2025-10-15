#!/usr/bin/env python3
"""Language detector for transcripts.

Detects language from transcript text using langdetect.
Updates manifest with detected language.
"""

import json
import sys
from pathlib import Path

# Try to import langdetect
try:
    from langdetect import detect, detect_langs
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    print(" langdetect not installed, defaulting to 'en'", file=sys.stderr)


def detect_language(text: str) -> tuple[str, float]:
    """Detect language from text.
    
    Args:
        text: Text to analyze
        
    Returns:
        (language_code, confidence)
    """
    if not LANGDETECT_AVAILABLE:
        return 'en', 1.0
    
    try:
        langs = detect_langs(text)
        if langs:
            return langs[0].lang, langs[0].prob
        return 'en', 0.0
    except Exception as e:
        print(f" Language detection error: {e}", file=sys.stderr)
        return 'en', 0.0


def process_job(job_dir: Path) -> bool:
    """Detect language from transcript and update manifest.
    
    Args:
        job_dir: Job directory containing manifest.json and transcript
        
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
    
    # Get transcript path
    if 'transcript' not in manifest:
        print(f" No transcript in manifest. Run transcriber first.", file=sys.stderr)
        return False
    
    transcript_path = Path(manifest['transcript']['json_path'])
    
    if not transcript_path.exists():
        print(f" Transcript not found: {transcript_path}", file=sys.stderr)
        return False
    
    # Load transcript
    with open(transcript_path, 'r', encoding='utf-8') as f:
        transcript_data = json.load(f)
    
    # Extract text from segments
    text = ' '.join(seg['text'] for seg in transcript_data.get('segments', []))
    
    if not text.strip():
        print(f" Empty transcript", file=sys.stderr)
        return False
    
    # Detect language
    lang, confidence = detect_language(text)
    
    print(f" Detected language: {lang} (confidence: {confidence:.2f})")
    
    # Update manifest
    manifest['metadata']['language'] = lang
    manifest['language_detection'] = {
        'language': lang,
        'confidence': confidence
    }
    
    # Also update transcript data
    transcript_data['language'] = lang
    with open(transcript_path, 'w', encoding='utf-8') as f:
        json.dump(transcript_data, f, indent=2)
    
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    print(f" Updated manifest with language: {lang}")
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Detect language from transcript")
    parser.add_argument("--job", type=Path, required=True,
                       help="Job directory containing manifest.json")
    
    args = parser.parse_args()
    
    success = process_job(args.job)
    sys.exit(0 if success else 1)
