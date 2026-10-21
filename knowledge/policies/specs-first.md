---
type: Policy
title: "Specs first, and links to code"
description: "The eight spec sections a component doc carries, the determinism slider, and the links between docs and code that tools/knowledge/doc-links checks."
status: stable
generated:
  by: aeion-factory/1.0
  at: 2026-10-20T00:00:00Z
sources:
  - id: tool
    resource: ../../tools/knowledge/doc-links
    title: "The link checker"
---

# Specs first

The spec is the source of truth; the code implements it. A component doc, and any new feature
before its code is written, has these sections in this order:

```markdown
## Intent              one or two sentences: what it is for, which decision it serves
## Data sources        | Source | What is read | Owner | Freshness |
## Inputs              exact structure: types, fields, units, allowed values; a link to the type
## Outputs             exact structure, plus every refusal and error code
## Invariants          numbered; each names the test that proves it
## Determinism         deterministic | bounded | adaptive, and why
## Acceptance checks   commands that pass or fail
## Out of scope        what it does not do, one line each
```

| Level | Who produces the output | How it is checked |
| --- | --- | --- |
| deterministic | code | unit and parity tests |
| bounded | a model, under a fixed output contract | a strict parser; unreadable output is a refusal |
| adaptive | a model, free text | never an authority: advice or a report |

# Links between docs and code

- **Doc to code:** the doc's frontmatter `sources` lists the files it describes
  (`resource: ../../src/area/file.ts`). A directory source is checked for existence only.
- **Code to doc:** a described file carries one header line `Spec: knowledge/<doc>.md`.
- `tools/knowledge/doc-links` fails when a pointer or a source does not resolve, and with
  `--diff origin/main` when a file changed while a doc covering it did not. Updating the doc, or a
  commit trailer `Docs-Checked: knowledge/<doc>.md -- <why no documented fact changed>`, passes.
- A link is a pointer, never copied content.
