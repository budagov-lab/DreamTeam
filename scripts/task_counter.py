#!/usr/bin/env python3
"""Task counter: show tasks_completed. Increment is done by update-task done."""

import sqlite3
import os
import sys

import project
DB_PATH = project.get_db_path()

TRIGGER_RESEARCHER = 20
TRIGGER_META_PLANNER = 50
TRIGGER_AUDITOR = 200


def get_count(cursor: sqlite3.Cursor) -> int:
    """Get current tasks_completed value."""
    cursor.execute("SELECT value FROM metrics WHERE metric = 'tasks_completed'")
    row = cursor.fetchone()
    return row[0] if row else 0


def status() -> int:
    """Print current count and total tasks."""
    if not os.path.exists(DB_PATH):
        print("Database not found. Run: python -m dreamteam init-db", file=sys.stderr)
        return 0

    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    cursor = conn.cursor()
    count = get_count(cursor)
    cursor.execute("SELECT COUNT(*) FROM tasks")
    total = cursor.fetchone()[0]
    conn.close()

    print(f"tasks_completed: {count} / {total}")
    if count > 0:
        if count % TRIGGER_RESEARCHER == 0:
            print("TRIGGER_RESEARCHER")
        if count % TRIGGER_META_PLANNER == 0:
            print("TRIGGER_META_PLANNER")
        if count % TRIGGER_AUDITOR == 0:
            print("TRIGGER_AUDITOR")
    return count


if __name__ == "__main__":
    status()
