# Æion CROA

**An independently usable, offline audit kit for the deterministic foundation.**

Use this module on an existing system without installing Factory, OPS, Observability or SpaceShip.
It prepares and validates evidence packets; it does not implement the controls it assesses.

Part of the modular [Æion SpaceShip framework](https://github.com/OualidGuennif/aeion-spaceship).
[Factory](https://github.com/OualidGuennif/aeion-factory) ·
[OPS](https://github.com/OualidGuennif/aeion-ops) ·
[CROA](https://github.com/OualidGuennif/aeion-croa) ·
[Observability](https://github.com/OualidGuennif/aeion-observability) ·
[SpaceShip](https://github.com/OualidGuennif/aeion-spaceship).
See the [module comparison and examples](https://github.com/OualidGuennif/aeion-spaceship/blob/main/docs/modules.md).

An independent, evidence-led audit kit for applying
[CROA — Constrained Reachability Orchestration Architecture](https://www.croaframework.org/).
Built on [Æion Factory](https://github.com/OualidGuennif/aeion-factory).

CROA is the work of **The CROA Project**, including **Yasmine Durand, Darrin Smith and
Sylvain Durand**. This kit adapts their work into audit questions, an evidence workflow and an
optional agent skill. It is not an official CROA product or certification.

## Start an audit

Python 3.9+ on Linux, macOS or WSL and the standard library are sufficient. The CLI reads a packet and staged
evidence; it never runs the audited repository or contacts a model/provider.

```bash
git clone https://github.com/OualidGuennif/aeion-croa.git
cd aeion-croa
mkdir -p audits/example/evidence
python3 tools/croa/audit.py init --system example > audits/example/audit.json
python3 tools/croa/audit.py validate audits/example/audit.json
python3 tools/croa/audit.py report audits/example/audit.json
```

The initial report exits **2** because nothing has been assessed. Follow the
[audit runbook](knowledge/operations/croa-audit.md) to record scope, findings and sanitized evidence.
Even a complete packet remains an assessment record; the CLI never awards a conformance level.

## Call it from Factory

Load [the croa-audit skill](integrations/croa-audit/SKILL.md) from a separately reviewed checkout.
[Integration instructions](knowledge/operations/croa-audit.md#calling-from-factory) cover Claude
Code and Codex discovery. Factory keeps its workflow; this repo owns the catalog, tools and
references. No service or installation into the target is required.

## References and checks

- [Audit contract](knowledge/components/croa-audit.md), [sources and reading notes](knowledge/references/croa-v1.0.1.md).
- [CROA v1.0.1](https://github.com/CROA-Project/CROA/tree/v1.0.1), pinned to
  `4d59192da9a0d00412c9d2ccb9e5ab68176803ff`; [white paper DOI](https://doi.org/10.5281/zenodo.22310276).
- [Credits and adaptations](CREDITS.md), [licensing by content](LICENSE).
- Run `python3 -m unittest discover -s tools/croa/tests -v` and the checks in [AGENTS.md](AGENTS.md).
