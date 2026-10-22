# Credits and adaptation notice

## The CROA Project

**CROA — Constrained Reachability Orchestration Architecture** is authored by **The CROA Project**.
The v1.0.1 citation names **Yasmine Durand, Darrin Smith and Sylvain Durand**. Thank you for
publishing an architecture, explicit limitations, errata and reference tests that can be examined.

- Website: https://www.croaframework.org/
- Repository: https://github.com/CROA-Project/CROA
- Requested release: https://github.com/CROA-Project/CROA/tree/v1.0.1
- Pinned source: https://github.com/CROA-Project/CROA/tree/4d59192da9a0d00412c9d2ccb9e5ab68176803ff
- v1.0.1 DOI: https://doi.org/10.5281/zenodo.22310276
- Original citation: https://github.com/CROA-Project/CROA/blob/4d59192da9a0d00412c9d2ccb9e5ab68176803ff/CITATION.cff
- Reference demonstrator: https://github.com/CROA-Project/croa-reference-harness

CROA specification/documentation: **CC BY 4.0**. Upstream code and machine-readable artifacts:
**Apache-2.0**. These are different licenses; this kit does not relicense upstream work.

**Æion changes:** grouped assessment prompts, version/provenance records, reading notes, an
agent skill, a local packet format, and original Python validation/reporting tools. Questions
and prose are adaptations of the specification, not official CROA normative requirements.
No CROA harness code, official schemas or complete specification are bundled. Upstream authors
have not reviewed or endorsed these adaptations; interpretation mistakes are ours.

## Æion Factory

The scaffold comes from https://github.com/OualidGuennif/aeion-factory at
`00fdbd0757b8ed3e08e71fa335de851234423c74`, MIT, copyright 2026 Oualid Guennif.
Its engineering workflow is retained. Existing Factory credits follow without removing attribution.

# Factory credits

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
