#!/usr/bin/env python3
import json
import re
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
TASKS_FILE = PROJECT_ROOT / "TASKS.md"
LOG_FILE = PROJECT_ROOT / ".agent_log.json"

def main():
    with open(TASKS_FILE) as f:
        content = f.read()

    pattern = r"^- \[([ x])\] ([KT]\d+\.\d+) (.+?)$"
    tasks = []

    for line in content.split("\n"):
        match = re.match(pattern, line.strip())
        if match:
            checked, task_id, description = match.groups()
            tasks.append({
                "id": task_id,
                "description": description,
                "complete": checked == "x"
            })

    completed = [t for t in tasks if t["complete"]]
    pending = [t for t in tasks if not t["complete"]]

    print(f"\n{'='*70}")
    print(f"PROJECT ALEXANDRIA - STATUS REPORT")
    print(f"Generated: {datetime.now().isoformat()}")
    print(f"{'='*70}\n")

    print(f"Progress: {len(completed)}/{len(tasks)} tasks complete ({int(len(completed)/len(tasks)*100)}%)\n")

    if pending:
        next_task = pending[0]
        print(f"NEXT TASK: {next_task['id']}")
        print(f"Description: {next_task['description'][:70]}")
        print(f"\nTo start: python scripts/agent_task.py {next_task['id']}\n")
    else:
        print("ALL TASKS COMPLETE!\n")

    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
