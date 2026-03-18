---
name: researcher-context-compression
description: Summarizes project state, updates architecture, compresses context. Use when TRIGGER_RESEARCHER fires (every 20 tasks) or when context has grown too large.
---

# Researcher Context Compression

## When to Use

- When `python -m dreamteam update-task <id> done` prints `TRIGGER_RESEARCHER` (source of truth)
- After every 20 completed tasks
- When context feels noisy or architecture is unclear

## Workflow

1. **Read from DB:** Terminal → `python -m dreamteam memory-get summaries`, `python -m dreamteam memory-get architecture`, `python -m dreamteam recent-tasks 20` (or MCP dreamteam_*)
2. **Summarize:** Condense last 20 tasks into a brief summary
3. **Update architecture:** Add new modules, dependencies, ownership
4. **Compress:** Remove redundant or outdated content (see Researcher agent compression rules)
5. **Write to DB:** Draft to `.dreamteam/temp/`, then Terminal → `python -m dreamteam memory-set summaries <file>`, `python -m dreamteam memory-set architecture <file>` (or MCP dreamteam_set_memory)

**CRITICAL:** Read and write memory ONLY via DB (memory-get, memory-set). Do NOT read/write `.dreamteam/memory/*.md` directly.

## Output

- Updated summaries and architecture in DB (via memory-set)
- Orchestrator runs memory-to-files after Researcher

## Rules

- Keep summaries concise
- Preserve critical architectural decisions
- Document module → owner mapping
