"""Manifest Writer - Creates export manifest listing all deliverables"""
import json, sys
from pathlib import Path

def create_manifest(job_dir: str):
    job_path = Path(job_dir)
    export_dir = Path('dist/export') / job_path.name
    export_dir.mkdir(parents=True, exist_ok=True)
    
    # Collect deliverables
    files = list(export_dir.glob('**/*'))
    deliverables = [str(f.relative_to(export_dir)) for f in files if f.is_file()]
    
    manifest = {
        'job_id': job_path.name,
        'export_directory': str(export_dir),
        'deliverables': deliverables,
        'mix_profile': 'clean',
        'persona': 'conversational_educator',
        'qc_passed': (job_path / 'qc_report.json').exists()
    }
    
    output_path = export_dir / 'export_manifest.json'
    with open(output_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f'Manifest created: {output_path}')
    return manifest

if __name__ == '__main__':
    create_manifest(sys.argv[1] if len(sys.argv) > 1 else 'tmp/test_job')
