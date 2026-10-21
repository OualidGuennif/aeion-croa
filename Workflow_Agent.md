# How an agent works in this repository

The order of work, every time. Each step names its skill or tool; the reasons are in the
knowledge base.

## 0. Before anything

- Read `AGENTS.md` (it is short). The session starts with a summary from the `SessionStart` hook:
  git status, recent commits, open tasks.
- Instructions that existed before the Factory, and the owner's words, win.

## 1. Plan (skill `plan`)

Enter plan mode. Inspect the code and the docs the task touches (`knowledge/index.md`, then the
area's doc; `tools/knowledge/doc-links --for <file>` names a file's doc). Propose the smallest
change that fits; list what you will not do. Wait for a yes.

## 2. Spec (skill `spec`)

For a feature or a component, write or update its spec sections first (intent, inputs, outputs,
invariants and their tests, acceptance checks). The spec is the source of truth.

## 3. Branch

`git switch -c task/<slug> origin/main`. One task, one branch.

## 4. Build in thin slices (skills `build`, `test`)

Change a little, then let the feedback speak: language-server diagnostics and the edit hook after
every edit, the tests after every slice. Commit each green slice. Never weaken a test to pass it.

## 5. Sign off (skill `sign-off`)

Tests for what changed; `tools/knowledge/doc-links --diff origin/main --worktree`; the docs the
change touches (skill `okf-update`); `work/current.md`; `AGENTS.md` if the map or a command
changed; `/claude-security` on a sensitive diff. The `Stop` hook reminds you once of anything left.

## 6. Pull request and review (skill `pr-review`)

`gh pr create` with what, why and the checks run. A fresh reviewer reviews; every finding is
verified; one comment: `Review: OK` or `Review: NOT OK`. Fix and repeat until OK.

## 7. Merge

After `Review: OK` and a green CI, squash-merge. Anything that needs a deploy or a human decision
waits for that human.

## 8. Learn (skills `pr-taste`, `retro`)

The owner's comments become preferences; the weekly retro turns repeated mistakes into hooks and
repeated procedures into skills.

## Loops that run without you

The outer loop (scheduled, read-only) opens issues; an inner run picks an `agent-ready` issue and
goes through steps 3–7. Commands: `command.md`.
