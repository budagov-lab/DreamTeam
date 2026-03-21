#!/usr/bin/env python3
"""Track subagent call lifecycle and reviewer-call caps per batch."""

import json
import os
import sqlite3
import sys
import uuid
from typing import Any

import project

DB_PATH = project.get_dev_experience_db_path()
REVIEWER_CAP_PER_BATCH = 45
VALID_ORCHESTRATORS = {"left", "right"}
VALID_END_STATUSES = {"completed", "failed", "timeout", "cancelled"}


def _ensure_db() -> None:
    if not os.path.exists(DB_PATH):
        from init_dev_experience import init_dev_experience
        init_dev_experience()


def _conn() -> sqlite3.Connection:
    _ensure_db()
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    return conn


def start_batch(orchestrator: str) -> str:
    orchestrator = orchestrator.lower()
    if orchestrator not in VALID_ORCHESTRATORS:
        raise ValueError(f"orchestrator must be one of: {sorted(VALID_ORCHESTRATORS)}")

    batch_id = f"{orchestrator}-{uuid.uuid4().hex[:12]}"
    with _conn() as conn:
        cur = conn.cursor()
        # Close any dangling active batch for the same orchestrator.
        cur.execute(
            """
            UPDATE batch_sessions
            SET status = 'replaced', ended_at = CURRENT_TIMESTAMP
            WHERE orchestrator = ? AND status = 'active'
            """,
            (orchestrator,),
        )
        cur.execute(
            """
            INSERT INTO batch_sessions (batch_id, orchestrator, status)
            VALUES (?, ?, 'active')
            """,
            (batch_id, orchestrator),
        )
        conn.commit()
    return batch_id


def _active_batch_id(cur: sqlite3.Cursor, orchestrator: str) -> str | None:
    cur.execute(
        """
        SELECT batch_id
        FROM batch_sessions
        WHERE orchestrator = ? AND status = 'active'
        ORDER BY started_at DESC
        LIMIT 1
        """,
        (orchestrator,),
    )
    row = cur.fetchone()
    return row["batch_id"] if row else None


def close_batch(orchestrator: str, status: str = "completed") -> bool:
    orchestrator = orchestrator.lower()
    with _conn() as conn:
        cur = conn.cursor()
        batch_id = _active_batch_id(cur, orchestrator)
        if not batch_id:
            return False
        cur.execute(
            """
            UPDATE batch_sessions
            SET status = ?, ended_at = CURRENT_TIMESTAMP
            WHERE batch_id = ?
            """,
            (status, batch_id),
        )
        conn.commit()
        return cur.rowcount > 0


def start_call(orchestrator: str, subagent_type: str, task_id: str | None = None) -> int:
    orchestrator = orchestrator.lower()
    if orchestrator not in VALID_ORCHESTRATORS:
        raise ValueError(f"orchestrator must be one of: {sorted(VALID_ORCHESTRATORS)}")

    with _conn() as conn:
        cur = conn.cursor()
        batch_id = _active_batch_id(cur, orchestrator)
        if not batch_id:
            batch_id = start_batch(orchestrator)
        cur.execute(
            """
            INSERT INTO subagent_calls (batch_id, task_id, orchestrator, subagent_type, status)
            VALUES (?, ?, ?, ?, 'started')
            """,
            (batch_id, task_id, orchestrator, subagent_type),
        )
        conn.commit()
        return int(cur.lastrowid)


def end_call(call_id: int, status: str, task_id: str | None = None, error_text: str | None = None) -> bool:
    status = status.lower()
    if status not in VALID_END_STATUSES:
        raise ValueError(f"status must be one of: {sorted(VALID_END_STATUSES)}")

    with _conn() as conn:
        cur = conn.cursor()
        if task_id is not None:
            cur.execute(
                """
                UPDATE subagent_calls
                SET status = ?, ended_at = CURRENT_TIMESTAMP,
                    duration_ms = CAST((julianday(CURRENT_TIMESTAMP) - julianday(started_at)) * 86400000 AS INTEGER),
                    task_id = COALESCE(?, task_id),
                    error_text = ?
                WHERE id = ? AND ended_at IS NULL
                """,
                (status, task_id, error_text, call_id),
            )
        else:
            cur.execute(
                """
                UPDATE subagent_calls
                SET status = ?, ended_at = CURRENT_TIMESTAMP,
                    duration_ms = CAST((julianday(CURRENT_TIMESTAMP) - julianday(started_at)) * 86400000 AS INTEGER),
                    error_text = ?
                WHERE id = ? AND ended_at IS NULL
                """,
                (status, error_text, call_id),
            )
        conn.commit()
        return cur.rowcount > 0


def stats(orchestrator: str) -> dict[str, Any]:
    orchestrator = orchestrator.lower()
    with _conn() as conn:
        cur = conn.cursor()
        batch_id = _active_batch_id(cur, orchestrator)
        if not batch_id:
            return {
                "orchestrator": orchestrator,
                "batch_id": None,
                "reviewer_calls_completed": 0,
                "open_calls": 0,
                "total_calls": 0,
                "reviewer_cap": REVIEWER_CAP_PER_BATCH,
                "reviewer_cap_reached": False,
            }

        cur.execute("SELECT COUNT(*) AS c FROM subagent_calls WHERE batch_id = ?", (batch_id,))
        total_calls = int(cur.fetchone()["c"])
        cur.execute(
            "SELECT COUNT(*) AS c FROM subagent_calls WHERE batch_id = ? AND ended_at IS NULL",
            (batch_id,),
        )
        open_calls = int(cur.fetchone()["c"])
        cur.execute(
            """
            SELECT COUNT(*) AS c
            FROM subagent_calls
            WHERE batch_id = ? AND subagent_type = 'reviewer' AND status = 'completed'
            """,
            (batch_id,),
        )
        reviewer_calls_completed = int(cur.fetchone()["c"])
        cur.execute(
            """
            SELECT COUNT(DISTINCT task_id) AS c
            FROM subagent_calls
            WHERE batch_id = ? AND subagent_type = 'git-ops' AND status = 'completed' AND task_id IS NOT NULL
            """,
            (batch_id,),
        )
        tasks_completed_in_batch = int(cur.fetchone()["c"])

        return {
            "orchestrator": orchestrator,
            "batch_id": batch_id,
            "reviewer_calls_completed": reviewer_calls_completed,
            "tasks_completed_in_batch": tasks_completed_in_batch,
            "open_calls": open_calls,
            "total_calls": total_calls,
            "reviewer_cap": REVIEWER_CAP_PER_BATCH,
            "reviewer_cap_reached": reviewer_calls_completed >= REVIEWER_CAP_PER_BATCH,
            "task_cap": 15,
            "task_cap_reached": tasks_completed_in_batch >= 15,
        }


def _usage() -> None:
    print(
        "Usage:\n"
        "  python subagent_calls.py start-batch <left|right>\n"
        "  python subagent_calls.py close-batch <left|right> [completed|switched|failed]\n"
        "  python subagent_calls.py start <left|right> <subagent_type> [task_id]\n"
        "  python subagent_calls.py end <call_id> <completed|failed|timeout|cancelled> [task_id] [error_text]\n"
        "  python subagent_calls.py stats <left|right>",
        file=sys.stderr,
    )


def main() -> None:
    if len(sys.argv) < 3:
        _usage()
        sys.exit(1)

    cmd = sys.argv[1].lower()
    try:
        if cmd == "start-batch":
            batch_id = start_batch(sys.argv[2])
            print(batch_id)
            return
        if cmd == "close-batch":
            status = sys.argv[3] if len(sys.argv) > 3 else "completed"
            ok = close_batch(sys.argv[2], status=status)
            print("closed" if ok else "no-active-batch")
            return
        if cmd == "start":
            task_id = sys.argv[4] if len(sys.argv) > 4 else None
            call_id = start_call(sys.argv[2], sys.argv[3], task_id)
            print(call_id)
            return
        if cmd == "end":
            call_id = int(sys.argv[2])
            status = sys.argv[3]
            task_id = sys.argv[4] if len(sys.argv) > 4 else None
            error_text = sys.argv[5] if len(sys.argv) > 5 else None
            ok = end_call(call_id, status, task_id, error_text)
            print("ok" if ok else "not-updated")
            return
        if cmd == "stats":
            print(json.dumps(stats(sys.argv[2]), ensure_ascii=False))
            return
    except Exception as e:
        print(f"subagent-calls error: {e}", file=sys.stderr)
        sys.exit(1)

    _usage()
    sys.exit(1)


if __name__ == "__main__":
    main()

