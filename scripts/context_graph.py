#!/usr/bin/env python3
"""Context graph: manage module/function dependencies for code navigation and refactoring."""

import sqlite3
import os
import sys
import json

import project
DB_PATH = project.get_db_path()


def add_module(module: str, functions: str | list, dependencies: str | list) -> None:
    """Add or update a module in context_graph."""
    if isinstance(functions, list):
        functions = json.dumps(functions)
    if isinstance(dependencies, list):
        dependencies = json.dumps(dependencies)

    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM context_graph WHERE module = ?", (module,))
    cursor.execute(
        "INSERT INTO context_graph (module, functions, dependencies, embedding) VALUES (?, ?, ?, NULL)",
        (module, functions, dependencies),
    )
    conn.commit()
    conn.close()


def list_modules() -> None:
    """List all modules in context graph."""
    if not os.path.exists(DB_PATH):
        print("Database not found. Run: dreamteam init-db", file=sys.stderr)
        return

    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    cursor = conn.cursor()
    cursor.execute("SELECT module, functions, dependencies FROM context_graph")
    rows = cursor.fetchall()
    conn.close()

    for module, functions, deps in rows:
        print(f"{module}: functions={functions}, deps={deps}")


def main() -> None:
    """CLI for context graph."""
    if len(sys.argv) < 2:
        print("Usage: python context_graph.py list | add <module> <functions_json> <deps_json>", file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "list":
        list_modules()
    elif cmd == "add" and len(sys.argv) >= 5:
        add_module(sys.argv[2], sys.argv[3], sys.argv[4])
        print(f"Added module {sys.argv[2]}")
    else:
        print("Unknown command or missing args.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
