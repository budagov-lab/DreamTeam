#!/usr/bin/env python3
"""Verify consistency between task files (.dreamteam/tasks/*.md) and database."""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from add_task import parse_task_file

import project
DB_PATH = project.get_db_path()
TASKS_DIR = project.get_tasks_dir()


def get_db_tasks():
    """Return dict task_id -> {status, title, priority, dependencies, owner}."""
    if not os.path.exists(DB_PATH):
        return {}
    import sqlite3
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, status, priority, dependencies, owner FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    return {r["id"]: r for r in rows}


def get_file_tasks():
    """Return dict task_id -> {status, title, priority, dependencies, owner}."""
    if not os.path.exists(TASKS_DIR):
        return {}
    result = {}
    for name in os.listdir(TASKS_DIR):
        if not name.endswith(".md"):
            continue
        path = os.path.join(TASKS_DIR, name)
        with open(path, encoding="utf-8") as f:
            content = f.read()
        data = parse_task_file(content)
        if data:
            result[data["id"]] = data
    return result


def verify() -> tuple[list[str], list[str], list[dict]]:
    """
    Compare DB vs files.
    Returns: (only_in_db, only_in_files, mismatches)
    """
    db_tasks = get_db_tasks()
    file_tasks = get_file_tasks()

    only_in_db = [tid for tid in db_tasks if tid not in file_tasks]
    only_in_files = [tid for tid in file_tasks if tid not in db_tasks]

    mismatches = []
    for tid in set(db_tasks) & set(file_tasks):
        db = db_tasks[tid]
        fl = file_tasks[tid]
        diff = {}
        for key in ("status", "title", "priority", "dependencies", "owner"):
            db_val = str(db.get(key, "") or "").strip()
            fl_val = str(fl.get(key, "") or "").strip()
            if key == "dependencies":
                import json
                try:
                    db_list = json.loads(db_val) if db_val else []
                    fl_list = json.loads(fl_val) if fl_val.startswith("[") else [x.strip() for x in (fl_val or "").split(",") if x.strip()]
                    db_val = ",".join(sorted(db_list)) if isinstance(db_list, list) else db_val
                    fl_val = ",".join(sorted(fl_list)) if isinstance(fl_list, list) else fl_val
                except (json.JSONDecodeError, TypeError):
                    pass
            if db_val != fl_val:
                diff[key] = {"db": db_val, "file": fl_val}
        if diff:
            mismatches.append({"id": tid, "diff": diff})

    return only_in_db, only_in_files, mismatches


def main() -> None:
    """Report verification results."""
    if not os.path.exists(DB_PATH):
        print("Database not found. Run: dreamteam init-db", file=sys.stderr)
        sys.exit(1)

    only_db, only_files, mismatches = verify()

    has_issues = bool(only_db or only_files or mismatches)

    if only_db:
        print("Only in DB (missing file):", ", ".join(only_db))
    if only_files:
        print("Only in files (missing in DB):", ", ".join(only_files))
    if mismatches:
        for m in mismatches:
            print(f"Mismatch {m['id']}:")
            for k, v in m["diff"].items():
                print(f"  {k}: db={v['db']!r} vs file={v['file']!r}")

    if not has_issues:
        print("OK: All tasks consistent between files and database.")
    else:
        print("\nFix: dreamteam sync-tasks (files -> DB)")
        sys.exit(1)


if __name__ == "__main__":
    main()
