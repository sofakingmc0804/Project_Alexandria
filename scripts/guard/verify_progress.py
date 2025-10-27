#!/usr/bin/env python3
"""Repository guard to keep agents aligned with source documents.

Rules enforced:
1. No new markdown documents may be introduced outside the approved list.
2. Any change touching code/config/assets must also update TASKS.md and add
   both a START and FINISH entry in the Progress Log section.
3. Guard execution must succeed regardless of whether git is installed; a
   snapshot of the workspace is persisted to detect changes deterministically.
"""

from __future__ import annotations

import difflib
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


APPROVED_MARKDOWN = {
    "PRD.md",
    "SPEC.md",
    "TASKS.md",
    "GUARD_SETUP.md",
    "GUARD_REALITY_CHECK.md",
    "CURATION_CHECKLIST.md",
    "Knowledge_Source_Organization.md",
    "FOUNDATION_CHECKLIST.md",
    "FOUNDATION_README.md",
    "PHASE0_COMPLETE.md",
    "PHASE2_COMPLETE.md",
    "PHASE3_COMPLETE.md",
    "PHASE4_COMPLETE.md",
}

PROGRESS_FILE = "TASKS.md"
PROGRESS_START_MARKER = "<!-- PROGRESS LOG START -->"
PROGRESS_END_MARKER = "<!-- PROGRESS LOG END -->"
DEVELOPER_MODE_ENV = "ALEXANDRIA_GUARD_MODE"

REPO_ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_PATH = REPO_ROOT / "tmp" / "guard_snapshot.json"

# Runtime globals populated by main()
GIT_AVAILABLE = False
SNAPSHOT_DATA: Dict[str, object] = {"manifest": {}, "tasks_md": ""}
CURRENT_MANIFEST: Dict[str, str] = {}
CURRENT_TASKS_CONTENT: str = ""


def developer_mode_enabled() -> bool:
    """Return True when guard should be bypassed for developer workflows."""

    value = os.environ.get(DEVELOPER_MODE_ENV, "")
    return value.strip().lower() == "developer"


def detect_git() -> bool:
    git_dir = REPO_ROOT / ".git"
    if not git_dir.exists():
        return False
    try:
        subprocess.check_output(["git", "rev-parse", "--is-inside-work-tree"], cwd=REPO_ROOT, text=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def run_git(args: List[str]) -> str:
    if not GIT_AVAILABLE:
        raise RuntimeError("git is not available in this workspace")
    return subprocess.check_output(["git", *args], cwd=REPO_ROOT, text=True).strip()


def hash_file(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            sha.update(chunk)
    return sha.hexdigest()


def should_skip_path(path: Path) -> bool:
    parts = path.parts
    if ".git" in parts:
        return True
    if any(part == "__pycache__" for part in parts):
        return True
    if parts and parts[0] == "tmp" and path.name == "guard_snapshot.json":
        return True
    return False


def compute_manifest() -> Dict[str, str]:
    manifest: Dict[str, str] = {}
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(REPO_ROOT)
        if should_skip_path(rel):
            continue
        manifest[str(rel).replace("\\", "/")] = hash_file(path)
    return manifest


def load_snapshot() -> Dict[str, object]:
    if SNAPSHOT_PATH.exists():
        try:
            return json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"manifest": {}, "tasks_md": ""}


def save_snapshot(manifest: Dict[str, str], tasks_content: str) -> None:
    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_PATH.write_text(
        json.dumps({"manifest": manifest, "tasks_md": tasks_content}, indent=2),
        encoding="utf-8",
    )


def determine_changes_from_manifest() -> Tuple[Set[str], Set[str]]:
    previous_manifest: Dict[str, str] = SNAPSHOT_DATA.get("manifest", {})  # type: ignore[assignment]
    changed: Set[str] = set()
    added_markdown: Set[str] = set()

    for path, digest in CURRENT_MANIFEST.items():
        if path not in previous_manifest:
            changed.add(path)
            if path.lower().endswith(".md") and os.path.basename(path) not in APPROVED_MARKDOWN:
                added_markdown.add(path)
        elif previous_manifest[path] != digest:
            changed.add(path)

    for path in previous_manifest:
        if path not in CURRENT_MANIFEST:
            changed.add(path)

    return changed, added_markdown


def get_worktree_status() -> Tuple[Set[str], Set[str]]:
    if GIT_AVAILABLE:
        try:
            output = run_git(["status", "--porcelain"])
            changed: Set[str] = set()
            added_markdown: Set[str] = set()

            for line in output.splitlines():
                if not line:
                    continue
                status = line[:2]
                path = line[3:] if len(line) > 3 and line[2] == " " else line[2:]
                if " -> " in path:
                    path = path.split(" -> ", 1)[1]
                path = path.strip()
                if not path:
                    continue
                path = path.replace("\\", "/")
                if status == "??":
                    if path.lower().endswith(".md") and os.path.basename(path) not in APPROVED_MARKDOWN:
                        added_markdown.add(path)
                    else:
                        changed.add(path)
                    continue
                changed.add(path)

            return changed, added_markdown
        except (RuntimeError, subprocess.CalledProcessError, FileNotFoundError):
            pass

    return determine_changes_from_manifest()


def _parse_diff_for_additions(diff_text: str) -> List[str]:
    additions: List[str] = []
    record = False
    for line in diff_text.splitlines():
        if line.startswith("@@"):
            if PROGRESS_START_MARKER in diff_text and PROGRESS_END_MARKER in diff_text:
                record = True
            continue
        if not line.startswith("+") or line.startswith("+++"):
            continue
        content = line[1:].strip()
        if content:
            additions.append(content)
    return additions


def get_progress_entries(content: str) -> List[str]:
    if not content:
        return []
    start = content.find(PROGRESS_START_MARKER)
    end = content.find(PROGRESS_END_MARKER)
    if start == -1 or end == -1 or end <= start:
        return []
    block = content[start + len(PROGRESS_START_MARKER):end]
    entries: List[str] = []
    for line in block.splitlines():
        entry = line.strip()
        if entry and not entry.startswith("<!--"):
            entries.append(entry)
    return entries


def extract_progress_additions(base: str | None = None) -> List[str]:
    if GIT_AVAILABLE:
        try:
            diff_text = run_git(["diff", "--unified=0", "HEAD", "--", PROGRESS_FILE])
            return _parse_diff_for_additions(diff_text)
        except (RuntimeError, subprocess.CalledProcessError, FileNotFoundError):
            pass

    previous_entries = set(get_progress_entries(SNAPSHOT_DATA.get("tasks_md", "")))
    current_entries = get_progress_entries(CURRENT_TASKS_CONTENT)
    return [entry for entry in current_entries if entry not in previous_entries]


def read_file_at_ref(ref: str, path: str) -> str:
    if ref == "WORKTREE":
        try:
            with open(REPO_ROOT / path, "r", encoding="utf-8") as handle:
                return handle.read()
        except FileNotFoundError:
            return ""
    if ref == "HEAD" and GIT_AVAILABLE:
        try:
            return run_git(["show", f"HEAD:{path}"])
        except (RuntimeError, subprocess.CalledProcessError):
            pass
    if path == PROGRESS_FILE:
        return SNAPSHOT_DATA.get("tasks_md", "")  # type: ignore[return-value]
    return ""


def extract_section(content: str, heading: str) -> str:
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*\n(.*?)(?=\n##\s+|\Z)", re.DOTALL | re.MULTILINE)
    match = pattern.search(content)
    return match.group(1).strip() if match else ""


def verify_checkbox_updates(finish_entries: List[str]) -> int:
    task_ids: List[str] = []
    for entry in finish_entries:
        match = re.search(r"\[FINISH .+?\] ([^\s]+)", entry)
        if match:
            task_ids.append(match.group(1))

    if not task_ids:
        return 0

    unchecked: List[str] = []
    for task_id in task_ids:
        pattern_done = re.compile(rf"[-*]\s*\[x\]\s*.*{re.escape(task_id)}", re.IGNORECASE)
        if not pattern_done.search(CURRENT_TASKS_CONTENT):
            unchecked.append(task_id)

    if unchecked:
        print("❌ FINISH entries logged but checkboxes NOT marked [x] in TASKS.md:")
        for task_id in unchecked:
            print(f"  - {task_id}: FINISH logged but checkbox still [ ]")
        print("\nYou MUST update TASKS.md checkboxes from [ ] to [x] when logging FINISH.")
        return 1

    return 0


def main() -> int:
    global GIT_AVAILABLE, SNAPSHOT_DATA, CURRENT_MANIFEST, CURRENT_TASKS_CONTENT

    if developer_mode_enabled():
        print("! Guard bypassed (ALEXANDRIA_GUARD_MODE=developer).")
        return 0

    original_skip = os.environ.get("ALEXANDRIA_GUARD_SKIP")
    os.environ["ALEXANDRIA_GUARD_SKIP"] = "1"

    GIT_AVAILABLE = detect_git()
    SNAPSHOT_DATA = load_snapshot()
    CURRENT_MANIFEST = compute_manifest()
    try:
        CURRENT_TASKS_CONTENT = (REPO_ROOT / PROGRESS_FILE).read_text(encoding="utf-8")
    except FileNotFoundError:
        CURRENT_TASKS_CONTENT = ""
    try:
        changed, added_markdown = get_worktree_status()

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

        if PROGRESS_FILE in changed:
            additions = extract_progress_additions()
            start_entries = [line for line in additions if line.startswith("[START ")]
            finish_entries = [line for line in additions if line.startswith("[FINISH ")]

            if start_entries or finish_entries:
                if not start_entries or not finish_entries:
                    print("❌ Progress log requires BOTH a [START …] and [FINISH …] entry for the work in this change.")
                    return 1

                pattern = re.compile(r"\[(START|FINISH) \d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z\] [^\s]+ - .+")
                bad_lines = [line for line in additions if (line.startswith("[START") or line.startswith("[FINISH")) and not pattern.match(line)]

                if bad_lines:
                    print("❌ Progress log entries must match '[START YYYY-MM-DDThh:mmZ] TASK-ID – summary'. Offending lines:")
                    for line in bad_lines:
                        print(f"  - {line}")
                    return 1

                checkbox_result = verify_checkbox_updates(finish_entries)
                if checkbox_result != 0:
                    return checkbox_result

                for finish_entry in finish_entries:
                    task_id_match = re.search(r"\[FINISH .+?\] ([^\s]+)", finish_entry)
                    if task_id_match:
                        task_id = task_id_match.group(1)
                        if monitored_changes and not any(path.startswith("tests/") for path in changed):
                            smoke_test_path = REPO_ROOT / "tests" / "test_pipeline_smoke.py"
                            if smoke_test_path.is_file():
                                try:
                                    subprocess.check_call(
                                        [sys.executable, str(smoke_test_path)],
                                        stdout=subprocess.DEVNULL,
                                        stderr=subprocess.DEVNULL,
                                        env={**os.environ},
                                    )
                                except subprocess.CalledProcessError:
                                    print(f"❌ Smoke test failed - claimed task {task_id} complete but pipeline broken")
                                    print("   Run: python tests/test_pipeline_smoke.py")
                                    return 1

                tests_changed = any(path.startswith("tests/") for path in changed)
                if not tests_changed:
                    print("❌ FINISH entries require accompanying test changes under tests/ to prove coverage.")
                    return 1

                print("🔒 Running pytest to enforce guardrails...")
                pytest_proc = subprocess.run(
                    [sys.executable, "-m", "pytest", "--maxfail=1", "--disable-warnings", "-q"],
                    capture_output=True,
                    text=True,
                    cwd=REPO_ROOT,
                    env={**os.environ},
                )

                if pytest_proc.returncode != 0:
                    print("❌ pytest failed. Output:")
                    print(pytest_proc.stdout)
                    print(pytest_proc.stderr)
                    return 1

                if "no tests ran" in pytest_proc.stdout.lower():
                    print("❌ pytest executed but reported 'no tests ran'. Add real automated tests before finishing a task.")
                    return 1

                current_tasks = CURRENT_TASKS_CONTENT
                previous_tasks = read_file_at_ref("HEAD", PROGRESS_FILE)
                current_backlog = extract_section(current_tasks, "Remediation Backlog")
                previous_backlog = extract_section(previous_tasks, "Remediation Backlog")

                if current_backlog == previous_backlog:
                    print("❌ The 'Remediation Backlog' section must be updated alongside FINISH entries to document next actions.")
                    return 1

                print("✅ pytest passed and guardrails satisfied.")

                save_snapshot(CURRENT_MANIFEST, CURRENT_TASKS_CONTENT)
                return 0
            else:
                print("❌ TASKS.md changed but no START/FINISH entries were added. Guard requires explicit progress logging.")
                return 1

        if not monitored_changes:
            save_snapshot(CURRENT_MANIFEST, CURRENT_TASKS_CONTENT)
            return 0

        if PROGRESS_FILE not in changed:
            print("❌ TASKS.md must be updated with progress log entries whenever work is done.")
            return 1

        save_snapshot(CURRENT_MANIFEST, CURRENT_TASKS_CONTENT)
        return 0

    finally:
        if original_skip is None:
            os.environ.pop("ALEXANDRIA_GUARD_SKIP", None)
        else:
            os.environ["ALEXANDRIA_GUARD_SKIP"] = original_skip


if __name__ == "__main__":
    sys.exit(main())
