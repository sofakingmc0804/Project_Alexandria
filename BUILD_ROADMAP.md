# ALEXANDRIA BUILD ROADMAP
**From Current State → Production MVP**

---

## CURRENT STATE
```
✅ 70% Complete - Framework Built
├── ✅ Phases 0-7 implemented
├── ✅ 59 Python modules
├── ✅ 10 personas
├── ✅ QC framework
└── ❌ Most operations are MOCKED
```

---

## BUILD STRATEGY

### 🎯 Goal: Ship functional MVP in 3 weeks

**Strategy**: Replace mocks with real implementations, focusing on critical path

---

## WEEK 1: AUDIO PIPELINE 🔴 CRITICAL

### Day 1: ASR Setup
**Goal**: Real audio transcription working

```bash
# Install Whisper
pip install faster-whisper

# Test installation
python -c "from faster_whisper import WhisperModel; print('OK')"
```

**Tasks:**
- [ ] Update `transcriber.py` to use faster-whisper
- [ ] Load model: `base.en` (fast) or `large-v3` (accurate)
- [ ] Test with sample audio
- [ ] Verify SRT + JSON output

**File**: `app/packages/asr/transcriber.py`

**Code Changes:**
```python
# Replace mock with:
from faster_whisper import WhisperModel

model = WhisperModel("base.en", device="cpu", compute_type="int8")
segments, info = model.transcribe(audio_path, word_timestamps=True)
```

**Estimated**: 4 hours

---

### Day 2: TTS Selection & Setup
**Goal**: Choose TTS engine and get it working

**Option A: Piper (Recommended for MVP)**
```bash
# Download Piper
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz
tar -xzf piper_amd64.tar.gz

# Download voice model
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
```

**Pros**: Fast, lightweight, easy install
**Cons**: Lower quality than F5

**Option B: F5-TTS (Better Quality)**
```bash
git clone https://github.com/SWivid/F5-TTS
cd F5-TTS && pip install -e .
```

**Pros**: Higher quality, more natural
**Cons**: Slower, GPU recommended, harder setup

**Tasks:**
- [ ] Choose engine (recommend Piper for speed)
- [ ] Install and test
- [ ] Generate test audio
- [ ] Verify output quality

**Estimated**: 4-6 hours

---

### Day 3: TTS Integration
**Goal**: synthesizer.py produces real WAV files

**File**: `app/packages/tts/synthesizer.py`

**Code Changes:**
```python
# For Piper:
import subprocess

def synthesize_piper(text: str, voice_model: str, output_path: str):
    cmd = f'echo "{text}" | ./piper --model {voice_model} --output_file {output_path}'
    subprocess.run(cmd, shell=True, check=True)

# For F5-TTS:
from f5_tts import F5TTS

model = F5TTS.from_pretrained("F5-TTS")
wav = model.generate(text, voice_id=voice_id, seed=seed)
```

**Tasks:**
- [ ] Update `synthesize()` method
- [ ] Test voice caching
- [ ] Verify deterministic output (same seed → same audio)
- [ ] Test with persona voices

**Estimated**: 6-8 hours

---

### Day 4: Audio Mixing
**Goal**: Real ffmpeg operations, actual audio mixing

```bash
# Install ffmpeg
# Windows: choco install ffmpeg
# Linux: sudo apt install ffmpeg
# Mac: brew install ffmpeg

pip install ffmpeg-python
```

**File**: `app/packages/mastering/mixer.py`

**Code Changes:**
```python
import ffmpeg

def concatenate_stems(stem_files: List[Path], output: Path):
    inputs = [ffmpeg.input(str(f)) for f in stem_files]
    ffmpeg.concat(*inputs, v=0, a=1).output(str(output)).run()

def normalize_lufs(input_file: Path, output: Path, target_lufs: float = -16.0):
    ffmpeg.input(str(input_file)).filter(
        'loudnorm', I=target_lufs, TP=-1.5, LRA=11
    ).output(str(output)).run()
```

**Tasks:**
- [ ] Implement stem concatenation
- [ ] Add crossfades between segments
- [ ] Implement LUFS normalization
- [ ] Test with multi-speaker stems

**Estimated**: 6-8 hours

---

### Day 5: LUFS Measurement
**Goal**: Real audio level validation

```bash
pip install pyloudnorm
```

**File**: `app/packages/eval/lufs_checker.py`

**Code Changes:**
```python
import pyloudnorm as pyln
import soundfile as sf

def measure_lufs(audio_file: Path) -> dict:
    data, rate = sf.read(audio_file)
    meter = pyln.Meter(rate)
    loudness = meter.integrated_loudness(data)
    return {
        'integrated_lufs': loudness,
        'true_peak_dbtp': pyln.peak_normalize(data).max()
    }
```

**Tasks:**
- [ ] Replace mock measurements
- [ ] Test with real audio
- [ ] Verify compliance checks
- [ ] Update qc_runner integration

**Estimated**: 2-4 hours

---

### Week 1 Deliverable
✅ **Real audio pipeline**: audio file → transcript → TTS → mixed WAV

**Test Command:**
```bash
# End-to-end test
cp test.mp3 inputs/
make ingest JOB=week1_test
make outline JOB=week1_test
make assemble JOB=week1_test

# Verify output
file dist/export/week1_test/output_mix.wav
# Should be: RIFF (little-endian) data, WAVE audio, 16-bit
```

---

## WEEK 2: EMBEDDINGS & RAG 🟡 HIGH PRIORITY

### Day 1: Embedding Models
**Goal**: Real semantic embeddings

```bash
pip install sentence-transformers
```

**File**: `app/packages/embed/embedder.py`

**Code Changes:**
```python
from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self):
        self.model = SentenceTransformer('BAAI/bge-large-en-v1.5')

    def embed(self, texts: List[str]) -> np.ndarray:
        return self.model.encode(texts, show_progress_bar=True)
```

**Tasks:**
- [ ] Install model (~2GB download)
- [ ] Update embedder.py
- [ ] Test with segment texts
- [ ] Verify embedding dimensions (1024 for bge-large)

**Estimated**: 4 hours

---

### Day 2: Vector Search
**Goal**: FAISS index working

```bash
pip install faiss-cpu  # or faiss-gpu if available
```

**File**: `app/packages/embed/indexer.py`

**Code Changes:**
```python
import faiss

def build_index(embeddings: np.ndarray) -> faiss.Index:
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # Inner product (cosine similarity)
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
    return index

def search(index: faiss.Index, query: np.ndarray, k: int = 5):
    faiss.normalize_L2(query)
    distances, indices = index.search(query, k)
    return indices, distances
```

**Tasks:**
- [ ] Implement real indexing
- [ ] Test retrieval
- [ ] Save/load index to disk
- [ ] Verify similarity scores

**Estimated**: 4 hours

---

### Day 3: Qdrant Setup
**Goal**: Vector database running

```bash
# Start Qdrant
docker run -d -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant

# Install client
pip install qdrant-client
```

**File**: `app/packages/rag_audit/source_indexer.py`

**Code Changes:**
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

client = QdrantClient("localhost", port=6333)

def create_collection():
    client.create_collection(
        collection_name="sources",
        vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
    )

def index_sources(chunks: List[dict], embeddings: np.ndarray):
    points = [
        PointStruct(id=i, vector=emb.tolist(), payload=chunk)
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings))
    ]
    client.upsert(collection_name="sources", points=points)
```

**Tasks:**
- [ ] Start Qdrant container
- [ ] Create collection
- [ ] Index test sources
- [ ] Verify with Qdrant UI (http://localhost:6333/dashboard)

**Estimated**: 4-6 hours

---

### Day 4: RAG Retrieval
**Goal**: Grounding verification working

**File**: `app/packages/rag_audit/auditor.py`

**Code Changes:**
```python
def verify_sentence(sentence: str, embedder, client) -> dict:
    # Embed sentence
    query_emb = embedder.embed([sentence])[0]

    # Retrieve from Qdrant
    results = client.search(
        collection_name="sources",
        query_vector=query_emb.tolist(),
        limit=5
    )

    # Check if top result is relevant (score > 0.7)
    if results and results[0].score > 0.7:
        return {
            'grounded': True,
            'source': results[0].payload,
            'score': results[0].score
        }
    return {'grounded': False}
```

**Tasks:**
- [ ] Implement retrieval
- [ ] Test with script sentences
- [ ] Calculate groundedness score
- [ ] Generate audit report

**Estimated**: 6 hours

---

### Day 5: Integration Testing
**Goal**: All embeddings/RAG working end-to-end

**Tasks:**
- [ ] Test: sources → Qdrant
- [ ] Test: segments → FAISS
- [ ] Test: script → RAG audit
- [ ] Verify groundedness scores realistic
- [ ] Fix any bugs

**Estimated**: 6 hours

---

### Week 2 Deliverable
✅ **Semantic search working**: Scripts verified against knowledge sources

**Test Command:**
```bash
# Test RAG
python app/packages/rag_audit/source_indexer.py tmp/week2_test
python app/packages/rag_audit/auditor.py tmp/week2_test

# Check report
cat tmp/week2_test/audit_report.json
# Should have: groundedness_score > 0.7
```

---

## WEEK 3: INTEGRATION & POLISH 🟢 MEDIUM PRIORITY

### Day 1-2: Wrapper Script (Phase 9)
**Goal**: One command to run entire pipeline

**File**: `run_show.sh`

```bash
#!/bin/bash
set -e

JOB_ID=$1
if [ -z "$JOB_ID" ]; then
    echo "Usage: ./run_show.sh <job_id>"
    exit 1
fi

echo "🎙️  ALEXANDRIA PIPELINE - Job: $JOB_ID"

echo "Phase K: Knowledge organization..."
make curate TOPIC=${TOPIC:-general}
make clean
make dedupe
make score
make pack TOPIC=${TOPIC:-general} LANG=en

echo "Phase 1: Ingestion & ASR..."
make ingest JOB=$JOB_ID

echo "Phase 2-3: Outline & Planning..."
make outline JOB=$JOB_ID

echo "Phase 3-5: Assembly & TTS..."
make assemble JOB=$JOB_ID

echo "Phase 7: QC & Publishing..."
make qc JOB=$JOB_ID
make publish JOB=$JOB_ID

echo "✅ Complete! Output: dist/export/$JOB_ID/"
```

**Tasks:**
- [ ] Write wrapper script
- [ ] Test with sample job
- [ ] Add error handling
- [ ] Add progress indicators

**Estimated**: 6-8 hours

---

### Day 3: Golden Fixture Test
**Goal**: End-to-end regression test

**File**: `tests/test_pipeline.py`

```python
def test_full_pipeline():
    """Golden fixture: known input → expected output"""
    job_id = "golden_test"

    # Setup
    shutil.copy("tests/fixtures/golden_input.mp3", f"inputs/{job_id}.mp3")

    # Run pipeline
    result = subprocess.run(["./run_show.sh", job_id], check=True)

    # Verify outputs exist
    export_dir = Path(f"dist/export/{job_id}")
    assert (export_dir / "output_mix.mp3").exists()
    assert (export_dir / "notes.md").exists()
    assert (export_dir / "qc_report.json").exists()

    # Verify QC passed
    qc = json.load(open(export_dir / "qc_report.json"))
    assert qc["passed"] == True
```

**Tasks:**
- [ ] Create golden fixture audio
- [ ] Write end-to-end test
- [ ] Run and verify
- [ ] Document expected behavior

**Estimated**: 4-6 hours

---

### Day 4: README & Documentation
**Goal**: Complete user documentation

**File**: `README.md`

**Sections:**
1. What is Alexandria?
2. Quick Start (5-minute guide)
3. Installation (dependencies + Docker)
4. Configuration (personas, output modes)
5. Usage (run_show.sh)
6. Troubleshooting
7. Architecture overview
8. Contributing

**Also update:**
- [ ] API documentation
- [ ] Configuration reference
- [ ] Persona guide
- [ ] Development guide

**Estimated**: 6-8 hours

---

### Day 5: Final Testing & Bug Fixes
**Goal**: Smooth MVP release

**Tasks:**
- [ ] Run full test suite
- [ ] Fix any failing tests
- [ ] Test on clean machine
- [ ] Performance profiling
- [ ] Memory leak checks
- [ ] Create release notes

**Estimated**: 8 hours

---

### Week 3 Deliverable
✅ **MVP v0.1 Released**: Documented, tested, ready to use

---

## POST-MVP ENHANCEMENTS

### Phase 4: Docker Deployment (Week 4)
- [ ] Configure all docker-compose services
- [ ] FastAPI endpoints
- [ ] Celery worker tasks
- [ ] Health checks
- [ ] Container orchestration

### Phase 5: Fill Test Gaps (Week 5)
- [ ] Phase 1-7 unit tests
- [ ] Integration tests
- [ ] Performance benchmarks
- [ ] 80%+ coverage

### Phase 6: Multilingual (Week 6)
- [ ] NLLB-200 translator
- [ ] Multi-language voices
- [ ] Language switching

---

## DEPENDENCY INSTALLATION ORDER

### Critical Path
```bash
# Week 1
pip install faster-whisper        # ASR
pip install ffmpeg-python          # Audio processing
pip install pyloudnorm             # LUFS measurement

# Week 2
pip install sentence-transformers  # Embeddings
pip install faiss-cpu             # Vector search
pip install qdrant-client         # Vector DB

# Docker
docker run -d -p 6333:6333 qdrant/qdrant

# TTS (choose one)
# Piper (easier):
wget https://github.com/rhasspy/piper/releases/latest
# F5-TTS (better):
git clone https://github.com/SWivid/F5-TTS && pip install -e .
```

### Optional (can install later)
```bash
pip install ragas             # Better RAGAS metrics
pip install datasketch        # Knowledge deduplication
pip install unstructured      # Document parsing
pip install celery redis      # Async workers
```

---

## RISK MITIGATION

### High Risk: TTS Integration
**Risk**: TTS engines hard to install/configure
**Mitigation**:
- Start with Piper (simpler)
- Have F5-TTS as backup
- Test early (Day 2)

### Medium Risk: Audio Quality
**Risk**: Output quality poor
**Mitigation**:
- Test with multiple voices
- Tune LUFS carefully
- Get user feedback early

### Low Risk: Embeddings/RAG
**Risk**: Already have mock framework
**Mitigation**:
- Well-documented libraries
- Straightforward integration

---

## SUCCESS METRICS

### MVP Definition
A working pipeline that:
✅ Takes audio/documents as input
✅ Produces podcast audio as output
✅ Supports 10 personas
✅ Passes QC checks
✅ Has documentation

### Quality Gates
- [ ] WER < 8% on test set
- [ ] LUFS within -16 ±1 LU
- [ ] Groundedness > 0.7
- [ ] All 37+ tests passing
- [ ] Documentation complete

---

## CURRENT ACTION ITEMS

**TODAY (Immediate):**
1. ✅ Read this roadmap
2. ✅ Choose TTS engine (Piper recommended)
3. ✅ Install faster-whisper
4. ✅ Test Whisper transcription
5. ✅ Update transcriber.py

**THIS WEEK:**
- Complete Week 1 tasks
- Get real audio pipeline working
- Test with sample content

**NEXT WEEK:**
- Week 2: Embeddings & RAG
- Week 3: Integration & docs

---

## QUESTIONS TO ANSWER

Before starting, decide:

1. **TTS Engine**: Piper (fast) or F5-TTS (quality)?
2. **Deployment**: Local-first or Docker-first?
3. **Quality vs Speed**: Which to optimize for?
4. **Test Coverage**: How much before MVP?

---

## FINAL NOTES

**The Good News:**
- Architecture is solid
- Framework is complete
- Just need real implementations

**The Challenge:**
- Audio/AI integrations take time
- Testing requires patience
- Quality tuning is iterative

**The Path Forward:**
- Follow this roadmap
- Replace mocks systematically
- Test at each milestone
- Ship MVP in 3 weeks

**Let's build! 🚀**
