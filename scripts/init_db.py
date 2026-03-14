#!/usr/bin/env python3
"""Initialize or reset the Autonomous Development System SQLite database."""

import sqlite3
import os
import sys

import project
DB_PATH = project.get_db_path()
MEMORY_DIR = project.get_memory_dir()


def init_db(reset: bool = False) -> None:
    """Create database and schema. If reset=True, drop existing tables first."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    cursor = conn.cursor()

    if reset:
        cursor.execute("DROP TABLE IF EXISTS tasks")
        cursor.execute("DROP TABLE IF EXISTS metrics")
        cursor.execute("DROP TABLE IF EXISTS context_graph")
        cursor.execute("DROP TABLE IF EXISTS vector_code")
        cursor.execute("DROP TABLE IF EXISTS memory")
        conn.commit()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT,
            status TEXT,
            priority INTEGER,
            dependencies TEXT,
            owner TEXT,
            content TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    try:
        cursor.execute("ALTER TABLE tasks ADD COLUMN content TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            metric TEXT PRIMARY KEY,
            value INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS context_graph (
            module TEXT,
            functions TEXT,
            dependencies TEXT,
            embedding BLOB
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vector_code (
            path TEXT,
            chunk TEXT,
            embedding BLOB,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            key TEXT PRIMARY KEY,
            content TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute(
        "INSERT OR IGNORE INTO metrics (metric, value) VALUES ('tasks_completed', 0)"
    )

    # Indexes for scheduler (WHERE status, ORDER BY priority, id) and done count
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_tasks_status_priority_id ON tasks(status, priority DESC, id)"
    )
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")

    # Migration: copy memory from files to DB if memory table is empty
    cursor.execute("SELECT COUNT(*) FROM memory")
    if cursor.fetchone()[0] == 0 and os.path.isdir(MEMORY_DIR):
        for key in ("summaries", "architecture"):
            path = os.path.join(MEMORY_DIR, f"{key}.md")
            if os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    content = f.read()
                cursor.execute(
                    "INSERT INTO memory (key, content, updated_at) VALUES (?, ?, datetime('now'))",
                    (key, content),
                )
                print(f"Migrated {key}.md to DB.")

    conn.commit()
    conn.close()
    print("Database initialized successfully.")


if __name__ == "__main__":
    reset = "--reset" in sys.argv
    init_db(reset=reset)
