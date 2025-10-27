"""Pytest configuration for Alexandria test suite."""

from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def _voice_cache_tmp(tmp_path_factory, monkeypatch):
    cache_dir = tmp_path_factory.mktemp("voice_cache")
    monkeypatch.setenv("ALEXANDRIA_VOICE_CACHE_DIR", str(cache_dir))
    yield
