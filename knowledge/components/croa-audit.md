---
type: Component
title: "CROA audit kit"
description: "A source-linked assessment catalog, bounded local evidence validator and report generator, with an optional Factory skill. No automatic conformance claim."
status: stable
license: CC-BY-4.0
sources:
  - id: cli
    resource: ../../tools/croa/audit.py
    title: "Packet validation and reporting"
  - id: tests
    resource: ../../tools/croa/tests/test_audit.py
    title: "Audit contract tests"
  - id: catalog
    resource: ../../catalog/checks.json
    title: "Adapted questions and pinned upstream revision"
  - id: skill
    resource: ../../integrations/croa-audit/SKILL.md
    title: "Callable workflow"
---

# CROA audit kit

Adapted from The CROA Project's v1.0.1 specification; see [credits](../../CREDITS.md).
The grouping, packet format, validation and reporting are Æion additions.

## Intent

Make an evidence-led CROA audit callable from Factory while keeping its catalog, code and
references in a separate repository. The calling auditor examines target code/configuration
and separately authorized runtime evidence. The CLI validates a recorded packet and staged
evidence; it does not scan or execute the target, enforce CROA, or certify a deployment.

## Data sources

| Source | What is read | Owner | Freshness |
| --- | --- | --- | --- |
| CROA source | Parts II, IV, V, VI; Appendix Q; errata and limitations | The CROA Project | Pinned v1.0.1 commit in catalog |
| Catalog | Nineteen grouped assessment questions with source sections | Æion, adapted with attribution | Current checkout |
| Audit packet | Scope, assessor, findings and evidence references | Assessor | Explicit audit period and target revision |
| Staged evidence | Bounded regular files under the packet's evidence/ directory | Evidence custodian | SHA-256 bound to each reference |
| Target | Selected non-secret code/configuration, read by calling auditor | Target owner | Named revision; dirty state stated separately |

## Inputs

`init --system NAME` emits an `aeion.croa.audit/v1` JSON packet to stdout:

- `schema_version`: exactly `aeion.croa.audit/v1`.
- `upstream`: the catalog's exact project, version and commit object.
- `scope`: `system`, nullable `revision`, `boundary`, `audit_period`, and `environment`
  (`evaluation` or `production`). The boundary names agents, systems, actions, exclusions and
  invariant version. An audit period is the actual observation period, not assumed live access.
- `assessor`: nullable `name` and `independence_basis`; `mode` is `self-assessment` or
  `independent-review`. An AI review of its own work remains a self-assessment.
- `checks`: exactly one record per catalog ID with `id`, `status`, `notes`, `evidence`.
- Finding status: `pass`, `fail`, `unknown`, or catalog-permitted `not_applicable`.
- Evidence: at most 20 `{path, sha256, kind}` references per check. Paths start with `evidence/`,
  are relative, and end in `.json`, `.jsonl`, `.md`, `.txt`, `.log` or `.csv`.
  Kinds: `code`, `configuration`, `executed_test`, `c5_log`, `system_log`, `assessment`.

Extra keys, duplicate JSON keys, non-finite numbers, missing/duplicate/unknown checks, control
characters and unsafe paths are invalid. Text fields are bounded to 4,000 characters. Packet
and evidence files are limited to 1 MiB each; unique evidence totals at most 16 MiB.

Unknown findings may have no evidence. Other statuses need notes and matching staged evidence.
Passing reference tests require executed-test artifacts and corroborating C5 extracts; passing
deployment assessment also needs configuration, network-test artifacts and governed-system logs.
Non-applicability requires a rationale and an assessment artifact and is allowed only for the
catalog's conditional tests. NT-008's composition cases cannot be skipped wholesale.

This is an Æion evidence index, not an official C-32, ECC or event schema. Applicability and
truth of evidence remain assessor judgments. Nineteen questions are not an exhaustive list of
every CROA normative requirement.

## Outputs

- `validate FILE`: JSON confirming structural and evidence-reference validity; exit 0 on success,
  3 on invalid input. Unknown findings are structurally valid.
- `report FILE [--format markdown|json]`: versioned source, scope, assessor, findings and evidence
  references. Exit 1 if any finding fails, otherwise 2 for unknowns or missing scope/assessor
  metadata, otherwise 0 (`recorded_for_review`). Argparse usage errors also exit 2 with usage text.
- Reports always contain `conformance_claim: false`, `conformance_level: null`. No score or level
  is inferred. A pass records the assessor's conclusion, not a property verified by the CLI.
- Commands write stdout/stderr only; output files are the caller's explicit redirection.

## Invariants

1. Unknown findings and incomplete scope cannot produce a completed record:
   `test_new_packet_is_incomplete`, `test_missing_scope_stays_incomplete`.
2. Pass counts never grant conformance: `test_complete_record_still_makes_no_claim`.
3. Failed findings dominate unknowns: `test_failure_outcome`.
4. Each catalog check occurs once: `test_missing_duplicate_and_extra_checks`.
5. Findings bind to bounded staged bytes: `test_hash_and_missing_evidence`,
   `test_evidence_limits`, `test_pass_requires_evidence_kinds`.
6. Evidence cannot escape via traversal, symlinks, hard links or special files:
   `test_forbidden_paths`, `test_symlinks_and_special_files`.
7. Ambiguous JSON, integer-conversion failures and unknown fields refuse without tracebacks:
   `test_invalid_json`, `test_integer_conversion_errors`, `test_unexpected_fields`.
8. Data cannot inject report markup: `test_markdown_escapes_data`.
9. Inputs are not modified: `test_cli_round_trip_is_read_only`.
10. Questions link to a pinned attributed source: `test_catalog_source_links`.

## Determinism

Parsing, file digest comparison, rendering and exit codes are deterministic. Hashes establish
correspondence to bytes, not authenticity, capture completeness, freshness or semantic correctness.
The calling auditor's conclusions remain advisory until an appropriate independent assessment
examines the deployment and full corroborating evidence.

No network, subprocess, target-code execution, credential lookup or model call exists in the
CLI. Evidence is deliberately staged and sanitized by the operator. Path checks are defense
in depth, not a secret-content scanner. Never point the tool at credentials.

## Acceptance checks

```bash
python3 -m unittest discover -s tools/croa/tests -v
tools/knowledge/knowledge-check
tools/knowledge/doc-links
tools/repo-health/repo-health
python3 tools/knowledge/tests/test_doc_links.py
python3 .claude/hooks/test_hooks.py
```

Exercise init/validate/report on a temporary packet: an unassessed report exits 2, and a finding
without required evidence exits 3. These test the kit, not CROA enforcement in a deployment.

## Out of scope

- Implementing CROA components, a sandbox, policy engine or runtime test harness.
- Automatically running target code, writing to the target or reading production.
- Certifying L4 or assessing L5, whose evidence criteria are incomplete in this version.
- Treating eight reference tests as exhaustive or a fresh AI reviewer as external certification.
- Changing Factory, Agentic OPS, upstream CROA or provider settings during an audit.
