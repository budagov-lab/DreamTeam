#!/usr/bin/env python3
"""Sync tasks from .dreamteam/tasks/ folder to database."""

import os
import sys

# Add scripts dir to path for imports
sys.path.insert(0, os.path.dirname(__file__))
from add_task import parse_task_file, add_task

import project
TASKS_DIR = project.get_tasks_dir()


def main() -> None:
    """Sync all task files to database."""
    if not os.path.exists(TASKS_DIR):
        print("Tasks directory not found.", file=sys.stderr)
        sys.exit(1)

    count = 0
    for name in sorted(os.listdir(TASKS_DIR)):
        if not name.endswith(".md"):
            continue
        path = os.path.join(TASKS_DIR, name)
        with open(path, encoding="utf-8") as f:
            content = f.read()
        task_data = parse_task_file(content)
        if task_data:
            task_data["content"] = content
            add_task(task_data)
            count += 1
            print(f"Synced {task_data['id']}")

    print(f"Synced {count} tasks.")


if __name__ == "__main__":
    main()
