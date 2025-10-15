#!/usr/bin/env python3
"""
Mandatory task execution wrapper.
All agent work MUST flow through this script.
"""
import sys
import json
import re
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
TASKS_FILE = PROJECT_ROOT / "TASKS.md"
LOG_FILE = PROJECT_ROOT / ".agent_log.json"

def load_log():
    if LOG_FILE.exists():
        with open(LOG_FILE) as f:
            return json.load(f)
    return {"tasks": {}, "sessions": []}

def save_log(log):
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)

def parse_tasks():
    """Extract all tasks from TASKS.md"""
    with open(TASKS_FILE) as f:
        content = f.read()

    # Match: - [ ] K0.01 ... or - [x] T1.02 ...
    pattern = r"^- \[([ x])\] ([KT]\d+\.\d+) (.+?)$"
    tasks = {}

    for line in content.split("\n"):
        match = re.match(pattern, line.strip())
        if match:
            checked, task_id, description = match.groups()
            tasks[task_id] = {
                "id": task_id,
                "description": description,
                "complete": checked == "x"
            }

    return tasks

def get_task_details(task_id):
    """Get full task details including Done when criteria"""
    with open(TASKS_FILE) as f:
        content = f.read()

    # Find task block
    pattern = f"- \\[[ x]\\] {task_id} (.+?)\n  \\*\\*Done when\\*\\*: (.+?)(?=\n\n|\n- \\[)"
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        return None

    return {
        "description": match.group(1).strip(),
        "done_criteria": match.group(2).strip()
    }

def mark_task_started(task_id):
    """Log task start"""
    log = load_log()
    log["tasks"][task_id] = {
        "started": datetime.now().isoformat(),
        "status": "in_progress"
    }
    save_log(log)
    print(f"✓ Task {task_id} marked as started")

def mark_task_complete(task_id):
    """Update TASKS.md checkbox and log"""
    # Update TASKS.md
    with open(TASKS_FILE) as f:
        content = f.read()

    # Replace [ ] with [x] for this task
    pattern = f"^(- \\[)( )(\\] {task_id} .+)$"
    updated = re.sub(pattern, r"\1x\3", content, flags=re.MULTILINE)

    if updated == content:
        print(f"✗ Task {task_id} not found or already complete")
        return False

    with open(TASKS_FILE, "w") as f:
        f.write(updated)

    # Update log
    log = load_log()
    if task_id in log["tasks"]:
        log["tasks"][task_id]["completed"] = datetime.now().isoformat()
        log["tasks"][task_id]["status"] = "complete"
    save_log(log)

    print(f"✓ Task {task_id} marked as complete in TASKS.md")
    return True

def validate_task_outputs(task_id):
    """Check if task outputs exist per Done when criteria"""
    details = get_task_details(task_id)
    if not details:
        print(f"✗ Cannot find task {task_id} in TASKS.md")
        return False

    criteria = details["done_criteria"]

    # Extract file paths from criteria
    # Matches: `/path/file.ext`, `file.ext`, `path/*.ext`
    file_patterns = re.findall(r'`([^`]+\.(py|json|yaml|yml|md|txt|csv|sh|sql))`', criteria)

    if not file_patterns:
        print(f"⚠ No file outputs specified in done criteria for {task_id}")
        print(f"  Criteria: {criteria}")
        return True  # Manual validation needed

    all_exist = True
    for file_path, _ in file_patterns:
        # Handle variable substitutions
        if "{" in file_path:
            # Pattern like /tmp/{job_id}/manifest.json
            # Check directory structure exists
            base = file_path.split("{")[0]
            if not Path(PROJECT_ROOT / base.strip("/")).exists():
                print(f"✗ Missing: {file_path} (base directory doesn't exist)")
                all_exist = False
            continue

        full_path = PROJECT_ROOT / file_path.strip("/")
        if not full_path.exists():
            print(f"✗ Missing required output: {file_path}")
            all_exist = False
        else:
            print(f"✓ Found: {file_path}")

    return all_exist

def check_prerequisites(task_id):
    """Ensure previous tasks in phase are complete"""
    tasks = parse_tasks()

    # Get phase from task_id (K, T0, T1, etc.)
    if task_id.startswith("K"):
        phase = "K"
    else:
        phase = task_id.split(".")[0]

    # Check all earlier tasks in same phase
    phase_tasks = [t for t in tasks.values() if t["id"].startswith(phase)]
    phase_tasks.sort(key=lambda x: x["id"])

    for task in phase_tasks:
        if task["id"] == task_id:
            break
        if not task["complete"]:
            print(f"✗ Cannot start {task_id}: prerequisite {task['id']} not complete")
            return False

    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/agent_task.py <task_id> [complete]")
        print("\nExamples:")
        print("  python scripts/agent_task.py K0.01        # Mark K0.01 started, ready to work")
        print("  python scripts/agent_task.py K0.01 complete   # Mark K0.01 complete, validate outputs")
        sys.exit(1)

    task_id = sys.argv[1]
    action = sys.argv[2] if len(sys.argv) > 2 else "start"

    tasks = parse_tasks()

    if task_id not in tasks:
        print(f"✗ Task {task_id} not found in TASKS.md")
        sys.exit(1)

    if action == "start":
        if tasks[task_id]["complete"]:
            print(f"✗ Task {task_id} already complete")
            sys.exit(1)

        if not check_prerequisites(task_id):
            sys.exit(1)

        mark_task_started(task_id)

        print(f"\n{'='*60}")
        print(f"TASK: {task_id}")
        print(f"{'='*60}")
        details = get_task_details(task_id)
        if details:
            print(f"\nDescription: {details['description']}")
            print(f"\nDone when: {details['done_criteria']}")
        print(f"\n{'='*60}")
        print(f"You may now work on this task.")
        print(f"When complete, run: python scripts/agent_task.py {task_id} complete")
        print(f"{'='*60}\n")

    elif action == "complete":
        if tasks[task_id]["complete"]:
            print(f"✗ Task {task_id} already marked complete")
            sys.exit(1)

        print(f"\nValidating outputs for {task_id}...")
        if not validate_task_outputs(task_id):
            print(f"\n✗ VALIDATION FAILED: Required outputs not found")
            print(f"Fix issues before marking complete.")
            sys.exit(1)

        if not mark_task_complete(task_id):
            sys.exit(1)

        print(f"\n✓ Task {task_id} complete!")

        # Show next task
        all_tasks = list(tasks.values())
        current_idx = [i for i, t in enumerate(all_tasks) if t["id"] == task_id][0]
        if current_idx + 1 < len(all_tasks):
            next_task = all_tasks[current_idx + 1]
            if not next_task["complete"]:
                print(f"\nNext task: {next_task['id']} - {next_task['description'][:60]}...")

    else:
        print(f"✗ Unknown action: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()
