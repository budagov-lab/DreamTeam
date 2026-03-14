# Git Worktrees for Parallel Agents

**Note:** DreamTeam defaults to **sequential execution** (no parallelism). Use worktrees only if you explicitly enable parallel workflows.

For parallel Composer agents, use **git worktrees** to isolate each agent's work.

## Setup

```bash
# Create worktrees for 5 parallel developers
git worktree add ../DreamTeam-composer-1 main
git worktree add ../DreamTeam-composer-2 main
git worktree add ../DreamTeam-composer-3 main
git worktree add ../DreamTeam-composer-4 main
git worktree add ../DreamTeam-composer-5 main
```

## Workflow per Agent

Each agent (composer_1 .. composer_5):

1. Works in its own worktree (e.g. `../DreamTeam-composer-1`)
2. Runs `dreamteam run-next` to get next task
3. Implements the task
4. Runs tests
5. Updates task status via `dreamteam update-task <id> done`
6. Runs `dreamteam task-counter`
7. Commits and pushes (or merges to main)

## Code Ownership

Assign modules to agents in `.dreamteam/memory/architecture.md`:

| Module | Owner |
|--------|-------|
| parser | composer_1 |
| database | composer_2 |
| ui | composer_3 |

This prevents conflicts when multiple agents work in parallel.

## Merging

Merge worktree branches back to main when tasks are complete. Resolve conflicts using the code ownership map.
