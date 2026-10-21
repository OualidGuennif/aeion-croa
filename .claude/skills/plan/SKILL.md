---
name: plan
description: Plans a non-trivial task before any change - inspects the code and docs it touches, proposes the smallest fitting change, lists what will not be done, and waits for a human's yes. Use when starting any task that touches more than a line or two.
---

# Plan

## Overview
Plan mode first: the cheapest bug is the one never written. Reasons: `knowledge/policies/engineering.md`.

## When to use
Any task beyond a typo. Not for a pure question (answer it) or a one-line fix with an obvious test.

## Process
1. Read `AGENTS.md`, then `knowledge/index.md` and the area's doc; `tools/knowledge/doc-links --for <file>` names a file's doc.
2. Read the real code: callers, contracts, tests, configuration. Note what already exists to reuse.
3. Write the plan: context (why), the change (files, functions, data), what is out of scope, the checks that will prove it.
4. Ask only the questions whose answer changes the plan.
5. Wait for an explicit yes before editing.

## Rationalizations
| Excuse | Rebuttal |
| --- | --- |
| "It's small, I'll just do it" | Small changes in unread code are how regressions start. Read first. |
| "I'll plan as I go" | Then the reviewer reverse-engineers the plan from the diff. |

## Red flags
A plan with no checks; a plan that adds an abstraction "for later"; editing before the yes.

## Verification
- [ ] Every file in the plan was opened and read.
- [ ] The plan names the commands that will prove it.
- [ ] A human said yes.
