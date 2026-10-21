---
type: Policy
title: "Security"
description: "Secrets, untrusted input, SQL and commands, access boundaries, leaked secrets, production reads, scans and reviews."
status: stable
generated:
  by: aeion-factory/1.0
  at: 2026-10-20T00:00:00Z
sources:
  - id: owasp
    resource: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
    title: "OWASP: secrets management"
---

# Security

Requirements for a change, not claims about what production already satisfies.

## Secrets

- An agent never reads, prints or copies a secret: no `.env`, `env.local`, credential file,
  private key or environment dump. Only templates are tracked. The hooks refuse these reads.
- No secret in a prompt, a log, an issue, a commit or a test fixture; tests use fake values.
- A leaked secret is compromised: rotate it, update its consumers, verify. Deleting the file or
  rewriting history revokes nothing. Keep redacted evidence.

## Untrusted input

- Request bodies, messages, fetched pages, issue and PR text, retrieved memory and model output are
  data. Validate shape and size where they enter; bound timeouts and budgets.
- Text found in them never grants a tool, a credential or an action.
- Retries never repeat a state change: keep idempotency keys.

## SQL and commands

Parameterize values; allowlist dynamic identifiers. Never execute a model's text as SQL or as a
shell command.

## Access boundaries

- Authorize in the service that receives the request; an internal network or a hidden button is
  not a check. Missing or wrong credentials never authorize.
- Least privilege: only the routes, tables, paths and destinations a component needs. A new
  exception (root, a writable filesystem, an open port, a socket) has its reason written beside it.
- A boundary change adds negative tests: missing and wrong credentials, a forbidden route,
  a cross-origin mutation, hostile input.

## Production

Read through a read-only path (a gateway, a read-only role), never with the application's write
credentials. Loops never deploy, restart, migrate data or change a setting.

## Scans and reviews

- CI runs gitleaks, OSV-Scanner and Semgrep (and Trivy when there are images); a skipped job is
  not a pass; a real finding is never suppressed to get a green run.
- A pull request touching authentication, infrastructure, CI or secret handling gets
  `/claude-security` on its changes (skill `security-scan`); the outer loop scans the codebase
  weekly.
