---
name: planner-task-decomposition
description: Planner breaks goals into epics and dispatches Sub-Planner per epic. Planner does NOT create task files — Sub-Planner does.
---

# Planner Task Decomposition

## CRITICAL: Planner Delegates to Sub-Planner

**Planner MUST NOT create task files directly.** Planner creates epic outline, then **dispatches Sub-Planner via mcp_task** for each epic. Sub-Planner creates task files.

## When to Use

- New goal or epic to implement
- User requests task breakdown or planning
- Meta Planner requests task resplitting

## Workflow (Planner)

1. **Read context:** `.dreamteam/memory/architecture.md`, `.dreamteam/memory/summaries.md`
2. **Break into epics** — 5–50 blocks. Write `.dreamteam/docs/epics/[goal-slug].md` with epic titles + short descriptions.
3. **For each epic** — **mcp_task** with `subagent_type: planner-sub`, prompt:
   - "Expand epic N: [title + 5–10 line desc]. Create TXXX–TYYY. Dependencies: [Tprev]." (First epic: deps [].)
4. **After each Sub-Planner** — Terminal: `python -m dreamteam sync-tasks`
5. **Return** when all epics expanded or limit reached (e.g. 33 tasks).

## What Sub-Planner Does (planner-sub)

- Reads epic + ID range from Planner prompt
- Creates task files in `.dreamteam/tasks/`
- Returns "DONE. Created TXXX–TYYY (N tasks)."

## Rules

- No circular dependencies
- **Small tasks:** 1–3 files per task, ~15–30 min each, single deliverable
- Dependencies must reference existing task IDs
- **Planner never creates task_XXX.md** — only Sub-Planner does
