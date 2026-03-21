"""Test full DB pipeline: sync -> scheduler -> update -> scheduler. Verifies writes commit."""

import os
import subprocess
import sys

import pytest

SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _run(cmd: list[str], cwd: str, env: dict | None = None) -> subprocess.CompletedProcess:
    env = env or {}
    full_env = {**os.environ, **env}
    full_env["PYTHONPATH"] = SCRIPTS
    return subprocess.run(
        [sys.executable] + cmd,
        cwd=cwd,
        env=full_env,
        capture_output=True,
        text=True,
    )


@pytest.fixture
def temp_project(tmp_path):
    """Create temp project with .dreamteam/tasks/ and 3 task files."""
    tasks_dir = tmp_path / ".dreamteam" / "tasks"
    db_dir = tmp_path / ".dreamteam" / "db"
    tasks_dir.mkdir(parents=True)
    db_dir.mkdir(parents=True)

    (tasks_dir / "task_001.md").write_text("""id: T001
title: First task
status: todo
priority: 1
dependencies: []
""")
    (tasks_dir / "task_002.md").write_text("""id: T002
title: Second task
status: todo
priority: 1
dependencies: [T001]
""")
    (tasks_dir / "task_003.md").write_text("""id: T003
title: Third task
status: todo
priority: 1
dependencies: [T001, T002]
""")

    return tmp_path


def test_pipeline_sync_scheduler_update(temp_project):
    """Full pipeline: init-db, sync, scheduler, update-task, scheduler. Verifies DB writes persist."""
    root = str(temp_project)
    env = {"DREAMTEAM_PROJECT": root}

    # 1. Init DB
    r = _run([os.path.join(SCRIPTS, "init_db.py")], cwd=root, env=env)
    assert r.returncode == 0, f"init_db failed: {r.stderr}"

    # 2. Sync tasks to DB
    r = _run([os.path.join(SCRIPTS, "sync_tasks.py")], cwd=root, env=env)
    assert r.returncode == 0, f"sync failed: {r.stderr}"
    assert "Synced 3 tasks" in r.stdout

    # 3. Scheduler returns T001 (no deps)
    r = _run([os.path.join(SCRIPTS, "scheduler.py")], cwd=root, env=env)
    assert r.returncode == 0
    task_id = r.stdout.strip()
    assert task_id == "T001", f"Expected T001, got {task_id!r}"

    # 4. Update T001 to done
    r = _run([os.path.join(SCRIPTS, "update_task.py"), "T001", "done"], cwd=root, env=env)
    assert r.returncode == 0, f"update failed: {r.stderr}"

    # 5. Scheduler returns T002 (T001 done)
    r = _run([os.path.join(SCRIPTS, "scheduler.py")], cwd=root, env=env)
    assert r.returncode == 0
    task_id = r.stdout.strip()
    assert task_id == "T002", f"Expected T002, got {task_id!r}"

    # 6. Update T002 to done
    r = _run([os.path.join(SCRIPTS, "update_task.py"), "T002", "done"], cwd=root, env=env)
    assert r.returncode == 0

    # 7. Scheduler returns T003
    r = _run([os.path.join(SCRIPTS, "scheduler.py")], cwd=root, env=env)
    assert r.returncode == 0
    assert r.stdout.strip() == "T003"


def test_add_task_commits_immediately(temp_project):
    """add_task must commit so next read sees the data."""
    root = str(temp_project)
    env = {"DREAMTEAM_PROJECT": root}

    _run([os.path.join(SCRIPTS, "init_db.py")], cwd=root, env=env)
    r = _run([os.path.join(SCRIPTS, "sync_tasks.py")], cwd=root, env=env)
    assert r.returncode == 0

    # Scheduler in separate process must see synced tasks
    r = _run([os.path.join(SCRIPTS, "scheduler.py")], cwd=root, env=env)
    assert r.stdout.strip() == "T001"


def test_update_task_commits_immediately(temp_project):
    """update_task must commit so scheduler sees new status."""
    root = str(temp_project)
    env = {"DREAMTEAM_PROJECT": root}

    _run([os.path.join(SCRIPTS, "init_db.py")], cwd=root, env=env)
    _run([os.path.join(SCRIPTS, "sync_tasks.py")], cwd=root, env=env)
    _run([os.path.join(SCRIPTS, "update_task.py"), "T001", "done"], cwd=root, env=env)

    # Scheduler in separate process must see T001 done
    r = _run([os.path.join(SCRIPTS, "scheduler.py")], cwd=root, env=env)
    assert r.stdout.strip() == "T002"


def test_run_next_full_flow(temp_project):
    """run-next: sync -> get task -> update done -> get next. Verifies no lag in writes."""
    root = str(temp_project)
    env = {"DREAMTEAM_PROJECT": root}

    _run([os.path.join(SCRIPTS, "init_db.py")], cwd=root, env=env)

    # First run-next: should sync, get T001, set in_progress
    r = _run([os.path.join(SCRIPTS, "run_next.py")], cwd=root, env=env)
    assert r.returncode == 0
    assert "NEXT TASK: T001" in r.stdout
    assert "All tasks complete" not in r.stdout

    # Mark T001 done
    _run([os.path.join(SCRIPTS, "update_task.py"), "T001", "done"], cwd=root, env=env)

    # Second run-next: should get T002
    r = _run([os.path.join(SCRIPTS, "run_next.py")], cwd=root, env=env)
    assert r.returncode == 0
    assert "NEXT TASK: T002" in r.stdout


def test_run_next_no_ready_tasks_is_not_complete(temp_project):
    """If no todo task is ready, run-next must not claim all tasks are complete."""
    root = str(temp_project)
    env = {"DREAMTEAM_PROJECT": root}

    _run([os.path.join(SCRIPTS, "init_db.py")], cwd=root, env=env)
    _run([os.path.join(SCRIPTS, "sync_tasks.py")], cwd=root, env=env)

    # Create a "no ready task" state:
    # - T001 blocked (not done)
    # - T002, T003 still todo and depend on unfinished tasks
    _run([os.path.join(SCRIPTS, "update_task.py"), "T001", "blocked"], cwd=root, env=env)

    r = _run([os.path.join(SCRIPTS, "run_next.py")], cwd=root, env=env)
    assert r.returncode == 0
    assert "All tasks complete." not in r.stdout
    assert "No ready tasks. Pending tasks remain." in r.stdout
