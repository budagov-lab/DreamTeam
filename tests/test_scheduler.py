"""Tests for scheduler.parse_dependencies and get_next_task."""

import sqlite3

import pytest

import scheduler
from scheduler import get_next_task, parse_dependencies


def test_parse_dependencies_empty():
    assert parse_dependencies(None) == []
    assert parse_dependencies("") == []
    assert parse_dependencies("[]") == []


def test_parse_dependencies_json():
    assert parse_dependencies('["T001", "T002"]') == ["T001", "T002"]
    assert parse_dependencies('["T001"]') == ["T001"]


def test_parse_dependencies_comma():
    assert parse_dependencies("T001, T002") == ["T001", "T002"]


def test_get_next_task_empty_db(monkeypatch, tmp_path):
    db_path = tmp_path / "db" / "dag.db"
    db_path.parent.mkdir(parents=True)
    import db as db_mod
    monkeypatch.setattr(db_mod, "DB_PATH", str(db_path))

    conn = sqlite3.connect(db_path, timeout=10.0)
    conn.executescript("""
        CREATE TABLE tasks (id TEXT PRIMARY KEY, title TEXT, status TEXT, priority INTEGER, dependencies TEXT, owner TEXT, created_at DATETIME, updated_at DATETIME);
        CREATE TABLE metrics (metric TEXT PRIMARY KEY, value INTEGER);
        INSERT INTO metrics VALUES ('tasks_completed', 0);
    """)
    conn.commit()
    conn.close()

    assert get_next_task() is None


def test_get_next_task_returns_ready(monkeypatch, tmp_path):
    db_path = tmp_path / "db" / "dag.db"
    db_path.parent.mkdir(parents=True)
    import db as db_mod
    monkeypatch.setattr(db_mod, "DB_PATH", str(db_path))

    conn = sqlite3.connect(db_path, timeout=10.0)
    conn.executescript("""
        CREATE TABLE tasks (id TEXT PRIMARY KEY, title TEXT, status TEXT, priority INTEGER, dependencies TEXT, owner TEXT, created_at DATETIME, updated_at DATETIME);
        CREATE TABLE metrics (metric TEXT PRIMARY KEY, value INTEGER);
        INSERT INTO metrics VALUES ('tasks_completed', 0);
        INSERT INTO tasks (id, title, status, priority, dependencies) VALUES ('T001', 'first', 'todo', 1, '[]');
        INSERT INTO tasks (id, title, status, priority, dependencies) VALUES ('T002', 'second', 'todo', 1, '["T001"]');
    """)
    conn.commit()
    conn.close()

    assert get_next_task() == "T001"


def test_get_next_task_waits_for_deps(monkeypatch, tmp_path):
    db_path = tmp_path / "db" / "dag.db"
    db_path.parent.mkdir(parents=True)
    import db as db_mod
    monkeypatch.setattr(db_mod, "DB_PATH", str(db_path))

    conn = sqlite3.connect(db_path, timeout=10.0)
    conn.executescript("""
        CREATE TABLE tasks (id TEXT PRIMARY KEY, title TEXT, status TEXT, priority INTEGER, dependencies TEXT, owner TEXT, created_at DATETIME, updated_at DATETIME);
        CREATE TABLE metrics (metric TEXT PRIMARY KEY, value INTEGER);
        INSERT INTO metrics VALUES ('tasks_completed', 0);
        INSERT INTO tasks (id, title, status, priority, dependencies) VALUES ('T001', 'first', 'done', 1, '[]');
        INSERT INTO tasks (id, title, status, priority, dependencies) VALUES ('T002', 'second', 'todo', 1, '["T001"]');
    """)
    conn.commit()
    conn.close()

    assert get_next_task() == "T002"
