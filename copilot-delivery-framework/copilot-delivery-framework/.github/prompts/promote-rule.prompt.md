---
agent: agent
description: Architect-only helper - promote a candidate rule to active after review.
---
Rule to promote: ${input:rule:Candidate rule ID, e.g. CS-021}.
Only proceed if the user confirms they are an approving architect and gives their name for `approved_by`.
1. Show the candidate file and its evidence; ask for confirmation of summary, severity, scope, detect and `acceptable_if_unfixed`.
2. Move it to `guidelines/rules/`, set `status: active`, `approved_by`, `added` (today), `review_by` (+6 months).
3. Run `pwsh scripts/powershell/Update-Rules.ps1` and show its result. Do not commit; leave that to the user.
