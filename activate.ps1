# Alexandria Repository Activation Script for PowerShell
# Run this script to enable guard-aware python in the current PowerShell session
# Usage: . .\activate.ps1

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = (Get-Item -Path $RepoRoot).FullName

# Add repo root to PATH so python.cmd is found first
$env:PATH = "$RepoRoot;$env:PATH"

# Define convenience alias for the python wrapper
function python {
    param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Args)
    & "$RepoRoot\python.cmd" @Args
}

Write-Host "[alexandria] Activated repository context" -ForegroundColor Green
Write-Host "[alexandria] Repository: $RepoRoot" -ForegroundColor Cyan
Write-Host "[alexandria] Updated PATH to find python wrapper first" -ForegroundColor Cyan
Write-Host "[alexandria] Type 'python --version' to test" -ForegroundColor Cyan
