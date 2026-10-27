# Current work

## Keep the Decisions API secret off command lines

- Owner decision: approved on 2026-10-27, HTTPS enforced; two pull requests, then merge.
- State: in progress on task/decisions-client-secret.
- Next: client.sh passes the bearer header on stdin and calls HTTPS only; docs updated.
- Blocker: none.
- Evidence: the bearer was a curl argument (visible to ps) and http:// URLs were accepted.
