# ALEXANDRIA SYSTEM ANALYSIS - COMPLETE STATE REPORT

**Analysis Date**: 2025-10-19
**Current Status**: Phases 0-7 Complete (70% of MVP)
**Files**: 59 Python modules, 15 configs, 24 test files

---

## EXECUTIVE SUMMARY

### What Alexandria Is
A podcast generation pipeline that transforms knowledge sources (NotebookLM exports, PDFs, documents) into professional podcast audio with configurable personas, multiple output formats, and comprehensive quality control.

### Current State
- **7 of 9 phases complete**
- **~60 Python modules** implemented
- **10 configurable personas**
- **Full QC suite** operational
- **Mock TTS/ASR** (needs real implementation)

### What Works Right Now
✅ End-to-end pipeline from source → script → mock audio
✅ Multi-persona script generation (10 personas)
✅ Quality control and validation
✅ Export packaging and RSS generation
✅ Length mode variants (full/condensed/topic_focus)
✅ Promo clip extraction and stem packaging

### What's Missing
❌ Real TTS engines (F5-TTS, Piper)
❌ Real ASR (Whisper integration)
❌ Actual audio processing (ffmpeg operations)
❌ Vector embeddings (sentence-transformers)
❌ RAG retrieval (Qdrant)
❌ End-to-end integration tests
❌ Docker deployment
❌ API/Worker services

---

## SYSTEM ARCHITECTURE

### Pipeline Flow

```
INPUT → KNOWLEDGE ORG → INGESTION → SEGMENTATION → PLANNING →
WRITING → GROUNDING → TTS → MASTERING → QC → PUBLISHING → OUTPUT
```

### Detailed Flow

**Phase K: Knowledge Organization**
```
PDFs/Docs → Curator → Normalizer → Deduplicator → Scorer → Knowledge Packs
```

**Phase 1: Ingestion & ASR**
```
Audio → Watcher → ffmpeg Normalize → Whisper → Language Detect → Transcript
```

**Phase 2: Segmentation & Embeddings**
```
Transcript → Segmenter → Embedder → FAISS Indexer → Graph Builder → Segments
```

**Phase 3: Planning & Writing**
```
Segments → Outliner → Selector → Scripter (w/ Persona) → Continuity Check → Script
```

**Phase 4: Grounding Audit**
```
Sources + Script → RAG Indexer → Auditor → Groundedness Report
```

**Phase 5: TTS & Mastering**
```
Script → TTS Synthesizer → Batch Stems → Mixer → Audio Exporter → Final Mix
```

**Phase 6: Variants**
```
Segments → Promo Clipper → Highlight Clips
Stems → Stem Packager → Clipchamp Export
```

**Phase 7: QC & Publishing**
```
Mix → RAGAS/WER/LUFS Checks → QC Runner → RSS Feed + Manifest → Publish
```

---

## PHASE-BY-PHASE STATUS

### ✅ Phase 0: Scaffolding - COMPLETE
**Files**: Makefile, requirements.txt, docker-compose.yml, configs/*, schemas/*

**Capabilities:**
- Complete directory structure
- Make targets for all phases
- Configuration templates (hosts, mastering, retrieval, output_menu)
- JSON schemas (manifest, segment, qc_report)
- Config validation script

**Gaps:**
- Docker services not tested
- Some dependencies not installed

---

### ✅ Phase K: Knowledge Organization - COMPLETE (MOCK)
**Location**: `app/packages/knowledge/`
**Files**: curator.py, normalizer.py, deduplicator.py, scorer.py, pack_builder.py

**What Works:**
- File cataloging with SHA256
- CSV-based tracking
- Knowledge pack creation by topic/language
- Quality scoring heuristics

**What's Mock:**
- GROBID/Unstructured extraction (needs Docker services)
- MinHash deduplication (needs datasketch library)

**To Make Real:**
1. Install GROBID via Docker
2. Add datasketch library
3. Test with real PDFs

---

### ✅ Phase 1: Ingestion & ASR - COMPLETE (MOCK ASR)
**Location**: `app/packages/ingest/`, `app/packages/asr/`
**Files**: watcher.py, normalizer.py, transcriber.py, language_detector.py

**What Works:**
- Format validation (.mp3, .wav, .m4a, .mp4)
- Manifest generation
- Language detection (langdetect)

**What's Mock:**
- ffmpeg normalization (creates placeholder files)
- Whisper transcription (returns mock text)

**To Make Real:**
1. Install faster-whisper
2. Implement real ffmpeg calls
3. Test with audio files

**Critical Priority**: ⚠️ HIGH - Blocks real pipeline testing

---

### ✅ Phase 2: Segmentation & Embeddings - COMPLETE (MOCK EMBEDDINGS)
**Location**: `app/packages/segment/`, `app/packages/embed/`, `app/packages/graph/`
**Files**: segmenter.py, embedder.py, indexer.py, builder.py

**What Works:**
- Segment creation (20-60s chunks)
- Schema validation
- Similarity graph computation
- Duplicate detection (>0.90 threshold)

**What's Mock:**
- Sentence embeddings (uses random vectors)
- FAISS indexing (creates placeholder)

**To Make Real:**
1. Install sentence-transformers
2. Install faiss-cpu
3. Load bge-large-en model
4. Test retrieval

**Critical Priority**: ⚠️ MEDIUM - Affects content quality

---

### ✅ Phase 3: Planning & Writing - COMPLETE
**Location**: `app/packages/planner/`, `app/packages/writer/`, `app/packages/continuity/`
**Files**: outliner.py, selector.py, scripter.py, checker.py, persona_loader.py

**What Works:**
✅ Length modes (full=60min, condensed=20min, topic_focus=10min)
✅ Segment selection with duplicate avoidance
✅ 10 personas (academic, casual, coach, educator, enthusiast, journalist, mentor, philosopher, storyteller, technical)
✅ Persona auto-discovery from configs/personas/
✅ Lexical preference application
✅ output_menu.yaml integration

**What's Mock:**
- LLM-based rewriting (uses simple string replacement)
- Continuity checking (placeholder logic)

**To Make Real (Optional):**
1. Add OpenAI/Anthropic API for real style transfer
2. Implement entity/claim extraction for continuity

**Priority**: 🔵 LOW - Current implementation functional

---

### ✅ Phase 4: Grounding Audit - COMPLETE (MOCK RAG)
**Location**: `app/packages/rag_audit/`
**Files**: source_indexer.py, auditor.py

**What Works:**
- Report generation framework
- Groundedness scoring structure

**What's Mock:**
- Qdrant indexing (no vector DB)
- RAG retrieval (mock scores)

**To Make Real:**
1. Install qdrant-client
2. Run Qdrant via Docker
3. Index sources with embeddings
4. Implement retrieval

**Priority**: ⚠️ MEDIUM - Important for quality, but not blocking

---

### ✅ Phase 5: TTS & Mastering - COMPLETE (MOCK TTS/AUDIO)
**Location**: `app/packages/tts/`, `app/packages/mastering/`, `app/packages/exporters/`
**Files**: synthesizer.py, batch_synth.py, mixer.py, audio_exporter.py, notes_generator.py

**What Works:**
- Deterministic file generation
- Voice caching framework
- Pipeline orchestration
- Show notes generation

**What's Mock:**
- TTS synthesis (creates empty WAV files)
- LUFS normalization (no actual processing)
- ffmpeg operations (file copies only)
- Chapter markers (metadata only)

**To Make Real:**
1. Install F5-TTS or Piper
2. Install ffmpeg-python
3. Install pyloudnorm
4. Implement real audio concatenation
5. Implement LUFS measurement

**Critical Priority**: 🔴 HIGHEST - Blocks audio output

---

### ✅ Phase 6: Variants & Customization - COMPLETE
**Location**: `app/packages/exporters/`, `configs/personas/`
**Files**: promo_clipper.py, stem_packager.py, 10 persona configs

**What Works:**
✅ Promo clip extraction (30-90s highlights)
✅ Scoring algorithm (duration/density/position)
✅ Stem packaging with Clipchamp naming
✅ Speaker detection from script
✅ 10 diverse personas
✅ Unlimited persona support
✅ Persona discovery CLI

**No Gaps**: Fully functional!

---

### ✅ Phase 7: QC & Publishing - COMPLETE (MOCK METRICS)
**Location**: `app/packages/eval/`, `app/packages/exporters/`
**Files**: ragas_scorer.py, wer_calculator.py, lufs_checker.py, qc_runner.py, rss_generator.py, manifest_writer.py

**What Works:**
✅ QC orchestration (5 check types)
✅ Pass/fail reporting
✅ WER calculation (Levenshtein distance)
✅ RSS feed generation
✅ Export manifest

**What's Mock:**
- RAGAS library integration
- Actual LUFS measurement
- Real TTS transcription for WER

**To Make Real:**
1. Install ragas library
2. Connect to real LUFS checker
3. Use real TTS output for WER

**Priority**: 🔵 LOW - Framework solid, metrics can be upgraded later

---

### ❌ Phase 8: Multilingual - NOT STARTED
**Tasks:**
- T8.01: NLLB-200 translator
- T8.02: Multilingual TTS voices

**Priority**: 🟢 FUTURE - V1 enhancement

---

### ❌ Phase 9: Integration & Handoff - NOT STARTED
**Tasks:**
- T9.01: run_show.sh wrapper script
- T9.02: Golden fixture end-to-end tests
- T9.03: README documentation

**Priority**: ⚠️ HIGH - Needed for MVP delivery

---

## DEPENDENCY STATUS

### Installed ✅
- pydantic (2.0+)
- yaml, json (config)
- pytest, hypothesis (testing)
- typer (CLI)
- datamodel-code-generator

### Missing ❌ (Critical)
```bash
# ASR
faster-whisper

# Embeddings & Vector Search
sentence-transformers
faiss-cpu
qdrant-client

# Audio Processing
ffmpeg-python
pyloudnorm

# TTS
# F5-TTS (external repo)
# Piper (external binary)

# RAG Evaluation
ragas

# Knowledge Processing
datasketch
grobid-client
unstructured

# Worker System
celery
redis
```

### Install Command (Partial)
```bash
pip install faster-whisper sentence-transformers faiss-cpu qdrant-client \
    ffmpeg-python pyloudnorm ragas datasketch unstructured celery redis
```

**Note**: F5-TTS and Piper require separate installation

---

## INFRASTRUCTURE STATUS

### Docker Services (docker-compose.yml)
| Service | Status | Purpose |
|---------|--------|---------|
| api (FastAPI) | ❌ Stub only | REST API |
| worker (Celery) | ❌ Stub only | Async tasks |
| qdrant | ❌ Not configured | Vector DB |
| grobid | ❌ Not configured | PDF extraction |
| redis | ❌ Not configured | Task queue |

**To Deploy:**
```bash
docker-compose up -d
# Then verify services
docker-compose ps
```

---

## TEST COVERAGE

### Current Tests (37 total)
- ✅ Phase 5 TTS modules (12 tests)
- ✅ Generated models (Hypothesis - 11 tests)
- ✅ API orchestration (1 test)
- ✅ Integration (1 test)
- ❌ Phases 1-4 (no tests)
- ❌ Phases 6-7 (no tests)

### Coverage Estimate: ~30%

### Missing Tests
- Phase 1: ASR pipeline
- Phase 2: Embeddings/graph
- Phase 3: Planning/writing
- Phase 4: RAG audit
- Phase 6: Exporters
- Phase 7: QC checks
- End-to-end: Golden fixtures

---

## BUILD ROADMAP FROM HERE

### MILESTONE 1: Make Audio Real (HIGHEST PRIORITY)
**Goal**: Get one real audio file out

**Tasks:**
1. ✅ Install faster-whisper
2. ✅ Implement real transcription in transcriber.py
3. ✅ Install F5-TTS or Piper
4. ✅ Implement real TTS in synthesizer.py
5. ✅ Install ffmpeg
6. ✅ Implement real mixing in mixer.py
7. ✅ Install pyloudnorm
8. ✅ Implement LUFS measurement
9. ✅ Test end-to-end: audio → transcript → script → TTS → mix

**Deliverable**: One real podcast episode from test audio

**Estimated Effort**: 2-3 days

---

### MILESTONE 2: Make Embeddings Real (HIGH PRIORITY)
**Goal**: Enable semantic search and RAG

**Tasks:**
1. ✅ Install sentence-transformers
2. ✅ Load bge-large-en model
3. ✅ Implement real embeddings in embedder.py
4. ✅ Install faiss-cpu
5. ✅ Build real FAISS index in indexer.py
6. ✅ Install Qdrant via Docker
7. ✅ Implement source indexing in source_indexer.py
8. ✅ Implement RAG retrieval in auditor.py
9. ✅ Test: sources → embeddings → RAG → groundedness score

**Deliverable**: Working RAG grounding verification

**Estimated Effort**: 1-2 days

---

### MILESTONE 3: Complete Integration (MEDIUM PRIORITY)
**Goal**: End-to-end pipeline working

**Tasks:**
1. ✅ Write run_show.sh wrapper (Phase 9)
2. ✅ Create golden fixture (Phase 9)
3. ✅ Write end-to-end test (Phase 9)
4. ✅ Test full pipeline: input → audio output
5. ✅ Fix any integration issues
6. ✅ Document in README (Phase 9)

**Deliverable**: Documented, tested pipeline

**Estimated Effort**: 2 days

---

### MILESTONE 4: Deploy Services (MEDIUM PRIORITY)
**Goal**: Docker deployment working

**Tasks:**
1. ✅ Configure Qdrant service
2. ✅ Configure GROBID service
3. ✅ Configure Redis
4. ✅ Implement FastAPI routes in api/main.py
5. ✅ Implement Celery tasks in worker/celery_app.py
6. ✅ Test Docker deployment
7. ✅ Add health checks

**Deliverable**: Containerized deployment

**Estimated Effort**: 2-3 days

---

### MILESTONE 5: Fill Test Gaps (LOW PRIORITY)
**Goal**: 80%+ test coverage

**Tasks:**
1. ✅ Add Phase 1 tests (ingestion/ASR)
2. ✅ Add Phase 2 tests (segmentation/embeddings)
3. ✅ Add Phase 3 tests (planning/writing)
4. ✅ Add Phase 4 tests (RAG audit)
5. ✅ Add Phase 6 tests (exporters)
6. ✅ Add Phase 7 tests (QC)
7. ✅ Run full test suite, fix failures

**Deliverable**: Comprehensive test suite

**Estimated Effort**: 3-4 days

---

### MILESTONE 6: Add Multilingual (FUTURE)
**Goal**: Phase 8 complete

**Tasks:**
1. ✅ Install NLLB-200
2. ✅ Implement translator.py
3. ✅ Add multilingual voice configs
4. ✅ Update TTS for language switching
5. ✅ Test with non-English content

**Deliverable**: Multilingual support

**Estimated Effort**: 2 days

---

## CRITICAL PATH TO MVP

**To get a working MVP (v0.1):**

```
Week 1: Audio Pipeline
├─ Day 1-2: Install Whisper, test transcription
├─ Day 3-4: Install TTS (F5 or Piper), test synthesis
└─ Day 5: Install ffmpeg, implement mixing

Week 2: Embeddings & Integration
├─ Day 1-2: Install embeddings, FAISS, Qdrant
├─ Day 3: Implement RAG retrieval
├─ Day 4-5: End-to-end testing

Week 3: Polish & Deploy
├─ Day 1-2: Write wrapper script, README
├─ Day 3-4: Docker deployment
└─ Day 5: Final testing, MVP release
```

**Total Effort**: ~3 weeks for functional MVP

---

## IMMEDIATE NEXT STEPS

### Step 1: Install Critical Dependencies
```bash
# ASR
pip install faster-whisper

# Audio
pip install ffmpeg-python pyloudnorm

# Embeddings
pip install sentence-transformers faiss-cpu

# Vector DB
docker run -d -p 6333:6333 qdrant/qdrant

# TTS (choose one)
# Option A: Piper (simpler)
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz
# Option B: F5-TTS (better quality)
git clone https://github.com/SWivid/F5-TTS && cd F5-TTS && pip install -e .
```

### Step 2: Replace Mocks
Priority order:
1. **transcriber.py** - Add Whisper
2. **synthesizer.py** - Add TTS engine
3. **mixer.py** - Add real ffmpeg
4. **embedder.py** - Add sentence-transformers
5. **source_indexer.py** - Add Qdrant

### Step 3: Test End-to-End
```bash
# Place test audio in inputs/
cp test.mp3 inputs/

# Run pipeline
make ingest JOB=test_001
make outline JOB=test_001
make assemble JOB=test_001
make qc JOB=test_001

# Verify output
ls dist/export/test_001/
# Should contain: output_mix.mp3, notes.md, qc_report.json, feed.xml
```

---

## CURRENT LIMITATIONS

### What You CANNOT Do Yet
❌ Process real audio (no Whisper)
❌ Generate real speech (no TTS)
❌ Mix actual audio (no ffmpeg)
❌ Semantic search (no embeddings)
❌ RAG grounding (no Qdrant)
❌ API access (no FastAPI)
❌ Async processing (no Celery)
❌ Multilingual (Phase 8)

### What You CAN Do Now
✅ Generate scripts with 10 personas
✅ Create outlines with 3 length modes
✅ Extract promo clips
✅ Package stems for Clipchamp
✅ Run QC checks (mock metrics)
✅ Generate RSS feeds
✅ Create export manifests

---

## ARCHITECTURE STRENGTHS

### What's Well-Designed
✅ **Modular pipeline** - Each phase independent
✅ **Config-driven** - No hardcoded values
✅ **Persona system** - Unlimited extensibility
✅ **Schema validation** - Type safety
✅ **QC framework** - Comprehensive checks
✅ **Export variants** - Multiple formats

### What Needs Improvement
⚠️ **Mock implementations** - Replace with real
⚠️ **Test coverage** - Only ~30%
⚠️ **Error handling** - Basic try/catch
⚠️ **Logging** - Minimal
⚠️ **Performance** - No optimization
⚠️ **Documentation** - Incomplete

---

## CONCLUSION

### Summary
Alexandria is **70% complete** with solid architecture and modular design. The framework is in place, but most AI/audio operations are mocked.

### To Ship MVP
**Focus on Milestone 1-3**: Install real dependencies, replace mocks, test end-to-end.

### Estimated Timeline
- **Functional MVP**: 3 weeks
- **Production-ready**: 6-8 weeks
- **V1 with multilingual**: 10-12 weeks

### Risk Assessment
🔴 **High Risk**: TTS/ASR integration complexity
🟡 **Medium Risk**: Docker deployment issues
🟢 **Low Risk**: Config/persona system (already solid)

---

**Next Action**: Choose TTS engine (F5 vs Piper) and install dependencies.
