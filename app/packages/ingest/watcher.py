#!/usr/bin/env python3
"""Input file watcher and manifest generator.

Scans /inputs directory for audio/video files, validates formats,
and creates initial manifest.json for processing pipeline.
"""

import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Supported input formats per SPEC.md
SUPPORTED_FORMATS = {'.mp3', '.wav', '.m4a', '.mp4', '.mpeg', '.mpg'}
MAX_FILE_SIZE = 5 * 1024 * 1024 * 1024  # 5GB limit


def compute_checksum(file_path: Path) -> str:
    """Compute SHA256 checksum of file."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def validate_file(file_path: Path) -> tuple[bool, Optional[str]]:
    """Validate input file format and size.
    
    Returns:
        (is_valid, error_message)
    """
    # Check file exists
    if not file_path.exists():
        return False, f"File not found: {file_path}"
    
    # Check format
    if file_path.suffix.lower() not in SUPPORTED_FORMATS:
        return False, f"Unsupported format: {file_path.suffix}. Supported: {', '.join(SUPPORTED_FORMATS)}"
    
    # Check size
    size = file_path.stat().st_size
    if size > MAX_FILE_SIZE:
        return False, f"File too large: {size / (1024**3):.2f} GB (max 5 GB)"
    
    if size == 0:
        return False, "File is empty"
    
    return True, None


def create_manifest(input_file: Path, job_id: str, output_dir: Path) -> Dict:
    """Create initial manifest for processing job.
    
    Args:
        input_file: Path to input audio/video file
        job_id: Unique job identifier
        output_dir: Directory to write manifest
        
    Returns:
        Manifest dictionary
    """
    checksum = compute_checksum(input_file)
    size = input_file.stat().st_size
    
    manifest = {
        "job_id": job_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "input_file": {
            "path": str(input_file),
            "filename": input_file.name,
            "size_bytes": size,
            "checksum_sha256": checksum,
            "format": input_file.suffix.lower().lstrip('.')
        },
        "status": "ingested",
        "pipeline_stage": "ingest",
        "files": [],
        "metadata": {
            "title": input_file.stem,
            "language": None,  # To be populated by language detector
            "persona": None,
            "mix_profile": None,
            "total_duration_seconds": None
        },
        "qc_metrics": {
            "passed": False
        },
        "config": {}
    }
    
    # Write manifest to output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "manifest.json"
    
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    print(f" Created manifest: {manifest_path}")
    print(f"  Job ID: {job_id}")
    print(f"  Input: {input_file.name}")
    print(f"  Size: {size / (1024**2):.2f} MB")
    print(f"  Checksum: {checksum[:16]}...")
    
    return manifest


def scan_inputs(inputs_dir: Path = None, tmp_dir: Path = None) -> List[Dict]:
    """Scan inputs directory and create manifests for new files.
    
    Args:
        inputs_dir: Directory containing input files (default: ./inputs)
        tmp_dir: Temporary directory for job workspaces (default: ./tmp)
        
    Returns:
        List of created manifests
    """
    if inputs_dir is None:
        inputs_dir = Path("inputs")
    if tmp_dir is None:
        tmp_dir = Path("tmp")
    
    if not inputs_dir.exists():
        print(f" Inputs directory not found: {inputs_dir}")
        return []
    
    manifests = []
    
    # Find all audio/video files
    input_files = []
    for ext in SUPPORTED_FORMATS:
        input_files.extend(inputs_dir.glob(f"*{ext}"))
    
    if not input_files:
        print(f"No input files found in {inputs_dir}")
        return []
    
    print(f"Found {len(input_files)} input file(s)")
    
    for input_file in sorted(input_files):
        # Validate file
        is_valid, error = validate_file(input_file)
        if not is_valid:
            print(f" Skipping {input_file.name}: {error}")
            continue
        
        # Generate job ID from filename + timestamp
        job_id = f"{input_file.stem}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        job_dir = tmp_dir / job_id
        
        # Check if already processed
        manifest_path = job_dir / "manifest.json"
        if manifest_path.exists():
            print(f" Manifest already exists for {input_file.name}, skipping")
            continue
        
        # Create manifest
        try:
            manifest = create_manifest(input_file, job_id, job_dir)
            manifests.append(manifest)
        except Exception as e:
            print(f" Error creating manifest for {input_file.name}: {e}")
            continue
    
    return manifests


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Scan inputs and create manifests")
    parser.add_argument("--inputs", type=Path, default=Path("inputs"),
                       help="Input directory (default: ./inputs)")
    parser.add_argument("--tmp", type=Path, default=Path("tmp"),
                       help="Temporary directory (default: ./tmp)")
    parser.add_argument("--file", type=Path,
                       help="Process single file instead of scanning directory")
    
    args = parser.parse_args()
    
    if args.file:
        # Process single file
        is_valid, error = validate_file(args.file)
        if not is_valid:
            print(f" Invalid file: {error}", file=sys.stderr)
            sys.exit(1)
        
        job_id = f"{args.file.stem}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        job_dir = args.tmp / job_id
        
        try:
            create_manifest(args.file, job_id, job_dir)
            sys.exit(0)
        except Exception as e:
            print(f" Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Scan directory
        manifests = scan_inputs(args.inputs, args.tmp)
        
        if manifests:
            print(f"\n Created {len(manifests)} manifest(s)")
            sys.exit(0)
        else:
            print("\n No manifests created")
            sys.exit(1)
