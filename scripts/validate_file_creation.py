#!/usr/bin/env python3
"""
Pre-commit hook: Block creation of forbidden files.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

FORBIDDEN_FILES = [
    "TODO.md", "NOTES.md", "CHANGELOG.md", "CONTRIBUTING.md",
    "ARCHITECTURE.md", "DESIGN.md", "PLAN.md", "ROADMAP.md",
    "IMPROVEMENTS.md", "IDEAS.md", "LESSONS.md", "POSTMORTEM.md"
]

FORBIDDEN_DIRS = [
    "docs/", "documentation/", "wiki/"
]

ALLOWED_DOCS = [
    "PRD.md", "SPEC.md", "TASKS.md", "README.md",
    "Knowledge_Source_Organization.md", "ONTOLOGY.yaml",
    "CURATION_CHECKLIST.md", "source_catalog.schema.json"
]

def check_staged_files():
    """Check git staged files for forbidden patterns"""
    import subprocess

    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=A"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )

        if result.returncode != 0:
            return []

        return result.stdout.strip().split("\n")
    except Exception:
        return []

def validate_file(file_path):
    """Check if file is allowed to be created"""
    file_path = Path(file_path)

    # Check forbidden files
    if file_path.name in FORBIDDEN_FILES:
        return False, f"Forbidden file: {file_path.name}"

    # Check forbidden directories
    for forbidden_dir in FORBIDDEN_DIRS:
        if str(file_path).startswith(forbidden_dir):
            return False, f"Forbidden directory: {forbidden_dir}"

    # Allow files in allowed locations
    if str(file_path).startswith("app/packages/"):
        return True, None

    if str(file_path).startswith("configs/"):
        return True, None

    if str(file_path).startswith("schemas/"):
        return True, None

    if str(file_path).startswith("scripts/"):
        return True, None

    if str(file_path).startswith("tests/"):
        return True, None

    if str(file_path).startswith("knowledge/"):
        return True, None

    if str(file_path).startswith("tmp/") or str(file_path).startswith("dist/"):
        return True, None

    # Check if it's an allowed doc
    if file_path.name in ALLOWED_DOCS and "/" not in str(file_path):
        return True, None

    # Root-level .md files not in allowed list
    if str(file_path).endswith(".md") and "/" not in str(file_path):
        return False, f"Forbidden root-level .md file: {file_path.name}"

    return True, None

def main():
    staged_files = check_staged_files()

    if not staged_files or staged_files == [""]:
        # No staged files or not in git repo
        sys.exit(0)

    violations = []

    for file_path in staged_files:
        valid, reason = validate_file(file_path)
        if not valid:
            violations.append(reason)

    if violations:
        print("✗ COMMIT BLOCKED: Forbidden files detected")
        print("\nViolations:")
        for v in violations:
            print(f"  - {v}")
        print("\nSee .agent_rules for file creation policy.")
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
