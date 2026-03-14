---
name: researcher-context-compression
description: Summarizes project state, updates architecture, compresses context. Use when TRIGGER_RESEARCHER fires (every 20 tasks) or when context has grown too large.
---

# Researcher Context Compression

## When to Use

- `dreamteam task-counter` outputs `TRIGGER_RESEARCHER`
- After every 20 completed tasks
- When context feels noisy or architecture is unclear

## Workflow

1. **Read:** Recent task files, `.dreamteam/memory/summaries.md`, `.dreamteam/memory/architecture.md`
2. **Summarize:** Condense last 20 tasks into a brief summary
3. **Update architecture:** Add new modules, dependencies, ownership
4. **Compress:** Remove redundant or outdated content
5. **Write:** Update `.dreamteam/memory/summaries.md` and `.dreamteam/memory/architecture.md`

## Output

- Updated `.dreamteam/memory/summaries.md` (history, progress)
- Updated `.dreamteam/memory/architecture.md` (modules, dependencies, rules)

## Rules

- Keep summaries concise
- Preserve critical architectural decisions
- Document module → owner mapping
