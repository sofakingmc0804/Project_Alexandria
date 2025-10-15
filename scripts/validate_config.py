"""
Configuration Validator
Validates all YAML configs have required fields
"""
import sys
from pathlib import Path
import yaml

REQUIRED_CONFIGS = {
    "configs/hosts.yaml": ["hosts", "language", "target_duration_minutes", "persona_id"],
    "configs/mastering.yaml": ["lufs_target", "processing", "crossfade_ms", "export_formats"],
    "configs/retrieval.yaml": ["embed_model", "db", "retrieval", "chunking", "quality"],
    "configs/output_menu.yaml": ["deliverables", "length_mode", "persona", "mix_profile"],
    "configs/personas/conversational_educator.yaml": ["id", "name", "voice_config", "tone_traits"]
}

def validate_config(config_path: str, required_fields: list) -> tuple[bool, list[str]]:
    """Validate a config file has required top-level fields."""
    path = Path(config_path)
    if not path.exists():
        return False, [f"Config file not found: {config_path}"]
    
    try:
        with open(path) as f:
            config = yaml.safe_load(f)
    except Exception as e:
        return False, [f"Failed to parse YAML: {e}"]
    
    if not isinstance(config, dict):
        return False, ["Config root must be a dictionary"]
    
    missing = [field for field in required_fields if field not in config]
    if missing:
        return False, [f"Missing required fields: {', '.join(missing)}"]
    
    return True, []

def main():
    """Validate all config files."""
    print("Validating Alexandria configuration files...")
    all_passed = True
    
    for config_path, required_fields in REQUIRED_CONFIGS.items():
        passed, errors = validate_config(config_path, required_fields)
        
        if passed:
            print(f" {config_path}")
        else:
            print(f" {config_path}")
            for error in errors:
                print(f"  {error}")
            all_passed = False
    
    if all_passed:
        print("\n All configuration files valid")
        return 0
    else:
        print("\n Configuration validation failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
