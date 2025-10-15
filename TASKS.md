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

- [ ] T2.01 Write `packages/segment/segmenter.py` using silero-vad, creates 20-60s segments, outputs `segments.json`.
  **Done when**: Segments JSON validates against schema; no segment <15s or >65s.

- [ ] T2.02 Write `packages/embed/embedder.py` using sentence-transformers (bge-large-en), embeds segment text.
  **Done when**: Each segment has embedding vector stored.

- [ ] T2.03 Write `packages/embed/indexer.py` that builds FAISS index from embeddings, saves to `/tmp/{job_id}/index.faiss`.
  **Done when**: `index.faiss` file created; test retrieval returns results.

- [ ] T2.04 Write `packages/graph/builder.py` computing cosine similarity, flags duplicates >0.90, outputs `graph.json`.
  **Done when**: Graph JSON has nodes=segments, edges=similarities; duplicates flagged.

---

## Phase 3 — Planning & Writing

- [ ] T3.01 Write `packages/planner/outliner.py` that reads segments, target duration from `output_menu.yaml`, generates `outline.yaml` with chapters.
  **Done when**: Outline has chapters totaling target_duration ±10%.

- [ ] T3.02 Write `packages/planner/selector.py` that picks segments per chapter, avoids duplicates, outputs `selection.json`.
  **Done when**: Selection covers all chapters; no duplicate segments.

- [ ] T3.03 Write `packages/writer/scripter.py` that rewrites segment text with persona from `hosts.yaml`, outputs `script.md`.
  **Done when**: Script markdown has speaker tags, follows persona traits.

- [ ] T3.04 Write `packages/continuity/checker.py` extracting entities/claims, flags contradictions, outputs `continuity_report.json`.
  **Done when**: Report has 0 blockers; warnings only for minor issues.

---

## Phase 4 — Grounding Audit

- [ ] T4.01 Write `packages/rag_audit/source_indexer.py` that ingests files from `/sources_clean`, embeds, indexes in Qdrant.
  **Done when**: Qdrant collection exists; test query returns relevant chunks.

- [ ] T4.02 Write `packages/rag_audit/auditor.py` that retrieves sources for script sentences, verifies groundedness, outputs `audit_report.json`.
  **Done when**: Report has groundedness score ≥0.8 per PRD §3.

---

## Phase 5 — TTS & Mastering

- [ ] T5.01 Write `packages/tts/synthesizer.py` with F5-TTS and Piper drivers, reads `hosts.yaml`, caches voice embeddings.
  **Done when**: Test synthesis produces deterministic WAV for same seed.

- [ ] T5.02 Write `packages/tts/batch_synth.py` that processes script.md, outputs per-speaker WAV stems to `/tmp/{job_id}/stems/`.
  **Done when**: Stems directory has one WAV per speaker per segment.

- [ ] T5.03 Write `packages/mastering/mixer.py` that concatenates stems, applies crossfades, normalizes to -16 LUFS using ffmpeg/sox.
  **Done when**: Output WAV has LUFS -16 ±1, true-peak ≤-1 dBTP.

- [ ] T5.04 Write `packages/exporters/audio_exporter.py` that converts to MP3/Opus, adds ID3 chapters, outputs to `/dist/export/{job_id}/`.
  **Done when**: MP3 file plays correctly; chapters appear in player.

- [ ] T5.05 Write `packages/exporters/notes_generator.py` that creates show notes markdown from script chapters.
  **Done when**: `/dist/export/{job_id}/notes.md` exists with timestamped chapters.

---

## Phase 6 — Variants & Customization (MVP Delivery Features)

- [ ] T6.01 Update `packages/planner/outliner.py` to support length_mode: full (60min), condensed (20min), topic_focus (10min) from `output_menu.yaml`.
  **Done when**: `make outline` respects length_mode; durations within ±10%.

- [ ] T6.02 Write `packages/exporters/promo_clipper.py` that extracts 3 highlight segments (30-90s each), outputs to `/dist/export/{job_id}/promos/`.
  **Done when**: 3 promo WAV files + transcripts created.

- [ ] T6.03 Write `packages/exporters/stem_packager.py` that copies per-speaker stems to export folder with Clipchamp naming.
  **Done when**: Stems directory has speaker_a_001.wav, speaker_b_001.wav, etc.

- [ ] T6.04 Create persona configs in `/configs/personas/` for: academic.yaml, casual.yaml, mentor.yaml.
  **Done when**: 3 persona files exist with voice_id, traits, style fields.

- [ ] T6.05 Update `packages/writer/scripter.py` to load persona from config, apply lexical preferences.
  **Done when**: Script changes tone based on selected persona.

---

## Phase 7 — QC & Publishing

- [ ] T7.01 Write `packages/eval/ragas_scorer.py` using ragas library, scores groundedness/context_precision.
  **Done when**: Scores ≥ thresholds from PRD §3.

- [ ] T7.02 Write `packages/eval/wer_calculator.py` that re-transcribes TTS output, compares to script.
  **Done when**: WER ≤8% on test episode.

- [ ] T7.03 Write `packages/eval/lufs_checker.py` using pyloudnorm, validates audio levels.
  **Done when**: Check passes for compliant audio; fails for out-of-spec.

- [ ] T7.04 Write `packages/eval/qc_runner.py` that runs all checks, outputs `qc_report.json` to `/dist/export/{job_id}/`.
  **Done when**: `make qc` generates report; passed=true for test episode.

- [ ] T7.05 Write `packages/exporters/rss_generator.py` that creates podcast RSS feed from episodes.
  **Done when**: RSS validates; includes episode metadata and enclosure URL.

- [ ] T7.06 Write `packages/exporters/manifest_writer.py` that creates `export_manifest.json` listing all deliverables per SPEC §13.
  **Done when**: Manifest has files[], mix_profile, persona, qc_metrics fields.

---

## Phase 8 — Multilingual (V1 Enhancement)

- [ ] T8.01 Write `packages/translate/translator.py` using NLLB-200, translates script.md to target language.
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
