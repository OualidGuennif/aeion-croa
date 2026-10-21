#!/usr/bin/env python3
"""Stop hook: before an agent stops, the docs its change touches are current (the sign-off).

Input: the Stop event on stdin. Only the files this session edited count (after-edit.py records
them). When one of them is code whose covering doc did not change (tools/knowledge/doc-links L3),
work/current.md did not change, or it opened a new top-level folder without AGENTS.md changing, it
blocks with the findings not shown yet in this session; a second stop always passes.
"""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOC_PREFIXES = ("knowledge/", "work/", ".claude/", "tech-watch/")


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=False)


event = json.load(sys.stdin)
if event.get("stop_hook_active"):
    sys.exit(0)
session = event.get("session_id", "none")
edited_log = Path(tempfile.gettempdir()) / f"claude-edited-{session}"
edited = set(edited_log.read_text().split()) if edited_log.exists() else set()
if not edited:
    sys.exit(0)

# The base is where this branch left main; on main itself only uncommitted work counts.
base = next((git("merge-base", "HEAD", ref).stdout.strip() for ref in ("origin/main", "main")
             if git("rev-parse", "--verify", "--quiet", ref).returncode == 0), "")
if not base:
    sys.exit(0)
changed = set(git("diff", "--name-only", f"{base}...HEAD").stdout.split())
changed |= set(git("diff", "--name-only", "HEAD").stdout.split())
changed |= set(git("ls-files", "--others", "--exclude-standard").stdout.split())
code = sorted(p for p in changed & edited if not p.startswith(DOC_PREFIXES) and not p.endswith(".md"))
if not code:
    sys.exit(0)

findings = []
links = subprocess.run([sys.executable, str(ROOT / "tools/knowledge/doc-links"), "--diff", base, "--worktree"],
                       cwd=ROOT, capture_output=True, text=True, check=False)
# L1 names path:line, L2 the doc, L3 the changed file: keep the ones about this session's files.
findings += [l for l in links.stdout.splitlines()
             if l.startswith("RULE L") and l.split()[2].split(":")[0] in (set(code) | edited)]
if "work/current.md" not in changed:
    findings.append("work/current.md did not change: update the task's entry, or delete it if the task is done.")
base_top = {p.split("/")[0] for p in git("ls-tree", "--name-only", base).stdout.split()}
new_top = sorted({p.split("/")[0] for p in code if "/" in p} - base_top)
if new_top and "AGENTS.md" not in changed:
    findings.append(f"new top-level {', '.join(new_top)} but AGENTS.md (repository map) did not change.")
if not findings:
    sys.exit(0)

# Each finding is shown once per session, so a long task is reminded, never looped.
seen_log = Path(tempfile.gettempdir()) / f"claude-sign-off-{session}"
seen = set(seen_log.read_text().split()) if seen_log.exists() else set()
digest = lambda line: hashlib.sha256(line.encode()).hexdigest()[:16]
fresh = [l for l in findings if digest(l) not in seen]
if not fresh:
    sys.exit(0)
with seen_log.open("a") as f:
    f.write("".join(digest(l) + "\n" for l in fresh))
reason = ("Sign-off before stopping: " + str(len(code)) + " code file(s) you edited changed since main.\n"
          + "\n".join(fresh[:10])
          + "\nUpdate them (skill okf-update), or say in your answer why no documented fact changed.")
print(json.dumps({"decision": "block", "reason": reason}))
sys.exit(0)
