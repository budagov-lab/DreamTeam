#!/usr/bin/env python3
"""Git commit and push for completed task. Usage: git_commit.py <task_id> <message>"""

import os
import subprocess
import sys

import project
ROOT = project.get_project_root()


def run(cmd: list[str], check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=check)


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: git_commit.py <task_id> <message>", file=sys.stderr)
        sys.exit(1)

    task_id = sys.argv[1]
    message = " ".join(sys.argv[2:])
    commit_msg = f"{task_id}: {message}"

    if not os.path.exists(os.path.join(ROOT, ".git")):
        print("Not a git repository. Skip.", file=sys.stderr)
        sys.exit(0)

    r = run(["git", "status", "--porcelain"])
    if not r.stdout.strip():
        print("No changes to commit.")
        return

    run(["git", "add", "-A"])
    r = run(["git", "commit", "-m", commit_msg])
    if r.returncode != 0:
        print("Commit failed:", r.stderr or r.stdout, file=sys.stderr)
        sys.exit(1)

    print(f"Committed: {commit_msg}")

    r = run(["git", "push"])
    if r.returncode != 0:
        print("Push failed (retrying once):", r.stderr or r.stdout, file=sys.stderr)
        r_retry = run(["git", "push"])
        if r_retry.returncode != 0:
            print("Push failed after retry (continuing):", r_retry.stderr or r_retry.stdout, file=sys.stderr)
        else:
            print("Pushed on retry.")
    else:
        print("Pushed.")


if __name__ == "__main__":
    main()
