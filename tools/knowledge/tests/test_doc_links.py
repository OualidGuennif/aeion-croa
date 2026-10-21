#!/usr/bin/env python3
"""Fixture tests for tools/knowledge/doc-links: throwaway git repos, the real tool run with --root.

Run with: python3 tools/knowledge/tests/test_doc_links.py
"""
import subprocess
import sys
import tempfile
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / "doc-links"
# Built in two parts so this file holds no pointer the real check would follow.
TAG = "Sp" + "ec:"
DOC = """---
type: Component
title: Example
sources:
  - id: code
    resource: ../../src/app.ts
    title: The code
  - id: folder
    resource: ../../src
    title: The whole folder
  - id: owner
    resource: owner request in chat, 2026-10-20
    title: Free text, not a path
---

Body.
"""
failures, passes = [], 0


def sh(repo, *args):
    return subprocess.run(args, cwd=repo, capture_output=True, text=True, check=False)


def repo():
    tmp = Path(tempfile.mkdtemp())
    (tmp / "knowledge/components").mkdir(parents=True)
    (tmp / "src").mkdir()
    (tmp / "knowledge/components/example.md").write_text(DOC)
    (tmp / "src/app.ts").write_text(f"// {TAG} knowledge/components/example.md\nexport const a = 1;\n")
    (tmp / "src/other.ts").write_text("export const b = 2;\n")
    sh(tmp, "git", "init", "-q", "-b", "main")
    sh(tmp, "git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "add", ".")
    sh(tmp, "git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-qm", "base")
    return tmp


def commit(tmp, message):
    sh(tmp, "git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-qam", message)


def check(name, tmp, args, want_code, want_text=""):
    global passes
    r = subprocess.run([sys.executable, str(TOOL), "--root", str(tmp), *args], capture_output=True, text=True)
    if r.returncode == want_code and want_text in r.stdout:
        passes += 1
    else:
        failures.append(f"{name}: exit {r.returncode}, want {want_code} with '{want_text}'\n{r.stdout}{r.stderr}")


t = repo()
check("links resolve, free text ignored", t, [], 0, "PASS")
check("the docs covering a file", t, ["--for", "src/app.ts"], 0, "knowledge/components/example.md")
check("a directory source covers no single file", t, ["--for", "src/other.ts"], 0, "")

(t / "src/app.ts").write_text(f"// {TAG} knowledge/components/example.md\nexport const a = 2;\n")
commit(t, "change app")
check("code changed, its doc did not", t, ["--diff", "HEAD~1"], 1, "RULE L3 src/app.ts")

t = repo()
(t / "src/other.ts").write_text("export const b = 3;\n")
commit(t, "change other")
check("a file only under a directory source asks for nothing", t, ["--diff", "HEAD~1"], 0, "PASS")

t = repo()
(t / "src/app.ts").write_text(f"// {TAG} knowledge/components/example.md\nexport const a = 2;\n")
commit(t, "change app\n\nDocs-Checked: knowledge/components/example.md -- no documented fact changed")
check("a declared check passes", t, ["--diff", "HEAD~1"], 0, "PASS")

t = repo()
(t / "src/app.ts").write_text(f"// {TAG} knowledge/components/example.md\nexport const a = 2;\n")
(t / "knowledge/components/example.md").write_text(DOC + "\nUpdated.\n")
check("the doc changed with the code (uncommitted)", t, ["--diff", "HEAD", "--worktree"], 0, "PASS")

t = repo()
(t / "src/other.ts").write_text(f"// {TAG} knowledge/components/example.md\n\nexport const b = 2;\n")
commit(t, "link other")
check("adding a Spec: line alone moves no fact", t, ["--diff", "HEAD~1"], 0, "PASS")

t = repo()
(t / "src/app.ts").write_text(f"// {TAG} knowledge/components/missing.md\n")
check("a Spec pointer to a missing doc", t, [], 1, "RULE L1 src/app.ts:1")
(t / "src/app.ts").unlink()
check("a source that disappeared", t, [], 1, "RULE L2 knowledge/components/example.md")

for f in failures:
    print("FAIL:", f)
print(f"{passes} passed, {len(failures)} failed")
sys.exit(1 if failures else 0)
