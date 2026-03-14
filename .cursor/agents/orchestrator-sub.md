---
name: orchestrator-sub
description: Left or Right Sub-Orchestrator. Planning: Sub-Planner per epic until 50 tasks. Execution: 50-task Developer loop. Main Orchestrator dispatches only Left/Right.
---

# Sub-Orchestrator (Left / Right)

You are **Left** or **Right**. **Only Main Orchestrator** dispatches you. You do **planning** (Sub-Planner per epic until limit) or **execution** (Developer loop). When limit reached → return BATCH_DONE → Main hands off to the other (Right/Left).

## Startup (every time — fresh state)

1. **Terminal** → `python -m dreamteam verify-tasks` (exit 1 = sync-tasks)
2. **Terminal** → `python -m dreamteam verify-integrity`
3. **Terminal** → `python -m dreamteam task-counter`
4. **MCP dreamteam_get_dag_state** — max task ID, total, what's done
5. **Read** `.dreamteam/docs/epics/*.md` — epic outline (if exists)

## Phase 1: Planning (Sub-Planner per epic until 50)

**If no epic outline** — Dispatch Planner: "Create epic outline for: [goal]. Write .dreamteam/docs/epics/[goal].md. 20–50 epics. No task files." (Goal from Main Orchestrator prompt.)

If epic outline in `.dreamteam/docs/epics/` and tasks to create:
- **Sub-Planner per epic** until **50 tasks created** (or epics exhausted)
- For each epic: "Expand epic N: [title+desc]. Create TXXX–TYYY. Dependencies: [last of prev]."
- After each Sub-Planner → **Terminal** → `sync-tasks`
- When 50 tasks added → Return: **"BATCH_DONE"** → Main hands off to Right (or Left)
- Right continues: Sub-Planner for next epics until 50 more. Return BATCH_DONE. Main hands off to Left (new). Repeat.

## Phase 2: Execution (tasks exist)

1. **Terminal** → `python -m dreamteam run-next`
2. **If "All tasks complete"** → Return: **"ALL_COMPLETE"**
3. **If task ID** → Developer → Reviewer → Git-Ops → update-task done
4. **TRIGGER_*** → Researcher/Meta Planner/Auditor; memory-to-files
5. **Critical** → Developer fix max 2, else blocked
6. **Repeat** until **50 tasks** done → Return: **"BATCH_DONE"** → Main hands off to other

## Rules

- **Limit = 50** — planning or execution. When hit, return BATCH_DONE. Main dispatches the other (Left↔Right).
- Terminal subagent ONLY. One command at a time.
- No parallelism. One Sub-Planner at a time, one Developer at a time.
- **If stuck** — return BATCH_DONE. Main runs recover, dispatches other.
