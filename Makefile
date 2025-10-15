# Alexandria Podcast Generation Pipeline
# All targets use WSL for cross-platform compatibility

.PHONY: help curate clean dedupe score pack ingest outline assemble stitch qc publish smoke-test

help: ## Show this help message
@echo "Alexandria Build Targets:"
@echo ""
@echo "Knowledge Organization:"
@echo "  make curate TOPIC=<topic>    - Add sources to catalog"
@echo "  make clean                    - Normalize sources (GROBID/Unstructured)"
@echo "  make dedupe                   - Mark duplicate sources"
@echo "  make score                    - Calculate quality scores"
@echo "  make pack TOPIC=<t> LANG=<l>  - Build knowledge pack"
@echo ""
@echo "Pipeline:"
@echo "  make ingest JOB=<id>          - Normalize inputs + ASR"
@echo "  make outline JOB=<id>         - Build content graph + outline"
@echo "  make assemble JOB=<id>        - Full pipeline: rewrite + TTS + master"
@echo "  make stitch JOB=<id>          - Quick concatenation (no rewrite)"
@echo "  make qc JOB=<id>              - Run quality checks (RAGAS/WER/LUFS)"
@echo "  make publish JOB=<id>         - Generate RSS + export"
@echo ""
@echo "Development:"
@echo "  make smoke-test               - Run foundation smoke test"
@echo "  make test                     - Run all unit tests"

# Knowledge Organization (Phase K)
curate: ## Add sources to catalog
@python app/packages/knowledge/curator.py $(TOPIC)

clean: ## Normalize sources with GROBID/Unstructured
@python app/packages/knowledge/normalizer.py

dedupe: ## Mark duplicate sources using MinHash
@python app/packages/knowledge/deduplicator.py

score: ## Calculate quality scores
@python app/packages/knowledge/scorer.py

pack: ## Build knowledge pack for topic+language
@python app/packages/knowledge/pack_builder.py --topic $(TOPIC) --lang $(LANG)

# Ingestion (Phase 1)
ingest: ## Normalize audio + run ASR
@python app/packages/ingest/watcher.py --job $(JOB)
@python app/packages/ingest/normalizer.py --job $(JOB)
@python app/packages/asr/transcriber.py --job $(JOB)
@python app/packages/asr/language_detector.py --job $(JOB)

# Planning (Phases 2-3)
outline: ## Segment + embed + build outline
@python app/packages/segment/segmenter.py --job $(JOB)
@python app/packages/embed/embedder.py --job $(JOB)
@python app/packages/embed/indexer.py --job $(JOB)
@python app/packages/graph/builder.py --job $(JOB)
@python app/packages/planner/outliner.py --job $(JOB)
@python app/packages/planner/selector.py --job $(JOB)

# Assembly (Phases 3-5)
assemble: ## Full pipeline: rewrite + RAG audit + TTS + mastering
@python app/packages/writer/scripter.py --job $(JOB)
@python app/packages/continuity/checker.py --job $(JOB)
@python app/packages/rag_audit/source_indexer.py --job $(JOB)
@python app/packages/rag_audit/auditor.py --job $(JOB)
@python app/packages/tts/batch_synth.py --job $(JOB)
@python app/packages/mastering/mixer.py --job $(JOB)
@python app/packages/exporters/audio_exporter.py --job $(JOB)
@python app/packages/exporters/notes_generator.py --job $(JOB)
@python app/packages/exporters/stem_packager.py --job $(JOB)
@python app/packages/exporters/promo_clipper.py --job $(JOB)
@python app/packages/exporters/manifest_writer.py --job $(JOB)

# Quick stitch (no rewrite)
stitch: ## Concatenate + normalize only
@python app/packages/mastering/mixer.py --job $(JOB) --mode stitch
@python app/packages/exporters/audio_exporter.py --job $(JOB)

# Quality Control (Phase 7)
qc: ## Run all quality checks
@python app/packages/eval/ragas_scorer.py --job $(JOB)
@python app/packages/eval/wer_calculator.py --job $(JOB)
@python app/packages/eval/lufs_checker.py --job $(JOB)
@python app/packages/eval/qc_runner.py --job $(JOB)

# Publishing
publish: ## Generate RSS feed + export manifest
@python app/packages/exporters/rss_generator.py --job $(JOB)
@python scripts/validate/validate_manifest.py dist/export/$(JOB)/export_manifest.json

# Development
smoke-test: ## Run foundation smoke test
@python tests/test_pipeline_smoke.py

test: ## Run all unit tests
@pytest tests/unit/ -v
