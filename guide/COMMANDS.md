# DreamTeam — Commands

Use `python -m dreamteam <command>` (works without PATH). Or `dreamteam` if in PATH.

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
| `dreamteam run-next` | git pull, verify, get next task, set in_progress, print instructions |
| `dreamteam scheduler` | Get next task ID (or NONE) |
| `dreamteam scheduler --list` | List all tasks |
| `dreamteam scheduler --ready` | List ready tasks |
| `dreamteam update-task <id> <status>` | Update status (todo, in_progress, done, blocked, deprecated) |
| `dreamteam verify-tasks` | Check DB ↔ files consistency |
| `dreamteam verify-integrity` | Check tasks_completed, gaps, orphan deps |
| `dreamteam sync-tasks` | Sync .dreamteam/tasks/ to DB (removed files → deprecated) |
| `dreamteam verify-sync` | Verify tasks have content in DB |
| `dreamteam git-commit <id> <msg>` | Add, commit, push for task (after Reviewer) |
| `dreamteam get-task <id>` | Get task content from DB (Developer loads fresh) |

## Task Counter & Triggers

| Command | Description |
|---------|-------------|
| `dreamteam task-counter` | Show tasks_completed / total, next TRIGGER_* |

**Triggers:** TRIGGER_LEARNING (10), TRIGGER_RESEARCHER (20), TRIGGER_META_PLANNER (50), TRIGGER_AUDITOR (200), TRIGGER_BATCH_SWITCH (15) — Orchestrators return BATCH_DONE to Dispatcher to switch before context overflow

## Memory (DB — Researcher/Auditor use only)

| Command | Description |
|---------|-------------|
| `dreamteam memory-get <summaries\|architecture\|goal>` | Get memory content from DB |
| `dreamteam memory-set <key> [file]` | Set memory in DB (stdin or file path) |
| `dreamteam set-goal "goal text"` | Store original goal from /start (for FixPlanner alignment) |
| `dreamteam memory-to-files` | Sync memory from DB to .dreamteam/memory/*.md |
| `dreamteam recent-tasks [N]` | List last N done tasks from DB |
| `dreamteam dag-state` | DAG state for Meta Planner (tasks, metrics from DB) |

**MCP dreamteam-db** — Use tools dreamteam_get_task, dreamteam_get_memory, dreamteam_set_memory, dreamteam_get_dag_state, dreamteam_recent_tasks instead of Terminal when available.

**Researcher, Meta Planner, Auditor** read/write memory via MCP or Terminal. Orchestrators run `memory-to-files` after Researcher.

## Learning Loop (DevExperience)

| Command | Description |
|---------|-------------|
| `dreamteam init-dev-experience` | Initialize DevExperience DB (done by init-db) |
| `dreamteam record-dev-experience <id> <approved\|critical> [attempts] [min]` | Record task experience (DevExperiencer) |
| `dreamteam dev-experience-history [N]` | Get last N records (Learning Agent) |

**Flow:** Reviewer → DevExperiencer (record) → Git-Ops. Every 10 tasks: Learning → FixPlanner. **On cyclic failure** (task blocked after 2 Critical): Learning runs immediately → FixPlanner.

## Resilience

| Command | Description |
|---------|-------------|
| `dreamteam recover` | Sync, fix tasks_completed drift, reset stuck (>60min), verify, integrity |
| `dreamteam recover --reset T001` | Reset specific task to todo |
| `dreamteam check-memory` | Validate summaries.md, architecture.md line limits |

## Vector Search (Qdrant, 100+ tasks, large knowledge base)

| Command | Description |
|---------|-------------|
| `pip install dreamteam[vector]` | Install Qdrant client, sentence-transformers, numpy |
| `dreamteam vector-index` | Index codebase into Qdrant |
| `dreamteam vector-search "<query>"` | Semantic search over indexed code |
| `QDRANT_URL=http://localhost:6333` | Use Qdrant server (optional; default: local path) |

## Workflow Example

```powershell
# 1. Deploy (first time)
python -m dreamteam new-project .

# 2. Add goal via /start in Cursor, or create tasks manually

# 3. Sync and run
python -m dreamteam sync-tasks
python -m dreamteam run-next

# 4. Execute task (Composer + @developer), then Reviewer (code-reviewer), then DevExperiencer (record)

# 5. After DevExperiencer (if approved): Launch Git-Ops subagent (task ID + short title). Git-Ops does commit.

# 6. Then (update-task done auto-increments counter, emits TRIGGER_LEARNING/TRIGGER_RESEARCHER/etc.):
python -m dreamteam update-task T001 done
python -m dreamteam run-next

# 7. If TRIGGER_LEARNING: Learning agent -> may dispatch FixPlanner
# 8. If TRIGGER_RESEARCHER: Researcher agent -> vector-index -> check-memory
# 9. If stuck: python -m dreamteam recover
```

## Parallelism

**Default: sequential.** One task, one subagent at a time. No parallel terminals.

For large projects (thousands of tasks): use `/run` — Dispatcher coordinates Left/Right Orchestrators in batches of 15 (batch = context switch, not project limit).
