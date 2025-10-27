"""Automatic guard enforcement on Python interpreter startup.

Any Python process launched from the repository will import this module
before executing user code. We leverage that hook to ensure the
repository guard has validated the current workspace snapshot. This
prevents forgetful or adversarial agents from bypassing guardrails by
simply skipping manual checks.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


# Skip when guard already running, during pytest, in developer mode, or when explicitly disabled
def _developer_mode_enabled() -> bool:
    return os.environ.get("ALEXANDRIA_GUARD_MODE", "").strip().lower() == "developer"


if os.environ.get("ALEXANDRIA_GUARD_SKIP") == "1":
    pass
elif _developer_mode_enabled():
    os.environ["ALEXANDRIA_GUARD_SKIP"] = "1"
elif any("pytest" in (arg or "") for arg in sys.argv[:2]):
    os.environ["ALEXANDRIA_GUARD_SKIP"] = "1"
else:
    REPO_ROOT = Path(__file__).resolve().parent
    guard_path = REPO_ROOT / "scripts" / "guard" / "verify_progress.py"

    if guard_path.exists():
        try:
            from scripts.guard import verify_progress as guard
        except Exception as exc:  # pragma: no cover - fatal import failure
            sys.stderr.write(f"[guard] Failed to import verify_progress: {exc}\n")
            sys.exit(1)

        snapshot = guard.load_snapshot()
        snapshot_manifest = snapshot.get("manifest", {})  # type: ignore[assignment]
        snapshot_tasks = snapshot.get("tasks_md", "")  # type: ignore[assignment]

        try:
            current_manifest = guard.compute_manifest()
            try:
                current_tasks = (guard.REPO_ROOT / guard.PROGRESS_FILE).read_text(encoding="utf-8")
            except FileNotFoundError:
                current_tasks = ""
        except Exception as exc:  # pragma: no cover - unexpected failure
            sys.stderr.write(f"[guard] Unable to analyze workspace: {exc}\n")
            sys.exit(1)

        if current_manifest != snapshot_manifest or current_tasks != snapshot_tasks:
            previous_skip = os.environ.get("ALEXANDRIA_GUARD_SKIP")
            os.environ["ALEXANDRIA_GUARD_SKIP"] = "1"
            rc = guard.main()
            if previous_skip is None:
                os.environ.pop("ALEXANDRIA_GUARD_SKIP", None)
            else:
                os.environ["ALEXANDRIA_GUARD_SKIP"] = previous_skip

            if rc != 0:
                sys.stderr.write("[guard] Enforcement failed. See guard output above.\n")
                sys.exit(rc)
