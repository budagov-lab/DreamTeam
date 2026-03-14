#!/usr/bin/env python3
"""Set memory content in database. Key: summaries | architecture. Reads from stdin or file."""

import os
import sys
from datetime import datetime, timezone

import project
DB_PATH = project.get_db_path()
MEMORY_DIR = project.get_memory_dir()

VALID_KEYS = ("summaries", "architecture")


def set_memory(key: str, content: str) -> bool:
    """Write memory content to DB."""
    if key not in VALID_KEYS:
        return False

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    import sqlite3
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    cursor = conn.cursor()

    # Ensure memory table exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            key TEXT PRIMARY KEY,
            content TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        """
        INSERT INTO memory (key, content, updated_at) VALUES (?, ?, ?)
        ON CONFLICT(key) DO UPDATE SET content = excluded.content, updated_at = excluded.updated_at
        """,
        (key, content, now),
    )
    conn.commit()
    conn.close()
    return True


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python memory_set.py <summaries|architecture> [file]", file=sys.stderr)
        print("  Reads from stdin if no file, else from file.", file=sys.stderr)
        sys.exit(1)

    key = sys.argv[1].lower()
    if key not in VALID_KEYS:
        print(f"Invalid key. Use: {', '.join(VALID_KEYS)}", file=sys.stderr)
        sys.exit(1)

    if len(sys.argv) >= 3:
        path = sys.argv[2]
        if not os.path.exists(path):
            print(f"File not found: {path}", file=sys.stderr)
            sys.exit(1)
        with open(path, encoding="utf-8") as f:
            content = f.read()
    else:
        content = sys.stdin.read()

    if set_memory(key, content):
        print(f"Memory {key} updated in DB.")
    else:
        print(f"Failed to update {key}.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
