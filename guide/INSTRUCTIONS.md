# Autonomous Development System — Instructions

## Overview

The Autonomous Development System enables **500–1000+ sequential tasks** without quality degradation. It uses multiple agent types, a task DAG, and memory layers.

**Pipeline:** Goal → Planner → Task DAG → Scheduler → Composer Agents → Testing → Task Counter → Triggers

---

## Quick Start

1. **Deploy project** (if not done):
   ```powershell
   python -m dreamteam new-project .
   ```

2. **Add a goal** — Use `/start` in Cursor chat, or Planner agent to decompose into tasks.

3. **Sync and run:**
   ```powershell
   python -m dreamteam sync-tasks
   python -m dreamteam run-next
   ```

4. **Execute tasks** — Assign to Developer agent (Composer). Use `python -m dreamteam update-task` for status.

5. **After each completed task:**
   ```powershell
   python -m dreamteam update-task <id> done
   python -m dreamteam run-next
   ```
   Triggers: Learning (10), Researcher (20), Meta Planner (50), Auditor (200).

---

## Agent Roles

| Agent | Trigger | Responsibility |
|-------|---------|----------------|
| **Planner** | On new goal | Decompose goals, design architecture, generate DAG |
| **Planner-Sub** | Dispatched by Planner per epic | Expand one epic into 15–25 subtasks |
| **Developer** | Scheduler assigns | Write code, run tests, fix errors, update task status |
| **Reviewer** | After each task | Review code quality, suggest fixes |
| **DevExperiencer** | After each Reviewer | Record task experience to DevExperience DB (for Learning loop) |
| **Git-Ops** | After DevExperiencer (if approved) | Add, commit, push (ONLY agent that commits) |
| **Learning** | Every 10 tasks | Analyze DevExperience, may update Developer, dispatch FixPlanner |
| **FixPlanner** | Dispatched by Learning | Correct tasks based on Learning analysis |
| **Researcher** | Every 20 tasks | Summarize, update architecture, compress context |
| **Meta Planner** | Every 50 tasks | Analyze tech debt, optimize DAG, resplit tasks |
| **Auditor** | Every 200 tasks | Check architecture, find duplicates, analyze dependencies |

---

## Task Lifecycle

1. **todo** — Ready to execute (dependencies done)
2. **in_progress** — Assigned to an agent
3. **done** — Completed and verified
4. **blocked** — Waiting on dependencies

---

## File Locations

- **Tasks:** `.dreamteam/tasks/task_XXX.md`
- **Agent prompts:** `.cursor/agents/*.md`
- **Memory:** `.dreamteam/memory/architecture.md`, `.dreamteam/memory/summaries.md`
- **Database:** `.dreamteam/db/dag.db`
- **Task format:** `.cursor/rules/autonomous-dev-system.mdc`

---

## Critical Rules

1. **Always read** `.dreamteam/memory/architecture.md` before making architectural changes.
2. **Update task status** via `python -m dreamteam update-task` (updates both file and DB).
3. **Respect code ownership** — check `.dreamteam/memory/architecture.md` for module owners.
4. **Run tests** before marking a task as done.
5. **No parallelism** — One task, one subagent at a time. Main Orchestrator dispatches Left/Right only.
