#!/usr/bin/env python3
import sys
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).parent.parent
TASKS_FILE = PROJECT_ROOT / "TASKS.md"

def add_progress_entry(task_id, action, summary):
    with open(TASKS_FILE, "r") as f:
        content = f.read()

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entry = f"[{action.upper()} {timestamp}] {task_id} – {summary}\n"

    start_marker = "<!-- PROGRESS LOG START -->"
    end_marker = "<!-- PROGRESS LOG END -->"

    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)

    if start_idx == -1 or end_idx == -1:
        print("Error: Progress log markers not found in TASKS.md")
        sys.exit(1)

    insert_pos = end_idx
    new_content = content[:insert_pos] + entry + content[insert_pos:]

    with open(TASKS_FILE, "w") as f:
        f.write(new_content)

    print(f"✓ Progress logged: {entry.strip()}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python scripts/update_progress_log.py <task_id> <START|FINISH> <summary>")
        sys.exit(1)

    task_id = sys.argv[1]
    action = sys.argv[2]
    summary = " ".join(sys.argv[3:])

    if action not in ["START", "FINISH"]:
        print("Action must be START or FINISH")
        sys.exit(1)

    add_progress_entry(task_id, action, summary)
