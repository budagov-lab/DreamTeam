#!/usr/bin/env python3
"""Researcher: prepare context for Researcher agent. Run when TRIGGER_RESEARCHER fires."""

import sqlite3
import os
import sys
import json

import project
DB_PATH = project.get_db_path()
TASKS_DIR = project.get_tasks_dir()
MEMORY_DIR = project.get_memory_dir()
DEFAULT_LAST_N = 20


def get_last_completed_tasks(n: int = DEFAULT_LAST_N) -> list[dict]:
    """Fetch last N completed tasks from database."""
    if not os.path.exists(DB_PATH):
        return []

    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, title, status, priority, dependencies, owner, updated_at
        FROM tasks
        WHERE status = 'done'
        ORDER BY updated_at DESC
        LIMIT ?
        """,
        (n,),
    )
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_task_file_content(task_id: str) -> str | None:
    """Read task file content if it exists."""
    for name in (f"task_{task_id[1:]}.md", f"{task_id}.md"):
        path = os.path.join(TASKS_DIR, name)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return f.read()
    return None


def main() -> None:
    """Output context for Researcher agent."""
    n = DEFAULT_LAST_N
    if "--n" in sys.argv:
        idx = sys.argv.index("--n")
        if idx + 1 < len(sys.argv):
            try:
                n = int(sys.argv[idx + 1])
            except ValueError:
                pass

    tasks = get_last_completed_tasks(n)
    if not tasks:
        print("No completed tasks found.")
        return

    print("# Last completed tasks (for Researcher context)\n")
    for t in tasks:
        print(f"- **{t['id']}**: {t['title']} (owner: {t['owner'] or 'unassigned'})")
        content = get_task_file_content(t["id"])
        if content:
            print(f"  ```\n  {content.strip()[:200]}...\n  ```")
        print()

    arch_path = os.path.join(MEMORY_DIR, "architecture.md")
    sum_path = os.path.join(MEMORY_DIR, "summaries.md")
    print("# Memory files to update\n")
    print(f"- {arch_path}")
    print(f"- {sum_path}")
    print("\nResearcher should update these files with summary and architecture changes.")
    print("\n# After writing, run:")
    print("  dreamteam check-memory")
    print("  dreamteam vector-index  # reindex codebase for semantic search")


if __name__ == "__main__":
    main()
