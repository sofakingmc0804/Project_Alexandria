# Async Orchestration Design

This module coordinates the Phase 5 audio pipeline using asynchronous tasks so CLI callers and future API/worker processes can await deterministic, well-typed results.

## Goals
- Wrap the existing synchronous building blocks (`batch_synth.synthesize_batch`, `mastering.mixer.mix_stems`, `audio_exporter.export_audio`, `notes_generator.generate_notes`) behind awaitable functions.
- Leverage the generated Pydantic models (`Segment`, `Chapter`, `QCReport`) to provide typed inputs/outputs and enable validation.
- Capture structured summaries (durations, generated artifact paths) for downstream QC and manifest writers.
- Remain dependency-light by running synchronous implementations in a thread executor while exposing async-friendly signatures.

## Proposed API Surface
- `AsyncPhase5Orchestrator.run_full_pipeline(...) -> Phase5Artifacts`
  - Accepts script path, output directories, and optional configs.
  - Returns a dataclass that includes stems, mix, export bundle, notes, and optional `QCReport` placeholder for later stages.
- Helper coroutines:
  - `generate_stems`
  - `mix_audio`
  - `export_derivatives`
  - `generate_notes`
- The helpers emit typed result objects derived from the `models_generated` package.

## Concurrency Strategy
- Use `asyncio.to_thread` for existing synchronous functions.
- Allow oversight with a shared `asyncio.TaskGroup`, so future enhancements can fan out work (e.g., running exports and notes in parallel).

## Error Handling
- Raise `Phase5OrchestrationError` with rich context to support guardrails and CLI exit codes.
- Record partial progress so retriable stages can resume if needed.

This design unlocks Dimension 3 of the AI code-generation rollout by defining a single orchestration layer that the CLI and future worker processes can reuse.