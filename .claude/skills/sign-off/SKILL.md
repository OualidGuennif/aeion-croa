---
name: sign-off
description: The checklist that ends a task before its pull request - tests, docs and their links, the task state, the AGENTS.md map, a security scan on sensitive diffs, and a pull request body with the checks run. Use at the end of every task.
---

# Sign off

## Overview
Done means proven and documented, not "the code is written". Reasons: `AGENTS.md`, definition of done.

## Process
1. The tests for what changed (the project's commands in `AGENTS.md`).
2. `tools/knowledge/doc-links --diff origin/main --worktree`: for each L3, update the doc (skill `okf-update`) or add `Docs-Checked: knowledge/<doc>.md -- <why no fact changed>` to a commit message.
3. `work/current.md`: update the task's entry, or delete it when done.
4. `AGENTS.md`: when a top-level folder, a command or a rule changed.
5. A sensitive diff (auth, infrastructure, CI, secrets): skill `security-scan` on the changes.
6. `gh pr create` with what, why, the checks run and their results, the docs touched; then skill `pr-review`.

## Red flags
"Tests pass" without the command; a PR body that lists no checks; a doc left for "later".

## Verification
- [ ] Each check above ran, with its result in the PR body.
- [ ] `doc-links --diff` passes.
