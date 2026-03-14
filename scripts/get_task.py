#!/usr/bin/env python3
"""Get task content by ID. Reads from DB (or file if DB has no content)."""

import os
import sys

import project
DB_PATH = project.get_db_path()
TASKS_DIR = project.get_tasks_dir()


def get_task(task_id: str) -> str | None:
    """Return full task content from DB or file."""
    if not os.path.exists(DB_PATH):
        return _get_from_file(task_id)

    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA table_info(tasks)")
        if not any(col[1] == "content" for col in cursor.fetchall()):
            conn.close()
            return _get_from_file(task_id)

        cursor.execute("SELECT content FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            return row[0]
    except Exception:
        conn.close()
    return _get_from_file(task_id)


def _get_from_file(task_id: str) -> str | None:
    """Fallback: read from file."""
    for name in (f"task_{task_id[1:]}.md", f"{task_id}.md"):
        path = os.path.join(TASKS_DIR, name)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return f.read()
    return None


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python get_task.py <task_id>", file=sys.stderr)
        sys.exit(1)

    task_id = sys.argv[1]
    content = get_task(task_id)
    if content:
        print(content)
    else:
        print(f"Task {task_id} not found.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
