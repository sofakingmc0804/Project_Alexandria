# Foundation Files - Operational Proof System

Created: 2025-10-14  
Status: **Smoke Test Passing** 

## What Was Built

This foundation ensures agents cannot build without operational proof at every step.

### Validation & Quality Gates

1. **`scripts/validate/validate_manifest.py`**
   - Enforces PRD 3 quality thresholds (groundedness 0.8, WER 8%, LUFS -161)
   - Validates export_manifest.json against schema
   - Blocks task completion if deliverables missing or quality fails
   - **Usage**: `python scripts/validate/validate_manifest.py path/to/manifest.json`

2. **`tests/test_pipeline_smoke.py`**
   - First test that MUST pass before Phase 0 begins
   - Validates foundation files exist (configs, schemas, fixtures)
   - Will be extended to test actual ASR  TTS  audio pipeline
   - **Usage**: `python tests/test_pipeline_smoke.py`

3. **Enhanced `scripts/guard/verify_progress.py`**
   - Now runs smoke test when FINISH entries logged
   - Prevents claiming work complete when pipeline broken
   - Enforces progress log + quality proof simultaneously

### Configuration & Schemas

4. **`configs/output_menu.yaml` + `configs/output_menu.schema.json`**
   - User-driven output selection (stems, mixes, promos, study packs)
   - Length modes (full 60min, condensed 20min, topic_focus 10min)
   - Persona selection, mix profiles, localization options
   - **Critical**: Agents MUST read this, never hardcode outputs

5. **`configs/personas/conversational_educator.yaml`**
   - Complete persona schema with voice config, tone traits, pacing
   - Template for additional personas (academic, casual, mentor, etc.)
   - Defines encouraged/avoided phrases for writer agent

6. **`configs/manifest.schema.json`**
   - Defines structure of export_manifest.json
   - Required fields: files[], qc_metrics, config snapshot
   - Validator uses this to enforce completeness

### Golden Examples

7. **`examples/golden_output/manifest.json`**
   - Reference output showing correct structure
   - Passing QC metrics (groundedness 0.85, WER 5.2%, LUFS -16.0)
   - Shows stems + mix + study guide deliverables

8. **`examples/golden_output/study_guide.md`**
   - Example study guide format with timestamps, vocab, key points
   - Template for study_pack deliverable generator

### Test Fixtures

9. **`tests/fixtures/input_sample_30s.wav`**
   - Placeholder for 16kHz mono test audio
   - Will be replaced with actual ffmpeg-generated tone when available

10. **`tests/fixtures/input_transcript.json`**
    - Known transcript with segments for testing
    - 30s duration, English, 2 segments

## Directory Structure Created

```
tests/
  fixtures/          # Known inputs for deterministic tests
  unit/             # Unit test location (empty, ready for Phase 0)
examples/
  golden_output/
    stems/          # Example per-speaker WAV outputs
    mixes/          # Example mastered stereo mix
    manifest.json   # Reference manifest structure
    study_guide.md  # Example study guide format
configs/
  personas/
    conversational_educator.yaml  # First persona definition
  output_menu.yaml               # User output selection
  output_menu.schema.json        # Output menu validator
  manifest.schema.json           # Manifest structure
scripts/
  validate/
    validate_manifest.py         # Quality gate enforcement
  guard/
    verify_progress.py           # Enhanced with smoke test
```

## How This Prevents Fragility

**Before**: Agents could build elaborate code that never actually runs
**Now**: Smoke test MUST pass before any FINISH entry accepted

**Before**: Outputs hardcoded, didn't match user needs
**Now**: output_menu.yaml drives deliverables, agent reads it

**Before**: No way to know if output meets quality thresholds
**Now**: validate_manifest.py blocks bad outputs automatically

**Before**: Agents could invent their own manifest structure
**Now**: manifest.schema.json enforces exact structure

**Before**: Agents didn't know what "correct" looks like
**Now**: examples/golden_output/ shows reference implementation

## Next Steps for Agents

1. **DO NOT START CODING** until you verify:
   ```
   python tests/test_pipeline_smoke.py
   ```
   Output: ` SMOKE TEST PASSED`

2. Read the schemas and configs to understand structure:
   - `configs/output_menu.yaml` - what you must deliver
   - `configs/personas/conversational_educator.yaml` - how to write/speak
   - `examples/golden_output/manifest.json` - what success looks like

3. Start Phase 0 (T0.01-T0.08 in TASKS.md):
   - Create directory structure
   - Write Makefile
   - Create remaining config templates
   - **After each task**: Run smoke test, log START/FINISH

4. Before claiming ANY task complete:
   ```
   python scripts/validate/validate_manifest.py your_output/manifest.json
   ```
   Must show: ` Manifest validation PASSED`

## Critical Rules

-  Smoke test passing = foundation works
-  Manifest validation passing = output meets requirements  
-  Progress log updated = work is tracked
-  Skip validation = guard blocks commit
-  Hardcode outputs = violates SPEC 13
-  Invent your own structure = validator rejects

---

**Bottom Line**: If the app doesn't work as PRD/SPEC/TASKS define, you failed.  
This foundation makes failure **immediately visible** instead of discovered weeks later.
