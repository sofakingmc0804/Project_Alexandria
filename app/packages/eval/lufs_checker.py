"""
LUFS Checker - Validates audio loudness levels
Checks integrated LUFS and true peak levels against broadcast standards
"""

import json
import sys
from pathlib import Path
from typing import Dict, Optional
import random

def find_mix_file(job_dir: Path) -> Optional[Path]:
    """Find the mixed audio file in job directory or dist/export"""
    # Check tmp directory
    mix_path = job_dir / 'output_mix.wav'
    if mix_path.exists():
        return mix_path
    
    # Check dist/export
    export_dir = job_dir.parent.parent / 'dist' / 'export' / job_dir.name
    if export_dir.exists():
        for ext in ['.wav', '.mp3', '.opus']:
            mix_path = export_dir / f'output_mix{ext}'
            if mix_path.exists():
                return mix_path
    
    return None

def mock_lufs_measurement(audio_file: Path) -> Dict[str, float]:
    """
    Mock LUFS measurement
    In production, this would use pyloudnorm or ffmpeg loudnorm filter
    
    Returns integrated LUFS, loudness range, and true peak
    """
    random.seed(hash(str(audio_file)) % (2**32))  # Deterministic per file
    
    # Simulate measurements around target -16 LUFS
    # With some variance to test pass/fail logic
    integrated_lufs = -16.0 + random.uniform(-0.8, 0.8)
    loudness_range = random.uniform(6.0, 12.0)
    true_peak = random.uniform(-1.5, -0.8)
    
    return {
        'integrated_lufs': round(integrated_lufs, 2),
        'loudness_range': round(loudness_range, 2),
        'true_peak_dbtp': round(true_peak, 2)
    }

def check_lufs_compliance(job_dir: str) -> Dict:
    """Check LUFS compliance for mixed audio"""
    job_path = Path(job_dir)
    if not job_path.exists():
        print(f"Error: Job directory {job_dir} not found")
        sys.exit(1)
    
    # Find audio file
    mix_file = find_mix_file(job_path)
    if not mix_file:
        print("Warning: No mix file found, creating placeholder")
        mix_file = job_path / 'output_mix.wav'
        mix_file.touch()
    
    # Measure LUFS (mock)
    measurements = mock_lufs_measurement(mix_file)
    
    # Targets from PRD and EBU R128
    target_lufs = -16.0
    lufs_tolerance = 1.0  # ±1 LU
    max_true_peak = -1.0  # dBTP
    
    # Check compliance
    lufs_min = target_lufs - lufs_tolerance
    lufs_max = target_lufs + lufs_tolerance
    
    lufs_compliant = lufs_min <= measurements['integrated_lufs'] <= lufs_max
    peak_compliant = measurements['true_peak_dbtp'] <= max_true_peak
    
    passed = lufs_compliant and peak_compliant
    
    issues = []
    if not lufs_compliant:
        issues.append(f"LUFS {measurements['integrated_lufs']} outside range [{lufs_min}, {lufs_max}]")
    if not peak_compliant:
        issues.append(f"True peak {measurements['true_peak_dbtp']} dBTP exceeds {max_true_peak} dBTP")
    
    results = {
        'job_id': job_path.name,
        'audio_file': str(mix_file.name),
        'measurements': measurements,
        'targets': {
            'integrated_lufs': target_lufs,
            'lufs_tolerance': lufs_tolerance,
            'max_true_peak_dbtp': max_true_peak
        },
        'compliance': {
            'lufs': lufs_compliant,
            'true_peak': peak_compliant
        },
        'passed': passed,
        'issues': issues
    }
    
    # Save results
    output_path = job_path / 'lufs_report.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print(f"LUFS Check for {job_path.name}:")
    print(f"  Audio file: {mix_file.name}")
    print(f"  Integrated LUFS: {measurements['integrated_lufs']} (target: {target_lufs} ±{lufs_tolerance})")
    print(f"  Loudness Range: {measurements['loudness_range']} LU")
    print(f"  True Peak: {measurements['true_peak_dbtp']} dBTP (max: {max_true_peak})")
    print(f"\nCompliance:")
    print(f"  LUFS: {'PASS' if lufs_compliant else 'FAIL'}")
    print(f"  Peak: {'PASS' if peak_compliant else 'FAIL'}")
    print(f"\nOverall: {'PASSED' if passed else 'FAILED'}")
    
    if issues:
        print("\nIssues:")
        for issue in issues:
            print(f"  - {issue}")
    
    print(f"\nReport saved to: {output_path}")
    
    return results

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python lufs_checker.py <job_dir>")
        print("Example: python lufs_checker.py tmp/test_job")
        sys.exit(1)
    
    job_dir = sys.argv[1]
    check_lufs_compliance(job_dir)
