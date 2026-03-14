# DreamTeam — Commands

Use `dreamteam` CLI (or `python -m dreamteam`). Run `dreamteam` with no args for help.

## Projects

| Command | Description |
|---------|-------------|
| `dreamteam new-project .` | Deploy in current folder (db, memory, tasks, .cursor) |
| `dreamteam new-project <path>` | Deploy in specified path |
| `dreamteam bootstrap` | Create .cursorrules for empty folder |
| `dreamteam current-project` | Show project root and paths |
| `DREAMTEAM_PROJECT=<path>` | Use specific project (env) |

Project root: 1) DREAMTEAM_PROJECT env 2) .dreamteam in cwd/parents 3) DreamTeam root

## Database

| Command | Description |
|---------|-------------|
| `dreamteam init-db` | Initialize SQLite (done by new-project) |
| `dreamteam init-db --reset` | Reset database |

## Task Management

| Command | Description |
|---------|-------------|
| `dreamteam add-task <file\|id>` | Add or update single task from file or task ID |
| `dreamteam run-next` | Verify, get next task, set in_progress, print instructions |
| `dreamteam scheduler` | Get next task ID (or NONE) |
| `dreamteam scheduler --list` | List all tasks |
| `dreamteam scheduler --ready` | List ready tasks |
| `dreamteam update-task <id> <status>` | Update status (todo, in_progress, done, blocked) |
| `dreamteam verify-tasks` | Check DB ↔ files consistency |
| `dreamteam sync-tasks` | Sync .dreamteam/tasks/ to DB |

## Task Counter & Triggers

| Command | Description |
|---------|-------------|
| `dreamteam task-counter` | Increment completed count, check triggers |
| `dreamteam task-counter --status` | Show count without incrementing |

**Triggers:** TRIGGER_RESEARCHER (20), TRIGGER_META_PLANNER (50), TRIGGER_AUDITOR (200)

## Resilience

| Command | Description |
|---------|-------------|
| `dreamteam recover` | Sync, reset stuck in_progress (>60min), verify |
| `dreamteam recover --reset T001` | Reset specific task to todo |
| `dreamteam check-memory` | Validate summaries.md, architecture.md line limits |

## Vector Memory (100+ tasks, optional)

| Command | Description |
|---------|-------------|
| `pip install dreamteam[vector]` | Install sentence-transformers, numpy |
| `dreamteam vector-index` | Index codebase |
| `dreamteam vector-search "<query>"` | Semantic search |

## Workflow Example

```powershell
# 1. Deploy (first time)
dreamteam new-project .

# 2. Add goal via /start in Cursor, or create tasks manually

# 3. Sync and run
dreamteam sync-tasks
dreamteam run-next

# 4. Execute task (Composer + @developer)

# 5. When done:
dreamteam update-task T001 done
dreamteam task-counter
dreamteam run-next

# 6. If stuck: dreamteam recover
# 7. If TRIGGER_RESEARCHER: Researcher agent → dreamteam check-memory → dreamteam vector-index
```

## Parallel Agents (Git Worktrees)

See `docs/GIT_WORKTREES.md`.
