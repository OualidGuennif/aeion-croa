---
type: Runbook
title: "The loops"
description: "Inner, middle and outer loops: the orchestrator's jobs, their models, tools and schedules, and what keeps the outer loop read-only."
status: stable
generated:
  by: aeion-factory/1.0
  at: 2026-10-20T00:00:00Z
sources:
  - id: orchestrator
    resource: ../../loops/orchestrator.sh
    title: "The orchestrator"
  - id: protocol
    resource: ../../loops/issue-protocol.md
    title: "The issue protocol"
  - id: client
    resource: ../../loops/decisions-api/client.sh
    title: "The Decisions API client"
---

# The loops

`loops/orchestrator.sh <job>` runs one job headless (`claude -p`) with its prompt
(`loops/prompts/`), model and thinking level (`loops/model-routing.md`), tool allowlist and
permission mode. It reads only the loop settings of `env.local` (never the Decisions API secret)
and runs nothing while `LOOPS_ENABLED` is not `true`; `--dry-run` prints the settings.

| Job | Schedule | Writes |
| --- | --- | --- |
| `outer` | daily | issues only (production through `PROD_READ_COMMAND`, the only allowed production read) |
| `docs` | daily | issues only |
| `security` | weekly and before releases | issues only |
| `middle` | every 30 min on working hours | review comments only |
| `watch` | monthly | a `tech-watch/pending/` package by pull request |
| `retro` | weekly | a pull request of hook rules, skills and preferences |
| `inner --issue N` | on demand or after triage | a branch and a pull request for one `agent-ready` issue |

Schedulers: `loops/schedules/crontab.example`, the launchd plist, or
`.github/workflows/outer-loop.yml` (off until the repository variable `OUTER_LOOP_ENABLED` is
`true`). Issues follow `loops/issue-protocol.md`. The Decisions API client
(`loops/decisions-api/client.sh`) refuses to run until `DECISION_API_ENABLED=true`.
