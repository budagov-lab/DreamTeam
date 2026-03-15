---
name: reviewer-code-review
description: Reviews code for quality, correctness, and adherence to architecture. Use after each task completion or when the user requests a code review.
---

# Reviewer Code Review

## When to Use

- After Developer completes a task
- User requests code review
- Before merging significant changes

## Workflow

1. **Read:** Changed files, task requirements (MCP dreamteam_get_task or Terminal get-task)
2. **Verify:** Dispatch Terminal subagent → run `pytest`. If tests fail → CRITICAL.
3. **Check:** Correctness, architecture compliance
4. **Report:** APPROVED or CRITICAL (one line, max 50 words for Critical points)

## Checklist

- [ ] Logic is correct, edge cases handled
- [ ] No security issues
- [ ] Follows project style
- [ ] Tests cover changes
- [ ] No circular dependencies introduced
- [ ] Module ownership respected

## Output Format (match Reviewer agent)

- **APPROVED** — tests pass, no critical issues
- **CRITICAL:** [1–3 bullet points, max 50 words] — must fix before done

One line only. No Suggestion/Nice-to-have — Orchestrator expects APPROVED or CRITICAL.
