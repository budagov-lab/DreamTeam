---
name: planner-sub-expand
description: Expands one epic into 15–25 detailed subtasks. Dispatched by Planner only — Planner breaks goal into epics, calls Sub-Planner per epic.
---

# Sub-Planner Expand

## When to Use

- **Planner** dispatches Sub-Planner per epic (Planner owns this flow, not Orchestrator)
- Planner creates epic outline, then calls Sub-Planner for each epic

## Workflow

1. Read epic description and ID range from Planner (via prompt)
2. Break epic into 15–25 small tasks (1–3 files, ~15–30 min each)
3. Create task files in `.dreamteam/tasks/` for given ID range
4. Set dependencies: first task → previous epic; within epic → prior subtasks
5. Return one line: "DONE. Created TXXX–TYYY (N tasks)."

## Rules

- Do NOT create tasks outside the given ID range
- Do NOT modify architecture.md
- Agent: `.cursor/agents/planner-sub.md`
