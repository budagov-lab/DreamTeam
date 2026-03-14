#!/usr/bin/env python3
"""Validate memory stays within bounds for 1000-task scaling. Reads from DB."""

import os
import sys

import project
DB_PATH = project.get_db_path()
MEMORY_DIR = project.get_memory_dir()
SUMMARIES_MAX_LINES = 150
ARCHITECTURE_MAX_LINES = 200


def _get_memory_content(key: str) -> str | None:
    """Get memory from DB, fallback to file."""
    if os.path.exists(DB_PATH):
        import sqlite3
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT content FROM memory WHERE key = ?", (key,))
            row = cursor.fetchone()
            conn.close()
            if row and row[0]:
                return row[0]
        except sqlite3.OperationalError:
            conn.close()
    path = os.path.join(MEMORY_DIR, f"{key}.md")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return f.read()
    return None


def check_summaries() -> tuple[bool, int, str]:
    """Return (ok, line_count, message). Reads from DB."""
    content = _get_memory_content("summaries")
    if not content:
        return True, 0, "summaries not found (ok for new project)"
    lines = len(content.splitlines())
    if lines > SUMMARIES_MAX_LINES:
        return False, lines, f"summaries has {lines} lines (max {SUMMARIES_MAX_LINES}). Researcher must compress."
    return True, lines, f"summaries: {lines} lines (ok)"


def check_architecture() -> tuple[bool, int, str]:
    """Return (ok, line_count, message). Reads from DB."""
    content = _get_memory_content("architecture")
    if not content:
        return True, 0, "architecture not found"
    lines = len(content.splitlines())
    if lines > ARCHITECTURE_MAX_LINES:
        return False, lines, f"architecture has {lines} lines (max {ARCHITECTURE_MAX_LINES}). Consider splitting."
    return True, lines, f"architecture: {lines} lines (ok)"


def main() -> None:
    """Validate memory files."""
    summaries_ok, sum_lines, sum_msg = check_summaries()
    arch_ok, arch_lines, arch_msg = check_architecture()

    print(sum_msg)
    print(arch_msg)

    if not summaries_ok:
        print("\nWARNING: summaries exceeds limit. Run Researcher with compression rules.", file=sys.stderr)
        sys.exit(1)
    if not arch_ok:
        print("\nWARNING: architecture exceeds limit.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
