#!/usr/bin/env python3
"""Project root resolution. All scripts use this for db, memory, tasks paths."""

import os

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
DREAMTEAM_ROOT = os.path.dirname(SCRIPTS_DIR)
PROJECT_MARKER = ".dreamteam"


def get_project_root() -> str:
    """
    Resolve project root (directory containing .dreamteam/):
    1. DREAMTEAM_PROJECT env
    2. Directory containing .dreamteam (cwd or parents)
    3. DREAMTEAM_PROJECT_CWD env = use cwd
    4. DreamTeam root (parent of scripts)
    """
    if env := os.environ.get("DREAMTEAM_PROJECT"):
        if os.path.isdir(env):
            return os.path.abspath(env)
    if os.environ.get("DREAMTEAM_PROJECT_CWD") == "1":
        return os.getcwd()
    cwd = os.getcwd()
    path = cwd
    for _ in range(10):
        marker = os.path.join(path, PROJECT_MARKER)
        if os.path.isdir(marker):
            return path
        parent = os.path.dirname(path)
        if parent == path:
            break
        path = parent
    return DREAMTEAM_ROOT


def get_data_root() -> str:
    """Project data root: project_root/.dreamteam/"""
    return os.path.join(get_project_root(), PROJECT_MARKER)


def get_db_path() -> str:
    return os.path.join(get_data_root(), "db", "dag.db")


def get_tasks_dir() -> str:
    return os.path.join(get_data_root(), "tasks")


def get_memory_dir() -> str:
    return os.path.join(get_data_root(), "memory")
