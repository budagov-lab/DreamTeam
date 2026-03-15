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

1. **Read from DB:** Terminal → `memory-get architecture`, `scheduler --list` (or MCP dreamteam_*)
2. **Scan codebase:** Modules, functions, dependencies (read source files)
3. **Check:** Duplicate functions, circular dependencies, layer violations
4. **Report:** List issues with severity
5. **Create tasks:** Refactor tasks for each critical issue
6. **Write architecture:** Draft → `.dreamteam/temp/`, then `memory-set architecture <file>`. DB only.

## Checks

- Duplicate functions across modules
- Circular dependencies in DAG or code
- Layer violations (e.g. UI depending on DB directly)
- Orphaned or dead code

## Output

- Audit report (markdown)
- Refactor tasks for critical issues
- **Architecture:** Write draft to `.dreamteam/temp/architecture_new.md`, then Terminal → `memory-set architecture <file>`. Do NOT write to `.dreamteam/memory/architecture.md` directly — DB only.
