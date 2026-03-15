---
name: developer-execution
description: Executes micro-tasks: writes code, runs tests, fixes errors, updates task status. Use when the scheduler assigns a task or when implementing a specific task from the task list.
---

# Developer Execution

## When to Use

- Scheduler returns a task ID
- User assigns a specific task to implement
- Task file has status `todo` and dependencies are done

## Workflow

1. **Get task:** Dispatch Terminal subagent → `python -m dreamteam get-task [id]` → read task content
2. **Verify dependencies:** All dependencies must be `done`
3. **Implement:** Write code per task requirements (task is in_progress from run-next)
4. **Test:** Dispatch Terminal subagent → run `pytest`, fix failures
5. **Return:** Deliver code. Do NOT mark done — Orchestrator does that after Reviewer + Git-Ops.

## Input

- Task ID (e.g. T001) from Orchestrator
- Architecture excerpt

## Output

- Code changes
- Test updates
- Task remains in_progress until Orchestrator runs update-task done (after Git-Ops)

## Rules

- **NO parallelism** — One task only.
- **Terminal subagent** — Developer dispatches Terminal (mcp_task, shell) for get-task, pytest, build. One command at a time.
- Check `.dreamteam/memory/architecture.md` for module ownership
- Run tests before returning
- **Do NOT run update-task** — Orchestrator runs it after Reviewer and Git-Ops
