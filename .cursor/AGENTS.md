# Autonomous Development System — Agent Configuration

This project uses the Autonomous Development System. Roles can be executed **as subagents** (via `mcp_task`) or by loading the prompt from `.cursor/agents/`.

## Subagents (Dispatch via mcp_task)

**Full details:** `.cursor/agents/orchestrator.md`

**When to dispatch subagents:**
- **Planner** — New goal in chat, epic decomposition, task breakdown
- **Developer** — Task from scheduler ready for implementation
- **Reviewer** — After each task completion (spec compliance, then code quality)
- **Git-Ops** — After Reviewer approval — git commit (ONLY Git-Ops does commits)
- **Terminal** — dreamteam commands (fallback when MCP unavailable)
- **MCP dreamteam-db** — DB tools: dreamteam_get_task, dreamteam_get_memory, dreamteam_set_memory, dreamteam_get_dag_state, dreamteam_recent_tasks
- **Researcher** — When `task_counter.py` prints `TRIGGER_RESEARCHER`
- **Meta Planner** — When `task_counter.py` prints `TRIGGER_META_PLANNER`
- **Auditor** — When `task_counter.py` prints `TRIGGER_AUDITOR`

**How to dispatch:**
- Use `mcp_task` with `subagent_type`: `developer`, `code-reviewer`, `planner`, `researcher`, `meta-planner`, `auditor`, `git-ops`, `shell` (Terminal)
- Git-Ops is the ONLY agent that does commits. Developer, Reviewer use MCP dreamteam_get_task (or Terminal) for task content. Orchestrator uses Terminal for run-next, sync-tasks, update-task.
- For Developer: include task ID, `.dreamteam/memory/architecture.md` snippet
- For Reviewer: include changed files, task ID, architecture rules (Reviewer uses Terminal get-task for task content)

**Workflow:**
1. Terminal → `python -m dreamteam run-next` → get next task ID
2. Dispatch Developer subagent with task ID (Developer uses Terminal for get-task, pytest)
3. After implementation → dispatch Reviewer subagent (code-reviewer)
4. On approval → Git-Ops (commit) → Terminal: update-task done, run-next
5. Then → `python -m dreamteam update-task <id> done` (auto-increments, TRIGGER_*); `python -m dreamteam run-next`
6. If trigger fired → dispatch corresponding subagent (Researcher/Meta Planner/Auditor)

## Agent Prompts

| Role | Prompt File | When to Use |
|------|-------------|-------------|
| Orchestrator | `.cursor/agents/orchestrator.md` | Dispatching subagents, coordinating task pipeline |
| Planner | `.cursor/agents/planner.md` | New goal, epic, or task decomposition |
| Developer | `.cursor/agents/developer.md` | Executing a task from scheduler |
| Reviewer | `.cursor/agents/reviewer.md` | After task completion, code review |
| Git-Ops | `.cursor/agents/git-ops.md` | Git commit (ONLY agent that does commits) |
| Terminal | `.cursor/agents/terminal.md` | dreamteam commands (no git-commit from Orchestrator) |
| Researcher | `.cursor/agents/researcher.md` | Every 20 tasks (TRIGGER_RESEARCHER) |
| Meta Planner | `.cursor/agents/meta-planner.md` | Every 50 tasks (TRIGGER_META_PLANNER) |
| Auditor | `.cursor/agents/auditor.md` | Every 200 tasks (TRIGGER_AUDITOR) |

## Skills

Project skills in `.cursor/skills/`:

- `planner-task-decomposition`
- `developer-execution`
- `researcher-context-compression`
- `meta-planner-optimization`
- `auditor-system-audit`
- `reviewer-code-review`

**Superpowers (subagent workflows):**
- `subagent-driven-development` — Execute plan with subagent per task + two-stage review
- **Parallelism is FORBIDDEN** — One task, one subagent at a time

## Rules

- `.cursor/rules/autonomous-dev-system.mdc` — Always apply
- `.cursor/rules/task-execution.mdc` — When editing `.dreamteam/tasks/**/*.md`
- `.cursor/agents/orchestrator.md` — When dispatching Developer/Reviewer/Planner (load this prompt)

## Commands

Use `python -m dreamteam`. See COMMANDS.md.
