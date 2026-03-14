# DreamTeam MCP DB Bridge

MCP server exposes database operations as tools. Subagents call tools directly instead of Terminal.

## Setup

1. Install: `pip install -e .` (editable — MCP needs scripts/ from repo)
2. Config: `.cursor/mcp.json` (in project)
3. **Restart Cursor** to load the server

## Tools (server: dreamteam-db)

| Tool | Description |
|------|-------------|
| `dreamteam_get_task` | Get task content by ID |
| `dreamteam_get_memory` | Get summaries or architecture from DB |
| `dreamteam_set_memory` | Set summaries or architecture in DB |
| `dreamteam_get_dag_state` | Full DAG (tasks, metrics) for Meta Planner |
| `dreamteam_recent_tasks` | Last N done tasks for Researcher |

## Usage (in agent prompts)

Use `call_mcp_tool` with server `dreamteam-db`:

- `dreamteam_get_task` — args: `{"task_id": "T001"}`
- `dreamteam_get_memory` — args: `{"key": "summaries"}` or `{"key": "architecture"}`
- `dreamteam_set_memory` — args: `{"key": "summaries", "content": "..."}`
- `dreamteam_get_dag_state` — args: `{}`
- `dreamteam_recent_tasks` — args: `{"limit": 20}`

## Fallback

If MCP server is not available, agents fall back to Terminal:
`python -m dreamteam get-task T001`, `memory-get summaries`, etc.
