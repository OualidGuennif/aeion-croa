# Commands

Everything you can run here, grouped by loop. Skills are invoked by name in a Claude Code session
(`/plan`, or "run the skill plan"); tools and loops from a shell.

## Skills (`.claude/skills/`)

| Skill | When |
| --- | --- |
| `plan` | start any non-trivial task: inspect, propose, wait for a yes |
| `spec` | a feature or component changes: write its spec sections first |
| `build` | implement in thin, tested slices |
| `test` | add or fix tests; never weaken an assertion |
| `sign-off` | end a task: tests, docs and links, task state, security on sensitive diffs |
| `pr-review` | a pull request is open: fresh reviewer, verified findings, one verdict comment |
| `ship` | merge and release behind green CI and the deploy's own guards |
| `okf-update` | a documented fact changed: the right doc, its links, its caps |
| `security-scan` | a sensitive diff, or the weekly job: `/claude-security` |
| `tech-watch` | the monthly technical watch |
| `pr-taste` | the owner commented on a PR: keep the durable preferences |
| `retro` | weekly or after a long session: lessons into hooks, skills and preferences |
| `loop-triage` | an outer-loop finding: turn it into an issue an inner loop can fix |
| `adopt` | apply the Factory to an existing repository, one phase at a time |

## Tools

```bash
tools/knowledge/knowledge-check                       # the knowledge base: frontmatter, links, caps
tools/knowledge/doc-links                             # docs <-> code links resolve (L1, L2)
tools/knowledge/doc-links --diff origin/main --worktree   # also: code changed without its doc (L3)
tools/knowledge/doc-links --for path/to/file          # the docs covering a file
tools/repo-health/repo-health [--json]                # comment blocks, file sizes, AGENTS.md and work caps
python3 tools/knowledge/tests/test_doc_links.py       # tool tests
python3 .claude/hooks/test_hooks.py                   # hook tests
```

## Loops (`loops/orchestrator.sh`)

```bash
loops/orchestrator.sh <job> [--dry-run] [--issue N]
#   inner     fix one `agent-ready` issue: branch, PR, review (needs --issue)
#   middle    review the open pull requests that have no verdict yet
#   outer     daily read-only health: production (read-only path), CI, open findings -> issues
#   docs      daily docs drift: doc-links, knowledge-check, stale dates -> issues
#   security  weekly codebase scan with /claude-security -> issues
#   watch     monthly technical watch -> a tech-watch package via PR
#   retro     weekly lessons from sessions and PR comments -> a PR of hooks, skills, preferences
```

Every job reads `env.local`, refuses to run while `LOOPS_ENABLED=false` (except `--dry-run`), and
prints the exact `claude -p` command it runs. Schedules: `loops/schedules/`.

## Plugins (Claude Code)

```bash
claude plugin marketplace add anthropics/claude-plugins-official
claude plugin install hookify@claude-plugins-official --scope project
claude plugin install skill-creator@claude-plugins-official --scope project
claude plugin install claude-security@claude-plugins-official --scope project
claude plugin marketplace add ./tools/claude-plugins --scope project      # local language servers
claude plugin install native-lsp@aeion-local --scope project
```

## Git flow

```bash
git switch -c task/<slug> origin/main
git commit -m "<what changed and why>"            # the pre-commit runs the checks
gh pr create --fill
# then, in a session: run the skill pr-review
```
