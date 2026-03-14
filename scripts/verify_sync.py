#!/usr/bin/env python3
"""Verify that tasks in DB have content. Exit 1 if any task missing content -> run sync-tasks."""

import os
import sys

import project
DB_PATH = project.get_db_path()


def main() -> None:
    if not os.path.exists(DB_PATH):
        print("Database not found. Run: python -m dreamteam init-db", file=sys.stderr)
        sys.exit(1)

    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA table_info(tasks)")
        if not any(col[1] == "content" for col in cursor.fetchall()):
            conn.close()
            print("DB missing content column. Run: python -m dreamteam sync-tasks", file=sys.stderr)
            sys.exit(1)

        cursor.execute("SELECT id FROM tasks WHERE content IS NULL OR content = ''")
        missing = [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()

    if missing:
        print("Tasks missing content in DB:", ", ".join(missing[:10]), end="")
        if len(missing) > 10:
            print(f" ... (+{len(missing) - 10} more)")
        else:
            print()
        print("Fix: python -m dreamteam sync-tasks", file=sys.stderr)
        sys.exit(1)

    print("OK: All tasks have content in DB.")


if __name__ == "__main__":
    main()
