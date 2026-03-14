#!/usr/bin/env python3
"""Index codebase for semantic search. Requires: pip install sentence-transformers numpy."""

import os
import sys
import sqlite3
from pathlib import Path

import project
DB_PATH = project.get_db_path()
PROJECT_ROOT = project.get_project_root()
EXCLUDE_DIRS = {"__pycache__", ".git", "node_modules", "venv", ".venv", "db"}
EXCLUDE_EXT = {".pyc", ".db", ".sqlite", ".png", ".jpg", ".ico"}
MAX_CHUNK_SIZE = 500
MIN_CHUNK_SIZE = 50


def get_code_files() -> list[tuple[str, str]]:
    """Yield (relative_path, content) for code files."""
    for root, _, files in os.walk(PROJECT_ROOT):
        rel_root = os.path.relpath(root, PROJECT_ROOT)
        if any(ex in rel_root for ex in EXCLUDE_DIRS):
            continue
        for f in files:
            ext = os.path.splitext(f)[1]
            if ext in EXCLUDE_EXT:
                continue
            if ext in (".py", ".ts", ".tsx", ".js", ".jsx", ".md", ".mdc"):
                path = os.path.join(root, f)
                try:
                    with open(path, encoding="utf-8", errors="ignore") as fp:
                        content = fp.read()
                    rel = os.path.relpath(path, PROJECT_ROOT)
                    yield rel, content
                except OSError:
                    pass


def chunk_content(path: str, content: str) -> list[tuple[str, str]]:
    """Split content into chunks (by function/class or by size)."""
    chunks = []
    lines = content.split("\n")
    current = []
    current_len = 0

    for line in lines:
        current.append(line)
        current_len += len(line) + 1
        if current_len >= MAX_CHUNK_SIZE:
            text = "\n".join(current)
            if len(text) >= MIN_CHUNK_SIZE:
                chunks.append((path, text))
            current = []
            current_len = 0

    if current and current_len >= MIN_CHUNK_SIZE:
        chunks.append((path, "\n".join(current)))

    if not chunks and content:
        chunks.append((path, content[:2000]))

    return chunks


def index_codebase() -> None:
    """Index all code files and store embeddings in vector_code."""
    try:
        from sentence_transformers import SentenceTransformer
        import numpy as np
    except ImportError:
        print("Install: pip install sentence-transformers numpy", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(DB_PATH):
        print("Database not found. Run: dreamteam init-db", file=sys.stderr)
        sys.exit(1)

    # Ensure vector_code table exists (init_db may have been run before it was added)
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS vector_code (
            path TEXT, chunk TEXT, embedding BLOB,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

    model = SentenceTransformer("all-MiniLM-L6-v2")
    chunks: list[tuple[str, str]] = []

    for path, content in get_code_files():
        for p, ch in chunk_content(path, content):
            chunks.append((p, ch))

    if not chunks:
        print("No code files to index.")
        return

    texts = [c[1] for c in chunks]
    paths = [c[0] for c in chunks]
    embeddings = model.encode(texts)

    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vector_code")
    for (path, chunk), emb in zip(zip(paths, texts), embeddings):
        cursor.execute(
            "INSERT INTO vector_code (path, chunk, embedding) VALUES (?, ?, ?)",
            (path, chunk[:10000], emb.astype(np.float32).tobytes()),
        )
    conn.commit()
    conn.close()
    print(f"Indexed {len(chunks)} chunks from {len(set(paths))} files.")


if __name__ == "__main__":
    index_codebase()
