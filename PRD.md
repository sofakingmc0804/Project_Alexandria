
# Product Requirements Document (PRD)

## 1) Product Vision
Build an **AI-first educational content factory** that:
- Ingests academic/business sources and NotebookLM outputs.
- Produces **hour-long, multilingual podcast-style discussions** with consistent hosts.
- Outputs additional learning artifacts (study guides, quizzes, knowledge graphs, mind maps, video explainers).
- Operates **fast, low-cost**, and **extensible**, prioritizing open-source components and “burst GPU” execution only when needed.

## 2) Target Users & Pain Points
- **Educators / Instructional designers**: need rapid, accurate, repeatable content with citations.
- **Content teams / L&D**: need multi-language outputs, brand-voice consistency, and distribution-ready packaging.
- **SMBs / Solo creators**: require minimal infra, automation, and low cost per episode.
- **Students / Lifelong learners**: need verifiable and engaging content with clear structure and summaries.

## 3) Goals (Success Criteria)
- **Speed**: Produce a 60-min podcast episode end-to-end within same day on 16 GB RAM (local CPU) or within 1 hour wall time via burst GPU for script stage.
- **Cost**: $0 core OSS stack; optional GPU burst ≤ $5 per 60-min episode. Zero ongoing API lock-in.
- **Quality**:
  - Groundedness ≥ 0.8; Context Precision ≥ 0.7 (RAGAS) on nightly samples.
  - LUFS normalization at −16 ± 1 LU.
  - WER (script vs TTS-transcript) ≤ 8% median on sample chapters.
- **Multilingual**: Support ≥ 10 target languages at launch; scalable via NLLB/M2M100.
- **Customization**: Every job delivers the mix menu chosen by the reviewer (e.g., stems, upload-ready stereo, highlight reels) plus persona and tone variants when requested.

## 4) Scope (MVP → V1)
### In Scope (MVP)
- NotebookLM **audio/video ingestion**, transcription (Whisper), segmentation.
- Content graph + deduplication, outline, continuity checks.
- RAG audit against user-provided sources (GROBID + Unstructured + FAISS/Qdrant, BGE/E5 embeddings).
- Re-voicing with **F5-TTS** (Apache-2.0) or **Piper** (MIT).
- Audio mastering, chapters, show notes/citations, RSS packaging.
- Multilingual generation (direct or translate+localize).
- Episode variants: full-length (target 60 min), condensed 20-min briefing, and 3× promo clips.

### In Scope (V1 Enhancements)
- Video outputs (Remotion slides; Manim for diagrams).
- Flashcards/quiz export (Anki), knowledge graph/mind map.
- Batch pipeline: assemble long-form episodes from multiple NotebookLM outputs.
- Simple UI (Next.js) for uploads, config, and job tracking.
- Customizable persona packs and tone sliders to match brand voice and audience segment.

### Out of Scope (for now)
- Custom proprietary LLM training.
- Real-time streaming co-hosts.
- Full LMS integration (export only).

## 5) User Stories (MVP)
- As a creator, I can drop N NotebookLM audio files into `/inputs` and get a **single 60-min podcast** with consistent voices, chapters, and notes.
- As an editor, I can configure **hosts/personas**, target language, and tone via a YAML file.
- As a reviewer, I can open a **QC report** with groundedness, WER, and loudness checks.
- As a publisher, I can export **RSS+MP3/Opus** and a **promo trailer** automatically.

## 6) Non-Functional Requirements
- **Reliability**: deterministic seeds for TTS; retries for long jobs; idempotent runs.
- **Performance**: parallel segment generation/voicing; bounded memory on 16 GB.
- **Security/Privacy**: all processing local by default; optional burst GPU with encrypted storage and auto-wipe.
- **Licensing**: use commercial-friendly OSS (F5-TTS/Piper). If XTTS is used, enforce non-commercial flags.

## 7) External Dependencies & Constraints
- NotebookLM outputs (user-provided). Respect Google terms for redistribution.
- OSS tools: Whisper, GROBID, Unstructured, FAISS/Qdrant, BGE/E5, F5-TTS/Piper, ffmpeg, sox, Remotion, Manim, Mermaid/Graphviz, NLLB/M2M100.
- Optional GPU burst provider (RunPod/Vast).

## 8) KPIs & Telemetry
- Episode throughput/day, avg time-to-air.
- Cost per episode (compute minutes × $/hr).
- Quality metrics (RAGAS scores, WER, LUFS deviation).
- Error rates and re-run counts.

## 9) Risks & Mitigations
- **License drift**: pin TTS choices; scan licenses in CI.
- **Audio inconsistency**: lock speaker embeddings/settings; batch-normalize.
- **Topic drift**: continuity checker + RAG audit; fail build on threshold drop.
- **Hardware limits**: segment jobs; optional burst GPU path built-in.

## 10) Rollout Plan
- Pilot 2 languages, 3 episodes.
- Expand to 5–10 languages, add video output.
- Harden CI, publish stable v1.0.

## 11) Output Packages & Market Fit
- **Core Deliverables**: per-speaker stems, mastered stereo mix, three highlight clips, study guide PDF.
- **Optional Adds**: music-light mix, language-localized mix, vertical promo video, transcript-only bundle.
- **Persona Catalog**: maintain at least five voice/tone presets (academic, narrative, casual, mentor, debate) with documented guardrails.
- **Length Controls**: allow reviewer to request full coverage, condensed briefing, or topic-focused mini-episodes; ensure timeboxes are met within ±10%.
- **Marketing Hooks**: each run emits a 120-word summary and CTA suggestions for podcast platforms and social promos.
