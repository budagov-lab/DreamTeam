# DreamTeam — Autonomous Development System

An autonomous development engine for **500–1000+ sequential tasks** without quality degradation. Built for fault tolerance, continuous learning, and sliding task planning.

**Quick Start:** `python -m dreamteam new-project .` (in empty folder) → Open in Cursor → `/start` + goal → `/run`

**Documentation:** [guide/](guide/) — README, INSTRUCTIONS, COMMANDS, INSTALL

---

## Under the Hood: How It Works

### Fault Tolerance — Nothing Gets Lost

The system is designed to recover from crashes, mismatches, and stuck tasks without manual intervention:

| Mechanism | What it does |
|-----------|--------------|
| **run-next** | Before each task: verifies DB↔files, auto-runs sync if mismatch, fixes `tasks_completed` drift, resets stuck tasks (>60 min in_progress) |
| **recover** | Full reset: sync tasks, fix metrics, reset stuck, verify integrity, check memory |
| **Strict sequence** | One agent at a time, one terminal command at a time — no race conditions, no parallel conflicts |
| **State in DB** | All state lives in SQLite (`.dreamteam/db/`). Session-agnostic: Orchestrator can resume after a break without losing context |

**Effect:** If something breaks, `recover` + `run-next` brings the pipeline back. No manual checkpoint needed.

---

### Learnability — The Pipeline Adapts

Instead of degrading over hundreds of tasks, the system improves from production feedback:

| Component | Role |
|-----------|------|
| **DevExperiencer** | After each Reviewer: records outcome (approved/critical), attempts, time, technologies |
| **Learning Agent** | Every 10 tasks (or on cyclic failure): analyzes DevExperience, updates Developer instructions, dispatches FixPlanner |
| **FixPlanner** | Corrects upcoming tasks: library changes, approach adjustments, dependency updates — aligned with original goal |
| **Developer updates** | Learning may edit `.cursor/agents/developer.md` when patterns suggest instruction changes |

**Effect:** The pipeline adapts to real production data. Blocked tasks and critical feedback feed back into the plan and agent behavior.

---

### Sliding Task Planning — The Plan Evolves

The task queue is not fixed. FixPlanner owns it and can reorder, deprecate, or correct tasks as the project evolves:

| Mechanism | Purpose |
|-----------|---------|
| **sort_order** | Explicit queue order. Lower = earlier. FixPlanner sets it when reordering. |
| **deprecated** | Removed from plan, kept in DB for history. Delete task file → sync-tasks marks it deprecated. |
| **FixPlanner** | Queue owner. Reorders (sort_order), deprecates (delete file), updates dependencies before deprecating. |
| **Meta Planner** | Every 50 tasks: optimizes DAG, resplits oversized tasks, addresses tech debt. |

**Effect:** The plan slides as new information arrives. Tasks can be reordered, replaced, or deprecated without breaking the pipeline. Goal stays fixed; implementation details adapt.

---

### RAG & Context — No Token Overflow

The Orchestrator runs in the main chat. Without control, context would explode over hundreds of tasks. The system solves this with **RAG + context minimization**:

| Mechanism | Purpose |
|-----------|---------|
| **Memory in DB** | `summaries`, `architecture`, `goal` live in SQLite. Researcher writes via `memory-set`; Orchestrator syncs to files with `memory-to-files`. Subagents read from DB or files. |
| **Vector search (Qdrant)** | `pip install dreamteam[vector]` — semantic search over codebase. Researcher uses it for 100+ task projects. Local storage or `QDRANT_URL` server. |
| **Compression** | Researcher replaces, not appends. Summaries stay ~150 lines. Context never explodes. |
| **Orchestrator: never read files** | Pass task ID only. "Execute task T001." Developer fetches content via MCP `dreamteam_get_task`. No architecture excerpts, no pasting. |
| **State in .dreamteam/** | All context lives in DB and files. Session-agnostic: Orchestrator can resume after a break. Terminal output + task ID is enough. |

**Effect:** Orchestrator stays lean. Subagents pull what they need. Over 1000 tasks, context stays bounded — no overflow.

---

## Pipeline Overview

```
Goal → Planner → Task DAG → Scheduler → Developer → Reviewer → DevExperiencer → Git-Ops → update-task → run-next
                                    ↓
                    Triggers: Learning (10) | Researcher (20) | Meta Planner (50) | Auditor (200)
```

---

## License

PolyForm Noncommercial 1.0.0 — personal, educational, non-profit only. See [LICENSE](LICENSE).
