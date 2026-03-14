#!/usr/bin/env python3
"""Update task status in the database (and optionally in the task file)."""

import sqlite3
import os
import sys
import re
from datetime import datetime, timezone

import project
DB_PATH = project.get_db_path()
TASKS_DIR = project.get_tasks_dir()

VALID_STATUSES = ("todo", "in_progress", "done", "blocked")

TRIGGER_RESEARCHER = 20
TRIGGER_META_PLANNER = 50
TRIGGER_AUDITOR = 200


def update_task_file(task_id: str, status: str, owner: str | None = None) -> bool:
    """Update status (and owner) in task markdown file."""
    for name in (f"task_{task_id[1:]}.md", f"{task_id}.md"):
        path = os.path.join(TASKS_DIR, name)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                content = f.read()
            content = re.sub(r"status:\s*\w+", f"status: {status}", content, flags=re.IGNORECASE)
            if owner is not None:
                content = re.sub(r"owner:\s*.+", f"owner: {owner}", content, flags=re.IGNORECASE)
                if "owner:" not in content.lower():
                    content = content.rstrip() + f"\nowner: {owner}\n"
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
    return False


def update_status(task_id: str, status: str, owner: str | None = None, sync_file: bool = True) -> bool:
    """Update task status."""
    if status not in VALID_STATUSES:
        print(f"Invalid status: {status}. Must be one of {VALID_STATUSES}", file=sys.stderr)
        return False

    if not os.path.exists(DB_PATH):
        print("Database not found. Run: dreamteam init-db", file=sys.stderr)
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    if owner is not None:
        cursor.execute(
            "UPDATE tasks SET status = ?, owner = ?, updated_at = ? WHERE id = ?",
            (status, owner, now, task_id),
        )
    else:
        cursor.execute(
            "UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?",
            (status, now, task_id),
        )
    affected = cursor.rowcount
    if affected > 0 and status == "done":
        cursor.execute(
            "UPDATE metrics SET value = value + 1 WHERE metric = 'tasks_completed'"
        )
        cursor.execute("SELECT value FROM metrics WHERE metric = 'tasks_completed'")
        row = cursor.fetchone()
        count = row[0] if row else 0
        if count % TRIGGER_RESEARCHER == 0 and count > 0:
            print("TRIGGER_RESEARCHER")
        if count % TRIGGER_META_PLANNER == 0 and count > 0:
            print("TRIGGER_META_PLANNER")
        if count % TRIGGER_AUDITOR == 0 and count > 0:
            print("TRIGGER_AUDITOR")
        print(f"tasks_completed: {count}")

    conn.commit()
    conn.close()

    if affected > 0 and sync_file:
        update_task_file(task_id, status, owner)

    return affected > 0


def main() -> None:
    """Update task status from CLI."""
    if len(sys.argv) < 3:
        print("Usage: python update_task.py <task_id> <status> [owner]", file=sys.stderr)
        print(f"Status: {', '.join(VALID_STATUSES)}", file=sys.stderr)
        sys.exit(1)

    task_id = sys.argv[1]
    status = sys.argv[2].lower()
    owner = None
    sync_file = True
    for i, arg in enumerate(sys.argv[3:], 3):
        if arg == "--no-sync-file":
            sync_file = False
        elif not arg.startswith("--"):
            owner = arg
            break

    if update_status(task_id, status, owner, sync_file):
        print(f"Task {task_id} set to {status}.")
    else:
        print(f"Failed to update task {task_id}.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
