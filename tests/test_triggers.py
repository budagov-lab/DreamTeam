import os
import subprocess
import sys
import pytest
import sqlite3

SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")

def _run(cmd: list[str], cwd: str, env: dict | None = None) -> subprocess.CompletedProcess:
    env = env or {}
    full_env = {**os.environ, **env}
    full_env["PYTHONPATH"] = SCRIPTS
    return subprocess.run(
        [sys.executable] + cmd,
        cwd=cwd,
        env=full_env,
        capture_output=True,
        text=True,
    )

@pytest.fixture
def clean_db(tmp_path):
    root = str(tmp_path)
    env = {"DREAMTEAM_PROJECT": root}
    # Pre-init schema
    r1 = _run([os.path.join(SCRIPTS, "init_db.py")], cwd=root, env=env)
    assert r1.returncode == 0, f"init_db failed: {r1.stderr}"
    r2 = _run([os.path.join(SCRIPTS, "init_dev_experience.py")], cwd=root, env=env)
    assert r2.returncode == 0, f"init_dev_experience failed: {r2.stderr}"
    return tmp_path, env

def test_triggers_1000_tasks(clean_db):
    """Stress test: 1000 tasks, verify all periodic triggers."""
    root_path, env = clean_db
    root = str(root_path)
    
    tasks_dir = os.path.join(root, ".dreamteam", "tasks")
    db_path = os.path.join(root, ".dreamteam", "db", "dag.db")
    os.makedirs(tasks_dir, exist_ok=True)
    
    # 1. Add 1000 tasks
    print("Generating 1000 tasks...")
    for i in range(1, 1001):
        # We'll use multiple of 10 for simplicity in this loop
        tid = f"T{i:03d}"
        path = os.path.join(tasks_dir, f"task_{tid[1:]}.md")
        # Add 'in_progress' to some so we can mark 'done'
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"id: {tid}\ntitle: Stress Test Task {i}\nstatus: todo\n")
            
    r = _run([os.path.join(SCRIPTS, "sync_tasks.py")], cwd=root, env=env)
    assert r.returncode == 0, f"sync_tasks failed: {r.stderr}"
    
    # Verify sync
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM tasks")
    actual_count = cur.fetchone()[0]
    
    # Verify initial metric IS zero
    cur.execute("SELECT value FROM metrics WHERE metric = 'tasks_completed'")
    res = cur.fetchone()
    initial_metric = res[0] if res else None
    conn.close()
    
    assert actual_count == 1000, f"Expected 1000 tasks, found {actual_count}. Sync output: {r.stdout!r}, Err: {r.stderr!r}"
    assert initial_metric == 0, f"Expected initial metric 0, found {initial_metric!r}"
    
    # 2. Sequential completions
    print("Completing 1000 tasks and checking triggers...")
    import time
    for i in range(1, 1001):
        tid = f"T{i:03d}"
        if i % 100 == 0:
            print(f"  ... verified {i} tasks ...")
            
        r = _run([os.path.join(SCRIPTS, "update_task.py"), tid, "done"], cwd=root, env=env)
        out = r.stdout
        err = r.stderr
        
        # Verify trigger rules (every 10, 15, 20, 50, 200)
        from scripts.triggers import (
            TRIGGER_LEARNING, TRIGGER_BATCH_SWITCH, TRIGGER_RESEARCHER, 
            TRIGGER_META_PLANNER, TRIGGER_AUDITOR
        )
        
        common_fail = f"Fail at {i}: Out: {out!r}, Err: {err!r}, Project: {root}, DB: {db_path}"

        # Check Learning (10)
        if i % TRIGGER_LEARNING == 0:
            assert "TRIGGER_LEARNING" in out, common_fail
        
        # Check Batch Switch (15)
        if i % TRIGGER_BATCH_SWITCH == 0:
            assert "TRIGGER_BATCH_SWITCH" in out, common_fail

        # Check Researcher (20)
        if i % TRIGGER_RESEARCHER == 0:
            assert "TRIGGER_RESEARCHER" in out, common_fail
            
        # Check Meta Planner (50)
        if i % TRIGGER_META_PLANNER == 0:
            assert "TRIGGER_META_PLANNER" in out, common_fail
            
        # Check Auditor (200)
        if i % TRIGGER_AUDITOR == 0:
            assert "TRIGGER_AUDITOR" in out, common_fail
        
        if i % 20 == 0:
            # Small simulation delay for OS sync
            time.sleep(0.01)
        else:
            time.sleep(0.001)
