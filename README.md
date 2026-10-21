# Æion Factory

A repository prepared for agentic development, before there is any product code in it: the rules
an agent reads first, a knowledge base bound to the code, skills, hooks, three loops (inner,
middle, outer) and a technical watch — all checked, all small, all optional beyond the first phase.

Built for Claude Code (CLI or desktop) with its plugins; other agents can follow the files as
documents. Start with one phase and keep the parts that solve a real problem.

## Start here

| You want to | Read |
| --- | --- |
| Understand the approach in seven phases | [`efficiency/00-EFFICIENCY.md`](efficiency/00-EFFICIENCY.md) |
| Remember the seven principles | [CRAFTED](efficiency/CRAFTED.md) |
| Use this as a new project | the steps below |
| Apply it to an existing repository | give your agent `efficiency/00-EFFICIENCY.md` and one chapter at a time (skill `adopt`) |
| Every command | [`command.md`](command.md) |
| How an agent works here | [`Workflow_Agent.md`](Workflow_Agent.md) |
| The same, for humans, as slides | [HTML slides](docs/slides/workflow-human.html) |

## A new project from the Factory

```bash
git clone https://github.com/OualidGuennif/aeion-factory.git my-project
cd my-project
tools/knowledge/knowledge-check
tools/knowledge/doc-links
tools/repo-health/repo-health
```

Git and Python 3 run these checks; shell tools target macOS, Linux or WSL. This is a checkout of
Factory: use GitHub's **Use this template** to create your own repository. Then adapt `AGENTS.md`,
add your build/test commands, and follow phase 1. Install only the plugins you need.

Optional loops and integrations stay off by default. The public export contains no environment
files, including templates; configure optional services yourself only after reviewing their docs.

## What is inside

```
AGENTS.md / CLAUDE.md   the router an agent reads first (CLAUDE.md links to it)
command.md              every command: skills, tools, loops, plugins, git flow
Workflow_Agent.md       the order of work for an agent
docs/slides/            the human workflow as HTML slides
efficiency/             the seven-phase guide: quarks → atoms → molecules → cells → organisms → constellations → galaxy
knowledge/              policies, components, decisions, operations, references (OKF format)
work/current.md         open tasks only
tech-watch/             the technical watch method and its dated packages
loops/                  the orchestrator, prompts, model routing, schedules, issue protocol, Decisions API client
tools/                  knowledge-check, doc-links, repo-health, local language-server plugins
.claude/                hooks, skills, path-scoped rules, hookify examples
.github/workflows/      CI (docs gates and security scans); optional PR review and outer loop
```

License: [MIT](LICENSE). Credits: [CREDITS.md](CREDITS.md). Security: [SECURITY.md](SECURITY.md).
