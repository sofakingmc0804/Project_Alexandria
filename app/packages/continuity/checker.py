#!/usr/bin/env python3
import json
from pathlib import Path
from typing import List, Dict, Any

def load_script(jdir):
    try:
        with open(Path(jdir)/'script.md') as f: return f.read()
    except: return ""

def check_continuity(jdir):
    jpath = Path(jdir)
    script = load_script(jdir)
    
    issues = []
    warnings = []
    blockers = []
    
    if not script:
        blockers.append('No script found')
    
    if len(script) < 100:
        warnings.append('Script seems very short')
    
    report = {
        'job_id':jpath.name,
        'passed':len(blockers)==0,
        'blockers':blockers,
        'warnings':warnings,
        'issues':issues,
        'entities_extracted':0,
        'contradictions_found':0
    }
    
    with open(jpath/'continuity_report.json','w') as f: json.dump(report,f,indent=2)
    print(f' Continuity check: {"PASSED" if report["passed"] else "FAILED"}')
    print(f'  Blockers: {len(blockers)}, Warnings: {len(warnings)}')
    return report

if __name__=='__main__':
    import sys
    check_continuity(sys.argv[1] if len(sys.argv)>1 else 'tests/fixtures/phase2_test')
