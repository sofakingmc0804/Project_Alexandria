"""
QC Runner - Orchestrates all quality checks and generates comprehensive QC report
Runs RAGAS, WER, LUFS checks and aggregates results
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
import subprocess

def run_ragas_check(job_dir: Path) -> Dict:
    try:
        result = subprocess.run(
            [sys.executable, 'app/packages/eval/ragas_scorer.py', str(job_dir)],
            capture_output=True, text=True, timeout=30
        )
        report_path = job_dir / 'ragas_scores.json'
        if report_path.exists():
            with open(report_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f'Warning: RAGAS check failed: {e}')
    return {'passed': False, 'error': 'Check failed'}

def run_wer_check(job_dir: Path) -> Dict:
    try:
        result = subprocess.run(
            [sys.executable, 'app/packages/eval/wer_calculator.py', str(job_dir)],
            capture_output=True, text=True, timeout=30
        )
        report_path = job_dir / 'wer_report.json'
        if report_path.exists():
            with open(report_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f'Warning: WER check failed: {e}')
    return {'passed': False, 'error': 'Check failed'}

def run_lufs_check(job_dir: Path) -> Dict:
    try:
        result = subprocess.run(
            [sys.executable, 'app/packages/eval/lufs_checker.py', str(job_dir)],
            capture_output=True, text=True, timeout=30
        )
        report_path = job_dir / 'lufs_report.json'
        if report_path.exists():
            with open(report_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f'Warning: LUFS check failed: {e}')
    return {'passed': False, 'error': 'Check failed'}

def load_continuity_report(job_dir: Path) -> Dict:
    report_path = job_dir / 'continuity_report.json'
    if not report_path.exists():
        return {'blockers': 0, 'warnings': 0, 'passed': True}
    with open(report_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    blockers = len([i for i in data.get('issues', []) if i.get('severity') == 'blocker'])
    return {
        'blockers': blockers,
        'warnings': len(data.get('issues', [])) - blockers,
        'passed': blockers == 0
    }

def check_deliverables(job_dir: Path) -> Dict:
    required_files = ['script.md', 'outline.yaml']
    missing = []
    present = []
    for file in required_files:
        file_path = job_dir / file
        if file_path.exists():
            present.append(file)
        else:
            missing.append(file)
    return {
        'required': required_files,
        'present': present,
        'missing': missing,
        'passed': len(missing) == 0
    }

def run_qc(job_dir: str) -> Dict:
    job_path = Path(job_dir)
    if not job_path.exists():
        print(f'Error: Job directory {job_dir} not found')
        sys.exit(1)
    
    print(f'Running QC checks for {job_path.name}...')
    print('1. RAGAS...')
    ragas_results = run_ragas_check(job_path)
    print('2. WER...')
    wer_results = run_wer_check(job_path)
    print('3. LUFS...')
    lufs_results = run_lufs_check(job_path)
    print('4. Continuity...')
    continuity_results = load_continuity_report(job_path)
    print('5. Deliverables...')
    deliverables_results = check_deliverables(job_path)
    
    all_passed = (
        ragas_results.get('passed', False) and
        wer_results.get('passed', False) and
        lufs_results.get('passed', False) and
        continuity_results.get('passed', True) and
        deliverables_results.get('passed', True)
    )
    
    issues = []
    if not ragas_results.get('passed', False):
        issues.extend(ragas_results.get('issues', ['RAGAS check failed']))
    if not wer_results.get('passed', False):
        issues.append(f"WER {wer_results.get('wer_percent', 0)}% exceeds threshold")
    if not lufs_results.get('passed', False):
        issues.extend(lufs_results.get('issues', ['LUFS check failed']))
    if continuity_results.get('blockers', 0) > 0:
        issues.append(f"{continuity_results['blockers']} continuity blockers found")
    if deliverables_results.get('missing'):
        issues.append(f"Missing files: {', '.join(deliverables_results['missing'])}")
    
    report = {
        'job_id': job_path.name,
        'passed': all_passed,
        'checks': {
            'ragas': {'passed': ragas_results.get('passed', False)},
            'wer': {'passed': wer_results.get('passed', False)},
            'lufs': {'passed': lufs_results.get('passed', False)},
            'continuity': {'passed': continuity_results.get('passed', True)},
            'deliverables': {'passed': deliverables_results.get('passed', True)}
        },
        'issues': issues
    }
    
    output_path = job_path / 'qc_report.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f"QC Result: {'PASSED' if all_passed else 'FAILED'}")
    print(f'Report: {output_path}')
    return report

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python qc_runner.py <job_dir>')
        sys.exit(1)
    run_qc(sys.argv[1])
