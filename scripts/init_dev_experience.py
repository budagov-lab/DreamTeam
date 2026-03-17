#!/usr/bin/env python3
"""Initialize DevExperience DB — production history for learning loop."""

import sqlite3
import os

import project # type: ignore
DB_PATH = project.get_dev_experience_db_path()


def init_dev_experience() -> None:
    """Create DevExperience database and schema."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    try:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_experience (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                reviewer_result TEXT NOT NULL,
                time_spent_minutes INTEGER,
                attempts_count INTEGER DEFAULT 1,
                technologies_used TEXT,
                approaches_used TEXT,
                critical_feedback TEXT,
                tokens_estimated INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_task_experience_task_id ON task_experience(task_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_task_experience_created ON task_experience(created_at)"
        )

        conn.commit()
    finally:
        conn.close()
    print("DevExperience DB initialized.")


if __name__ == "__main__":
    init_dev_experience()
