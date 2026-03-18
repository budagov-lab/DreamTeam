---
name: meta-planner-optimization
description: Analyzes technical debt, optimizes DAG, resplits tasks. Use when TRIGGER_META_PLANNER fires (every 50 tasks) or when DAG needs optimization.
---

# Meta Planner Optimization

## When to Use

- When `python -m dreamteam update-task <id> done` prints `TRIGGER_META_PLANNER` (source of truth)
- After every 50 completed tasks
- When DAG has bottlenecks or tech debt accumulates

## Workflow

1. **Read from DB:** Terminal → `python -m dreamteam dag-state`, `python -m dreamteam memory-get summaries`, `python -m dreamteam memory-get architecture`
2. **Analyze:** Review DAG, task distribution, tech debt
3. **Identify:** Bottlenecks, oversized tasks, missing tasks
4. **Optimize:** Resplit tasks, add refactor tasks, adjust priorities
5. **Output:** New task files in .dreamteam/tasks/, architecture recommendations for Researcher

## Output

- New task files
- Refactor tasks added to DAG
- Architecture change recommendations for Researcher

## Rules

- Do not break existing dependencies
- Refactor tasks should have clear scope
- Document rationale for changes
