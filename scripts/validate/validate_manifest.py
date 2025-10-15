"""
Manifest Validator - Blocks bad outputs before task completion
Validates export_manifest.json against schema and PRD quality thresholds
"""
import json
import sys
from pathlib import Path
from jsonschema import validate, ValidationError

SCHEMA_PATH = Path(__file__).parent.parent / "configs" / "manifest.schema.json"

# PRD 3 Quality Thresholds
GROUNDEDNESS_MIN = 0.8
CONTEXT_PRECISION_MIN = 0.7
WER_MAX = 8.0
LUFS_TARGET = -16.0
LUFS_TOLERANCE = 1.0
TRUE_PEAK_MAX = -1.0

def validate_manifest(manifest_path: Path) -> tuple[bool, list[str]]:
    """
    Validate manifest file against schema and quality gates.
    Returns (passed, issues[])
    """
    issues = []
    
    # Load manifest
    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
    except Exception as e:
        return False, [f"Failed to load manifest: {e}"]
    
    # Schema validation
    try:
        with open(SCHEMA_PATH) as f:
            schema = json.load(f)
        validate(instance=manifest, schema=schema)
    except ValidationError as e:
        return False, [f"Schema validation failed: {e.message}"]
    except Exception as e:
        return False, [f"Schema load error: {e}"]
    
    # Quality gates (PRD 3)
    qc = manifest.get("qc_metrics", {})
    
    if qc.get("groundedness", 0) < GROUNDEDNESS_MIN:
        issues.append(f"Groundedness {qc.get('groundedness')} < {GROUNDEDNESS_MIN}")
    
    if qc.get("context_precision", 0) < CONTEXT_PRECISION_MIN:
        issues.append(f"Context precision {qc.get('context_precision')} < {CONTEXT_PRECISION_MIN}")
    
    if qc.get("wer", 100) > WER_MAX:
        issues.append(f"WER {qc.get('wer')}% > {WER_MAX}%")
    
    lufs = qc.get("lufs", 0)
    if abs(lufs - LUFS_TARGET) > LUFS_TOLERANCE:
        issues.append(f"LUFS {lufs} outside {LUFS_TARGET}{LUFS_TOLERANCE}")
    
    true_peak = qc.get("true_peak_db", 0)
    if true_peak > TRUE_PEAK_MAX:
        issues.append(f"True peak {true_peak}dB > {TRUE_PEAK_MAX}dB")
    
    # File existence checks
    files_missing = []
    for file_entry in manifest.get("files", []):
        file_path = Path(file_entry["path"])
        if not file_path.exists():
            files_missing.append(str(file_path))
    
    if files_missing:
        issues.append(f"Missing files: {', '.join(files_missing)}")
    
    # Required deliverables check (from config)
    config = manifest.get("config", {})
    required_types = set()
    for deliverable in config.get("deliverables", []):
        if deliverable == "stems":
            required_types.add("stem")
        elif deliverable == "upload_mix":
            required_types.add("mix")
        elif deliverable == "promo_pack":
            required_types.add("promo")
    
    actual_types = {f["type"] for f in manifest.get("files", [])}
    missing_types = required_types - actual_types
    if missing_types:
        issues.append(f"Missing required file types: {missing_types}")
    
    passed = len(issues) == 0 and qc.get("passed", False)
    return passed, issues

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_manifest.py <path_to_export_manifest.json>")
        sys.exit(1)
    
    manifest_path = Path(sys.argv[1])
    passed, issues = validate_manifest(manifest_path)
    
    if passed:
        print(f" Manifest validation PASSED: {manifest_path}")
        sys.exit(0)
    else:
        print(f" Manifest validation FAILED: {manifest_path}")
        for issue in issues:
            print(f"  - {issue}")
        sys.exit(1)
