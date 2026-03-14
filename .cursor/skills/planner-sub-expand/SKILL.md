---
name: planner-sub-expand
description: Expands one epic into 15–25 detailed subtasks. Use when Main Planner created epic outline and Orchestrator needs subtasks per epic.
---

# Sub-Planner Expand

## When to Use

- Main Planner created epic outline (`.dreamteam/docs/epics/*.md`)
- Goal needs 500+ tasks — use Main Planner + Sub-Planner flow
- Orchestrator dispatches Sub-Planner per epic

## Workflow

1. Read epic description and ID range from Orchestrator
2. Break epic into 15–25 small tasks (1–3 files, ~15–30 min each)
3. Create task files in `.dreamteam/tasks/` for given ID range
4. Set dependencies: first task → previous epic; within epic → prior subtasks
5. Return one line: "DONE. Created TXXX–TYYY (N tasks)."

## Rules

- Do NOT create tasks outside the given ID range
- Do NOT modify architecture.md
- Agent: `.cursor/agents/planner-sub.md`
