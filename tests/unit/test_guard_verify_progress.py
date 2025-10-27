"""Tests for guard script workflow enforcement."""

from types import SimpleNamespace

from scripts.guard import verify_progress as guard


BASE_TASKS = """
## Remediation Backlog
- [ ] REM-010 Placeholder
""".strip()


def _patch_common(monkeypatch, tmp_path, *, backlog_current: str, backlog_previous: str):
    monkeypatch.delenv("ALEXANDRIA_GUARD_MODE", raising=False)

    repo_root = tmp_path
    (repo_root / "scripts" / "guard").mkdir(parents=True)
    (repo_root / "tests" / "unit").mkdir(parents=True)
    (repo_root / "TASKS.md").write_text(backlog_current, encoding="utf-8")

    monkeypatch.setattr(guard, "REPO_ROOT", repo_root)
    monkeypatch.setattr(guard, "detect_git", lambda: False)
    monkeypatch.setattr(guard, "load_snapshot", lambda: {"manifest": {}, "tasks_md": backlog_previous})
    monkeypatch.setattr(guard, "compute_manifest", lambda: {"TASKS.md": "hash"})
    monkeypatch.setattr(guard, "save_snapshot", lambda manifest, tasks: None)

    monkeypatch.setattr(guard, "get_worktree_status", lambda: ({"scripts/guard/verify_progress.py", "TASKS.md", "tests/unit/test_dummy.py"}, set()))
    monkeypatch.setattr(guard, "extract_progress_additions", lambda base=None: [
        "[START 2025-10-15T08:50Z] GOV-002 - Extend guardrails",
        "[FINISH 2025-10-15T08:55Z] GOV-002 - Guard updated",
    ])
    monkeypatch.setattr(guard, "verify_checkbox_updates", lambda finish: 0)

    def fake_read(ref: str, path: str) -> str:
        return backlog_current if ref == "WORKTREE" else backlog_previous

    monkeypatch.setattr(guard, "read_file_at_ref", fake_read)
    monkeypatch.setattr(guard.os.path, "isfile", lambda _: False)
    monkeypatch.setattr(
        guard.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="1 passed", stderr=""),
    )
    monkeypatch.setattr(guard.subprocess, "check_call", lambda *args, **kwargs: 0)


def test_guard_fails_when_backlog_not_updated(monkeypatch, tmp_path):
    _patch_common(monkeypatch, tmp_path, backlog_current=BASE_TASKS, backlog_previous=BASE_TASKS)

    result = guard.main()
    assert result == 1


def test_guard_passes_when_backlog_updated(monkeypatch, tmp_path):
    updated_tasks = """
## Remediation Backlog
- [x] REM-005 Harden Phase 5 audio pipeline
- [ ] REM-060 Automate guard workflow execution
""".strip()

    _patch_common(monkeypatch, tmp_path, backlog_current=updated_tasks, backlog_previous=BASE_TASKS)

    result = guard.main()
    assert result == 0


def test_guard_bypassed_in_developer_mode(monkeypatch):
    monkeypatch.setenv("ALEXANDRIA_GUARD_MODE", "developer")

    result = guard.main()
    assert result == 0
