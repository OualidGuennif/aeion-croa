---
name: security-scan
description: Runs a verified security scan with the claude-security plugin - on a branch's changes for a sensitive pull request, or on the codebase for the weekly outer loop - and turns verified findings into fixes or issues. Use when a diff touches auth, infrastructure, CI or secret handling, and weekly.
---

# Security scan

## Overview
The `claude-security` plugin maps the code, searches each component, and has separate verifiers try to disprove every finding; only survivors are reported. Policy: `knowledge/policies/security.md`.

## Process
1. Installed? `/plugin install claude-security@claude-plugins-official` (project scope), `/reload-plugins`.
2. Changes: `/claude-security scan my branch at medium`. Codebase (weekly): `/claude-security` → scan codebase at medium, every top-level folder scanned or excluded on purpose.
3. Read `CLAUDE-SECURITY-*/CLAUDE-SECURITY-RESULTS.md` (the folder is git-ignored).
4. A finding in this PR's diff: fix it on the branch. Elsewhere: skill `loop-triage` opens an issue (severity, file:line, scenario, fix; no exploit detail beyond the fix).
5. Never paste a secret; never suppress a real finding.

## Red flags
Running it on every diff (it costs tokens); treating a skipped scan as a pass.

## Verification
- [ ] The scan's summary is quoted in the PR or the issue.
