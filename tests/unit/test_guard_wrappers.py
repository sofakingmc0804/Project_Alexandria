from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_posix_wrapper_enforces_guard() -> None:
    script = REPO_ROOT / "python"
    assert script.exists(), "POSIX python wrapper must exist"

    content = _read(script)
    assert "verify_progress.py" in content
    assert "ALEXANDRIA_GUARD_SKIP" in content


def test_windows_wrapper_enforces_guard() -> None:
    script = REPO_ROOT / "python.cmd"
    assert script.exists(), "Windows python wrapper must exist"

    content = _read(script)
    assert "verify_progress.py" in content
    assert "ALEXANDRIA_GUARD_SKIP" in content


def test_site_shim_runs_guard() -> None:
    site_module = REPO_ROOT / "site.py"
    assert site_module.exists(), "site.py shim must exist"

    content = _read(site_module)
    assert "verify_progress.py" in content
    assert "_load_standard_site" in content