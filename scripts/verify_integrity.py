#!/usr/bin/env python3
"""Verify DB integrity: tasks_completed vs done count, gaps, orphan deps. Prevents 'lost' tasks."""

import json
import os
import re
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(__file__))
import project

DB_PATH = project.get_db_path()


def _parse_deps(deps_str):
    if not deps_str or deps_str.strip() in ("", "[]"):
        return []
    try:
        p = json.loads(deps_str)
        return p if isinstance(p, list) else []
    except json.JSONDecodeError:
        return [x.strip() for x in deps_str.split(",") if x.strip()]


def verify() -> tuple[list[str], bool]:
    """Returns (errors, ok)."""
    errors = []
    if not os.path.exists(DB_PATH):
        errors.append("Database not found. Run: dreamteam init-db")
        return errors, False

    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    cur = conn.cursor()

    # 1. tasks_completed must equal count of done tasks
    cur.execute("SELECT value FROM metrics WHERE metric = 'tasks_completed'")
    row = cur.fetchone()
    metric_count = row[0] if row else 0
    cur.execute("SELECT COUNT(*) FROM tasks WHERE status = 'done'")
    actual_done = cur.fetchone()[0]
    if metric_count != actual_done:
        errors.append(
            f"Integrity: tasks_completed={metric_count} but {actual_done} tasks have status=done. "
            f"Run: dreamteam recover (or fix metrics manually)"
        )

    # 2. Orphan deps: task references dep that doesn't exist
    cur.execute("SELECT id, dependencies FROM tasks")
    all_ids = set()
    orphan_deps = []
    for tid, deps_str in cur.fetchall():
        all_ids.add(tid)
    cur.execute("SELECT id, dependencies FROM tasks")
    for tid, deps_str in cur.fetchall():
        deps = _parse_deps(deps_str)
        for d in deps:
            if d not in all_ids:
                orphan_deps.append(f"{tid} depends on missing {d}")
    if orphan_deps:
        errors.append("Orphan deps (task references non-existent): " + "; ".join(orphan_deps[:5]))
        if len(orphan_deps) > 5:
            errors[-1] += f" ... +{len(orphan_deps) - 5} more"

    # 3. Gap check: for T001, T002, ... T999 pattern
    cur.execute("SELECT id FROM tasks ORDER BY id")
    ids = [r[0] for r in cur.fetchall()]
    tnum = re.compile(r"^T(\d+)$", re.I)
    numeric_ids = []
    for i in ids:
        m = tnum.match(i)
        if m:
            numeric_ids.append((i, int(m.group(1))))
    if numeric_ids:
        numeric_ids.sort(key=lambda x: x[1])
        prev = 0
        gaps = []
        for tid, n in numeric_ids:
            if prev and n > prev + 1:
                gaps.append(f"T{prev + 1:03d}-T{n - 1:03d}")
            prev = n
        if gaps:
            errors.append("Gap (missing task IDs): " + ", ".join(gaps[:3]))
            if len(gaps) > 3:
                errors[-1] += f" ... +{len(gaps) - 3} more"

    conn.close()
    return errors, len(errors) == 0


def main() -> None:
    errors, ok = verify()
    if ok:
        print("OK: Integrity check passed.")
        return
    for e in errors:
        print(e, file=sys.stderr)
    print("\nFix: dreamteam recover (resync, reset stuck). Or fix DB manually.", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
