"""DreamTeam MCP server — DB tools for subagents. Run: python -m dreamteam.mcp_server"""

from mcp.server.fastmcp import FastMCP

from dreamteam.db_bridge import (
    get_task,
    get_memory,
    set_memory,
    get_dag_state,
    get_recent_tasks,
)

mcp = FastMCP(
    "dreamteam-db",
    description="DreamTeam database bridge. Tasks, memory, DAG for autonomous development.",
)


@mcp.tool()
def dreamteam_get_task(task_id: str) -> str:
    """Get task content by ID from database. Returns full task markdown or error message."""
    content = get_task(task_id)
    if content:
        return content
    return f"Task {task_id} not found."


@mcp.tool()
def dreamteam_get_memory(key: str) -> str:
    """Get memory content from database. Key: 'summaries' or 'architecture'."""
    if key not in ("summaries", "architecture"):
        return f"Invalid key. Use: summaries, architecture"
    content = get_memory(key)
    if content:
        return content
    return f"No content for {key}."


@mcp.tool()
def dreamteam_set_memory(key: str, content: str) -> str:
    """Set memory content in database. Key: 'summaries' or 'architecture'."""
    if key not in ("summaries", "architecture"):
        return f"Invalid key. Use: summaries, architecture"
    if set_memory(key, content):
        return f"Memory {key} updated in DB."
    return f"Failed to update {key}."


@mcp.tool()
def dreamteam_get_dag_state() -> str:
    """Get full DAG state: tasks, statuses, dependencies, metrics. For Meta Planner."""
    state = get_dag_state()
    if not state:
        return "Database not found or empty."
    lines = ["# DAG state\n", "## Metrics"]
    for k, v in state.get("metrics", {}).items():
        lines.append(f"- {k}: {v}")
    lines.append("\n## Tasks")
    for t in state.get("tasks", []):
        tid = t.get("id", "")
        status = t.get("status", "")
        prio = t.get("priority", 0)
        title = t.get("title", "")
        deps = t.get("dependencies") or "[]"
        lines.append(f"- {tid} | {status} | P{prio} | {title} | deps: {deps}")
    lines.append("\nMeta Planner should: analyze tech debt, optimize DAG, resplit tasks.")
    return "\n".join(lines)


@mcp.tool()
def dreamteam_recent_tasks(limit: int = 20) -> str:
    """Get last N done tasks from database. For Researcher context."""
    tasks = get_recent_tasks(limit)
    if not tasks:
        return "No done tasks found."
    lines = ["# Recent done tasks\n"]
    for t in tasks:
        lines.append(f"## {t['id']}: {t['title']}")
        if t.get("excerpt"):
            lines.append(t["excerpt"])
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
