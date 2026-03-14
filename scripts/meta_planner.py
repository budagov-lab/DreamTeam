#!/usr/bin/env python3
"""Meta Planner: prepare context for Meta Planner agent. Run when TRIGGER_META_PLANNER fires."""

import sqlite3
import os
import sys
import json

import project
DB_PATH = project.get_db_path()


def get_dag_state() -> dict:
    """Fetch full DAG state for Meta Planner."""
    if not os.path.exists(DB_PATH):
        return {}

    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, status, priority, dependencies, owner FROM tasks ORDER BY id"
    )
    tasks = [dict(row) for row in cursor.fetchall()]
    cursor.execute("SELECT metric, value FROM metrics")
    metrics = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()

    return {"tasks": tasks, "metrics": metrics}


def main() -> None:
    """Output context for Meta Planner agent."""
    state = get_dag_state()
    if not state:
        print("Database not found or empty.")
        return

    print("# DAG state (for Meta Planner)\n")
    print("## Metrics")
    for k, v in state["metrics"].items():
        print(f"- {k}: {v}")

    print("\n## Tasks")
    for t in state["tasks"]:
        print(f"- {t['id']} | {t['status']} | P{t['priority']} | {t['title']} | deps: {t['dependencies'] or '[]'}")

    print("\nMeta Planner should: analyze tech debt, optimize DAG, resplit tasks, create refactor tasks.")


if __name__ == "__main__":
    main()
