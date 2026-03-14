#!/usr/bin/env python3
"""Scheduler: select next available task for execution."""

import sqlite3
import os
import sys
import json

import db


def get_done_ids(cursor: sqlite3.Cursor) -> set[str]:
    """Return set of task IDs with status 'done'."""
    cursor.execute("SELECT id FROM tasks WHERE status = 'done'")
    return {row[0] for row in cursor.fetchall()}


def parse_dependencies(deps_str: str | None) -> list[str]:
    """Parse dependencies from JSON string or comma-separated list."""
    if not deps_str or deps_str.strip() in ("", "[]"):
        return []
    try:
        parsed = json.loads(deps_str)
        return parsed if isinstance(parsed, list) else [str(parsed)]
    except json.JSONDecodeError:
        return [s.strip() for s in deps_str.split(",") if s.strip()]


def get_next_task() -> str | None:
    """Return next task ID ready for execution, or None.
    Order: priority DESC, id ASC. First task with all deps in done_ids.
    For fresh project: T001 (deps=[]) is always first."""
    if not os.path.exists(db.DB_PATH):
        print("Database not found. Run: dreamteam init-db", file=sys.stderr)
        return None

    with db.conn() as (conn, cursor):
        done_ids = get_done_ids(cursor)
        cursor.execute(
            """
            SELECT id, title, status, priority, dependencies
            FROM tasks
            WHERE status = 'todo'
            ORDER BY priority DESC, id ASC
            """
        )
        rows = cursor.fetchall()

    for task_id, title, status, priority, deps_str in rows:
        deps = parse_dependencies(deps_str)
        if all(d in done_ids for d in deps):
            return task_id

    return None


def list_tasks() -> None:
    """List all tasks with status."""
    if not os.path.exists(db.DB_PATH):
        print("Database not found. Run: dreamteam init-db", file=sys.stderr)
        return

    with db.conn() as (conn, cursor):
        cursor.execute(
            "SELECT id, title, status, priority, dependencies FROM tasks ORDER BY id"
        )
        rows = cursor.fetchall()

    for task_id, title, status, priority, deps in rows:
        print(f"{task_id} | {status} | P{priority} | {title} | deps: {deps or '[]'}")


def list_ready() -> None:
    """List tasks ready for execution."""
    if not os.path.exists(db.DB_PATH):
        print("Database not found. Run: dreamteam init-db", file=sys.stderr)
        return

    with db.conn() as (conn, cursor):
        done_ids = get_done_ids(cursor)
        cursor.execute(
            """
            SELECT id, title, status, priority, dependencies
            FROM tasks
            WHERE status = 'todo'
            ORDER BY priority DESC, id ASC
            """
        )
        rows = cursor.fetchall()

    for task_id, title, status, priority, deps_str in rows:
        deps = parse_dependencies(deps_str)
        if all(d in done_ids for d in deps):
            print(f"{task_id} | P{priority} | {title}")


if __name__ == "__main__":
    if "--list" in sys.argv:
        list_tasks()
    elif "--ready" in sys.argv:
        list_ready()
    else:
        task_id = get_next_task()
        print(task_id if task_id else "NONE")
