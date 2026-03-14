# DreamTeam — Task Flow

## End-to-End Flow

```
User /start + goal
       │
       ▼
┌──────────────┐
│   Planner    │  Creates .dreamteam/tasks/task_001.md, task_002.md, ...
│   (agent)    │  Updates .dreamteam/memory/architecture.md
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  sync-tasks  │  Reads .dreamteam/tasks/*.md → inserts/updates DB
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   run-next   │  verify → [sync if needed] → integrity fix → scheduler → get task ID → set in_progress
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Scheduler   │  DB query: status=todo, deps all done → first by priority
│  (internal)  │  T001 has deps=[] → always ready first
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Developer   │  Dispatches Terminal: get-task -> task content. Implements.
│  (agent)     │  Dispatches Terminal: pytest. Returns.
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Reviewer   │  Dispatches Terminal: get-task, pytest. Reviews, approves.
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Git-Ops    │  ONLY agent that does commits. Dispatches Terminal: git-commit.
│   (agent)    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ update-task  │  status=done → DB + file. Auto-increments tasks_completed.
│    done      │  Prints TRIGGER_* if 20/50/200.
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   run-next   │  Get next task (T002, T003, ...). Repeat.
└──────────────┘
```

## Where Developer Gets the First Task

1. **run-next** runs **scheduler** (Orchestrator dispatches Terminal)
2. **Scheduler** queries DB: `SELECT ... WHERE status='todo' ORDER BY priority DESC, id ASC`
3. For each todo task, checks: all dependencies in `done_ids`?
4. **T001** (first task) usually has `dependencies: []` → always ready
5. Scheduler returns `T001`
6. run-next sets T001 to in_progress, prints "NEXT TASK: T001"
7. Orchestrator passes task ID to Developer. Developer dispatches Terminal → get-task T001 → loads task content from DB

## Task Counter (Systematic)

| Metric | Where | When |
|--------|-------|------|
| tasks_completed | DB metrics table | Incremented when update-task done |
| TRIGGER_* | Printed by update-task | When count % 20/50/200 == 0 |
| Progress N of M | run-next output | Before each task |

**Systematic flow:** update-task done (auto-increments tasks_completed, emits TRIGGER_*) → run-next

**task-counter** — read-only: shows `tasks_completed / total`, next TRIGGER_*. No separate step in flow.
