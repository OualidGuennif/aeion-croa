#!/usr/bin/env python3
# Spec: knowledge/operations/build-and-test.md
"""SessionStart hook: at most 25 lines of facts — uncommitted changes, recent commits, open tasks,
and the health scorecard — so a new or resumed session starts from evidence."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def out(*command):
    return [l for l in subprocess.run(command, cwd=ROOT, capture_output=True, text=True).stdout.split("\n") if l.strip()]


lines = []
# Uncommitted changes: one you cannot explain is not yours.
status = out("git", "status", "--short")
lines.append(f"git status: {len(status)} changed path(s)" if status else "git status: clean")
lines += ["  " + s for s in status[:6]]
# The last commits.
lines.append("last commits:")
lines += ["  " + s for s in out("git", "log", "-5", "--oneline")]
# Open tasks.
work = ROOT / "work/current.md"
titles = [l[3:] for l in work.read_text(encoding="utf-8").split("\n") if l.startswith("## ")] if work.exists() else []
lines.append(f"work/current.md: {len(titles)} open task(s)")
lines += ["  " + t[:110] for t in titles[:6]]
# The scorecard.
lines += out("tools/repo-health/repo-health")
print("\n".join(lines[:25]))
