---
type: Reference
title: "CROA v1.0.1 sources and reading notes"
description: "Pinned authorship, specification, licensing, evidence requirements, source drift and limitations used by the independent Æion audit kit."
status: stable
license: CC-BY-4.0
sources:
  - id: upstream
    resource: https://github.com/CROA-Project/CROA/tree/4d59192da9a0d00412c9d2ccb9e5ab68176803ff
    title: "Pinned v1.0.1 repository"
  - id: provenance
    resource: ../../catalog/upstream.json
    title: "Source hashes and reading inventory"
  - id: credits
    resource: ../../CREDITS.md
    title: "Attribution and adaptation notice"
---

# CROA v1.0.1: sources and reading notes

An Æion reading aid adapted from **The CROA Project**, not a replacement specification.
Authors credited upstream: **Yasmine Durand, Darrin Smith and Sylvain Durand**. Sources retrieved
on 2026-10-23; repository commit: `4d59192da9a0d00412c9d2ccb9e5ab68176803ff`.

## Cite the original work

The CROA Project. *CROA — Constrained Reachability Orchestration Architecture: A Framework for
Deterministic Governance of Agentic AI Execution.* Version 1.0.1. Original
[citation metadata](https://github.com/CROA-Project/CROA/blob/4d59192da9a0d00412c9d2ccb9e5ab68176803ff/CITATION.cff).

- Website: https://www.croaframework.org/
- GitHub: https://github.com/CROA-Project/CROA
- Requested tag: https://github.com/CROA-Project/CROA/tree/v1.0.1
- v1.0.1 deposit: https://doi.org/10.5281/zenodo.22310276
- Earlier v1.0 record: https://doi.org/10.5281/zenodo.21063423
- Reference demonstrator: https://github.com/CROA-Project/croa-reference-harness

The toolkit pins the repository content as well as naming the release. The tag includes later
repairs and text identifying itself as v1.0.1.1; it is not byte-identical to the September
deposit. The spec README still cites v1.0 while CITATION.cff cites v1.0.1. Record both facts
instead of silently mixing publication versions.

## Architecture used by the audit

An agent proposes an action. A deterministic control plane grounds and evaluates it, compiles
an Execution Change Contract (ECC), and mediates its redemption at the execution boundary.
The claim is conditional on the modeled action space, registered invariants and network-enforced
containment; it does not establish every permitted effect's safety or registry completeness.

| ID | Upstream role |
| --- | --- |
| C1 | Policy Authority |
| C2 | Execution Governor |
| C3 | Path Resolver / Federated Path Resolver |
| C4 | Invariant Monitor |
| C5 | Audit and Provenance Store |
| C6 | Execution Firewall |
| C7 | Contract Compiler |

These numbers identify roles, not pipeline order: C3 precedes C2 and C7 precedes C6. The source
is [Part II](https://github.com/CROA-Project/CROA/blob/4d59192da9a0d00412c9d2ccb9e5ab68176803ff/spec/parts/part-2-reference-architecture.md).

## Findings that change audit behavior

- **Scope and independence.** Part VI §§28–29 assesses a deployed system in a named boundary
  for an audit period. Source review or implementer statements alone cannot establish L4.
  A fresh AI reviewer does not by itself establish external assessor independence.
- **Real network boundary.** P4 needs tested network enforcement and governed-system access
  logs corroborating C5. A hook, policy document or mocked firewall is insufficient.
- **Seven deployment properties.** P1–P7 include audit durability/availability. P7's production
  requirements cannot be omitted because an older enumeration says six. Pilot limits are declared.
- **Admission versus completion.** `ECC_COMPILED` records compilation; `EXECUTION_AUTHORIZED`
  records C6 admission. Later completion, failure or effect records establish outcomes.
- **Durability before transition.** I6.1 permits deferred central replication under a bounded
  RTO after local durable commitment. It does not permit unrecorded execution.
- **Eight reference tests.** NT-001–NT-008 are reference cases. Part VI §29.3 adds threat-specific,
  ECC-integrity, concurrency and conditional AQL/delegation tests; Part V §27.3 sets the minimum
  negative test per threat class. Eight passes are not exhaustive.
- **Conditional reference tests.** Appendix Q states applicability only for NT-008 Part A
  (delegation), and its closing note lists the NT-005 and NT-006 properties as minimum evidence.
  This kit lets NT-005 be excluded when no invariant is evaluated by an E3 method (Part II §5.2),
  NT-006 when no invariant uses TP-W, TP-C or TP-X (Part VI §28.5.1), and NT-007 when no governed
  exception exists: an Æion interpretation. §28.5.1 is non-normative; normative §28.3 and the
  Part II trajectory-presence criterion require active trajectory analysis at L4, so a missing
  trajectory capability is a C4 finding even when NT-006 is excluded. TH-1 trajectory tests and
  same-`ecc.id` concurrent redemption (§29.3) stay unconditional.
- **I8 interpretation.** Authority attenuates along delegation; composition cannot launder
  authority. The union of authorized actions may still be jointly unsafe. Appendix Q's closing
  least-authorized-participant wording conflicts with the corrected I8 text; retain the caveat.
- **AQL and L5.** AQL is recommended at L4 and required at L5; absence at L4 requires the stated
  residual. L5's distinguishing evidence criteria remain insufficiently specified in this version.
- **Concurrency.** Replay prevention does not serialize distinct actions against a cumulative
  limit. Pinned Parts II §4.6.3 and VI §29.3 add that requirement/test; general commit-time
  authorization freshness remains a separate issue.
- **Harness limitations.** The reference harness is a demonstrator. Mock tests and its known
  defect record do not transfer enforcement guarantees to a real deployment.
- **Part III artifact identifiers.** Part III was already a short Policy-as-Code text in the
  deposit; its §7.3, §7.4 and Chapters 9–11, including the cited §10, were added after it (errata
  E-16). §10.1–§10.4 require the threat assessment, a structural rationale for a class judged not
  relevant, the negative tests in CI, a mitigation map and an accepted-residuals record, but name
  no RTM or C-identifier. Part VI §29.2 still cites "RTM (Part III)" and "C-22 (Part III §10.1;
  Part V)". RTM stays normative in Part IV §18.2 and Part VI §29.2/§29.4; C-22–C-25 and C-29 are
  named in Part V's conformance requirements, C-32 in Part VI. The catalog uses them as named there.

Sources: pinned Parts II, III, IV, V and VI, Appendix Q,
[errata](https://github.com/CROA-Project/CROA/blob/4d59192da9a0d00412c9d2ccb9e5ab68176803ff/spec/errata-v1.0.md),
[limitations](https://github.com/CROA-Project/CROA/blob/4d59192da9a0d00412c9d2ccb9e5ab68176803ff/docs/limitations.md)
and [harness defects](https://github.com/CROA-Project/CROA/blob/4d59192da9a0d00412c9d2ccb9e5ab68176803ff/spec/known-defects-harness.md).

## Source precedence and adaptations

The official website's public application content was retrieved after browser extraction failed.
It presents an earlier seven-test baseline and v1.0 DOI. Use it for orientation; use pinned Parts
and explicit errata for precise questions. Informative examples do not override normative Parts.
Record unresolved conflicts rather than silently creating an Æion normative interpretation.

CROA prose is CC BY 4.0; upstream code/machine-readable artifacts are Apache-2.0. This kit adapts
prose into grouped questions, notes and a skill under CC BY 4.0, and adds original MIT-licensed
Python tools. No upstream harness code or official JSON schema is bundled or executed. The
packet format is Æion's own evidence index. See [LICENSE](../../LICENSE) and [credits](../../CREDITS.md).

The questions simplify evidence collection. They do not alter CROA, define an official profile,
imply endorsement or provide certification.
