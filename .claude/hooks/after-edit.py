#!/usr/bin/env python3
# Spec: knowledge/operations/build-and-test.md
"""PostToolUse hook on Edit and Write: the fast checks that apply to the edited file.

Silent with exit 0 when they pass; exit 2 with at most 15 lines (the rule and its fix) when not.
It also records the file for the Stop sign-off, and names the doc that covers it, once per session.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run(*command):
    return subprocess.run(command, cwd=ROOT, capture_output=True, text=True)


event = json.load(sys.stdin)
session = event.get("session_id", "none")
path = Path(event.get("tool_input", {}).get("file_path", "")).resolve()
if ROOT not in path.parents or not path.is_file():
    sys.exit(0)
rel = path.relative_to(ROOT).as_posix()
problems = []

# Remember what this session edited: the Stop sign-off looks at these files only.
with (Path(tempfile.gettempdir()) / f"claude-edited-{session}").open("a") as f:
    f.write(rel + "\n")

# The knowledge base and the files agents read first.
if rel.startswith(("knowledge/", "work/")) or path.name in ("AGENTS.md", "CLAUDE.md"):
    result = run("tools/knowledge/knowledge-check")
    problems += [l for l in result.stdout.splitlines() if l.startswith("FAIL ")]

# Add your project's per-file checks here (formatter, linter), e.g. shellcheck for *.sh.

# Code a doc covers: name the doc, once per file and session.
hint = ""
if not rel.startswith(("knowledge/", "work/")) and path.suffix != ".md":
    docs = run("tools/knowledge/doc-links", "--for", rel).stdout.split()
    seen = Path(tempfile.gettempdir()) / f"claude-doc-hint-{session}"
    if docs and rel not in (seen.read_text().split() if seen.exists() else []):
        with seen.open("a") as f:
            f.write(rel + "\n")
        hint = f"{rel} is covered by {', '.join(docs)}: update it if a documented fact changed."

if problems:
    print(f"Checks after editing {rel}:", file=sys.stderr)
    print("\n".join(problems[:15] + ([hint] if hint else [])), file=sys.stderr)
    sys.exit(2)
if hint:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": hint}}))
sys.exit(0)
