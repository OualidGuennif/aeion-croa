---
name: pr-review
description: Reviews a pull request with a fresh subagent, verifies every finding, and posts one short verdict on it (Review OK or NOT OK with at most five findings and file:line). Use after opening a pull request and after each push of fixes.
---

# Review a pull request

## Overview
A fresh context catches what the author's context hides. One comment, one verdict. Flow: `knowledge/policies/engineering.md`.

## Process
1. `gh pr view <n> --json number,title,files,additions,deletions` and `gh pr checks <n>`.
2. Start ONE fresh, read-only reviewer subagent with: the PR number, `git diff origin/main...HEAD`, `AGENTS.md`, and the docs `tools/knowledge/doc-links --for <file>` names. Ask for findings ranked by severity, each with path:line and a concrete failure scenario.
3. A sensitive diff: also skill `security-scan` on the changes, or say it was not run.
4. Verify every finding yourself; drop what you cannot confirm.
5. Post with `gh pr comment <n> --body-file <file>`:
   ```
   Review: OK            (or)   Review: NOT OK
   - <high|medium|low> path:line -- the finding (at most five)
   Checks: CI <state>; doc-links <result>; tests <what ran>
   ```
6. NOT OK: fix on the branch, push, review again. OK and CI green: `gh pr merge --squash --delete-branch`. A human decision waits before the merge; a deploy after it.

## Rationalizations
| Excuse | Rebuttal |
| --- | --- |
| "I wrote it, I know it's fine" | That is why the reviewer is fresh. |

## Red flags
Approving through the forge's review API; merging on red CI; a secret in a comment.

## Verification
- [ ] The verdict comment is on the PR, with the checks line.
