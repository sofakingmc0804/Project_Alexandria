@echo off
REM Alexandria Repository Activation Script
REM Run this batch file to enable guard-aware python in the current CMD session
REM Usage: activate.cmd

setlocal EnableExtensions EnableDelayedExpansion

set "REPO_ROOT=%~dp0"
set "REPO_ROOT=%REPO_ROOT:~0,-1%"

REM Add repo root to PATH so python.cmd is found first
set "PATH=%REPO_ROOT%;%PATH%"

REM Alternative: Set environment variable to skip guard when invoking from batch
REM set "ALEXANDRIA_BATCH_CONTEXT=1"

echo [alexandria] Activated repository context
echo [alexandria] Repository: %REPO_ROOT%
echo [alexandria] Updated PATH to find python wrapper first
echo [alexandria] Type "python --version" to test

endlocal & set "PATH=%PATH%"
