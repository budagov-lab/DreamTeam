#!/usr/bin/env python3
"""Get memory content from database. Key: summaries | architecture."""

import os
import sys

import project
DB_PATH = project.get_db_path()
MEMORY_DIR = project.get_memory_dir()

VALID_KEYS = ("summaries", "architecture")


def get_memory(key: str) -> str | None:
    """Return memory content from DB, or from file if DB empty (migration)."""
    if key not in VALID_KEYS:
        return None

    if not os.path.exists(DB_PATH):
        return _fallback_from_file(key)

    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT content FROM memory WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            return row[0]
    except sqlite3.OperationalError:
        conn.close()
        return _fallback_from_file(key)
    return _fallback_from_file(key)


def _fallback_from_file(key: str) -> str | None:
    """Fallback: read from file (migration from file-based memory)."""
    name = f"{key}.md"
    path = os.path.join(MEMORY_DIR, name)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return f.read()
    return None


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python memory_get.py <summaries|architecture>", file=sys.stderr)
        sys.exit(1)

    key = sys.argv[1].lower()
    if key not in VALID_KEYS:
        print(f"Invalid key. Use: {', '.join(VALID_KEYS)}", file=sys.stderr)
        sys.exit(1)

    content = get_memory(key)
    if content:
        print(content)
    else:
        print(f"No content for {key}.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
