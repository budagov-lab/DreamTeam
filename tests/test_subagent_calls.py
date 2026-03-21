"""Tests for subagent call tracking in DevExperience DB."""

import sqlite3

import init_dev_experience
import subagent_calls


def test_subagent_calls_lifecycle(monkeypatch, tmp_path):
    db_path = tmp_path / ".dreamteam" / "db" / "dev_experience.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(init_dev_experience, "DB_PATH", str(db_path))
    monkeypatch.setattr(subagent_calls, "DB_PATH", str(db_path))

    init_dev_experience.init_dev_experience()

    batch_id = subagent_calls.start_batch("left")
    assert batch_id.startswith("left-")

    call_id = subagent_calls.start_call("left", "reviewer", "T001")
    assert isinstance(call_id, int) and call_id > 0

    stats = subagent_calls.stats("left")
    assert stats["batch_id"] == batch_id
    assert stats["open_calls"] == 1
    assert stats["reviewer_calls_completed"] == 0

    assert subagent_calls.end_call(call_id, "completed", "T001") is True
    stats = subagent_calls.stats("left")
    assert stats["open_calls"] == 0
    assert stats["reviewer_calls_completed"] == 1
    assert stats["tasks_completed_in_batch"] == 0
    assert stats["reviewer_cap_reached"] is False

    git_call_id = subagent_calls.start_call("left", "git-ops", "T001")
    assert subagent_calls.end_call(git_call_id, "completed", "T001") is True
    stats = subagent_calls.stats("left")
    assert stats["tasks_completed_in_batch"] == 1
    assert stats["task_cap_reached"] is False

    assert subagent_calls.close_batch("left", "completed") is True

    # Ensure ended_at recorded.
    conn = sqlite3.connect(str(db_path), timeout=10.0)
    try:
        cur = conn.cursor()
        cur.execute("SELECT status, ended_at FROM batch_sessions WHERE batch_id = ?", (batch_id,))
        row = cur.fetchone()
        assert row[0] == "completed"
        assert row[1] is not None
    finally:
        conn.close()

