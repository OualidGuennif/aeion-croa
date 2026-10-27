# Current work

## Check extensionless scripts and keep the efficiency bundle current

- Owner decision: approved on 2026-10-27; two pull requests, then merge to main.
- State: in progress on task/doc-links-scripts.
- Next: doc-links scans shebang scripts; regenerate the bundle with a CI freshness check; map docs/.
- Blocker: none.
- Evidence: a broken Spec: line in tools/git-hooks/pre-commit passed doc-links before the fix.
