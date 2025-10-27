# Guard System Reality Check

## The Short Answer to "Is it automatic?"

**NO.** True automatic activation requires admin privileges to modify system PATH or install to site-packages, which we don't have.

## What We CAN Do (Without Admin)

### Option 1: Explicit Wrapper (Always Works, No Setup)
\\\ash
.\python.cmd --version          # Windows CMD/PowerShell
./python --version              # Linux/macOS/WSL
\\\

**Zero setup, works immediately from anywhere in repo.**

### Option 2: Per-Session Activation (Convenient, Per-Session)
\\\powershell
. .\activate.ps1
python --version
\\\

**Setup takes 1 second, must redo each new terminal session.**

### Option 3: PowerShell Profile (Semi-Permanent, PowerShell Only)
\\\powershell
python scripts/guard/install_powershell_alias.py
# Restart PowerShell
python --version  # Works only in repo directory
\\\

**Setup once, works across restarts, but only in PowerShell + only in repo directory.**

## Why Not Fully Automatic?

1. **Windows PATH**  System PATH is controlled by system registry (needs admin)
2. **Python site-packages**  .pth files in site-packages need write access (typically needs admin)
3. **Python Startup**  sitecustomize.py doesn't work with frozen Python 3.13 on Windows
4. **PYTHONSTARTUP**  Environment variable-based approach could work but still requires setup

## What We've Built

1.  **Python Wrappers**  Always work, zero setup, explicit
2.  **Activation Scripts**  Per-session convenience, easy refresh
3.  **PowerShell Profile Installer**  Optional permanent setup for PowerShell
4.  **Guard System**  Deterministic enforcement regardless of invocation method

## Recommendation

**For Maximum Reliability:** Use explicit wrapper
\\\ash
.\python.cmd -m pytest tests/
\\\

**For Convenience in Development:** Activate once per session
\\\powershell
. .\activate.ps1
python -m pytest tests/
\\\

**For CI/CD:** Use explicit wrapper in scripts
\\\yaml
script:
  - .\python.cmd -m pytest tests/
\\\

Both approaches guarantee guard enforcement. Neither requires admin or system-level modifications.
