---
name: ship
description: Merges and releases a reviewed change behind a green CI and the deploy's own guards, with a changelog line and a rollback path. Use when a pull request has Review OK and green CI, or when cutting a release.
---

# Ship

## Process
1. Confirm `Review: OK` is the latest verdict and `gh pr checks` is green on the head commit.
2. Squash-merge; the message says what changed and why (it is the history).
3. Release: run the release gate (skill `security-scan` on the changes since the last tag, `tools/knowledge/doc-links`), tag, write the changelog line.
4. Deploy only through the project's deploy procedure and its guards, with a human's go when the project requires it. Never bypass a guard.
5. After the deploy, read the result through the read-only path and record it in `work/current.md`.

## Red flags
A deploy from an unmerged branch; a skipped CI run at the deployed commit; no rollback plan.

## Verification
- [ ] The deployed commit has a green CI run.
- [ ] The rollback command is known before the deploy.
