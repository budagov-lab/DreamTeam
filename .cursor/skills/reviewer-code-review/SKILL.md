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

1. **Read:** Changed files, task requirements
2. **Verify:** Dispatch Terminal subagent → run `pytest` (or project test command). If tests fail → Critical.
3. **Check:** Correctness, architecture compliance
4. **Report:** Issues with severity (Critical, Suggestion, Nice-to-have)

## Checklist

- [ ] Logic is correct, edge cases handled
- [ ] No security issues
- [ ] Follows project style
- [ ] Tests cover changes
- [ ] No circular dependencies introduced
- [ ] Module ownership respected

## Output Format

- 🔴 **Critical:** Must fix before done
- 🟡 **Suggestion:** Consider improving
- 🟢 **Nice to have:** Optional enhancement
