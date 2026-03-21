#!/usr/bin/env python3
"""DreamTeam CLI entry point."""

import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(REPO_ROOT, "scripts")

SCRIPT_MAP = {
    "add-task": "add_task.py",
    "run-next": "run_next.py",
    "scheduler": "scheduler.py",
    "sync-tasks": "sync_tasks.py",
    "verify-tasks": "verify_tasks.py",
    "verify-integrity": "verify_integrity.py",
    "recover": "recover.py",
    "update-task": "update_task.py",
    "task-counter": "task_counter.py",
    "init-db": "init_db.py",
    "check-memory": "check_memory.py",
    "current-project": "current_project.py",
    "vector-index": "vector_index.py",
    "vector-search": "vector_search.py",
    "git-commit": "git_commit.py",
    "get-task": "get_task.py",
    "verify-sync": "verify_sync.py",
    "memory-get": "memory_get.py",
    "memory-set": "memory_set.py",
    "set-goal": "set_goal.py",
    "memory-to-files": "memory_to_files.py",
    "recent-tasks": "recent_tasks.py",
    "dag-state": "meta_planner.py",
    "init-dev-experience": "init_dev_experience.py",
    "record-dev-experience": "record_dev_experience.py",
    "dev-experience-history": "get_dev_experience_history.py",
    "subagent-calls": "subagent_calls.py",
    "dashboard": "dashboard.py",
    "auditor": "auditor.py",
    "researcher": "researcher.py",
    "context-graph": "context_graph.py",
}


CURSORRULES_TEMPLATE = """# DreamTeam — Autonomous Development System

## Deploy (if .dreamteam/ does not exist)

Run: `python -m dreamteam new-project .`

## All commands

Use `python -m dreamteam <command>` (or `dreamteam` if in PATH).

| Command | Action |
|---------|--------|
| dreamteam new-project . | Deploy environment |
| dreamteam run-next | Get next task |
| dreamteam sync-tasks | Sync tasks to DB |
| dreamteam verify-tasks | Verify consistency |
| dreamteam update-task <id> <status> | Update task |
| dreamteam task-counter | Show progress (tasks_completed / total, next triggers) |
| dreamteam recover | Recovery |
| dreamteam check-memory | Validate memory |
| dreamteam current-project | Show project root |
| dreamteam git-commit <id> <msg> | Add, commit, push for task |
| dreamteam auditor | Run system audit |
| dreamteam researcher | Run researcher context prep |

## After deploy

Rules from .cursor/rules/, agents from .cursor/agents/
"""


def _run_bootstrap() -> None:
    """Create .cursorrules in cwd for empty project."""
    cwd = os.getcwd()
    path = os.path.join(cwd, ".cursorrules")
    with open(path, "w", encoding="utf-8") as f:
        f.write(CURSORRULES_TEMPLATE)
    print(f"Created {path}")
    print()
    print("Open this folder in Cursor. The AI will use dreamteam commands.")
    print("If project not deployed, say: 'Deploy DreamTeam' or 'dreamteam new-project .'")


def run_script(script_name: str, args: list[str], cwd: str | None = None) -> int:
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    if not os.path.exists(script_path):
        print(f"Script not found: {script_path}", file=sys.stderr)
        return 1
    env = {**os.environ, "PYTHONPATH": SCRIPTS_DIR}
    r = subprocess.run(
        [sys.executable, script_path] + args,
        cwd=cwd or os.getcwd(),
        env=env,
    )
    return r.returncode


def main() -> None:
    if len(sys.argv) < 2:
        print("DreamTeam — Autonomous Development System")
        print()
        print("Usage: dreamteam <command> [args]")
        print()
        print("Commands:")
        print("  new-project <path>    Create new project (db, memory, tasks, .cursor)")
        print("  add-task <file|id>    Add or update single task from file")
        print("  run-next             Get next task, print instructions")
        print("  scheduler            Get next task ID")
        print("  sync-tasks           Sync tasks from files to DB")
        print("  verify-tasks         Verify DB/file consistency")
        print("  verify-integrity     Verify tasks_completed, gaps, orphan deps")
        print("  recover              Recovery: sync, reset stuck, verify")
        print("  update-task <id> <status>  Update task status")
        print("  task-counter         Show progress (tasks_completed / total)")
        print("  init-db              Initialize database")
        print("  check-memory         Validate memory file sizes")
        print("  current-project      Show current project root")
        print("  vector-index         Index codebase for semantic search")
        print("  vector-search <q>    Semantic search over indexed code")
        print("  git-commit <id> <msg>  Add, commit, push for task")
        print("  get-task <id>         Get task content from DB")
        print("  verify-sync           Verify tasks have content in DB")
        print("  memory-get <key>      Get summaries/architecture from DB")
        print("  memory-set <key> [file]  Set memory in DB (stdin or file)")
        print("  memory-to-files      Sync memory from DB to files")
        print("  recent-tasks [N]     List last N done tasks from DB")
        print("  dag-state            DAG state for Meta Planner (from DB)")
        print("  dashboard            Launch Analytics Web Dashboard")
        print("  auditor              Run system audit (architecture/deps)")
        print("  researcher           Prepare context for Researcher agent")
        print("  subagent-calls       Track subagent calls per batch")
        print("  context-graph list   Show module/function dependency graph")
        print("  bootstrap            Create .cursorrules in cwd (for empty project)")
        print()
        sys.exit(0)

    cmd = sys.argv[1].lower().replace("_", "-")
    args = sys.argv[2:] # type: ignore

    if cmd == "bootstrap":
        _run_bootstrap()
        return

    if cmd == "new-project":
        sys.path.insert(0, SCRIPTS_DIR)
        import new_project # type: ignore
        path = args[0] if len(args) > 0 else os.getcwd()
        root = new_project.create_project(path)
        print(f"Project created: {root}")
        print()
        print("To use this project:")
        print(f"  cd {root}")
        print("  python -m dreamteam run-next")
        print()
        print("Or set env: DREAMTEAM_PROJECT=" + root)
        print()
        print("Each project has its own: .dreamteam/ (db, memory, tasks), .cursor/ — brains are isolated.")
        return

    if cmd in SCRIPT_MAP:
        cwd = os.getcwd()
        sys.path.insert(0, SCRIPTS_DIR)
        import project # type: ignore
        cwd = project.get_project_root()
        exit_code = run_script(SCRIPT_MAP[cmd], args, cwd=cwd)
        sys.exit(exit_code)

    print(f"Unknown command: {cmd}", file=sys.stderr)
    sys.exit(1)
