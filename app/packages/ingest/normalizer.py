#!/usr/bin/env python3
"""Audio normalizer using ffmpeg.

Converts input audio/video to WAV 16kHz mono for pipeline processing.
Uses WSL ffmpeg on Windows for better compatibility.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Check if we should use WSL for audio processing (Windows)
USE_WSL = os.environ.get('USE_WSL_AUDIO', 'true').lower() == 'true' and sys.platform == 'win32'


def get_ffmpeg_command() -> str:
    """Get appropriate ffmpeg command for the platform."""
    if USE_WSL:
        return 'wsl'
    return 'ffmpeg'


def normalize_audio(input_path: Path, output_path: Path, sample_rate: int = 16000) -> bool:
    """Normalize audio to WAV 16kHz mono using ffmpeg.
    
    Args:
        input_path: Input audio/video file
        output_path: Output WAV file path
        sample_rate: Target sample rate (default: 16000)
        
    Returns:
        True if successful, False otherwise
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Build ffmpeg command
    if USE_WSL:
        # WSL path conversion
        wsl_input = str(input_path).replace('\\', '/')
        wsl_output = str(output_path).replace('\\', '/')
        
        cmd = [
            'wsl', 'bash', '-c',
            f"ffmpeg -i '{wsl_input}' -ar {sample_rate} -ac 1 -sample_fmt s16 '{wsl_output}' -y 2>&1"
        ]
    else:
        cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-ar', str(sample_rate),
            '-ac', '1',  # mono
            '-sample_fmt', 's16',  # 16-bit PCM
            str(output_path),
            '-y'  # overwrite
        ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            print(f" ffmpeg error: {result.stderr}", file=sys.stderr)
            return False
        
        if not output_path.exists():
            print(f" Output file not created: {output_path}", file=sys.stderr)
            return False
        
        size = output_path.stat().st_size
        print(f" Normalized: {input_path.name}  {output_path.name}")
        print(f"  Sample rate: {sample_rate} Hz")
        print(f"  Channels: mono")
        print(f"  Output size: {size / (1024**2):.2f} MB")
        
        return True
        
    except FileNotFoundError:
        print(f" ffmpeg not found. Install ffmpeg or enable WSL.", file=sys.stderr)
        return False
    except Exception as e:
        print(f" Error: {e}", file=sys.stderr)
        return False


def process_job(job_dir: Path, sample_rate: int = 16000) -> bool:
    """Process a job by normalizing its input audio.
    
    Args:
        job_dir: Job directory containing manifest.json
        sample_rate: Target sample rate
        
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
    
    input_file = Path(manifest['input_file']['path'])
    
    if not input_file.exists():
        print(f" Input file not found: {input_file}", file=sys.stderr)
        return False
    
    # Create normalized directory
    normalized_dir = job_dir / "normalized"
    output_file = normalized_dir / f"{input_file.stem}_normalized.wav"
    
    # Normalize
    success = normalize_audio(input_file, output_file, sample_rate)
    
    if success:
        # Update manifest
        manifest['pipeline_stage'] = 'normalized'
        manifest['normalized_audio'] = {
            'path': str(output_file),
            'sample_rate': sample_rate,
            'channels': 1,
            'format': 'wav',
            'size_bytes': output_file.stat().st_size
        }
        
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        print(f" Updated manifest: {manifest_path}")
    
    return success


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Normalize audio to WAV 16kHz mono")
    parser.add_argument("--job", type=Path,
                       help="Job directory containing manifest.json")
    parser.add_argument("--input", type=Path,
                       help="Input audio file (direct mode)")
    parser.add_argument("--output", type=Path,
                       help="Output WAV file (direct mode)")
    parser.add_argument("--sample-rate", type=int, default=16000,
                       help="Target sample rate (default: 16000)")
    
    args = parser.parse_args()
    
    if args.job:
        # Process job mode
        success = process_job(args.job, args.sample_rate)
        sys.exit(0 if success else 1)
    elif args.input and args.output:
        # Direct mode
        success = normalize_audio(args.input, args.output, args.sample_rate)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()
        print("\nError: Must specify either --job or both --input and --output", file=sys.stderr)
        sys.exit(1)
