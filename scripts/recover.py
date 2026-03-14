#!/usr/bin/env python3
"""Recovery: fix DB/file sync, reset stuck tasks, validate memory."""

import os
import sys
import sqlite3
from datetime import datetime, timezone, timedelta

import project
DB_PATH = project.get_db_path()
STUCK_MINUTES = 60  # in_progress older than this -> reset to todo


def sync_tasks() -> bool:
    """Run sync_tasks.py."""
    import subprocess
    root = project.get_project_root()
    r = subprocess.run(
        [sys.executable, os.path.join(os.path.dirname(__file__), "sync_tasks.py")],
        cwd=root,
        capture_output=True,
        text=True,
    )
    print(r.stdout or "")
    if r.stderr:
        print(r.stderr, file=sys.stderr)
    return r.returncode == 0


def reset_stuck_tasks(minutes: int = STUCK_MINUTES) -> list[str]:
    """Reset in_progress tasks older than minutes to todo."""
    if not os.path.exists(DB_PATH):
        return []

    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    cursor = conn.cursor()
    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "SELECT id FROM tasks WHERE status = 'in_progress' AND updated_at < ?",
        (cutoff,),
    )
    stuck = [row[0] for row in cursor.fetchall()]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    for tid in stuck:
        cursor.execute("UPDATE tasks SET status = 'todo', updated_at = ? WHERE id = ?", (now, tid))
    conn.commit()
    conn.close()
    return stuck


def fix_tasks_completed_metric() -> bool:
    """Set metrics.tasks_completed = count of done tasks. Fixes drift."""
    if not os.path.exists(DB_PATH):
        return False
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM tasks WHERE status = 'done'")
    actual = cur.fetchone()[0]
    cur.execute(
        "INSERT INTO metrics (metric, value) VALUES ('tasks_completed', ?) ON CONFLICT(metric) DO UPDATE SET value = excluded.value",
        (actual,),
    )
    conn.commit()
    conn.close()
    return True


def reset_task(task_id: str) -> bool:
    """Reset specific task from in_progress to todo."""
    if not os.path.exists(DB_PATH):
        return False
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE tasks SET status = 'todo', updated_at = ? WHERE id = ? AND status = 'in_progress'", (now, task_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    if affected:
        sys.path.insert(0, os.path.dirname(__file__))
        from update_task import update_task_file
        update_task_file(task_id, "todo")
    return affected > 0


def main() -> None:
    """Run recovery steps. Use: recover.py [--reset T001]"""
    if "--reset" in sys.argv:
        idx = sys.argv.index("--reset")
        if idx + 1 < len(sys.argv):
            tid = sys.argv[idx + 1]
            if reset_task(tid):
                print(f"Reset {tid} to todo.")
            else:
                print(f"Task {tid} not found or not in_progress.", file=sys.stderr)
            return
    print("Recovery: sync, reset stuck, verify")
    print("-" * 40)

    # 1. Sync files -> DB
    print("1. Syncing tasks...")
    sync_tasks()

    # 2. Fix tasks_completed metric if drifted
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        cur = conn.cursor()
        cur.execute("SELECT value FROM metrics WHERE metric = 'tasks_completed'")
        m = cur.fetchone()
        cur.execute("SELECT COUNT(*) FROM tasks WHERE status = 'done'")
        actual = cur.fetchone()[0]
        conn.close()
        if m is not None and m[0] != actual:
            fix_tasks_completed_metric()
            print(f"2. Fixed tasks_completed: {m[0]} -> {actual} (actual done count)")
        else:
            print("2. tasks_completed OK (no drift)")

    # 3. Reset stuck in_progress
    stuck = reset_stuck_tasks()
    if stuck:
        print(f"3. Reset stuck tasks (in_progress >{STUCK_MINUTES}min): {', '.join(stuck)}")
        # Also update task files
        sys.path.insert(0, os.path.dirname(__file__))
        from update_task import update_task_file
        for tid in stuck:
            update_task_file(tid, "todo")
    else:
        print("3. No stuck tasks.")

    # 4. Verify
    print("4. Verifying...")
    import subprocess
    root = project.get_project_root()
    r = subprocess.run(
        [sys.executable, os.path.join(os.path.dirname(__file__), "verify_tasks.py")],
        cwd=root,
        capture_output=True,
        text=True,
    )
    print(r.stdout or "")
    if r.returncode != 0:
        print("Verify failed. Run sync_tasks again if needed.", file=sys.stderr)

    # 4b. Integrity check
    print("4b. Integrity check...")
    r = subprocess.run(
        [sys.executable, os.path.join(os.path.dirname(__file__), "verify_integrity.py")],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        print(r.stderr or r.stdout or "", file=sys.stderr)
        print("Integrity failed. tasks_completed may be wrong — recover fixed it in step 2.", file=sys.stderr)
    else:
        print(r.stdout or "OK")

    # 5. Check memory
    print("5. Checking memory...")
    r = subprocess.run(
        [sys.executable, os.path.join(os.path.dirname(__file__), "check_memory.py")],
        cwd=root,
        capture_output=True,
        text=True,
    )
    print(r.stdout or "")
    if r.returncode != 0:
        print("Memory check failed. Run Researcher to compress.", file=sys.stderr)

    print("-" * 40)
    print("Recovery done. Run: dreamteam run-next")


if __name__ == "__main__":
    main()
