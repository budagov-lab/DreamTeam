# Autonomous Development System

An autonomous development engine capable of executing **500–1000+ tasks** in sequence without quality degradation.

## Architecture

```
Goal → Planner → Task DAG → Scheduler → Composer Agents → Testing → Task Counter → Triggers
```

**Triggers:**
- Every 10 tasks → Learning (DevExperience analysis, may update Developer, dispatch FixPlanner)
- Every 20 tasks → Researcher (context compression)
- Every 50 tasks → Meta Planner (DAG optimization)
- Every 200 tasks → Auditor (architecture audit)

## Quick Start

**Engine and project are separate.** DreamTeam folder = engine only. Your project = separate folder.

```powershell
# 1. Install engine (clone + install)
git clone https://github.com/budagov/DreamTeam.git
cd DreamTeam
.\setup.ps1               # or: ./setup.sh  (installs only, no project)

# 2. Create project in a CLEAN folder (not inside DreamTeam!)
cd C:\Projects\my-app     # empty folder
python -m dreamteam new-project .

# 3. Open my-app in Cursor → /start + goal → /run
```

Result: `my-app/` has only `.dreamteam/`, `.cursor/`, and your `src/` — no engine code.

## Documentation

- [INSTALL.md](INSTALL.md) — Install from clone, troubleshooting
- [INSTRUCTIONS.md](INSTRUCTIONS.md) — System overview and usage
- [COMMANDS.md](COMMANDS.md) — All CLI commands

## Projects

Each project has its own **`.dreamteam/`** (db, memory, tasks) — brains are isolated.

- `python -m dreamteam new-project .` — deploy in current folder
- Project root: `DREAMTEAM_PROJECT` env, or `.dreamteam` in cwd/parents

## Project Structure

```
your-project/
  .dreamteam/    — project data (db, memory, tasks)
  .cursor/       — agents, rules (from new-project)
  src/           — your code
```

## 500+ Tasks: Dispatcher + Left/Right Orchestrators

For large projects (thousands of tasks), use `/run` — Dispatcher coordinates Left/Right Orchestrators in batches of 15 (batch = context switch). Planning: Orchestrators dispatch Planner; Planner expands ALL epics via Sub-Planner (no task limit). Execution: Developer → Reviewer → DevExperiencer → Git-Ops loop. Alternate Left ↔ Right until ALL_COMPLETE.

## Under the Hood: What the Autonomous Agent Has Inside

The system is built for **self-sustaining execution** over 500–1000+ tasks. Three core mechanisms keep quality stable and prevent drift:

### 1. Learning Loop (DevExperience)

- **DevExperiencer** — After each Reviewer, records task outcome (approved/critical), attempts, time, technologies, approaches.
- **Learning Agent** — Every 10 tasks, or **on cyclic failure** (task blocked after 2 Critical retries). Analyzes DevExperience, updates Developer, dispatches FixPlanner.
- **FixPlanner** — Dispatched by Learning. Corrects upcoming tasks based on analysis (e.g. library change, approach adjustment).
- **Developer updates** — Learning may edit `.cursor/agents/developer.md` when a clear pattern suggests instruction changes.

**Effect:** The pipeline adapts to real production data instead of degrading over time.

### 2. RAG (Retrieval-Augmented Context)

- **Memory in DB** — `summaries`, `architecture`, `goal` live in SQLite. Researcher writes via `memory-set`; Left/Right sync to files with `memory-to-files`. **Goal** — stored at /start via `set-goal`; FixPlanner verifies plan changes against it.
- **Vector search (Qdrant)** — `pip install dreamteam[vector]` enables `vector-index` and `vector-search`. Uses Qdrant: local storage (`.dreamteam/db/qdrant/`) by default, or `QDRANT_URL` for server. Used by Researcher for 100+ task projects and large knowledge bases.
- **Compression** — Researcher replaces, not appends. Keeps context bounded (~150 lines summaries) so context never explodes.

**Effect:** Agents get relevant context without token overflow across hundreds of tasks.

### 3. Self-Maintenance Chain (Triggers)

| Every N tasks | Agent       | Action                                      |
|---------------|-------------|---------------------------------------------|
| 10            | Learning    | Analyze DevExperience → FixPlanner, Developer |
| 20            | Researcher  | Compress summaries, update architecture     |
| 50            | Meta Planner| Optimize DAG, resplit tasks, tech debt       |
| 200           | Auditor     | Architecture audit, duplicates, dependencies|

**Trigger flow:** `update-task <id> done` increments `tasks_completed` and prints `TRIGGER_*` when count is divisible. Orchestrators dispatch the corresponding agent (Learning, Researcher, Meta Planner, Auditor). No manual checkpoint.

**Effect:** Context stays compressed, DAG stays optimized, architecture stays coherent. The chain never breaks; Orchestrators always know the next step.

### Flow Continuity (Nothing Drops)

- **run-next** — Auto-runs `sync-tasks` if verify fails; fixes `tasks_completed` drift; always returns next task or "All tasks complete".
- **update-task done** — Increments counter, prints `TRIGGER_*` when divisible. Orchestrators react immediately.
- **recover** — Syncs tasks, fixes drift, resets stuck (>60 min in_progress), verifies integrity. Use after crash or mismatch.
- **Strict sequence** — Developer → Reviewer → DevExperiencer → Git-Ops → update-task → run-next. No parallel agents; one command at a time.

## Development

```powershell
pip install -e ".[dev]"
pytest tests
```

## License

PolyForm Noncommercial 1.0.0 (Government Use Prohibited) — personal, educational, non-profit only. No commercial use. No government use. See [LICENSE](../LICENSE)

## Requirements

- Python 3.10+
- **Core:** stdlib only (scheduler, task_counter, etc.)
- **Vector search (100+ tasks, large knowledge base):** `pip install dreamteam[vector]` — Qdrant (local or server), sentence-transformers, semantic search
