#!/usr/bin/env python3
"""Install PowerShell profile alias for guard-aware python wrapper on Windows."""

from __future__ import annotations

import os
import platform
import sys
from pathlib import Path


def install_powershell_alias() -> None:
    """Add python alias to PowerShell profile on Windows."""
    if platform.system() != "Windows":
        print("[alias] PowerShell profile installation skipped on non-Windows platform.")
        return

    ps_profile_path = Path.home() / "Documents" / "PowerShell" / "profile.ps1"
    ps_profile_dir = ps_profile_path.parent
    ps_profile_dir.mkdir(parents=True, exist_ok=True)

    alias_code = """
# Alexandria Repository Guard-Aware Python Alias
# Ensures 'python' command runs python.cmd wrapper, triggering guardrails
function python {
    param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Args)
    & ".\python.cmd" @Args
}
"""

    # Check if already installed
    if ps_profile_path.exists():
        content = ps_profile_path.read_text(encoding="utf-8")
        if "Alexandria Repository Guard-Aware Python Alias" in content:
            print(f"[alias] PowerShell profile already configured at {ps_profile_path}")
            return

    # Append alias to profile
    if ps_profile_path.exists():
        ps_profile_path.write_text(ps_profile_path.read_text(encoding="utf-8") + alias_code, encoding="utf-8")
    else:
        ps_profile_path.write_text(alias_code, encoding="utf-8")

    print(f"[alias] PowerShell profile updated at {ps_profile_path}")
    print("[alias] Run: . $PROFILE to reload, or restart PowerShell for changes to take effect.")


def main() -> None:
    """Main entry point."""
    repo_root = Path(__file__).resolve().parents[2]
    install_powershell_alias()


if __name__ == "__main__":
    main()
