# Security policy

Security fixes go to the default branch; older releases are not maintained unless stated here.

## Reporting a vulnerability

Report it to the repository owner through an existing private channel. Use a private advisory
on GitHub when that feature is available. Never put exploit details, credentials, personal data or raw production
logs in an issue, a pull request or a commit. If a credential may have leaked, say so at once
without copying it: it is rotated, not just deleted.

## Audit evidence

Stage sanitized evidence deliberately. A valid packet or matching file digest does not establish
that its contents are true, complete or safe to publish. Audit artifacts are ignored by Git by
default; review them before sharing. The CLI is not a sandbox for the audited system.

## Where the rules are

- [Security policy](knowledge/policies/security.md): secrets, untrusted input, access boundaries,
  scans and reviews.
- [Engineering policy](knowledge/policies/engineering.md): how changes are made and reviewed.
