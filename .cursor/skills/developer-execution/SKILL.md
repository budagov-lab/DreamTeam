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

1. **Get task:** Read task file from `.dreamteam/tasks/task_XXX.md`
2. **Verify dependencies:** All dependencies must be `done`
3. **Set status:** Update to `in_progress` in file and database
4. **Implement:** Write code per task requirements
5. **Test:** Run tests, fix failures
6. **Complete:** Set status to `done`, update database
7. **Run task counter:** `dreamteam task-counter`

## Input

- Task ID (e.g. T001)
- Task file content

## Output

- Code changes
- Test updates
- Task status: `done`
- Database updated

## Rules

- Check `.dreamteam/memory/architecture.md` for module ownership
- Run tests before marking done
- Update both task file and database
