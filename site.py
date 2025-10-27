"""Repository guard bootstrap overriding the standard library site module.

This module runs the Alexandria guard before delegating to Python's real
``site`` implementation. By placing this file at the repository root, any
``python`` process launched from this workspace will import it ahead of the
stdlib copy, ensuring guard enforcement is mandatory.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import sysconfig
from pathlib import Path
from types import ModuleType


REPO_ROOT = Path(__file__).resolve().parent
GUARD_SCRIPT = REPO_ROOT / "scripts" / "guard" / "verify_progress.py"


def _load_standard_site() -> ModuleType:
    stdlib_site = Path(sysconfig.get_path("stdlib")) / "site.py"
    if not stdlib_site.exists():  # pragma: no cover - catastrophic interpreter state
        raise ImportError(f"Standard library site module not found at {stdlib_site}")

    spec = importlib.util.spec_from_file_location("_alexandria_std_site", stdlib_site)
    if spec is None or spec.loader is None:  # pragma: no cover - catastrophic interpreter state
        raise ImportError("Unable to load standard library site module")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_guard() -> None:
    if not GUARD_SCRIPT.exists():
        return

    env = os.environ.copy()
    previous_skip = env.get("ALEXANDRIA_GUARD_SKIP")
    env["ALEXANDRIA_GUARD_SKIP"] = "1"

    result = subprocess.run(
        [sys.executable, str(GUARD_SCRIPT)],
        cwd=str(REPO_ROOT),
        text=True,
        env=env,
    )

    if previous_skip is None:
        env.pop("ALEXANDRIA_GUARD_SKIP", None)
    else:
        env["ALEXANDRIA_GUARD_SKIP"] = previous_skip

    if result.returncode != 0:
        sys.stderr.write("[guard] Enforcement failed. See guard output above.\n")
        sys.stderr.flush()
        sys.exit(result.returncode)


if (
    os.environ.get("ALEXANDRIA_GUARD_SKIP") != "1"
    and os.environ.get("ALEXANDRIA_GUARD_MODE", "").strip().lower() != "developer"
):
    _run_guard()

_STANDARD_SITE = _load_standard_site()


def __getattr__(name: str):  # pragma: no cover - compatibility fallback
    return getattr(_STANDARD_SITE, name)


for _name in dir(_STANDARD_SITE):
    if _name.startswith("__") and _name not in {"__all__", "__doc__", "__file__", "__loader__", "__package__"}:
        continue
    globals()[_name] = getattr(_STANDARD_SITE, _name)

__doc__ = getattr(_STANDARD_SITE, "__doc__", __doc__)
__all__ = getattr(_STANDARD_SITE, "__all__", globals().get("__all__", []))
