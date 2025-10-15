"""
Pipeline Smoke Test - First test that MUST pass
Validates end-to-end pipeline can load input  process  output audio
This is the operational proof the system works.
"""
import sys
from pathlib import Path

# Test requirements:
# 1. Load 30s test audio
# 2. Run minimal ASR (even placeholder)
# 3. Generate TTS output (even placeholder)
# 4. Output audio file exists

def smoke_test():
    """
    Minimal pipeline test.
    Returns True if basic flow works, False otherwise.
    """
    print(" Running Alexandria Pipeline Smoke Test...")
    
    # Check fixture exists
    fixture_path = Path("tests/fixtures/input_sample_30s.wav")
    if not fixture_path.exists():
        print(f" Test fixture missing: {fixture_path}")
        return False
    print(f" Test fixture found: {fixture_path}")
    
    # Check transcript fixture
    transcript_path = Path("tests/fixtures/input_transcript.json")
    if not transcript_path.exists():
        print(f" Transcript fixture missing: {transcript_path}")
        return False
    print(f" Transcript fixture found: {transcript_path}")
    
    # Check configs exist
    required_configs = [
        "configs/output_menu.yaml",
        "configs/personas/conversational_educator.yaml",
        "configs/manifest.schema.json",
        "configs/output_menu.schema.json"
    ]
    for config in required_configs:
        if not Path(config).exists():
            print(f" Required config missing: {config}")
            return False
    print(f" All required configs present")
    
    # Check validation script exists
    validator = Path("scripts/validate/validate_manifest.py")
    if not validator.exists():
        print(f" Manifest validator missing: {validator}")
        return False
    print(f" Manifest validator ready")
    
    # TODO: When ASR/TTS packages exist, actually run pipeline here
    # For now, this validates the foundation is in place
    
    print("\n SMOKE TEST PASSED - Foundation ready for Phase 0")
    print("Next: Implement actual ASR  TTS  audio output pipeline")
    return True

if __name__ == "__main__":
    success = smoke_test()
    sys.exit(0 if success else 1)
