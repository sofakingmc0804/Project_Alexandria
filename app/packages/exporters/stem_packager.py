"""
Stem Packager - Copies per-speaker stems to export folder with Clipchamp naming
Provides stems in format: speaker_a_001.wav, speaker_b_001.wav, etc.
"""

import json
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Any

def load_script(job_dir: Path) -> str:
    """Load script to understand speaker assignments"""
    script_path = job_dir / 'script.md'
    if not script_path.exists():
        return ""
    with open(script_path, 'r', encoding='utf-8') as f:
        return f.read()

def extract_speakers_from_script(script: str) -> List[str]:
    """
    Extract unique speakers from script in order of appearance
    Looks for lines like **Speaker A:** or **Host:**
    """
    speakers = []
    for line in script.split('\n'):
        if line.startswith('**') and ':' in line:
            # Extract speaker name between ** and :
            speaker = line.split('**')[1].split(':')[0].strip()
            if speaker and speaker not in speakers:
                speakers.append(speaker)
    return speakers if speakers else ['Speaker A', 'Speaker B']

def package_stems(job_dir: str, export_dir: str = None):
    """
    Package stems from job directory to export location
    with Clipchamp-compatible naming
    """
    job_path = Path(job_dir)
    if not job_path.exists():
        print(f"Error: Job directory {job_dir} not found")
        sys.exit(1)

    # Determine export directory
    if export_dir:
        export_path = Path(export_dir)
    else:
        export_path = job_path.parent.parent / 'dist' / 'export' / job_path.name / 'stems'

    export_path.mkdir(parents=True, exist_ok=True)

    # Find stems directory
    stems_dir = job_path / 'stems'
    if not stems_dir.exists():
        print(f"Warning: Stems directory not found at {stems_dir}")
        print("Creating placeholder stems for demonstration...")
        stems_dir.mkdir(parents=True, exist_ok=True)
        # Create mock stems
        for i in range(2):
            (stems_dir / f'speaker_{chr(97+i)}_stem.wav').touch()

    # Load script to identify speakers
    script = load_script(job_path)
    speakers = extract_speakers_from_script(script)

    # Map speakers to letter identifiers
    speaker_map = {}
    for i, speaker in enumerate(speakers):
        letter = chr(97 + i)  # a, b, c, d...
        speaker_map[speaker] = letter

    print(f"Identified {len(speakers)} speakers: {', '.join(speakers)}")

    # Copy stems with Clipchamp naming convention
    stem_files = list(stems_dir.glob('*.wav'))
    if not stem_files:
        print("Warning: No WAV stem files found")
        return

    copied = 0
    manifest_entries = []

    for stem_file in sorted(stem_files):
        # Try to identify speaker from filename
        stem_name = stem_file.stem
        speaker_id = None

        # Check if filename contains speaker identifier
        for speaker, letter in speaker_map.items():
            if speaker.lower().replace(' ', '_') in stem_name.lower():
                speaker_id = letter
                break
            if f'speaker_{letter}' in stem_name.lower():
                speaker_id = letter
                break

        # If no match, assign sequentially
        if not speaker_id and copied < len(speaker_map):
            speaker_id = chr(97 + copied)

        if speaker_id:
            # Clipchamp naming: speaker_a_001.wav, speaker_a_002.wav, etc.
            segment_num = copied + 1
            output_name = f'speaker_{speaker_id}_{segment_num:03d}.wav'
            output_path = export_path / output_name

            shutil.copy2(stem_file, output_path)
            print(f"Copied {stem_file.name} -> {output_name}")

            manifest_entries.append({
                'source_file': str(stem_file.name),
                'export_file': output_name,
                'speaker_id': speaker_id,
                'segment_number': segment_num
            })
            copied += 1

    # Save stem manifest
    manifest = {
        'job_id': job_path.name,
        'export_directory': str(export_path),
        'stem_count': copied,
        'speakers': {letter: sp for sp, letter in speaker_map.items()},
        'stems': manifest_entries
    }

    manifest_path = export_path / 'stem_manifest.json'
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    print(f"\nPackaged {copied} stems to {export_path}")
    print(f"Manifest: {manifest_path}")
    print("\nStem files ready for Clipchamp import!")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python stem_packager.py <job_dir> [export_dir]")
        print("Example: python stem_packager.py tmp/test_job dist/export/test_job/stems")
        sys.exit(1)

    job_dir = sys.argv[1]
    export_dir = sys.argv[2] if len(sys.argv) > 2 else None

    package_stems(job_dir, export_dir)
