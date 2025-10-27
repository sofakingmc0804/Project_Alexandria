# Guard-Aware Python Execution

The Alexandria repository enforces deterministic guardrails on all Python code execution. This document explains how the guard system works and how to use it.

## Quick Summary

**Truly automatic (zero setup):**
- ❌ Not possible without admin privileges or modifying system PATH

**Recommended for development (one-time per session):**
- ✅ Source activation script: `. .\activate.ps1` (PowerShell), `source ./activate.sh` (Bash)
- After activation, all `python` commands use guard wrapper

**Recommended for explicit safety:**
- ✅ Use `./python` or `.\python.cmd` directly (always works, no setup needed)

**For CI/CD pipelines:**
- ✅ Use explicit wrapper paths or source activation at pipeline start

## Overview

The guard system consists of multiple enforcement layers:

1. **Python Wrappers** (`python`, `python.cmd`) — Run guard before delegating to real interpreter
2. **Activation Scripts** (`activate.ps1`, `activate.sh`, `activate.cmd`) — Add repo to PATH and enable aliases (per-session)
3. **Sitecustomize** (`sitecustomize.py`) — Attempts guard on interpreter startup (limited effectiveness)
4. **PowerShell Profile Installation** — Optional permanent setup via `install_powershell_alias.py`

## Quick Start

### Most Reliable: Use Explicit Wrapper (Works Everywhere, No Setup)

```powershell
# Windows PowerShell
.\python.cmd -m pytest tests/
.\python.cmd scripts/my_script.py
```

```bash
# Linux/macOS/WSL Bash
./python -m pytest tests/
./python scripts/my_script.py
```

### Recommended for Interactive Development: Activate Session

**PowerShell (Windows)**
```powershell
# One-time per session in repo root:
. .\activate.ps1

# Now 'python' uses guard wrapper
python --version
python -m pytest tests/
```

**Bash/Zsh (Linux/macOS/WSL)**
```bash
# One-time per session in repo root:
source ./activate.sh

# Now 'python' uses guard wrapper
python --version
python -m pytest tests/
```

**CMD (Windows)**
```cmd
# One-time per session in repo root:
activate.cmd

# Now 'python' uses guard wrapper
python --version
python -m pytest tests/
```

## Enforcement Layers

### Layer 1: Python Wrappers (Always Available)
The repository includes native Python wrappers that locate the real interpreter and invoke the guard before execution:

- **POSIX** (`./python`) — Bash script for Linux/macOS/WSL
- **Windows** (`.\python.cmd`) — Batch script for CMD.exe

**Advantages:**
- Works without any setup
- Works from any directory
- Explicit and transparent

**How to use:**
```bash
# Direct invocation (works everywhere without setup)
./python -c "print('hello')"
./python -m pytest tests/

# Explicit path on Windows
.\python.cmd -c "print('hello')"
.\python.cmd -m pytest tests/
```

### Layer 2: Activation Scripts (Per-Session)
Use these to temporarily enable guard-aware Python in the current shell session. After activation, typing `python` (without `./` prefix) will use the guard wrapper.

**Advantages:**
- More convenient than `./python` for repeated commands
- No permanent changes to system
- Per-session (doesn't affect new terminals)

**PowerShell** (`.\activate.ps1`)
```powershell
. .\activate.ps1
python --version  # Uses guard wrapper
```

**Bash** (`./activate.sh`)
```bash
source ./activate.sh
python --version  # Uses guard wrapper
```

**CMD** (`activate.cmd`)
```cmd
activate.cmd
python --version  # Uses guard wrapper
```

### Layer 3: PowerShell Profile (Optional, Permanent)
For PowerShell on Windows, you can permanently install the guard alias to your user profile. This makes `python` always invoke the guard wrapper when working in the repo.

**Advantages:**
- Permanent (survives shell restarts)
- One-time setup

**Limitations:**
- Only works when in repo directory
- PowerShell-specific
- Requires manual invocation to install

**Installation:**
```powershell
python scripts/guard/install_powershell_alias.py
# or
make install-ps-alias  # if you have 'make' tool

# Then restart PowerShell
```

After installation, restart PowerShell and:
```powershell
python --version  # Uses guard wrapper (only works in repo directory)
```

### Layer 4: Sitecustomize (Limited, Not Recommended)
The `sitecustomize.py` module attempts to run the guard on Python interpreter startup. However, this is unreliable on Windows with frozen Python distributions.

**Status:** Fallback only, not primary enforcement.

## Recommended Workflow

### For Development (Local Testing) - Option A: Explicit Wrapper (Safest)
```bash
# Works from repo root, no setup needed
./python -m pytest tests/
./python scripts/my_script.py
./python -c "import mymodule"
```

**Pros:** Always works, explicit, transparent  
**Cons:** Requires `./` prefix

### For Development (Local Testing) - Option B: Activation Script (Most Convenient)
```bash
# Activate once per session
. .\activate.ps1  # PowerShell
# or
source ./activate.sh  # Bash

# All Python commands now use guard wrapper
python -m pytest tests/
python scripts/my_script.py
python -c "import mymodule"
```

**Pros:** Cleaner commands, familiar workflow  
**Cons:** Must activate each session

### For CI/CD Pipelines (Most Reliable)
```bash
# Option 1: Explicit wrapper (always works)
./python -m pytest tests/

# Option 2: Source activation at pipeline start
source ./activate.sh
python -m pytest tests/
```

### For Permanent PowerShell Setup (Windows Only)
```powershell
# One-time installation
python scripts/guard/install_powershell_alias.py

# Restart PowerShell, then in repo directory:
python --version  # ✓ Uses guard wrapper
```

**Note:** Only works when cd'd into repo directory

## Troubleshooting

### "python: command not found"
- Ensure you've sourced the activation script: `. ./activate.ps1` or `source ./activate.sh`
- Or use explicit path: `./python --version`

### "python.cmd: The term is not recognized"
- PowerShell doesn't search current directory by default
- Use `. ./activate.ps1` to add repo to PATH and create alias
- Or use explicit path: `.\python.cmd --version`

### Guard doesn't run
- Verify activation: `echo $env:PATH` (PowerShell) or `echo $PATH` (Bash)
- Should show repo root as first entry
- Try explicit wrapper: `./python --version` (should trigger guard)

### Guard blocks execution
- Run `python scripts/guard/verify_progress.py` to see detailed failure reason
- Most common: Code changes without corresponding TASKS.md updates
- See `TASKS.md` for progress log conventions

## Technical Details

### Guard Rules
1. No new markdown files outside approved list (PRD.md, SPEC.md, TASKS.md, etc.)
2. Code changes require TASKS.md progress entries with [START] and [FINISH] timestamps
3. FINISH entries require checkbox update in TASKS.md ([x])
4. FINISH entries require test changes under `tests/`
5. Remediation Backlog section must be updated with FINISH entries

### Snapshot System
The guard uses a deterministic snapshot (`tmp/guard_snapshot.json`) to detect workspace changes without requiring Git. The snapshot includes:
- File manifest (SHA256 hashes of all tracked files)
- Current TASKS.md content

### Environment Variable Control
- `ALEXANDRIA_GUARD_SKIP=1`  Bypass guard (used internally to prevent recursion)
- When running guard subprocess, wrapper sets this flag to avoid infinite loops

## See Also
- `scripts/guard/verify_progress.py`  Main guard implementation
- `scripts/guard/install_powershell_alias.py`  PowerShell profile installer
- `TASKS.md`  Progress log format and governance rules
