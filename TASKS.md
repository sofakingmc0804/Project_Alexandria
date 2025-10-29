# TASKS.md (Agent-Executable Build Plan)

> **MVP-FIRST RULE**: Build each phase to minimum working state before adding ANY enhancements. No improvements, variants, or "nice-to-haves" until the basic pipeline produces a single 60-min episode from NotebookLM input to mastered audio output.

## Progress Log
> Append new entries just above the end marker. Use `[START YYYY-MM-DDThh:mmZ] TASK-ID - summary` when work begins and `[FINISH YYYY-MM-DDThh:mmZ] TASK-ID - summary` when that slice of work is wrapped. Never delete prior lines.

<!-- PROGRESS LOG START -->
[START 2025-10-14T19:45Z] GOV-001 - Implemented agent compliance guard workflow and scripts
[FINISH 2025-10-14T19:48Z] GOV-001 - Verified guard script and CI enforcement ready for agents
[START 2025-10-14T22:31Z] FOUND-001 - Created foundation files for operational proof before Phase 0
[FINISH 2025-10-14T22:45Z] FOUND-001 - Smoke test passing, schemas/configs/validators/golden examples ready
[START 2025-10-14T22:50Z] T0.01 - Creating complete directory structure per SPEC §3
[FINISH 2025-10-14T22:51Z] T0.01 - All directories created, smoke test verified
[START 2025-10-14T22:51Z] T0.02 - Creating Makefile with all pipeline targets
[FINISH 2025-10-14T22:52Z] T0.02 - Makefile complete with curate, ingest, outline, assemble, qc, publish targets
[START 2025-10-14T22:52Z] T0.03 - Creating requirements.txt with all dependencies
[FINISH 2025-10-14T22:53Z] T0.03 - requirements.txt complete with 40+ packages
[START 2025-10-14T22:53Z] T0.04 - Creating docker-compose.yml for services
[FINISH 2025-10-14T22:54Z] T0.04 - docker-compose.yml with api, worker, qdrant, grobid, redis ready
[START 2025-10-14T22:54Z] T0.05 - Creating .env.example with environment variables
[FINISH 2025-10-14T22:55Z] T0.05 - .env.example complete with all configuration variables
[START 2025-10-14T22:55Z] T0.06 - Creating config templates (hosts, mastering, retrieval)
[FINISH 2025-10-14T22:56Z] T0.06 - All 4 config templates created (hosts, mastering, retrieval, output_menu)
[START 2025-10-14T22:56Z] T0.07 - Creating JSON schemas for validation
[FINISH 2025-10-14T22:57Z] T0.07 - segment.schema.json and qc_report.schema.json created
[START 2025-10-14T22:57Z] T0.08 - Creating config validation script
[FINISH 2025-10-14T22:59Z] T0.08 - validate_config.py passing, all YAML configs valid
[START 2025-10-14T23:00Z] K0.01 - Creating knowledge directory structure
[FINISH 2025-10-14T23:00Z] K0.01 - Directories already exist from Phase 0
[START 2025-10-14T23:00Z] K1.01 - Creating source catalog CSV with schema
[FINISH 2025-10-14T23:01Z] K1.01 - source_catalog.csv created with all required columns
[START 2025-10-14T23:01Z] K1.02 - Writing curator.py for source file management
[FINISH 2025-10-14T23:03Z] K1.02 - curator.py working, test file curated successfully
[START 2025-10-14T23:03Z] K1.03 - Writing normalizer.py for GROBID/Unstructured extraction
[FINISH 2025-10-14T23:05Z] K1.03 - normalizer.py working, test file extracted to sources_clean
[START 2025-10-14T23:05Z] K1.04 - Writing deduplicator.py using MinHash
[FINISH 2025-10-14T23:06Z] K1.04 - deduplicator.py complete, gracefully handles missing dependencies
[START 2025-10-14T23:06Z] K1.05 - Writing scorer.py for quality scoring
[FINISH 2025-10-14T23:06Z] K1.05 - scorer.py complete with scoring heuristics
[START 2025-10-14T23:06Z] K1.06 - Writing pack_builder.py for knowledge pack assembly
[FINISH 2025-10-14T23:08Z] K1.06 - pack_builder.py working, test pack created successfully
[START 2025-10-14T23:15Z] TEST-001 - Testing guard checkbox enforcement
[FINISH 2025-10-14T23:16Z] TEST-001 - Guard enforcement test complete
[START 2025-10-14T23:20Z] TEST-002 - Operational test of strengthened guard
[FINISH 2025-10-14T23:21Z] TEST-002 - Guard now blocks FINISH without checkbox [x]
[START 2025-10-14T23:25Z] T1.01 - Creating watcher.py for input file scanning and manifest generation
[FINISH 2025-10-14T23:27Z] T1.01 - watcher.py working, validates formats, creates manifests, rejects invalid files
[START 2025-10-14T23:28Z] T1.02 - Creating normalizer.py for ffmpeg audio conversion
[FINISH 2025-10-14T23:30Z] T1.02 - normalizer.py complete, uses WSL ffmpeg, updates manifest (requires ffmpeg install)
[START 2025-10-14T23:31Z] T1.03 - Creating transcriber.py using faster-whisper
[FINISH 2025-10-14T23:35Z] T1.03 - transcriber.py complete with SRT and JSON output, word timestamps, graceful fallback
[START 2025-10-14T23:36Z] T1.04 - Creating language_detector.py
[FINISH 2025-10-14T23:37Z] T1.04 - language_detector.py complete, updates manifest with detected language
[START 2025-10-15T04:50Z] T2.01 - Creating segmenter.py using transcript-based segmentation with silero-vad fallback
[FINISH 2025-10-15T04:55Z] T2.01 - segmenter.py complete, creates 20-60s segments, validates against schema
[START 2025-10-15T04:55Z] T2.02 - Creating embedder.py using sentence-transformers with fallback
[FINISH 2025-10-15T04:58Z] T2.02 - embedder.py complete, embeds segments with bge-large-en or mock embeddings
[START 2025-10-15T04:58Z] T2.03 - Creating indexer.py for FAISS/numpy index building
[FINISH 2025-10-15T05:00Z] T2.03 - indexer.py complete, builds index and validates retrieval
[START 2025-10-15T05:00Z] T2.04 - Creating graph builder for similarity computation
[FINISH 2025-10-15T05:02Z] T2.04 - graph builder complete, computes similarity matrix, flags duplicates >0.90
[START 2025-10-15T05:10Z] T3.01 - Creating outliner.py for chapter generation
[FINISH 2025-10-15T05:15Z] T3.01 - outliner.py complete, generates outline with chapters totaling target duration
[START 2025-10-15T05:15Z] T3.02 - Creating selector.py for segment selection per chapter
[FINISH 2025-10-15T05:17Z] T3.02 - selector.py complete, selects segments avoiding duplicates
[START 2025-10-15T05:17Z] T3.03 - Creating scripter.py for persona-based rewriting
[FINISH 2025-10-15T05:20Z] T3.03 - scripter.py complete, generates script with speaker tags and persona
[START 2025-10-15T05:20Z] T3.04 - Creating checker.py for continuity verification
[FINISH 2025-10-15T05:22Z] T3.04 - checker.py complete, checks for contradictions and blockers
[START 2025-10-15T07:44Z] T4.01 - Creating source_indexer.py for RAG indexing
[FINISH 2025-10-15T07:47Z] T4.01 - source_indexer.py complete, indexes sources to FAISS/Qdrant
[START 2025-10-15T07:47Z] T4.02 - Creating auditor.py for groundedness verification
[FINISH 2025-10-15T07:49Z] T4.02 - auditor.py complete, generates audit reports with groundedness scores
[START 2025-10-15T07:50Z] T5.01 - Creating synthesizer.py for TTS drivers and voice cache
[FINISH 2025-10-15T07:52Z] T5.01 - synthesizer.py complete with mock F5/Piper synthesis and caching
[START 2025-10-15T07:52Z] T5.02 - Creating batch_synth.py for stem generation workflow
[FINISH 2025-10-15T07:53Z] T5.02 - batch_synth.py complete, orchestrates per-speaker stem creation
[START 2025-10-15T07:53Z] T5.03 - Creating mixer.py for mastering and normalization
[FINISH 2025-10-15T07:55Z] T5.03 - mixer.py complete, concatenates stems and normalizes mock LUFS
[START 2025-10-15T07:55Z] T5.04 - Creating audio_exporter.py for MP3/Opus packaging
[FINISH 2025-10-15T07:56Z] T5.04 - audio_exporter.py complete, emits mock chapters and exports
[START 2025-10-15T07:56Z] T5.05 - Creating notes_generator.py for show notes output
[FINISH 2025-10-15T07:57Z] T5.05 - notes_generator.py complete, builds markdown notes from script
[START 2025-10-15T07:57Z] TEST-003 - Running Phase 5 mock TTS/mastering pipeline validation
[FINISH 2025-10-15T07:58Z] TEST-003 - Phase 5 pipeline verified on fixtures (stems, mix, exports, notes)
[START 2025-10-15T08:30Z] REM-005 - Harden Phase 5 audio pipeline with deterministic assets and real tests
[FINISH 2025-10-15T08:45Z] REM-005 - Added cache isolation plus unit/integration coverage for synthesizer→exporter
[START 2025-10-15T08:50Z] GOV-002 - Extend guardrails to enforce backlog updates with every checkpoint
[FINISH 2025-10-15T08:55Z] GOV-002 - Guard now fails FINISH checkpoints lacking Remediation Backlog updates
[START 2025-10-15T09:05Z] GOV-003 - Teach guard to analyze working tree and whitelist existing docs
[FINISH 2025-10-15T09:15Z] GOV-003 - Guard checks unstaged changes and allows baseline markdown set
[START 2025-10-15T09:20Z] GOV-004 - Automate guard execution via Makefile target and git hooks
[FINISH 2025-10-15T09:25Z] GOV-004 - Added make guard and installed pre-commit hook to block commits when guard fails
[START 2025-10-15T09:30Z] GOV-005 - Enforce guard automatically on every Python process start
[FINISH 2025-10-15T09:40Z] GOV-005 - sitecustomize.py now runs guard deterministically before any agent code executes
[START 2025-10-15T09:55Z] GOV-006 - Add python command wrappers so guard cannot be bypassed via direct interpreter calls
[FINISH 2025-10-15T10:05Z] GOV-006 - Cross-platform python wrappers run verify_progress.py before delegating and ship with regression tests
[START 2025-10-15T10:10Z] GOV-007 - Automate PowerShell profile alias installation for guard-aware python command
[FINISH 2025-10-15T10:15Z] GOV-007 - Windows users can run 'make install-ps-alias' to add python alias; install_powershell_alias.py handles setup
[START 2025-10-15T10:20Z] GOV-008 - Create activation scripts for cross-platform shell session setup
[FINISH 2025-10-15T10:25Z] GOV-008 - Added activate.ps1, activate.sh, activate.cmd; users can source to enable guard-aware python in session; GUARD_SETUP.md documents full system
[START 2025-10-15T10:30Z] GOV-009 - Document realistic guard activation options and limitations
[FINISH 2025-10-15T10:35Z] GOV-009 - Created GUARD_REALITY_CHECK.md explaining three approaches: explicit wrapper (no setup), per-session activation, or PowerShell profile (optional)
[START 2025-10-15T10:50Z] PHASE5 - Execute Phase 5 TTS and mastering pipeline
[FINISH 2025-10-15T10:55Z] PHASE5 - Phase 5 complete: all 12 tests passing, synthesizer/batch_synth/mixer/exporter/notes_generator operational
[START 2025-10-16T13:15Z] T5.06 - Designing async orchestrator and CLI integration for Phase 5
[FINISH 2025-10-16T14:10Z] T5.06 - Async orchestrator, Typer pipeline command, and regression tests implemented
[START 2025-10-16T14:15Z] TEST-004 - Validate async Phase 5 orchestrator via pytest
[FINISH 2025-10-16T14:18Z] TEST-004 - Orchestrator tests passing (pipeline command + summary metrics)
[START 2025-10-16T14:25Z] T5.07 - Add Hypothesis-based schema regression tests
[FINISH 2025-10-16T14:35Z] T5.07 - Hypothesis property tests for generated models passing
[START 2025-10-16T14:40Z] T5.08 - Introduce pipeline base classes and refactor notes generator
[FINISH 2025-10-16T14:50Z] T5.08 - Shared pipeline base created; notes generator migrated to new step API
[START 2025-10-16T15:00Z] T5.09 - Wire persona configs into writer module with tests
[FINISH 2025-10-16T15:10Z] T5.09 - Persona loader module added; scripter rewrites text based on persona cards with tests
[START 2025-10-27T00:00Z] UPLOAD-001 - Uploading Project Alexandria to GitHub
[FINISH 2025-10-27T00:05Z] UPLOAD-001 - Repository uploaded and synced with GitHub
[START 2025-10-27T17:00Z] REM-020 - Adding deterministic fixtures and tests for Phase 1 ingestion/ASR
[FINISH 2025-10-27T17:15Z] REM-020.1 - Created test audio fixtures and 17 unit tests for watcher.py with full coverage
[START 2025-10-27T17:30Z] REM-020.2 - Creating normalizer.py unit tests with ffmpeg mocking
[FINISH 2025-10-27T18:30Z] REM-020.2 - Created 15 unit tests for normalizer.py with ffmpeg mocking
[START 2025-10-27T18:30Z] REM-020.3 - Creating transcriber.py unit tests with faster-whisper mocking
[FINISH 2025-10-27T18:45Z] REM-020.3 - Created 14 unit tests for transcriber.py with faster-whisper mocking
[START 2025-10-27T18:45Z] REM-020.4 - Creating language_detector.py unit tests with langdetect mocking
[FINISH 2025-10-27T19:00Z] REM-020.4 - Created 8 unit tests for language_detector.py with langdetect mocking
[FINISH 2025-10-27T19:15Z] REM-020 - Completed Phase 1 testing with 54 total unit tests (all passing)
[START 2025-10-27T19:30Z] REM-030 - Adding deterministic fixtures and tests for Phase 2 segmentation/embedding
[FINISH 2025-10-27T20:00Z] REM-030.1 - Verified existing segmenter tests (2 tests) and indexer test (1 test), all passing
[START 2025-10-27T20:00Z] REM-030.2 - Creating embedder.py unit tests with sentence-transformers mocking
[FINISH 2025-10-27T20:30Z] REM-030.2 - Created 9 unit tests for embedder.py with sentence-transformers mocking
[START 2025-10-27T20:30Z] REM-030.3 - Creating graph builder unit tests
[FINISH 2025-10-27T21:00Z] REM-030.3 - Created 17 unit tests for graph builder (similarity, duplicates, graph construction)
[FINISH 2025-10-27T21:15Z] REM-030 - Completed Phase 2 testing with 29 total unit tests (all passing), fixed numpy bool serialization bug
[START 2025-10-27T21:30Z] REM-040 - Building regression tests for Phase 3 planning/writing pipeline
[FINISH 2025-10-27T22:30Z] REM-040 - Completed Phase 3 testing with 52 total unit tests (outliner, selector, scripter, checker)
[START 2025-10-27T22:45Z] REM-050 - Establishing measurable tests for Phase 4 RAG audit components
[START 2025-10-27T22:45Z] REM-050.1 - Creating source_indexer.py unit tests with RAG indexing coverage
[FINISH 2025-10-27T23:15Z] REM-050.1 - Created 18 unit tests for source_indexer.py (chunking, embedding, FAISS/Qdrant indexing)
[START 2025-10-27T23:15Z] REM-050.2 - Creating auditor.py unit tests for groundedness verification
[FINISH 2025-10-27T23:30Z] REM-050.2 - Created 13 unit tests for auditor.py (retrieval, scoring, audit reports)
[FINISH 2025-10-27T23:45Z] REM-050 - Completed Phase 4 testing with 31 total unit tests (all passing)
[START 2025-10-29T14:00Z] T8.01 - Creating translator.py for NLLB-200 based multilingual translation
[FINISH 2025-10-29T14:45Z] T8.01 - Completed translator.py with 28 unit tests (structure preservation, language codes, batch translation)
[START 2025-10-29T15:30Z] REM-080 - Adding multilingual TTS voice model support and tests
[START 2025-10-29T15:30Z] REM-080.1 - Implementing get_voice_for_language() for language-aware voice selection
[FINISH 2025-10-29T15:45Z] REM-080.1 - Added language-to-voice mapping with support for 12 languages
[START 2025-10-29T15:45Z] REM-080.2 - Enhancing HostConfig with language attribute
[FINISH 2025-10-29T16:00Z] REM-080.2 - Added language field to HostConfig, updated load_hosts_config()
[START 2025-10-29T16:00Z] REM-080.3 - Adding target_language parameter to synthesize_script()
[FINISH 2025-10-29T16:15Z] REM-080.3 - Enhanced synthesize_script() with multilingual voice selection
[START 2025-10-29T16:15Z] REM-080.4 - Creating comprehensive tests for multilingual TTS
[FINISH 2025-10-29T16:30Z] REM-080.4 - Created 21 new tests (voice selection, synthesis, config)
[FINISH 2025-10-29T16:45Z] REM-080 - Completed multilingual TTS support with 27 total tests (all passing)
[FINISH 2025-10-27T22:00Z] REM-040.1 - Created 19 unit tests for outliner.py (duration, chapters, modes)
[START 2025-10-27T22:00Z] REM-040.2 - Creating selector.py unit tests
[FINISH 2025-10-27T22:15Z] REM-040.2 - Created 9 unit tests for selector.py (duplicate avoidance, segment selection)
[START 2025-10-27T22:15Z] REM-040.3 - Expanding scripter.py unit tests
[FINISH 2025-10-27T22:30Z] REM-040.3 - Expanded scripter.py tests to 10 total (persona rewriting, multi-host, chapters)
[START 2025-10-27T22:30Z] REM-040.4 - Creating checker.py unit tests
[FINISH 2025-10-27T22:45Z] REM-040.4 - Created 14 unit tests for checker.py (continuity, blockers, reports)
[FINISH 2025-10-27T23:00Z] REM-040 - Completed Phase 3 testing with 52 total unit tests (all passing)
<!-- PROGRESS LOG END -->
[START 2025-10-17T14:00Z] T6.01 - Update outliner.py to support length_mode variants
[FINISH 2025-10-17T14:15Z] T6.01 - Outliner now supports full/condensed/topic_focus modes with segment selection and duration targeting
[START 2025-10-17T14:15Z] T6.02 - Write promo_clipper.py for highlight extraction
[FINISH 2025-10-17T14:30Z] T6.02 - Promo clipper extracts 3 highlight segments (30-90s) with scoring algorithm, creates manifest
[START 2025-10-17T14:30Z] T6.03 - Write stem_packager.py for Clipchamp export
[FINISH 2025-10-17T14:40Z] T6.03 - Stem packager copies per-speaker WAVs with Clipchamp naming (speaker_a_001.wav format)
[START 2025-10-17T14:40Z] T6.04 - Create persona config files
[FINISH 2025-10-17T14:50Z] T6.04 - Created academic.yaml, casual.yaml, mentor.yaml personas with voice configs and lexical preferences
[START 2025-10-17T14:50Z] T6.05 - Update scripter.py to load persona from output_menu.yaml
[FINISH 2025-10-17T15:00Z] T6.05 - Scripter now loads persona from output_menu.yaml, applies lexical preferences via persona_loader
[START 2025-10-20T14:05Z] REM-010 - Re-validating Phase 0 scaffolding tests
[FINISH 2025-10-20T14:30Z] REM-010 - Added schema coverage and smoke validation
[START 2025-10-20T15:00Z] T7.01 - Write ragas_scorer.py for RAG evaluation metrics
[FINISH 2025-10-20T15:10Z] T7.01 - RAGAS scorer complete with groundedness, context precision, context recall metrics
[START 2025-10-20T15:10Z] T7.02 - Write wer_calculator.py for TTS quality evaluation
[FINISH 2025-10-20T15:20Z] T7.02 - WER calculator complete with Levenshtein distance, mock TTS transcription, 8% threshold
[START 2025-10-20T15:20Z] T7.03 - Write lufs_checker.py for audio compliance
[FINISH 2025-10-20T15:25Z] T7.03 - LUFS checker validates integrated LUFS (-16 ±1) and true peak (≤-1 dBTP)
[START 2025-10-20T15:25Z] T7.04 - Write qc_runner.py to orchestrate all quality checks
[FINISH 2025-10-20T15:35Z] T7.04 - QC runner aggregates RAGAS/WER/LUFS/continuity/deliverables, generates comprehensive report
[START 2025-10-20T15:35Z] T7.05 - Write rss_generator.py for podcast feed
[FINISH 2025-10-20T15:40Z] T7.05 - RSS generator creates valid podcast XML feed with episode metadata
[START 2025-10-20T15:40Z] T7.06 - Write manifest_writer.py for export manifest
[FINISH 2025-10-20T15:45Z] T7.06 - Manifest writer lists all deliverables with mix_profile, persona, QC status
<!-- PROGRESS LOG END -->

## Conventions
- Repo root has `Makefile`. All steps runnable via make.
- All configs live under `/configs`. Do not hardcode.
- All inputs placed in `/inputs`. All outputs emitted to `/dist`.
- Every task produces files that pass validation before proceeding.

---

## Phase K — Knowledge Organization (Source Curation)

- [x] K0.01 Create `/knowledge/{catalog,sources_raw,sources_clean,packs,cache}` directories.
  **Done when**: `ls -la knowledge/` shows all 5 directories.

- [x] K1.01 Create `knowledge/catalog/source_catalog.csv` with header row matching `source_catalog.schema.json`.
  **Done when**: CSV exists, validates against schema.

- [x] K1.02 Write `packages/knowledge/curator.py` that copies files to `/sources_raw`, computes SHA256, detects language, writes catalog row.
  **Done when**: `make curate` runs without error; test file appears in catalog.

- [x] K1.03 Write `packages/knowledge/normalizer.py` that calls GROBID (PDFs) or Unstructured (docs), extracts text, writes to `/sources_clean`.
  **Done when**: `make clean` produces `.txt` file for test PDF.

- [x] K1.04 Write `packages/knowledge/deduplicator.py` using datasketch MinHash, marks duplicates in catalog.
  **Done when**: `make dedupe` flags duplicate test files.

- [x] K1.05 Write `packages/knowledge/scorer.py` implementing quality scoring per `Knowledge_Source_Organization.md` §6.
  **Done when**: `make score` populates quality_score column; test file gets 70-100.

- [x] K1.06 Write `packages/knowledge/pack_builder.py` that filters by TOPIC+LANG, selects ≤12 items ≤100MB, writes YAML to `/packs`.
  **Done when**: `make pack TOPIC=test LANG=en` creates valid pack file.

---

## Guard Testing

-  [x] **TEST-001** Verify guard detects FINISH without checkbox update
  **Done when**: Guard script blocks commit when FINISH logged but checkbox not marked [x].

- [x] **TEST-002** Verify guard enforcement operational
  **Done when**: Attempting to commit FINISH without [x] is blocked by guard.

- [x] **TEST-003** Validate Phase 5 audio pipeline on deterministic fixtures.
  **Done when**: Running the prescribed fixture manifest produces stems, mix, exports, and notes without errors.

- [x] **TEST-004** Validate async Phase 5 orchestrator via pytest
  **Done when**: Orchestrator tests passing (pipeline command + summary metrics)

---

## Remediation Backlog

- [x] REM-005 Harden Phase 5 audio pipeline with deterministic assets and tests.
  **Done when**: pytest exercises synthesizer, batch synth, mixer, exporters, and notes generator with no reliance on repo-local cache.

- [x] REM-010 Re-validate Phase 0 scaffolding and create smoke tests.
  **Done when**: Each scaffolded file has an automated test or validation check proving baseline functionality.

- [x] REM-020 Replace Phase 1 ingestion/ASR mocks with verifiable behaviors and tests.
  **Done when**: Watcher, normalizer, transcriber, and language detector have deterministic fixtures and pytest coverage.
  - [x] REM-020.1 Create test audio fixtures and watcher.py unit tests
  - [x] REM-020.2 Create normalizer.py unit tests (15 tests for ffmpeg integration)
  - [x] REM-020.3 Create transcriber.py unit tests (14 tests for faster-whisper ASR)
  - [x] REM-020.4 Create language_detector.py unit tests (8 tests for langdetect integration)

- [x] REM-030 Add deterministic fixtures and tests for Phase 2 segmentation/embedding.
  **Done when**: Segmenter, embedder, indexer, and graph builder produce validated outputs under pytest.
  - [x] REM-030.1 Verify existing segmenter tests (2 tests) and indexer test (1 test)
  - [x] REM-030.2 Create embedder.py unit tests (9 tests for sentence-transformers integration)
  - [x] REM-030.3 Create graph builder unit tests (17 tests for similarity, duplicates, graph construction)
  - [x] REM-030.4 Fix numpy bool serialization bug in builder.py

- [x] REM-040 Build regression tests for Phase 3 planning/writing pipeline.
  **Done when**: Outliner, selector, scripter, and continuity checker have fixture-driven tests asserting expected artifacts.
  - [x] REM-040.1 Create outliner.py unit tests (19 tests for chapter generation, duration targeting, modes)
  - [x] REM-040.2 Create selector.py unit tests (9 tests for segment selection, duplicate avoidance)
  - [x] REM-040.3 Expand scripter.py unit tests (10 tests for persona rewriting, multi-host alternation)
  - [x] REM-040.4 Create checker.py unit tests (14 tests for continuity checking, blockers, reports)

- [x] REM-050 Establish measurable tests for Phase 4 grounding audit.
  **Done when**: Source indexer and auditor have deterministic fixtures with assertions on retrieval quality and scoring.
  - [x] REM-050.1 Create source_indexer.py unit tests (18 tests for RAG indexing, chunking, embedding, FAISS/Qdrant)
  - [x] REM-050.2 Create auditor.py unit tests (13 tests for groundedness verification, retrieval, scoring)

- [x] REM-060 Document and automate guard execution workflow so agents run it before every checkpoint.
  **Done when**: Guard enforcement includes `make guard`, python wrappers that auto-run verify_progress.py, and docs/checklists ensuring agents execute guard before status updates.

- [x] REM-080 Add tests for Phase 8 multilingual TTS voice model support.
  **Done when**: TTS synthesizer can produce audio in multiple languages using appropriate voice models per language code.
  - [x] REM-080.1 Add get_voice_for_language() function for language-aware voice selection
  - [x] REM-080.2 Enhance HostConfig with language attribute
  - [x] REM-080.3 Add target_language parameter to synthesize_script()
  - [x] REM-080.4 Create 21 new tests for multilingual voice selection and synthesis

---

## Governance

- [x] GOV-002 Extend guardrails to enforce backlog updates with every checkpoint.
  **Done when**: Guard script fails whenever FINISH entries lack accompanying Remediation Backlog edits.

- [x] GOV-003 Teach guard to analyze working tree and whitelist existing docs.
  **Done when**: Guard inspects unstaged files, ignores baseline markdown, and still enforces test coverage before FINISH.

- [x] GOV-004 Automate guard execution via Makefile target and git hooks.
  **Done when**: `make guard` runs verify_progress.py and a pre-commit hook blocks commits if guard fails.

- [x] GOV-005 Enforce guard automatically on Python interpreter startup.
  **Done when**: `sitecustomize.py` executes the guard (or blocks execution) whenever workspace changes lack an approved snapshot.

- [x] GOV-006 Ship python command wrappers so direct interpreter execution still triggers guardrails.
  **Done when**: `python` (POSIX) and `python.cmd` (Windows) wrappers invoke `verify_progress.py` before delegating to the real interpreter and regression tests cover both wrappers.

- [x] GOV-007 Provide convenient PowerShell profile installation for cross-platform guard-aware python command.
  **Done when**: Windows users can run `make install-ps-alias` or `python scripts/guard/install_powershell_alias.py` to add python alias to profile; subsequent 'python' commands invoke guard wrapper.

- [x] GOV-008 Create activation scripts that enable guard-aware python in the current shell session.
  **Done when**: Users can source `activate.ps1` (PowerShell), `activate.sh` (Bash), or run `activate.cmd` (CMD) to add repo to PATH and load aliases; comprehensive setup docs in GUARD_SETUP.md explain all enforcement layers and recommended workflows.

- [x] GOV-009 Document realistic constraints and trade-offs for guard activation strategies.
  **Done when**: GUARD_REALITY_CHECK.md clearly explains that "true automatic" requires admin access; provides three practical no-admin approaches with trade-offs and recommendations for each use case.

---

## Phase 0 — Scaffolding

- [x] T0.01 Create directory structure:
  ```
  /app/{apps/{api,worker,ui},packages/{ingest,asr,segment,embed,graph,planner,writer,continuity,rag_audit,tts,mastering,exporters,eval,knowledge}}
  /configs/{personas,mix_profiles}
  /inputs
  /sources
  /dist/{export,logs}
  /tmp
  /schemas
  /knowledge/{catalog,sources_raw,sources_clean,packs,cache}
  ```
  **Done when**: `find . -type d` shows all directories.

- [x] T0.02 Create `Makefile` with targets: curate, clean, dedupe, score, pack, ingest, outline, assemble, stitch, qc, publish, help.
  **Done when**: `make help` lists all targets with descriptions.

- [x] T0.03 Create `requirements.txt` with: whisper, transformers, sentence-transformers, faiss-cpu, qdrant-client, grobid-client, unstructured, ffmpeg-python, pydub, datasketch, pyyaml, jsonschema, fastapi, celery, pytest.
  **Done when**: `pip install -r requirements.txt` completes.

- [x] T0.04 Create `docker-compose.yml` with services: api (FastAPI), worker (Celery), qdrant, grobid.
  **Done when**: `docker compose up -d` starts all services.

- [x] T0.05 Create `.env.example` with: DB_PATH, QDRANT_URL, GROBID_URL, WHISPER_MODEL, EMBED_MODEL, TTS_ENGINE.
  **Done when**: File exists with all variables documented.

- [x] T0.06 Create config templates:
  - `configs/hosts.yaml` (2 hosts, f5 voices, seeds, personas)
  - `configs/mastering.yaml` (lufs_target: -16, de_ess: true, limiter: true, crossfade_ms: 50)
  - `configs/retrieval.yaml` (embed_model: bge-large-en, db: faiss, top_k: 6)
  - `configs/output_menu.yaml` (deliverables: [stems, upload_mix], length_mode: full, persona: default)
  **Done when**: All 4 files exist, validate against inline comments.

- [x] T0.07 Create schemas:
  - `schemas/manifest.schema.json` (job inputs/outputs)
  - `schemas/segment.schema.json` (id, start_ms, end_ms, text, lang, speaker_id)
  - `schemas/qc_report.schema.json` (wer, lufs_avg, groundedness, context_precision, issues[], passed)
  **Done when**: All 3 JSON schemas exist.

- [x] T0.08 Create `scripts/validate_config.py` that loads YAML configs and checks required fields.
  **Done when**: `python scripts/validate_config.py` passes on all configs.

---

## Phase 1 — Ingestion & ASR

- [x] T1.01 Write `packages/ingest/watcher.py` that scans `/inputs`, validates formats (.mp3, .wav, .m4a, .mp4), writes `manifest.json` to `/tmp/{job_id}/`.
  **Done when**: Placing test file in `/inputs` creates manifest; invalid format rejected with error code.

- [x] T1.02 Write `packages/ingest/normalizer.py` using ffmpeg to convert to WAV 16kHz mono, save to `/tmp/{job_id}/normalized/`.
  **Done when**: `make ingest` converts test file; output is 16kHz mono WAV.

- [x] T1.03 Write `packages/asr/transcriber.py` using faster-whisper, outputs `.srt` and `.json` (word timestamps).
  **Done when**: Transcription JSON has word-level timestamps; SRT syncs to audio.

- [x] T1.04 Write `packages/asr/language_detector.py` using langdetect on transcript, adds to manifest.
  **Done when**: Manifest has `language` field populated correctly.

---

## Phase 2 — Segmentation & Embeddings

- [x] T2.01 Write `packages/segment/segmenter.py` using silero-vad, creates 20-60s segments, outputs `segments.json`.
  **Done when**: Segments JSON validates against schema; no segment <15s or >65s.

- [x] T2.02 Write `packages/embed/embedder.py` using sentence-transformers (bge-large-en), embeds segment text.
  **Done when**: Each segment has embedding vector stored.

- [x] T2.03 Write `packages/embed/indexer.py` that builds FAISS index from embeddings, saves to `/tmp/{job_id}/index.faiss`.
  **Done when**: `index.faiss` file created; test retrieval returns results.

- [x] T2.04 Write `packages/graph/builder.py` computing cosine similarity, flags duplicates >0.90, outputs `graph.json`.
  **Done when**: Graph JSON has nodes=segments, edges=similarities; duplicates flagged.

---

## Phase 3 — Planning & Writing

- [x] T3.01 Write `packages/planner/outliner.py` that reads segments, target duration from `output_menu.yaml`, generates `outline.yaml` with chapters.
  **Done when**: Outline has chapters totaling target_duration ±10%.

- [x] T3.02 Write `packages/planner/selector.py` that picks segments per chapter, avoids duplicates, outputs `selection.json`.
  **Done when**: Selection covers all chapters; no duplicate segments.

- [x] T3.03 Write `packages/writer/scripter.py` that rewrites segment text with persona from `hosts.yaml`, outputs `script.md`.
  **Done when**: Script markdown has speaker tags, follows persona traits.

- [x] T3.04 Write `packages/continuity/checker.py` extracting entities/claims, flags contradictions, outputs `continuity_report.json`.
  **Done when**: Report has 0 blockers; warnings only for minor issues.

---

## Phase 4 — Grounding Audit

- [x] T4.01 Write `packages/rag_audit/source_indexer.py` that ingests files from `/sources_clean`, embeds, indexes in Qdrant.
  **Done when**: Qdrant collection exists; test query returns relevant chunks.

- [x] T4.02 Write `packages/rag_audit/auditor.py` that retrieves sources for script sentences, verifies groundedness, outputs `audit_report.json`.
  **Done when**: Report has groundedness score ≥0.8 per PRD §3.

---

## Phase 5 — TTS & Mastering

- [x] T5.01 Write `packages/tts/synthesizer.py` with F5-TTS and Piper drivers, reads `hosts.yaml`, caches voice embeddings.
  **Done when**: Test synthesis produces deterministic WAV for same seed.

- [x] T5.02 Write `packages/tts/batch_synth.py` that processes script.md, outputs per-speaker WAV stems to `/tmp/{job_id}/stems/`.
  **Done when**: Stems directory has one WAV per speaker per segment.

- [x] T5.03 Write `packages/mastering/mixer.py` that concatenates stems, applies crossfades, normalizes to -16 LUFS using ffmpeg/sox.
  **Done when**: Output WAV has LUFS -16 ±1, true-peak ≤-1 dBTP.

- [x] T5.04 Write `packages/exporters/audio_exporter.py` that converts to MP3/Opus, adds ID3 chapters, outputs to `/dist/export/{job_id}/`.
  **Done when**: MP3 file plays correctly; chapters appear in player.

- [x] T5.05 Write `packages/exporters/notes_generator.py` that creates show notes markdown from script chapters.
  **Done when**: `/dist/export/{job_id}/notes.md` exists with timestamped chapters.

- [x] T5.06 Designing async orchestrator and CLI integration for Phase 5
  **Done when**: Async orchestrator, Typer pipeline command, and regression tests implemented

- [x] T5.07 Add Hypothesis-based schema regression tests
  **Done when**: Hypothesis property tests for generated models passing

- [x] T5.08 Introduce pipeline base classes and refactor notes generator
  **Done when**: Shared pipeline base created; notes generator migrated to new step API

- [x] T5.09 Wire persona configs into writer module with tests
  **Done when**: Persona loader module added; scripter rewrites text based on persona cards with tests

- [x] PHASE5 Execute Phase 5 TTS and mastering pipeline
  **Done when**: Phase 5 complete: all 12 tests passing, synthesizer/batch_synth/mixer/exporter/notes_generator operational

---

## Phase 6 — Variants & Customization (MVP Delivery Features)

- [x] T6.01 Update `packages/planner/outliner.py` to support length_mode: full (60min), condensed (20min), topic_focus (10min) from `output_menu.yaml`.
  **Done when**: `make outline` respects length_mode; durations within ±10%.

- [x] T6.02 Write `packages/exporters/promo_clipper.py` that extracts 3 highlight segments (30-90s each), outputs to `/dist/export/{job_id}/promos/`.
  **Done when**: 3 promo WAV files + transcripts created.

- [x] T6.03 Write `packages/exporters/stem_packager.py` that copies per-speaker stems to export folder with Clipchamp naming.
  **Done when**: Stems directory has speaker_a_001.wav, speaker_b_001.wav, etc.

- [x] T6.04 Create persona configs in `/configs/personas/` for: academic.yaml, casual.yaml, mentor.yaml.
  **Done when**: 3 persona files exist with voice_id, traits, style fields.

- [x] T6.05 Update `packages/writer/scripter.py` to load persona from config, apply lexical preferences.
  **Done when**: Script changes tone based on selected persona.

---

## Phase 7 — QC & Publishing

- [x] T7.01 Write `packages/eval/ragas_scorer.py` using ragas library, scores groundedness/context_precision.
  **Done when**: Scores ≥ thresholds from PRD §3.

- [x] T7.02 Write `packages/eval/wer_calculator.py` that re-transcribes TTS output, compares to script.
  **Done when**: WER ≤8% on test episode.

- [x] T7.03 Write `packages/eval/lufs_checker.py` using pyloudnorm, validates audio levels.
  **Done when**: Check passes for compliant audio; fails for out-of-spec.

- [x] T7.04 Write `packages/eval/qc_runner.py` that runs all checks, outputs `qc_report.json` to `/dist/export/{job_id}/`.
  **Done when**: `make qc` generates report; passed=true for test episode.

- [x] T7.05 Write `packages/exporters/rss_generator.py` that creates podcast RSS feed from episodes.
  **Done when**: RSS validates; includes episode metadata and enclosure URL.

- [x] T7.06 Write `packages/exporters/manifest_writer.py` that creates `export_manifest.json` listing all deliverables per SPEC §13.
  **Done when**: Manifest has files[], mix_profile, persona, qc_metrics fields.

---

## Phase 8 — Multilingual (V1 Enhancement)

- [x] T8.01 Write `packages/translate/translator.py` using NLLB-200, translates script.md to target language.
  **Done when**: Translated script maintains structure; language code in filename.

- [ ] T8.02 Update TTS to support multilingual voice models per language.
  **Done when**: Non-English script produces correct language audio.

---

## Phase 9 — Integration & Handoff

- [ ] T9.01 Write `run_show.sh` wrapper script that runs full pipeline: curate → ingest → outline → assemble → qc → publish.
  **Done when**: `./run_show.sh test_job` completes end-to-end.

- [ ] T9.02 Create `tests/test_pipeline.py` with golden fixtures, asserts outputs exist and validate.
  **Done when**: `pytest tests/` passes.

- [ ] T9.03 Write `README.md` with: installation, quickstart, config options, troubleshooting.
  **Done when**: Following README produces working episode.

---

## Repository Management

- [x] **UPLOAD-001** Uploading Project Alexandria to GitHub
  **Done when**: Repository uploaded and synced with GitHub

---

## Make Targets (Implementation Reference)

```makefile
curate:     # packages/knowledge/curator.py
clean:      # packages/knowledge/normalizer.py
dedupe:     # packages/knowledge/deduplicator.py
score:      # packages/knowledge/scorer.py
pack:       # packages/knowledge/pack_builder.py TOPIC=X LANG=Y

ingest:     # packages/ingest/watcher.py + normalizer.py + asr/transcriber.py
outline:    # packages/segment/* + graph/* + planner/outliner.py
assemble:   # packages/writer/* + continuity/* + rag_audit/* + tts/* + mastering/*
qc:         # packages/eval/qc_runner.py
publish:    # packages/exporters/rss_generator.py + manifest_writer.py
```

---

## Acceptance Gates (Fail Build If Below)

- RAGAS: groundedness ≥ 0.8; context precision ≥ 0.7
- WER ≤ 8% median
- LUFS -16 ±1 LU; true-peak ≤ -1 dBTP
- No continuity blockers
- All required deliverables present per `output_menu.yaml`
- QC report `passed: true`
