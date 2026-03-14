"""Tests for project.get_project_root and path helpers."""

import os

import pytest

import project


def test_get_db_path():
    root = project.get_project_root()
    db = project.get_db_path()
    assert "db" in db and "dag.db" in db
    assert root in db or os.path.dirname(db).startswith(root)


def test_get_tasks_dir():
    root = project.get_project_root()
    data = project.get_data_root()
    tasks = project.get_tasks_dir()
    assert tasks == os.path.join(data, "tasks")
    assert data.startswith(root)


def test_get_memory_dir():
    root = project.get_project_root()
    data = project.get_data_root()
    memory = project.get_memory_dir()
    assert memory == os.path.join(data, "memory")
    assert data.startswith(root)


def test_dreamteam_project_env(monkeypatch, tmp_path):
    monkeypatch.setenv("DREAMTEAM_PROJECT", str(tmp_path))
    assert project.get_project_root() == str(tmp_path)
    monkeypatch.delenv("DREAMTEAM_PROJECT", raising=False)


def test_dreamteam_project_env_invalid(monkeypatch):
    monkeypatch.setenv("DREAMTEAM_PROJECT", "/nonexistent/path/xyz")
    root = project.get_project_root()
    assert root != "/nonexistent/path/xyz"
