---
name: auditor-system-audit
description: Audits architecture, finds duplicates, analyzes dependencies. Use when TRIGGER_AUDITOR fires (every 200 tasks) or when architecture drift is suspected.
---

# Auditor System Audit

## When to Use

- `dreamteam task-counter` outputs `TRIGGER_AUDITOR`
- After every 200 completed tasks
- When duplicate code or circular dependencies are suspected

## Workflow

1. **Scan codebase:** Modules, functions, dependencies
2. **Check:** Duplicate functions, circular dependencies, layer violations
3. **Report:** List issues with severity
4. **Create tasks:** Refactor tasks for each critical issue

## Checks

- Duplicate functions across modules
- Circular dependencies in DAG or code
- Layer violations (e.g. UI depending on DB directly)
- Orphaned or dead code

## Output

- Audit report (markdown)
- Refactor tasks for critical issues
- Update `.dreamteam/memory/architecture.md` with findings
