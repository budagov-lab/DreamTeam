"""Shared DB operations for MCP tools. Resolves project root and delegates to scripts."""

import os
import sys

# Add scripts to path so we can import project and script modules
_SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

import project  # noqa: E402

DB_PATH = project.get_db_path
TASKS_DIR = project.get_tasks_dir
MEMORY_DIR = project.get_memory_dir
get_project_root = project.get_project_root


def get_task(task_id: str) -> str | None:
    """Get task content from DB or file fallback."""
    from get_task import get_task as _get
    return _get(task_id)


def get_memory(key: str) -> str | None:
    """Get memory (summaries|architecture) from DB."""
    from memory_get import get_memory as _get
    return _get(key)


def set_memory(key: str, content: str) -> bool:
    """Set memory in DB."""
    from memory_set import set_memory as _set
    return _set(key, content)


def get_dag_state() -> dict:
    """Get full DAG state (tasks, metrics) from DB."""
    from meta_planner import get_dag_state as _get
    return _get()


def get_recent_tasks(limit: int = 20) -> list[dict]:
    """Get last N done tasks from DB."""
    import sqlite3
    path = project.get_db_path()
    if not os.path.exists(path):
        return []
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA table_info(tasks)")
        has_content = any(col[1] == "content" for col in cursor.fetchall())
        if has_content:
            cursor.execute(
                "SELECT id, title, content FROM tasks WHERE status = 'done' ORDER BY updated_at DESC LIMIT ?",
                (limit,),
            )
        else:
            cursor.execute(
                "SELECT id, title, '' FROM tasks WHERE status = 'done' ORDER BY updated_at DESC LIMIT ?",
                (limit,),
            )
        rows = cursor.fetchall()
    except sqlite3.OperationalError:
        rows = []
    conn.close()
    return [
        {"id": r[0], "title": r[1], "excerpt": (r[2] or "")[:500] if len(r) > 2 else ""}
        for r in rows
    ]
