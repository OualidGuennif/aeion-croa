---
name: build
description: Implements an approved plan in thin, tested slices, letting language-server diagnostics and the edit hooks speak after every edit, and committing each green slice. Use when implementing a planned change.
---

# Build

## Overview
Thin vertical slices: each one compiles, passes its tests and is committed. Rules: `knowledge/policies/engineering.md`.

## When to use
After `plan` (and `spec` when behaviour changes). Not before a yes.

## Process
1. Branch: `git switch -c task/<slug> origin/main`.
2. Pick the smallest slice that moves toward the plan; write its test first when practical.
3. Edit; read the diagnostics and hook output after each edit; fix before moving on.
4. Run the slice's tests; commit with a message that says what and why.
5. Repeat. Stop and re-plan if the plan turns out wrong.

## Rationalizations
| Excuse | Rebuttal |
| --- | --- |
| "I'll run the tests at the end" | Then one failure hides behind ten changes. |
| "This helper will be useful later" | No abstraction without two real users. |

## Red flags
A commit with failing tests; a slice touching ten files; silenced diagnostics.

## Verification
- [ ] Every commit passed the pre-commit and its tests.
- [ ] The diff contains only what the plan named.
