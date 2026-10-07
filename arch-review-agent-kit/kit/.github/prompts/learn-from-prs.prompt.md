---
description: Learn architect review rules from historical PR comments (incremental)
agent: pr-review-miner
---
Mine the harvested PR review comments and propose rule candidates.

Scope/filters (optional): ${input:scope:e.g. "all new", "PRs 400-480", "only .cs files", "only architect=jdoe"}

If no harvest exists yet, show the exact command to create it:
`pwsh -File scripts/Get-PrReviewComments.ps1 -Reviewer <architect-login> -Limit 50`
Process only PRs not listed in `harvest/processed-prs.json` unless I say otherwise. Finish with the summary table and the list of questions for the architect.
