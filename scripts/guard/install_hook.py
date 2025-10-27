"""Install Git hooks to enforce guard execution before commits."""

from __future__ import annotations

import os
from pathlib import Path
import stat


HOOK_TEMPLATE = """#!/bin/sh
python scripts/guard/verify_progress.py
status=$?
if [ $status -ne 0 ]; then
    echo "Guard check failed. Commit aborted." >&2
    exit $status
fi
"""


def install_pre_commit(repo_root: Path) -> Path:
    hooks_dir = repo_root / ".git" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    hook_path = hooks_dir / "pre-commit"
    hook_path.write_text(HOOK_TEMPLATE, encoding="utf-8")
    hook_path.chmod(hook_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return hook_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    hook_path = install_pre_commit(repo_root)
    print(f"Installed guard pre-commit hook at {hook_path}")


if __name__ == "__main__":
    main()