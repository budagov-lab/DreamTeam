#!/usr/bin/env python3
"""Shared database connection. All scripts use project.get_db_path()."""

import contextlib
import sqlite3

import project # type: ignore

DB_PATH = project.get_db_path()


@contextlib.contextmanager
def conn():
    """Context manager: yields (conn, cursor), auto-closes."""
    c = sqlite3.connect(DB_PATH, timeout=10.0)
    cur = c.cursor()
    try:
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")
        yield c, cur
    finally:
        c.close()
