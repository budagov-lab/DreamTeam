#!/usr/bin/env python3
"""Add or update a task in the database from a markdown file."""

import sqlite3
import os
import sys
import re
import json
from datetime import datetime, timezone
from typing import Any

import project # type: ignore
DB_PATH = project.get_db_path()
TASKS_DIR = project.get_tasks_dir()


def parse_task_file(content: str) -> dict[str, Any] | None:
    """Parse task markdown frontmatter into dict."""
    # Match id:, title:, status:, priority:, dependencies:, owner:
    patterns = {
        "id": r"^id:\s*(.+)",
        "title": r"^title:\s*(.+)",
        "status": r"^status:\s*(.+)",
        "priority": r"^priority:\s*(\d+)",
        "dependencies": r"^dependencies:\s*(.+)",
        "owner": r"^owner:\s*(.+)",
        "sort_order": r"^sort_order:\s*(\d+)",
    }
    result: dict[str, Any] = {}
    for key, pattern in patterns.items():
        m = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
        if m:
            val = m.group(1).strip()
            if key == "dependencies":
                val = val.strip("[]")
                if val:
                    try:
                        result[key] = json.dumps([x.strip() for x in val.split(",")])
                    except Exception:
                        result[key] = "[]"
                else:
                    result[key] = "[]"
            elif key == "priority":
                result[key] = int(val) if val.isdigit() else 1
            elif key == "sort_order":
                result[key] = int(val) if val.lstrip("-").isdigit() else 0
            else:
                result[key] = val
    if "id" not in result:
        return None
    result.setdefault("title", "")
    result.setdefault("status", "todo")
    result.setdefault("priority", 1)
    result.setdefault("dependencies", "[]")
    result.setdefault("owner", "")
    result.setdefault("sort_order", 0)
    return result


def _ensure_content_column(cursor: sqlite3.Cursor) -> None:
    """Add content column if missing (migration)."""
    cursor.execute("PRAGMA table_info(tasks)")
    if not any(col[1] == "content" for col in cursor.fetchall()):
        cursor.execute("ALTER TABLE tasks ADD COLUMN content TEXT")


def _ensure_sort_order_column(cursor: sqlite3.Cursor) -> None:
    """Add sort_order column if missing (migration)."""
    cursor.execute("PRAGMA table_info(tasks)")
    if not any(col[1] == "sort_order" for col in cursor.fetchall()):
        cursor.execute("ALTER TABLE tasks ADD COLUMN sort_order INTEGER DEFAULT 0")


def add_task_to_cursor(
    cursor: sqlite3.Cursor,
    task_data: dict[str, Any],
    now: str | None = None,
    upsert: bool = True,
) -> None:
    """Insert or update task using existing cursor. No commit. For batch sync."""
    if now is None:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    content = task_data.get("content", "")
    _ensure_content_column(cursor)
    _ensure_sort_order_column(cursor)
    sort_order = task_data.get("sort_order", 0)
    if upsert:
        cursor.execute(
            """
            INSERT INTO tasks (id, title, status, priority, dependencies, owner, content, sort_order, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title = excluded.title,
                status = excluded.status,
                priority = excluded.priority,
                dependencies = excluded.dependencies,
                owner = excluded.owner,
                content = excluded.content,
                sort_order = excluded.sort_order,
                updated_at = excluded.updated_at
            """,
            (
                task_data["id"],
                task_data["title"],
                task_data["status"],
                task_data["priority"],
                task_data["dependencies"],
                task_data.get("owner", ""),
                content,
                sort_order,
                now,
                now,
            ),
        )
    else:
        cursor.execute(
            """
            INSERT OR IGNORE INTO tasks (id, title, status, priority, dependencies, owner, content, sort_order, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task_data["id"],
                task_data["title"],
                task_data["status"],
                task_data["priority"],
                task_data["dependencies"],
                task_data.get("owner", ""),
                content,
                sort_order,
                now,
                now,
            ),
        )


def add_task(task_data: dict[str, Any], upsert: bool = True) -> bool:
    """Insert or update task in database (single task, commits)."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    cursor = conn.cursor()
    try:
        add_task_to_cursor(cursor, task_data, upsert=upsert)
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding task: {e}", file=sys.stderr)
        return False
    finally:
        conn.close()
    return False


def main() -> None:
    """Add task from file or stdin."""
    if len(sys.argv) < 2:
        print("Usage: python add_task.py <task_id|file_path>", file=sys.stderr)
        sys.exit(1)

    arg = sys.argv[1]
    content = ""

    if os.path.exists(arg):
        with open(arg, encoding="utf-8") as f:
            content = f.read()
    else:
        path = os.path.join(TASKS_DIR, f"{arg}.md")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                content = f.read()

    if not content:
        print(f"Task file not found: {arg}", file=sys.stderr)
        sys.exit(1)

    task_data = parse_task_file(content)
    if task_data is None:
        print("Could not parse task (missing id)", file=sys.stderr)
        sys.exit(1)
        return
    task_data["content"] = content
    add_task(task_data)
    print(f"Task {task_data['id']} added/updated.")


if __name__ == "__main__":
    main()
