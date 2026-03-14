---
name: planner-task-decomposition
description: Decomposes goals into a task DAG, designs architecture, and generates executable tasks. Use when starting a new goal, epic, or feature, or when the user asks for planning or task breakdown.
---

# Planner Task Decomposition

## When to Use

- New goal or epic to implement
- User requests task breakdown or planning
- Meta Planner requests task resplitting

## Workflow

1. **Read context:** `.dreamteam/memory/architecture.md`, `.dreamteam/memory/summaries.md`
2. **Decompose:** Epic → Feature → Module → Tasks
3. **Define dependencies:** Build DAG (no cycles)
4. **Assign priorities:** Higher number = higher priority
5. **Create task files:** `.dreamteam/tasks/task_XXX.md`
6. **Insert into database:** Use `dreamteam sync-tasks` or direct SQLite

## Task Format

See `.cursor/rules/autonomous-dev-system.mdc`.

## Output

- Task markdown files in `.dreamteam/tasks/`
- Database rows in `.dreamteam/db/dag.db` (tasks table)
- Updated `.dreamteam/memory/architecture.md` if new modules are introduced

## Rules

- No circular dependencies
- **Small tasks:** 1–3 files per task, ~15–30 min each, single deliverable
- Dependencies must reference existing task IDs
- **1000 tasks:** Create 200–250 per batch; return; Orchestrator dispatches again for next batch
