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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS batch_sessions (
                batch_id TEXT PRIMARY KEY,
                orchestrator TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                ended_at DATETIME
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subagent_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id TEXT NOT NULL,
                task_id TEXT,
                orchestrator TEXT NOT NULL,
                subagent_type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'started',
                started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                ended_at DATETIME,
                duration_ms INTEGER,
                error_text TEXT
            )
        """)
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_task_experience_task_id ON task_experience(task_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_task_experience_created ON task_experience(created_at)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_batch_sessions_orch_status ON batch_sessions(orchestrator, status)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_subagent_calls_batch ON subagent_calls(batch_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_subagent_calls_orch_type ON subagent_calls(orchestrator, subagent_type)"
        )
        
        # Migration: add missing columns if already exists
        cols = (
            ("time_spent_minutes", "INTEGER"),
            ("attempts_count", "INTEGER DEFAULT 1"),
            ("technologies_used", "TEXT"),
            ("approaches_used", "TEXT"),
            ("critical_feedback", "TEXT"),
            ("tokens_estimated", "INTEGER"),
        )
        for col, col_type in cols:
            try:
                cursor.execute(f"ALTER TABLE task_experience ADD COLUMN {col} {col_type}")
            except sqlite3.OperationalError:
                pass  # Already exists

        conn.commit()
    finally:
        conn.close()
    print("DevExperience DB initialized.")


if __name__ == "__main__":
    init_dev_experience()
