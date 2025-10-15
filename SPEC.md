
# Technical Specification (SPEC)

## 1) System Overview
```
NotebookLM media → Transcribe (Whisper) → Segment & Embed → Content Graph & Dedupe
→ Outline & Rewrite (RAG) → Continuity Check → TTS (F5/Piper) → Mastering → Export
                         ↘ RAG Audit (GROBID+Unstructured+FAISS/Qdrant, BGE/E5) ↗
```

## 2) Core Services & Responsibilities
- **ingest**: file watcher, metadata, format normalization, language detection.
- **asr**: Whisper (large-v3 or medium) with diarization option; produce .srt & .json.
- **segment**: 20–60s segments, silence-aware; store timestamps and text.
- **embed**: BGE/E5 embeddings; store vectors in FAISS (embedded) or Qdrant.
- **graph**: build similarity graph, dedupe with MinHash/cosine; tag topics.
- **planner**: episode outline/beat sheet from transcript summaries.
- **writer**: segment-level rewrite with retrieval; persona/tone injection.
- **continuity**: entities/claims table; contradiction detection.
- **rag_audit**: verify rewritten script lines; attach citations or patch text.
- **tts**: F5-TTS (Apache-2.0) or Piper (MIT); lock speaker embeddings/rate/pitch.
- **master**: ffmpeg/sox chain: -16 LUFS, de-ess, limiter, crossfade(25–75ms).
- **export**: MP3/Opus, chapters.json, notes.md, rss.xml; optional MP4 video (Remotion).

## 3) Directory Layout
```
/app
  /apps
    /api           # FastAPI for orchestration & status
    /worker        # Celery/RQ workers for long jobs
    /ui            # Next.js minimal UI (Phase 2)
  /packages
    /ingest        # watcher, metadata
    /asr           # Whisper wrappers
    /segment       # silero VAD or librosa-based segmentation
    /embed         # BGE/E5 + FAISS/Qdrant
    /graph         # content graph, dedupe
    /planner       # outline generator
    /writer        # RAG-powered rewriting
    /continuity    # entity/claims checker
    /rag_audit     # verification + citations
    /tts           # F5/Piper synthesizers
    /mastering     # ffmpeg/sox utils
    /exporters     # audio, notes, rss, video
    /eval          # RAGAS, WER, LUFS checks
  /configs         # YAML for hosts, languages, mastering, retrieval
  /inputs          # drop NotebookLM files here
  /sources         # user documents (PDF/Docs/HTML)
  /dist            # final outputs
  /tmp             # temp assets/caches
```

## 4) Configuration (YAML examples)
`configs/hosts.yaml`
```yaml
hosts:
  - id: host_a
    voice: f5:en_male_01   # or piper:en_US-amy-low
    rate: 1.0
    pitch: 0.0
    seed: 42
  - id: host_b
    voice: f5:en_female_02
    rate: 0.98
    pitch: -0.1
language: en
target_duration_minutes: 60
personas:
  style: "inquisitive, friendly, concise"
```

`configs/mastering.yaml`
```yaml
lufs_target: -16
de_ess: true
limiter: true
crossfade_ms: 50
```

`configs/retrieval.yaml`
```yaml
embed_model: "bge-large-en"
db: "faiss"
top_k: 6
rerank: "bge-reranker-large"
```

## 5) API Endpoints (FastAPI)
- `POST /jobs/assemble` – payload: {project_id, lang, mode(stitch|assemble), inputs[]}
- `GET /jobs/{id}` – status, metrics, logs
- `POST /jobs/qc` – run RAGAS/WER/LUFS on an artifact
- `POST /publish/rss` – generate/update rss.xml

## 6) Data Schemas
- **Segment**: {id, start_ms, end_ms, text, lang, source_file, embedding_vector_ref}
- **Chapter**: {id, title, start_ms, end_ms}
- **QCReport**: {wer, lufs_avg, groundedness, context_precision, issues[]}

## 7) Algorithms & Heuristics
- **Segmentation**: phrase boundaries + silence detection; 20–60s targets.
- **Graph dedupe**: cosine similarity > 0.90 or MinHash Jaccard > 0.85 → candidate duplicates.
- **Continuity**: entity map (name, alias) + claims table; scan contradictions via prompts + rules.
- **RAG audit**: for each factual sentence → retrieve top-k → verify or patch; attach citations.

## 8) Model Choices
- **ASR**: Whisper large-v3 for highest accuracy; fallback to medium for speed.
- **Embeddings**: BGE-M3 or E5-Mistral.
- **Generator**: Qwen2.5 7B/13B (quantized). CPU local (overnight) or GPU burst via vLLM.
- **TTS**: F5-TTS (quality) or Piper (speed), both commercial-friendly.
- **Translator**: NLLB-200 / M2M100 when needed.

## 9) Build & Deployment
- **Docker Compose** services: api, worker, qdrant, grobid, unstructured, tts, ffmpeg toolset.
- **Makefile targets**:
  - `make ingest` – normalize & transcribe inputs
  - `make outline` – build content graph + outline
  - `make assemble` – rewrite + continuity + rag_audit + tts + master
  - `make stitch` – loudness-normalized concatenation
  - `make qc` – WER/RAGAS/LUFS report
  - `make publish` – RSS + artifacts to /dist
- **CI/CD**: run unit tests + eval thresholds (fail build on RAGAS/WER regression).

## 10) Observability
- Structured logs (JSON), artifact lineage (hashes), metrics (durations, cost estimates), Prometheus exporters (optional).

## 11) Security & Privacy
- Local processing by default; if GPU burst used, encrypt temp storage, auto-delete upon completion; redact PII in transcripts if configured.

## 12) Test Plan (high level)
- Unit tests for each package (ingest/asr/segment/etc.).
- Golden fixtures: small set of NotebookLM audios + source PDFs.
- Integration tests: end-to-end assemble produces MP3 + notes + chapters.
- Eval tests: RAGAS ≥ 0.8/0.7; WER ≤ 8%; LUFS within spec.

## 13) Output Customization Layer
- **Menu Config (`configs/output_menu.yaml`)**: declares which deliverables an agent run must produce (e.g., `stems`, `upload_mix`, `promo_pack`, `social_loop`, `study_pack`). Defaults to stems + upload mix; never hardcode in code.
- **Mix Variants**: `stems` store per-speaker WAV, music beds, ambience. `upload_mix` is LUFS-compliant stereo WAV. `music_light`, `music_heavy`, or other variants map to preset EQ/bed curves documented in `/configs/mix_profiles/`.
- **Length Modes**: support `full` (target 60 min), `condensed` (~20 min), `topic_focus` (≤10 min per topic). Planner service must enforce ±10% tolerance and adjust outlines/segment counts accordingly.
- **Persona & Tone Controls**: persona cards live in `/configs/personas/`. Cards define voice ids, cadence, lexical preferences, and disallowed phrases. Writer and TTS layers must read these at runtime; no baked-in defaults beyond `persona_default`.
- **Highlight & Promo Logic**: promo clips auto-pull high-salience segments using engagement score + novelty heuristics; each clip exports WAV + transcript + CTA stub.
- **Clipchamp Templates**: for any deliverable needing manual polish (stems, promo pack), generate `.json` templates with track naming, color coding, and marker annotations (intro, CTA, sponsor slot).
- **Manifest**: every bundle emits `export_manifest.json` listing files, intended use, duration, persona, mix profile, and QC metrics.
- **Localization Hooks**: when non-English sources detected, include optional translation track; translator agent writes coverage note so downstream marketing can decide.

## 14) Guardrails
- Two retry attempts max per stage; on failure raise `needs_human` flag in manifest.
- Preserve previous outputs when regenerating (suffix with `_v{n}`) to avoid data loss.
- Do not auto-upload or publish; final distribution remains manual.
