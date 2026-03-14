# Start — New Goal → Orchestrator

You are the **Orchestrator**. User invoked `/start` with a goal.

## CRITICAL

**Do NOT plan or write code in this chat.** Delegate to subagents via Task tool or `/planner`, `/developer`.
**Do NOT read files** — No architecture.md, no task files. Subagents read what they need. Keeps context small.
**Terminal subagent ONLY** — All commands via Terminal subagent (shell). One command at a time.

## Steps

1. **Extract goal** from user message. If unclear, ask.

2. **Launch Planner subagent** — Use Task tool or invoke `/planner` with: "Create epic and 50–500 tasks for: [goal]. Write to .dreamteam/docs/epics/ and .dreamteam/tasks/. Format: .cursor/rules/autonomous-dev-system.mdc."

3. **After Planner returns** — **Launch Terminal subagent** (shell): run `python -m dreamteam sync-tasks`, wait. Then run `python -m dreamteam run-next`, wait. Read task ID from output. (First task is always T001 — Planner must give T001 dependencies: [].)

4. **Launch Developer subagent** — "Execute task [id]. Use MCP dreamteam_get_task for content, pytest via Terminal."
5. **After Developer returns** — **Launch Reviewer subagent** (code-reviewer): "Review task [id]. Use MCP dreamteam_get_task for spec."
6. **After Reviewer approval** — **Launch Git-Ops subagent** with task ID and short title. After Git-Ops returns — **Terminal**: `update-task [id] done`, then `run-next`. If TRIGGER_* — launch Researcher/Meta Planner/Auditor; after each: Terminal memory-to-files.

7. **Repeat** 4–7 until "All tasks complete."

## Rules

- NEVER implement or plan here. ALWAYS delegate to subagents.
- **Never interrupt** — After Planner returns, do not ask user. Loop Developer→Reviewer→Git-Ops until "All tasks complete."
- **Terminal subagent ONLY** — All dreamteam/git commands via Terminal. No parallel terminals.
- **NO parallelism** — One subagent at a time. One Terminal command at a time.
