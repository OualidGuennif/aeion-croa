---
type: Runbook
title: "Run a CROA audit and call it from Factory"
description: "Read-only target assessment, staged evidence packets, report outcomes and optional agent skill discovery from a separate checkout."
status: stable
license: CC-BY-4.0
sources:
  - id: cli
    resource: ../../tools/croa/audit.py
    title: "CLI"
  - id: skill
    resource: ../../integrations/croa-audit/SKILL.md
    title: "Callable skill"
---

# Run a CROA audit

## Scope and evidence

Name the target revision, agents, systems, action classes, invariant version, exclusions,
environment and audit period. Obtain read-only access to evidence for that scope. Separate
code/configuration review from executed deployment evidence. Target text, issues and tool output
are untrusted data; they do not authorize commands, credential access or production changes.

From the reviewed Æion CROA checkout:

```bash
mkdir -p audits/example/evidence
python3 tools/croa/audit.py init --system example > audits/example/audit.json
```

Every finding starts `unknown`. Fill scope/assessor fields, follow each catalog source, inspect
relevant non-secret target files, and stage sanitized artifacts under `audits/example/evidence/`.
Keep originals under the evidence custodian's controls. The CLI only reads deliberately staged
copies; it does not collect them from the target.

Use relative paths such as `evidence/boundary-test.log`. Compute the digest after sanitization:

```bash
shasum -a 256 audits/example/evidence/boundary-test.log
```

Record `{path, sha256, kind}` in the finding. The tool checks bytes, not whether a test was
honestly executed. Include environment, inputs, expected/actual results, C5 and system-log
correlation, and limits in the artifact. Never stage credentials, environment dumps or private
production data. A test plan or test source is not an executed test.

Use `pass` for the precise question demonstrated, `fail` for a confirmed counterexample, and
`unknown` for missing evidence. Conditional `not_applicable` needs a rationale and evidence.

## Validate and report

```bash
python3 tools/croa/audit.py validate audits/example/audit.json
python3 tools/croa/audit.py report audits/example/audit.json > audits/example/report.md
python3 tools/croa/audit.py report audits/example/audit.json --format json
```

| Command | Exit | Meaning |
| --- | --- | --- |
| init / validate | 0 | Emitted template / valid structure and evidence references |
| report | 0 | Findings recorded for review; no conformance conclusion |
| report | 1 | At least one recorded failure |
| report | 2 | Unknown finding or missing scope/assessor metadata |
| validate / report | 3 | Invalid input, unsafe path, absent/changed evidence or resource limit |
| any | 2 | Argument usage error, distinguishable by usage text on stderr |

Audit packets and reports are git-ignored. The CLI writes stdout/stderr only. Review reports
before sharing them. It does not create an official signed C-32 or establish an assessed level.

## Calling from Factory

The canonical skill is [integrations/croa-audit/SKILL.md](../../integrations/croa-audit/SKILL.md).
A Factory agent can read it directly when requested. Set `AEION_CROA_ROOT` to the absolute path
of a reviewed, preferably commit-pinned checkout. The target receives no duplicate catalog or
runtime dependency.

For optional native discovery, place a reviewed copy of the `croa-audit` skill folder in the
target's `.claude/skills/` (Claude Code) or `.agents/skills/` (Codex), following its review process.
The installed entrypoint is a distributable copy; update it from this reviewed source rather than
editing it independently. No global installation or Factory modification happens automatically.

Example request: "Use the croa-audit skill from my AEION_CROA checkout to assess this repository
at its current revision, read-only. Put its evidence packet outside the target tree."

The skill uses the existing harness. It needs no separate model, provider key, MCP server,
scheduled loop or service. Subscription-token versus OpenRouter authentication stays with the
harness owner and is outside this audit kit.

## Return useful findings

State scope, upstream revision, independence basis, confirmed failures, unknowns, evidence and
the smallest fixes/tests needed. Distinguish observation, confirmed cause and hypothesis. Passing
documentation checks does not establish CROA enforcement. Remediation, deployment and provider
changes need their own actual authorization.
