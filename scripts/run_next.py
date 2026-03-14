#!/usr/bin/env python3
"""One-step orchestrator: verify, get next task, print instructions. Run this to start each task round."""

import os
import sys
import subprocess

import project
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = project.get_project_root()


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run command in project root."""
    return subprocess.run(
        cmd,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=check,
    )


def _git_pull() -> None:
    """Pull latest changes before starting a task. Skip if not a git repo or pull fails."""
    r = run(["git", "pull"], check=False)
    if r.returncode == 0:
        if r.stdout and r.stdout.strip():
            print("Git pull:", r.stdout.strip())
    else:
        err = (r.stderr or r.stdout or "").lower()
        skip = (
            "not a git repository" in err
            or "not found" in err
            or "no tracking information" in err
            or "please specify which branch" in err
        )
        if not skip:
            print("Git pull failed (continuing):", (r.stderr or r.stdout or "").strip(), file=sys.stderr)


def main() -> None:
    """One round: git pull -> verify -> [auto init-db + sync if needed] -> get task -> print instructions."""
    # 0. Update from remote before each task
    _git_pull()

    # 1. Verify consistency; if mismatch, init-db (if needed) + sync
    r = run([sys.executable, os.path.join(SCRIPTS_DIR, "verify_tasks.py")], check=False)
    if r.returncode != 0:
        db_path = project.get_db_path()
        if not os.path.exists(db_path):
            run([sys.executable, os.path.join(SCRIPTS_DIR, "init_db.py")], check=False)
        print("Syncing tasks to DB...", file=sys.stderr)
        r2 = run([sys.executable, os.path.join(SCRIPTS_DIR, "sync_tasks.py")], check=False)
        if r2.returncode != 0:
            print("FAIL: sync-tasks failed. Run: python -m dreamteam init-db", file=sys.stderr)
            sys.exit(1)

    # 2. Verify tasks have content in DB; if missing, sync
    r = run([sys.executable, os.path.join(SCRIPTS_DIR, "verify_sync.py")], check=False)
    if r.returncode != 0:
        print("Syncing task content to DB...", file=sys.stderr)
        r2 = run([sys.executable, os.path.join(SCRIPTS_DIR, "sync_tasks.py")], check=False)
        if r2.returncode != 0:
            print("FAIL: sync-tasks failed.", file=sys.stderr)
            sys.exit(1)
        r = run([sys.executable, os.path.join(SCRIPTS_DIR, "verify_sync.py")], check=False)
        if r.returncode != 0:
            print("FAIL: Tasks still missing content. Run: python -m dreamteam sync-tasks", file=sys.stderr)
            sys.exit(1)

    # 3. Quick integrity fix: tasks_completed must match actual done count
    try:
        import sqlite3
        db_path = project.get_db_path()
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT value FROM metrics WHERE metric = 'tasks_completed'")
            m = cur.fetchone()
            cur.execute("SELECT COUNT(*) FROM tasks WHERE status = 'done'")
            actual = cur.fetchone()[0]
            if m is not None and m[0] != actual:
                cur.execute(
                    "INSERT INTO metrics (metric, value) VALUES ('tasks_completed', ?) ON CONFLICT(metric) DO UPDATE SET value = excluded.value",
                    (actual,),
                )
                conn.commit()
                print("Fixed tasks_completed drift.", file=sys.stderr)
            conn.close()
    except Exception:
        pass

    # 4. Get next task
    r = run([sys.executable, os.path.join(SCRIPTS_DIR, "scheduler.py")])
    task_id = (r.stdout or "").strip()

    if not task_id or task_id.upper() == "NONE":
        # Diagnostic: show project root and task count when "complete"
        total = 0
        try:
            import sqlite3
            db_path = project.get_db_path()
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM tasks")
                total = cur.fetchone()[0]
                conn.close()
        except Exception:
            pass
        print("All tasks complete.")
        print(f"  Project: {PROJECT_ROOT}")
        print(f"  Tasks in DB: {total}")
        if total == 0:
            print("  Hint: No tasks. Run from project folder or set DREAMTEAM_PROJECT=<path>")
        return

    # 5. Set in progress
    run([sys.executable, os.path.join(SCRIPTS_DIR, "update_task.py"), task_id, "in_progress"])

    # 6. Get progress (completed, total)
    completed = 0
    total = 0
    try:
        import sqlite3
        db_path = project.get_db_path()
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT value FROM metrics WHERE metric = 'tasks_completed'")
            row = cur.fetchone()
            completed = row[0] if row else 0
            cur.execute("SELECT COUNT(*) FROM tasks")
            total = cur.fetchone()[0]
            conn.close()
    except Exception:
        pass

    # 7. Print instructions
    print("=" * 60)
    print(f"NEXT TASK: {task_id}  ({completed + 1} of {total})")
    print("=" * 60)
    print()
    print("1. Orchestrator: Dispatch Developer with task ID. Developer uses MCP dreamteam_get_task or Terminal get-task " + task_id)
    print("2. After Reviewer approval: Launch Git-Ops subagent (task ID + short title). Git-Ops does commit.")
    print("3. Then run (update-task done auto-increments counter and emits TRIGGER_*):")
    print()
    print(f"   python -m dreamteam update-task {task_id} done")
    print("   python -m dreamteam run-next")
    print()
    print("4. If update-task prints TRIGGER_RESEARCHER:")
    print("   Researcher agent -> python -m dreamteam vector-index -> python -m dreamteam check-memory")
    print()
    print("5. For new session (every ~20-50 tasks): python -m dreamteam verify-tasks ; python -m dreamteam verify-integrity")
    print("=" * 60)


if __name__ == "__main__":
    main()
