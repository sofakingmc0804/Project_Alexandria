#!/usr/bin/env python3
"""Repository guard to keep agents aligned with source documents.

Rules enforced:
1. No new markdown documents may be introduced outside the approved list.
2. Any change touching code/config/assets must also update TASKS.md and add
   both a START and FINISH entry in the Progress Log section.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from typing import List, Set


APPROVED_MARKDOWN = {
    "PRD.md",
    "SPEC.md",
    "TASKS.md",
    "CURATION_CHECKLIST.md",
    "Knowledge_Source_Organization.md",
}

PROGRESS_FILE = "TASKS.md"
PROGRESS_START_MARKER = "<!-- PROGRESS LOG START -->"
PROGRESS_END_MARKER = "<!-- PROGRESS LOG END -->"


def run_git(args: List[str]) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def diff_against_base() -> str:
    base_ref = os.environ.get("GITHUB_BASE_REF")
    if base_ref:
        base = f"origin/{base_ref}"
    else:
        base = "origin/main"

    try:
        run_git(["rev-parse", base])
        return base
    except subprocess.CalledProcessError:
        # Fallback to previous commit when base isn't available (e.g. local runs)
        try:
            run_git(["rev-parse", "HEAD^"])
            return "HEAD^"
        except subprocess.CalledProcessError as exc:  # pragma: no cover
            print("Unable to determine base for diff", file=sys.stderr)
            raise exc


def get_changed_files(base: str) -> Set[str]:
    output = run_git(["diff", "--name-only", f"{base}...HEAD"])
    return {line.strip() for line in output.splitlines() if line.strip()}


def get_added_markdown(base: str) -> Set[str]:
    output = run_git(["diff", "--name-only", "--diff-filter=A", f"{base}...HEAD"])
    added = {line.strip() for line in output.splitlines() if line.strip() and line.strip().lower().endswith(".md")}
    return added


def extract_progress_additions(base: str) -> List[str]:
    try:
        diff_text = run_git(["diff", "--unified=0", f"{base}...HEAD", PROGRESS_FILE])
    except subprocess.CalledProcessError:
        return []

    additions: List[str] = []
    record = False
    for line in diff_text.splitlines():
        if line.startswith("@@"):
            # determine if hunk overlaps the progress log block
            if PROGRESS_START_MARKER in diff_text and PROGRESS_END_MARKER in diff_text:
                record = True
            continue
        if not line.startswith("+") or line.startswith("+++"):
            continue
        content = line[1:].strip()
        if content:
            additions.append(content)
    return additions


def verify_checkbox_updates(base: str, finish_entries: List[str]) -> int:
    """Verify that FINISH entries have corresponding checked boxes in TASKS.md."""
    # Extract task IDs from FINISH entries
    task_ids = []
    for entry in finish_entries:
        match = re.search(r"\[FINISH .+?\] ([^\s]+)", entry)
        if match:
            task_ids.append(match.group(1))
    
    if not task_ids:
        return 0  # No task IDs to verify
    
    # Get TASKS.md diff to see checkbox changes
    try:
        diff_text = run_git(["diff", "--unified=5", f"{base}...HEAD", PROGRESS_FILE])
    except subprocess.CalledProcessError:
        return 0
    
    # Look for checkbox updates from [ ] to [x] for each task
    unchecked_tasks = []
    for task_id in task_ids:
        # Pattern: task ID followed by checkbox change from [ ] to [x]
        # We need to see: -  - [ ] **{task_id}** and +  - [x] **{task_id}**
        checkbox_pattern = re.compile(
            rf"-\s*-\s*\[\s*\]\s*\*\*{re.escape(task_id)}\*\*.*?\n\+\s*-\s*\[x\]\s*\*\*{re.escape(task_id)}\*\*",
            re.MULTILINE | re.DOTALL
        )
        
        if not checkbox_pattern.search(diff_text):
            unchecked_tasks.append(task_id)
    
    if unchecked_tasks:
        print(f"❌ FINISH entries logged but checkboxes NOT marked [x] in TASKS.md:")
        for task_id in unchecked_tasks:
            print(f"  - {task_id}: FINISH logged but checkbox still [ ]")
        print("\nYou MUST update TASKS.md checkboxes from [ ] to [x] when logging FINISH.")
        return 1
    
    return 0


def main() -> int:
    base = diff_against_base()
    changed = get_changed_files(base)

    added_markdown = get_added_markdown(base)
    disallowed = [path for path in added_markdown if os.path.basename(path) not in APPROVED_MARKDOWN]
    if disallowed:
        print("❌ New documentation files are not allowed:")
        for path in disallowed:
            print(f"  - {path}")
        print("Use existing source documents (PRD.md, SPEC.md, TASKS.md, Knowledge_Source_Organization.md, CURATION_CHECKLIST.md).")
        return 1

    monitored_changes = [
        path
        for path in changed
        if not path.endswith(".md")
        or os.path.basename(path) not in APPROVED_MARKDOWN
    ]

    # If only docs changed, we do not require progress log updates.
    if not monitored_changes:
        return 0

    if PROGRESS_FILE not in changed:
        print("❌ TASKS.md must be updated with progress log entries whenever work is done.")
        return 1

    additions = extract_progress_additions(base)
    start_entries = [line for line in additions if line.startswith("[START ")]
    finish_entries = [line for line in additions if line.startswith("[FINISH ")]

    if not start_entries or not finish_entries:
        print("❌ Progress log requires BOTH a [START …] and [FINISH …] entry for the work in this change.")
        return 1

    # Basic format validation to keep entries machine parsable
    pattern = re.compile(r"\[(START|FINISH) \d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z\] [^\s]+ - .+")
    bad_lines = [line for line in additions if line.startswith("[START") or line.startswith("[FINISH") if not pattern.match(line)]

    if bad_lines:
        print("❌ Progress log entries must match '[START YYYY-MM-DDThh:mmZ] TASK-ID – summary'. Offending lines:")
        for line in bad_lines:
            print(f"  - {line}")
        return 1

    # Verify checkboxes are updated for FINISH entries
    checkbox_result = verify_checkbox_updates(base, finish_entries)
    if checkbox_result != 0:
        return checkbox_result

    # Validate task acceptance criteria (when FINISH entry exists)
    for finish_entry in finish_entries:
        task_id_match = re.search(r"\[FINISH .+?\] ([^\s]+)", finish_entry)
        if task_id_match:
            task_id = task_id_match.group(1)
            # TODO: Parse TASKS.md for this task_id's "Done when" criteria
            # For now, just verify smoke test passes when code changes
            if monitored_changes and not any(path.endswith("test_pipeline_smoke.py") for path in changed):
                # Check if smoke test exists and passes
                import os.path
                smoke_test_path = "tests/test_pipeline_smoke.py"
                if os.path.isfile(smoke_test_path):
                    try:
                        subprocess.check_call([sys.executable, smoke_test_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    except subprocess.CalledProcessError:
                        print(f"❌ Smoke test failed - claimed task {task_id} complete but pipeline broken")
                        print("   Run: python tests/test_pipeline_smoke.py")
                        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())