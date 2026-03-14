#!/usr/bin/env python3
"""List recent done tasks from DB. For Researcher context."""

import os
import sys

import project
DB_PATH = project.get_db_path()


def main() -> None:
    """Output last N done tasks (id, title, content excerpt)."""
    limit = 20
    if len(sys.argv) >= 2 and sys.argv[1].isdigit():
        limit = int(sys.argv[1])

    if not os.path.exists(DB_PATH):
        print("Database not found.", file=sys.stderr)
        sys.exit(1)

    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA table_info(tasks)")
        has_content = any(col[1] == "content" for col in cursor.fetchall())
        if has_content:
            cursor.execute(
                """
                SELECT id, title, content FROM tasks
                WHERE status = 'done'
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (limit,),
            )
        else:
            cursor.execute(
                """
                SELECT id, title, '' FROM tasks
                WHERE status = 'done'
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (limit,),
            )
        rows = cursor.fetchall()
    except sqlite3.OperationalError:
        rows = []
    conn.close()

    print("# Recent done tasks\n")
    for task_id, title, content in rows:
        excerpt = (content or "")[:500].replace("\n", " ") if content else ""
        print(f"## {task_id}: {title}")
        if excerpt:
            print(excerpt)
        print()


if __name__ == "__main__":
    main()
