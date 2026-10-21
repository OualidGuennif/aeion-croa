---
type: Reference
title: "Knowledge index"
description: "The entry point: to do X, open Y."
status: stable
generated:
  by: aeion-factory/1.0
  at: 2026-10-20T00:00:00Z
---

# Knowledge

Open only what the task needs. Each folder has its own `index.md`.

| To | Open |
| --- | --- |
| Follow a durable rule (engineering, security, specs, layout, UI, the owner's taste) | [policies/index.md](policies/index.md) |
| Change a component | [components/index.md](components/index.md) (one spec per unit) |
| Understand why a choice exists | [decisions/index.md](decisions/index.md) |
| Build, test, run the loops, recover | [operations/index.md](operations/index.md) |
| External material worth keeping | [references/index.md](references/index.md) |
| A volatile state summary (check `stale_after`) | [current/index.md](current/index.md) |

Task state lives in [`../work/current.md`](../work/current.md), never here. The story of a change
lives in its commit message.
