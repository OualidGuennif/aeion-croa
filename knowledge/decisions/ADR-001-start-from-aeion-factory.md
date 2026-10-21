---
type: Decision
title: "ADR-001 Start from Æion Factory"
description: "The repository starts from Æion Factory: a router AGENTS.md, an OKF knowledge base linked to code, skills, hooks, three loops; optional services off by default."
status: stable
generated:
  by: aeion-factory/1.0
  at: 2026-10-20T00:00:00Z
sources:
  - id: guide
    resource: ../../efficiency/00-EFFICIENCY.md
    title: "The seven-phase guide"
---

# ADR-001 — Start from Æion Factory

## Context
Agents work best with short, routed instructions, docs bound to code, and fast feedback; humans
should not have to review every change by hand.

## Decision
The repository uses the Factory's structure: `AGENTS.md` as a router, `knowledge/` in the OKF
format with links to code checked by `doc-links`, skills and hooks in `.claude/`, the branch + PR +
review flow, and the scheduled read-only outer loop. The Decisions API and the memory service are
off until a human turns them on.

## Consequences
Every task ends with a sign-off and a review comment; docs drift fails CI; outer findings arrive
as issues. Revisit when the trinity measures (Phase 7) degrade.

## Alternatives considered
- One large instruction file: costs tokens on every task, helps none (Phase 1).
- Auto-fixing outer loop: bypasses review; rejected.
