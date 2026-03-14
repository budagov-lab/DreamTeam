# Autonomous Development System

An autonomous development engine capable of executing **500–1000+ tasks** in sequence without quality degradation.

## Architecture

```
Goal → Planner → Task DAG → Scheduler → Composer Agents → Testing → Task Counter → Triggers
```

**Triggers:**
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

## 500+ Tasks: Main Orchestrator + Left/Right

For large projects, use `/run` — Main Orchestrator dispatches Left/Right Sub-orchestrators in batches of 50. Planning: Sub-Planner per epic until 50 tasks. Execution: Developer → Reviewer → Git-Ops loop. Alternate Left ↔ Right until ALL_COMPLETE.

## Development

```powershell
pip install -e ".[dev]"
pytest tests
```

## Requirements

- Python 3.10+
- **Core:** stdlib only (scheduler, task_counter, etc.)
- **Optional (100+ tasks):** `pip install dreamteam[vector]` for vector memory / semantic search
