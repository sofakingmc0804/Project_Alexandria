"""REM-010 smoke tests validating Phase 0 scaffolding assets."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

from scripts.validate_config import REQUIRED_CONFIGS, validate_config
from tests import test_pipeline_smoke


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_required_directories_exist():
    """Phase 0 directory scaffold is present."""

    required_dirs = [
        "app/apps/api",
        "app/apps/worker",
        "app/apps/ui",
        "app/packages/ingest",
        "app/packages/asr",
        "app/packages/segment",
        "app/packages/embed",
        "app/packages/graph",
        "app/packages/planner",
        "app/packages/writer",
        "app/packages/continuity",
        "app/packages/rag_audit",
        "app/packages/tts",
        "app/packages/mastering",
        "app/packages/exporters",
        "app/packages/eval",
        "configs/personas",
        "configs/mix_profiles",
        "inputs",
        "sources",
        "dist",
        "tmp",
        "schemas",
        "knowledge/catalog",
        "knowledge/sources_raw",
        "knowledge/sources_clean",
        "knowledge/packs",
        "knowledge/cache",
    ]

    missing = [path for path in required_dirs if not (REPO_ROOT / path).is_dir()]
    assert not missing, f"Missing scaffold directories: {missing}"


def test_required_files_exist():
    """Core Phase 0 files ship with the repository."""

    required_files = [
        "Makefile",
        "docker-compose.yml",
        ".env.example",
        "requirements.txt",
        "SPEC.md",
        "PRD.md",
        "scripts/validate_config.py",
        "tests/test_pipeline_smoke.py",
        "schemas/segment.schema.json",
        "schemas/qc_report.schema.json",
        "configs/manifest.schema.json",
        "configs/output_menu.schema.json",
    ]

    missing = [path for path in required_files if not (REPO_ROOT / path).is_file()]
    assert not missing, f"Missing scaffold files: {missing}"


def test_makefile_targets_present():
    """Makefile exposes all Phase 0 targets described in the plan."""

    targets = {
        "curate",
        "clean",
        "dedupe",
        "score",
        "pack",
        "ingest",
        "outline",
        "assemble",
        "stitch",
        "qc",
        "publish",
        "help",
        "smoke-test",
        "test",
        "guard",
    }

    makefile_text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    defined_targets = set(re.findall(r"^([a-z0-9\-/]+):", makefile_text, flags=re.MULTILINE))

    missing = sorted(targets - defined_targets)
    assert not missing, f"Makefile missing targets: {missing}"


def test_docker_compose_services_defined():
    """docker-compose declares required baseline services."""

    compose = yaml.safe_load((REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8"))
    services = set((compose or {}).get("services", {}).keys())
    expected = {"api", "worker", "qdrant", "grobid", "redis"}

    missing = sorted(expected - services)
    assert not missing, f"docker-compose.yml missing services: {missing}"


def test_env_example_contains_required_keys():
    """Environment template exports the baseline configuration variables."""

    env_text = (REPO_ROOT / ".env.example").read_text(encoding="utf-8")
    expected_keys = {
        "QDRANT_URL=",
        "GROBID_URL=",
        "REDIS_URL=",
        "CELERY_BROKER_URL=",
        "CELERY_RESULT_BACKEND=",
        "WHISPER_MODEL=",
        "EMBED_MODEL=",
        "TTS_ENGINE=",
        "INPUTS_PATH=",
        "SOURCES_PATH=",
        "DIST_PATH=",
        "TMP_PATH=",
        "KNOWLEDGE_PATH=",
        "MIN_GROUNDEDNESS=",
        "MIN_CONTEXT_PRECISION=",
        "MAX_WER=",
        "TARGET_LUFS=",
    }

    missing = sorted(key for key in expected_keys if key not in env_text)
    assert not missing, f".env.example missing keys: {missing}"


def test_config_validator_accepts_templates():
    """Config validation script passes against shipped templates."""

    failures: list[str] = []
    for config_path, fields in REQUIRED_CONFIGS.items():
        passed, errors = validate_config(config_path, fields)
        if not passed:
            failures.append(f"{config_path}: {errors}")

    assert not failures, f"Config validator failures: {failures}"


def test_json_schemas_define_required_fields():
    """Baseline JSON schemas expose the fields downstream stages rely upon."""

    schema_expectations: dict[str, dict[str, set[str]]] = {
        "schemas/segment.schema.json": {
            "required": {"id", "start_ms", "end_ms", "text", "lang"},
            "properties": {"id", "start_ms", "end_ms", "text", "lang"},
        },
        "schemas/qc_report.schema.json": {
            "required": {"job_id", "timestamp", "passed", "metrics"},
            "properties": {"metrics"},
        },
        "configs/manifest.schema.json": {
            "required": {"job_id", "timestamp", "files", "metadata", "qc_metrics", "config"},
            "properties": {"files", "metadata", "qc_metrics", "config"},
        },
        "configs/output_menu.schema.json": {
            "required": {"deliverables", "length_mode", "persona", "mix_profile"},
            "properties": {"deliverables", "length_mode", "persona", "mix_profile"},
        },
    }

    for relative_path, expectations in schema_expectations.items():
        schema_path = REPO_ROOT / relative_path
        data = json.loads(schema_path.read_text(encoding="utf-8-sig"))

        assert data.get("type") == "object", f"{relative_path} must define an object schema"

        defined_required = set(data.get("required", []))
        missing_required = expectations["required"] - defined_required
        assert not missing_required, f"{relative_path} missing required entries: {sorted(missing_required)}"

        properties = data.get("properties")
        assert isinstance(properties, dict) and properties, f"{relative_path} must define properties"

        missing_properties = expectations["properties"] - set(properties)
        assert not missing_properties, f"{relative_path} missing properties: {sorted(missing_properties)}"

        if relative_path == "schemas/qc_report.schema.json":
            metrics = properties.get("metrics", {})
            metrics_required = set(metrics.get("required", []))
            expected_metrics = {"groundedness", "context_precision", "wer", "lufs"}
            missing_metrics = expected_metrics - metrics_required
            assert not missing_metrics, f"qc_report metrics missing: {sorted(missing_metrics)}"

        if relative_path == "configs/manifest.schema.json":
            files_schema = properties.get("files", {})
            items_schema = files_schema.get("items", {})
            item_required = set(items_schema.get("required", []))
            expected_items = {"path", "type", "size_bytes"}
            missing_item_fields = expected_items - item_required
            assert not missing_item_fields, f"manifest files missing: {sorted(missing_item_fields)}"


def test_pipeline_smoke_fixture_passes():
    """Baseline pipeline smoke test passes with committed fixtures."""

    assert test_pipeline_smoke.smoke_test()


def test_requirements_contain_minimum_packages():
    """Phase 0 requirements pin the minimal runtime and test stack."""

    requirement_lines = [
        line.strip()
        for line in (REPO_ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    packages = {line.split(">=")[0].split("==")[0].strip() for line in requirement_lines}
    expected = {
        "pydantic",
        "pyyaml",
        "numpy",
        "fastapi",
        "httpx",
        "typer[all]",
        "pytest",
        "pytest-asyncio",
        "hypothesis",
    }

    missing = sorted(expected - packages)
    assert not missing, f"requirements.txt missing packages: {missing}"
