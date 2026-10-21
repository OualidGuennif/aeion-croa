---
type: Reference
title: "Sources behind the Factory"
description: "The research, docs and tools the guide's recommendations rest on, with links."
status: stable
generated:
  by: aeion-factory/1.0
  at: 2026-10-20T00:00:00Z
sources:
  - id: credits
    resource: ../../CREDITS.md
    title: "Credits"
---

Æion Factory is an orchestration layer over other people's ideas and tools. Thank you.

## Tools and plugins

- **Anthropic, Claude Code and its official plugins** — `hookify` (hook rules from Markdown and from
  conversation corrections), `skill-creator` (skill drafting, evals, description optimization),
  `claude-security` (verified security scans of a codebase or a change), and the LSP plugin format.
  https://github.com/anthropics/claude-plugins-official · https://code.claude.com/docs
- **Addy Osmani, `agent-skills`** (MIT) — the skill anatomy (overview, when to use, process,
  rationalizations, red flags, verification) and the DEFINE → PLAN → BUILD → VERIFY → REVIEW → SHIP
  lifecycle that the Factory's skills follow. https://github.com/addyosmani/agent-skills ·
  "Own the Outer Loop" (2026).
- **Vectorize, Hindsight** (MIT) — agent memory with retain, recall and reflect.
  https://github.com/vectorize-io/hindsight
- **The language servers:** Microsoft TypeScript 7 (native `tsc --lsp`), Deno's built-in server,
  Eclipse JDT Language Server.

## Research and practice

- Chroma, *Context Rot* (2025) — long inputs degrade every model measured.
- Gloaguen et al., context files and agent success (arXiv 2602.11988, 2026).
- Lulla et al., AGENTS.md and agent runtime (arXiv 2601.20404, 2026).
- Anthropic, *Effective context engineering for AI agents* (2025).
- Doc-to-code trace links with LLMs (arXiv 2506.16440, 2025).
- Microsoft Learn, the developer inner and outer loop.
- Cyrille Martraire, *Living Documentation*.
- OWASP cheat sheets: secrets management, database security.
- GitHub docs: security policies, CODEOWNERS.

Mistakes in how these ideas are combined here are ours, not theirs.
