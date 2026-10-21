---
name: loop-triage
description: Turns an outer-loop finding into one well-formed issue - deduplicated, labelled by severity and readiness, with evidence, the smallest fix and how to verify - so an inner run can pick it up. Use when an outer-loop job finds something.
---

# Loop triage

Protocol: `loops/issue-protocol.md`.

1. Search: `gh issue list --label loop:outer --search "<symptom>"`. Comment on an existing issue instead of duplicating it.
2. Write: title = the rule or symptom; body = where (path:line or the read that failed), the evidence, the smallest fix, how to verify. No secret, no exploit detail beyond the fix.
3. Label: `loop:outer`, `severity:<high|medium|low>`, and `agent-ready` only when the fix is clear, small and needs no human decision; otherwise `needs-owner`.
4. `gh issue create --title ... --body-file ... --label ...`.
