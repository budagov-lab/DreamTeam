#!/usr/bin/env python3
"""Semantic search over indexed codebase. Requires: pip install sentence-transformers numpy."""

import os
import sys
import sqlite3

import project
DB_PATH = project.get_db_path()
DEFAULT_TOP_K = 5


def search(query: str, top_k: int = DEFAULT_TOP_K) -> list[tuple[str, str, float]]:
    """Return list of (path, chunk, score) sorted by relevance."""
    try:
        from sentence_transformers import SentenceTransformer
        import numpy as np
    except ImportError:
        print("Install: pip install sentence-transformers numpy", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(DB_PATH):
        print("Database not found. Run: dreamteam init-db", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    cursor = conn.cursor()
    cursor.execute("SELECT path, chunk, embedding FROM vector_code")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No index. Run: dreamteam vector-index", file=sys.stderr)
        return []

    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_emb = model.encode([query], convert_to_numpy=True).astype(np.float32)

    results = []
    for path, chunk, emb_blob in rows:
        emb = np.frombuffer(emb_blob, dtype=np.float32)
        score = float(np.dot(query_emb[0], emb) / (np.linalg.norm(query_emb[0]) * np.linalg.norm(emb) + 1e-9))
        results.append((path, chunk, score))

    results.sort(key=lambda x: x[2], reverse=True)
    return results[:top_k]


def main() -> None:
    """CLI: python vector_search.py <query> [--top N]"""
    if len(sys.argv) < 2:
        print("Usage: python vector_search.py <query> [--top N]", file=sys.stderr)
        sys.exit(1)

    args = sys.argv[1:]
    top_k = DEFAULT_TOP_K
    if "--top" in args:
        idx = args.index("--top")
        if idx + 1 < len(args):
            try:
                top_k = int(args[idx + 1])
            except ValueError:
                pass
        args = args[:idx] + args[idx + 2:]
    query = " ".join(args)

    results = search(query, top_k)
    for path, chunk, score in results:
        preview = chunk[:200].replace("\n", " ") + ("..." if len(chunk) > 200 else "")
        print(f"[{score:.3f}] {path}")
        print(f"  {preview}")
        print()


if __name__ == "__main__":
    main()
