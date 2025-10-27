#!/usr/bin/env bash
# Alexandria Repository Activation Script for Bash
# Run this script to enable guard-aware python in the current shell session
# Usage: source ./activate.sh

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Add repo root to PATH so python wrapper is found first
export PATH="$REPO_ROOT:$PATH"

echo "[alexandria] Activated repository context"
echo "[alexandria] Repository: $REPO_ROOT"
echo "[alexandria] Updated PATH to find python wrapper first"
echo "[alexandria] Type 'python --version' to test"
