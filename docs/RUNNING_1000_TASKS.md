# Running 1000 Tasks — Resilience Guide

## Quick Loop

```powershell
dreamteam run-next
# -> Get task, execute with Composer, then:
dreamteam update-task <TASK_ID> done
dreamteam task-counter
dreamteam run-next
```

Repeat. Each `run-next` prints the exact commands for the next round.

## Session Checkpoints (every 20–50 tasks)

Context grows. To avoid limits:

1. Start a **new chat session**
2. Run: `dreamteam verify-tasks` ; `dreamteam verify-integrity`
3. Say: **"Continue"** or **"Execute next task"**
4. Orchestrator resumes from scheduler

## When Something Breaks

| Problem | Fix |
|---------|-----|
| DB/file mismatch | `dreamteam sync-tasks` |
| Task stuck in_progress (subagent crashed) | `dreamteam recover --reset T001` |
| Multiple stuck tasks | `dreamteam recover` (resets all >60min) |
| summaries.md too large | Run Researcher, then `dreamteam check-memory` |
| tasks_completed drift / gaps | `dreamteam verify-integrity` ; `dreamteam recover` |
| General recovery | `dreamteam recover` |

## Triggers (automatic)

- **Every 20 tasks:** TRIGGER_RESEARCHER → Researcher agent, dreamteam check-memory, dreamteam vector-index
- **Every 50 tasks:** TRIGGER_META_PLANNER → Meta Planner agent
- **Every 200 tasks:** TRIGGER_AUDITOR → Auditor agent

## Minimal "Continue" Prompt

Paste this to resume:

```
Continue. Execute next task from scheduler. Use dreamteam run-next or dreamteam scheduler to get task ID.
```

## One-Touch Flow

1. `dreamteam run-next` — prints task + instructions
2. Execute task (Composer + @developer)
3. Run the 3 commands printed
4. Go to 1

No manual scheduler/update-task juggling — run-next does it.
