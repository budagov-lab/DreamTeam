#!/usr/bin/env python3
"""Sync memory from DB to files. Run after Researcher/Auditor so other agents can read from files."""

import os
import sys

import project
DB_PATH = project.get_db_path()
MEMORY_DIR = project.get_memory_dir()


def main() -> None:
    """Copy memory from DB to .dreamteam/memory/*.md files."""
    if not os.path.exists(DB_PATH):
        print("Database not found.", file=sys.stderr)
        sys.exit(1)

    import sqlite3
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT key, content FROM memory")
        rows = cursor.fetchall()
    except sqlite3.OperationalError:
        conn.close()
        print("Memory table not found. Run memory-set first.", file=sys.stderr)
        sys.exit(1)
    conn.close()

    os.makedirs(MEMORY_DIR, exist_ok=True)
    count = 0
    for key, content in rows:
        if content:
            path = os.path.join(MEMORY_DIR, f"{key}.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            count += 1
            print(f"Synced {key} to {path}")

    if count == 0:
        print("No memory content in DB.")
    else:
        print(f"Synced {count} memory keys to files.")


if __name__ == "__main__":
    main()
