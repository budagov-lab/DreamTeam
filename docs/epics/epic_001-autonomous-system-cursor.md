# Epic 001: Autonomous Development System inside Cursor

## Goal

Build an autonomous development engine that runs **inside Cursor**, accepts goals via chat, and executes projects through a task DAG with parallel subagents.

## Vision

```
User (Cursor chat) → Goal
       ↓
Planner (subagent) → Task DAG
       ↓
Scheduler → Next task
       ↓
Developer (subagent) → Code + Tests
       ↓
Reviewer (subagent) → Approval
       ↓
Task Counter → Triggers (Researcher, Meta Planner, Auditor)
```

## Features

### Feature 1: Goal-to-Task Pipeline
- User sets goal via Cursor chat
- Planner decomposes into tasks (Epic → Feature → Module → Tasks)
- Tasks synced to `.dreamteam/tasks/` and `.dreamteam/db/dag.db`

### Feature 2: Task Execution Loop
- Scheduler selects next ready task
- Developer implements, runs tests, updates status
- Task counter increments, triggers fire at 20/50/200

### Feature 3: Subagent Integration
- **Planner** — dispatched when new goal or epic
- **Developer** — dispatched per task from scheduler
- **Reviewer** — dispatched after each task (spec + quality)
- **Researcher** — dispatched every 20 tasks (TRIGGER_RESEARCHER)
- **Meta Planner** — dispatched every 50 tasks (TRIGGER_META_PLANNER)
- **Auditor** — dispatched every 200 tasks (TRIGGER_AUDITOR)

### Feature 4: Memory & Triggers
- `.dreamteam/memory/architecture.md` — module ownership, dependencies
- `.dreamteam/memory/summaries.md` — progress, decisions
- Automatic trigger detection via `task_counter.py`

## Task DAG (from epic)

| ID | Title | Dependencies | Owner |
|----|-------|--------------|-------|
| T001 | implement parser | [] | composer_1 |
| T002 | add database layer | [T001] | composer_2 |
| T003 | Add subagent dispatch for Developer | [T002] | — |
| T004 | Add subagent dispatch for Reviewer | [T003] | — |
| T005 | Add subagent dispatch for Planner | [] | — |
| T006 | Document subagent workflow in AGENTS.md | [T003, T004, T005] | — |
| T007 | Add Researcher subagent on TRIGGER_RESEARCHER | [T006] | — |
| T008 | Add Meta Planner subagent on TRIGGER_META_PLANNER | [T007] | — |
| T009 | Add Auditor subagent on TRIGGER_AUDITOR | [T008] | — |

## Success Criteria

- User can say "Build X" in Cursor chat
- Planner subagent creates task DAG
- Developer subagent executes tasks from scheduler
- Reviewer subagent reviews each completion
- Triggers automatically invoke Researcher, Meta Planner, Auditor
- System runs 500–1000 tasks without quality degradation

## Dependencies

- Cursor IDE with Composer
- `mcp_task` for subagent dispatch (generalPurpose, code-reviewer, etc.)
- Python 3.10+ for scripts
- SQLite for `.dreamteam/db/dag.db`
