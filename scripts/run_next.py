#!/usr/bin/env python3
"""One-step dispatcher: verify, get next task, print instructions."""

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


def main() -> None:
    """One round: verify -> [auto init-db + sync if needed] -> get task -> print instructions."""
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

    # 3. Quick integrity fix + ensure indexes (migration for existing DBs)
    try:
        sys.path.insert(0, SCRIPTS_DIR)
        import db_utils
        db_path = project.get_db_path()
        if os.path.exists(db_path):
            import sqlite3
            conn = sqlite3.connect(db_path, timeout=10.0)
            try:
                cur = conn.cursor()
                # Ensure scheduler indexes exist
                cur.execute(
                    "CREATE INDEX IF NOT EXISTS idx_tasks_status_priority_id ON tasks(status, priority DESC, id)"
                )
                cur.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
                conn.commit()
                
                # Fix metrics drift
                db_utils.fix_tasks_completed_metric()
            finally:
                conn.close()
    except Exception:
        pass

    # 4. Get next task
    r = run([sys.executable, os.path.join(SCRIPTS_DIR, "scheduler.py")])
    task_id = (r.stdout or "").strip()

    if not task_id or task_id.upper() == "NONE":
        # Distinguish true completion from "no ready tasks" states (blocked/in_progress/deps unmet).
        total = 0
        done = 0
        deprecated = 0
        todo = 0
        in_progress = 0
        blocked = 0
        try:
            import sqlite3
            db_path = project.get_db_path()
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path, timeout=10.0)
                try:
                    cur = conn.cursor()
                    cur.execute("SELECT COUNT(*) FROM tasks")
                    total = cur.fetchone()[0]
                    cur.execute("SELECT COUNT(*) FROM tasks WHERE status = 'done'")
                    done = cur.fetchone()[0]
                    cur.execute("SELECT COUNT(*) FROM tasks WHERE status = 'deprecated'")
                    deprecated = cur.fetchone()[0]
                    cur.execute("SELECT COUNT(*) FROM tasks WHERE status = 'todo'")
                    todo = cur.fetchone()[0]
                    cur.execute("SELECT COUNT(*) FROM tasks WHERE status = 'in_progress'")
                    in_progress = cur.fetchone()[0]
                    cur.execute("SELECT COUNT(*) FROM tasks WHERE status = 'blocked'")
                    blocked = cur.fetchone()[0]
                finally:
                    conn.close()
        except Exception:
            pass

        truly_complete = total > 0 and (done + deprecated == total)
        if truly_complete:
            print("All tasks complete.")
        else:
            print("No ready tasks. Pending tasks remain.")
        print(f"  Project: {PROJECT_ROOT}")
        print(f"  Tasks in DB: {total}")
        print(
            "  Statuses: "
            f"done={done}, deprecated={deprecated}, todo={todo}, in_progress={in_progress}, blocked={blocked}"
        )
        if total == 0:
            print("  Hint: No tasks. Run from project folder or set DREAMTEAM_PROJECT=<path>")
        elif not truly_complete:
            print("  Hint: Run python -m dreamteam verify-integrity and python -m dreamteam recover")
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
            conn = sqlite3.connect(db_path, timeout=10.0)
            try:
                cur = conn.cursor()
                cur.execute("SELECT value FROM metrics WHERE metric = 'tasks_completed'")
                row = cur.fetchone()
                completed = row[0] if row else 0
                cur.execute("SELECT COUNT(*) FROM tasks")
                total = cur.fetchone()[0]
            finally:
                conn.close()
    except Exception:
        pass

    # 7. Print instructions
    print("=" * 60)
    print(f"NEXT TASK: {task_id}  ({completed + 1} of {total})")
    print("=" * 60)
    print()
    print("1. Dispatcher: Deploy specialized Orchestrator with task ID. Orchestrator uses MCP dreamteam_get_task or Terminal get-task " + task_id)
    print("2. After Reviewer approval: Launch Git-Ops subagent (task ID + short title). Git-Ops handles commit/push.")
    print("3. Then run (update-task done auto-increments counter and emits TRIGGER_*):")
    print()
    print(f"   python -m dreamteam update-task {task_id} done")
    print("   python -m dreamteam run-next")
    print()
    print("4. If update-task prints TRIGGER_LEARNING (every 10): Learning -> FixPlanner")
    print("5. If update-task prints TRIGGER_RESEARCHER:")
    print("   Researcher agent -> python -m dreamteam memory-to-files -> python -m dreamteam vector-index -> python -m dreamteam check-memory")
    print()
    print("6. Dispatcher auto-checkpoint every 15 tasks per batch (context switch; project can have thousands of tasks)")
    print("=" * 60)


if __name__ == "__main__":
    main()
