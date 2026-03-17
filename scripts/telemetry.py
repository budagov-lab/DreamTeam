#!/usr/bin/env python3
"""Telemetry module for calculating task tokens and saving to DevExperience DB."""

import sqlite3
import os
import subprocess
from datetime import datetime, timezone

import project

DEV_EXP_DB = project.get_dev_experience_db_path()


def estimate_tokens_for_task(task_id: str) -> int:
    """Heuristic: run git diff, count lines added + roughly memory context.
    1 line ~ 10 tokens. Base context ~ 2500 tokens."""
    base_tokens = 3000
    try:
        r = subprocess.run(
            ["git", "diff", "HEAD", "--stat"],
            cwd=project.get_project_root(),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if r.returncode == 0:
            lines = r.stdout.splitlines()
            if lines:
                # Last line usually: " 3 files changed, 100 insertions(+), 20 deletions(-)"
                last = lines[-1]
                insertions = 0
                import re
                m = re.search(r"(\d+)\s+insertions?\(\+\)", last)
                if m:
                    insertions = int(m.group(1))
                return base_tokens + (insertions * 15)
    except Exception:
        pass
    
    return base_tokens


def record_task_duration(task_id: str, minutes: int, tokens: int) -> None:
    """Updates time and tokens in task_experience (or inserts if missing)."""
    if not os.path.exists(DEV_EXP_DB):
        return
        
    conn = sqlite3.connect(DEV_EXP_DB, timeout=10.0)
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        
        # See if task exists (from Reviewer)
        cursor.execute(
            "SELECT id FROM task_experience WHERE task_id = ? ORDER BY id DESC LIMIT 1", 
            (task_id,)
        )
        row = cursor.fetchone()
        
        if row:
            cursor.execute(
                "UPDATE task_experience SET time_spent_minutes = ?, tokens_estimated = ? WHERE id = ?",
                (minutes, tokens, row[0])
            )
        else:
            cursor.execute(
                """
                INSERT INTO task_experience
                (task_id, reviewer_result, time_spent_minutes, attempts_count, tokens_estimated)
                VALUES (?, 'approved', ?, 1, ?)
                """,
                (task_id, minutes, tokens)
            )
        conn.commit()
    finally:
        conn.close()
