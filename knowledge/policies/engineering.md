---
type: Policy
title: "How code is written here"
description: "Steps that read top to bottom, comments that say why, no needless abstraction, and the branch, pull request and review flow."
status: stable
generated:
  by: aeion-factory/1.0
  at: 2026-10-20T00:00:00Z
sources:
  - id: guide
    resource: ../../efficiency/1-quarks.md
    title: "Phase 1 of the guide"
---

# How code is written here

## Code reads top to bottom

A function that chains steps writes them one after the other, one call per step, each preceded
by a one-line comment saying the step's intent (a level above the code, never a paraphrase).

```ts
// Read the request; never re-fetch it here.
const order = parseOrder(request.body);
// Price it with the rules in force today.
const total = priceOrder(order, rules);
// Fail closed: an unreadable total is a refusal, never a guess.
return totalOrRefusal(total);
```

Not done here: one line chaining several steps; a helper around a single call; an interface with
one implementation; a "Manager", "Factory" or "Helper" without two real users; a parameter added
"in case". Allowed: a deep function whose name says everything and which hides real complexity.

## Comments

| Where | At most | What it says |
| --- | --- | --- |
| File or class header | 10 lines | what it is for, its authority boundary, `Spec: knowledge/<doc>.md` |
| Public method | 6 lines | its contract: inputs, output, refusals |
| Inside a function | 1 line per step (3 for a non-obvious trap) | the intent, or the why |

Never in a comment: dates, ticket numbers, the story of a bug, or a list of what is not done. The
story goes in the commit message.

## Branch, pull request, review

- One branch per task, `task/<slug>`, from an up-to-date default branch; small commits.
- `gh pr create` with what, why and the checks run (skill `sign-off`).
- The skill `pr-review`: a fresh subagent reviews; every finding is verified; one comment:
  `Review: OK` or `Review: NOT OK` with at most five findings.
- Merge after `Review: OK` and a green CI. A deploy or a human decision waits for that human.
- The owner's comments become preferences (skill `pr-taste`).

## Before changing code

Locate the current owner of the behaviour, its tests and its spec; change the minimum; keep
existing contracts unless the task requires changing them. No abstraction is created "for later".
