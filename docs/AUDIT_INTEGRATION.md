# Audit: Module Integration

**Date:** 2025-03-14

## Summary

| Category | Status | Notes |
|----------|--------|-------|
| MCP ↔ db_bridge ↔ scripts | ⚠️ | db_bridge requires scripts/ — OK for editable install, fails for pip install |
| CLI ↔ scripts | ✅ | All commands mapped |
| Agent prompts ↔ MCP/Terminal | ✅ | Consistent |
| Orchestrator flow | ✅ Fixed | Added memory-to-files after Auditor |
| DB schema | ✅ | init_db, new_project, memory table aligned |
| run_next instructions | ✅ Fixed | Now mentions MCP |

---

## 1. MCP Server — db_bridge — scripts

**Flow:** `mcp_server.py` → `db_bridge.py` → `scripts/*.py` (get_task, memory_get, etc.)

**Issue:** db_bridge computes `_SCRIPTS_DIR = os.path.dirname(os.path.dirname(__file__)) + "/scripts"`. When dreamteam is installed via `pip install .` (non-editable), `__file__` points to site-packages; `scripts/` is NOT in the package. **Fails.**

**OK when:** `pip install -e .` (editable) or running from DreamTeam repo.

**Recommendation:** Document that `pip install -e .` is required, or bundle scripts in package.

---

## 2. memory-to-files after Auditor

**Issue:** Auditor writes architecture via `dreamteam_set_memory`. Other agents (Developer, Planner) read from `.dreamteam/memory/architecture.md` files. After Auditor, memory-to-files is NOT run. **Gap.**

**Fix:** Add memory-to-files after Auditor returns (same as after Researcher).

---

## 3. run_next.py instructions

**Current:** "Developer uses Terminal get-task"

**Should be:** "Developer uses MCP dreamteam_get_task or Terminal get-task"

---

## 4. start.md step 4

**Current:** "Use Terminal subagent to run get-task"

**Should mention:** MCP dreamteam_get_task preferred when available.

---

## 5. Orchestrator dispatch instruction (step 2)

**Current:** "Use Terminal subagent to run get-task [id]"

**Should be:** "Use MCP dreamteam_get_task or Terminal get-task for task content"

---

## 6. Verified OK

- CLI SCRIPT_MAP: all 20 commands present
- init_db: memory table, migration from files
- new_project: memory table, seed from files, temp dir
- memory_to_files: reads from memory table
- check_memory: reads from DB (with file fallback)
- Terminal.md: lists all agent commands
- Agent prompts: MCP + Terminal fallback consistent
