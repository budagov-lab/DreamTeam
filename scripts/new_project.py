#!/usr/bin/env python3
"""Create a new DreamTeam project. Usage: new_project.py <path> or new_project.py (creates in cwd)."""

import os
import sys
import shutil

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
DREAMTEAM_ROOT = os.path.dirname(SCRIPTS_DIR)
CURSOR_SOURCE = os.path.join(DREAMTEAM_ROOT, ".cursor")
ARCHITECTURE_TEMPLATE = """# Architecture

## Modules

(Add module descriptions as the project grows. Code ownership map: module → owner.)

| Module | Description | Owner |
|--------|-------------|-------|
| (add modules) | | |

## Dependencies

(Define layer hierarchy and module dependencies.)

```
Layer 1 (low-level):
Layer 2: business logic
Layer 3 (UI):
```

## Rules

- No circular dependencies
- Lower layers must not depend on upper layers
- Respect code ownership when editing modules
"""

SUMMARIES_TEMPLATE = """# Summaries

## Progress

(Researcher updates this every 20 tasks.)

## Key Decisions

(Architectural decisions and rationale.)
"""


def create_project(path: str) -> str:
    """Create project structure. Returns project root."""
    root = os.path.abspath(path)
    os.makedirs(root, exist_ok=True)

    data_root = os.path.join(root, ".dreamteam")
    os.makedirs(data_root, exist_ok=True)
    dirs = ["db", "memory", "tasks", "docs", "docs/epics"]
    for d in dirs:
        os.makedirs(os.path.join(data_root, d), exist_ok=True)

    # Copy .cursor (agents, skills, rules) — stays at project root for Cursor IDE
    cursor_dest = os.path.join(root, ".cursor")
    if os.path.normpath(CURSOR_SOURCE) == os.path.normpath(cursor_dest):
        pass  # Same path (new-project . from DreamTeam root) — keep existing .cursor
    elif os.path.isdir(CURSOR_SOURCE):
        if os.path.exists(cursor_dest):
            shutil.rmtree(cursor_dest)
        shutil.copytree(CURSOR_SOURCE, cursor_dest)
    else:
        os.makedirs(cursor_dest, exist_ok=True)
        print("Warning: .cursor not found in DreamTeam, created empty .cursor/", file=sys.stderr)

    arch = os.path.join(data_root, "memory", "architecture.md")
    if not os.path.exists(arch):
        with open(arch, "w", encoding="utf-8") as f:
            f.write(ARCHITECTURE_TEMPLATE)

    summaries = os.path.join(data_root, "memory", "summaries.md")
    if not os.path.exists(summaries):
        with open(summaries, "w", encoding="utf-8") as f:
            f.write(SUMMARIES_TEMPLATE)

    # Init db
    db_path = os.path.join(data_root, "db", "dag.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    import sqlite3
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    for t in ("tasks", "metrics", "context_graph", "vector_code"):
        c.execute(f"DROP TABLE IF EXISTS {t}")
    conn.commit()
    c.execute("""CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY, title TEXT, status TEXT, priority INTEGER,
        dependencies TEXT, owner TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")
    c.execute("CREATE TABLE IF NOT EXISTS metrics (metric TEXT PRIMARY KEY, value INTEGER)")
    c.execute("CREATE TABLE IF NOT EXISTS context_graph (module TEXT, functions TEXT, dependencies TEXT, embedding BLOB)")
    c.execute("CREATE TABLE IF NOT EXISTS vector_code (path TEXT, chunk TEXT, embedding BLOB, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)")
    c.execute("INSERT OR IGNORE INTO metrics (metric, value) VALUES ('tasks_completed', 0)")
    conn.commit()
    conn.close()

    return root


def main() -> None:
    if len(sys.argv) >= 2:
        path = sys.argv[1]
    else:
        path = os.getcwd()

    root = create_project(path)
    print(f"Project created: {root}")
    print()
    print("To use this project:")
    print(f"  cd {root}")
    print(f"  python {os.path.join(SCRIPTS_DIR, 'run_next.py')}")
    print()
    print("Or set env: DREAMTEAM_PROJECT=" + root)
    print()
    print("Each project has its own: .dreamteam/ (db, memory, tasks), .cursor/ (agents, rules) — brains are isolated.")


if __name__ == "__main__":
    main()
