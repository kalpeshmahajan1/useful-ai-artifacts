---
agent: agent
description: Turn exported PR review comments into candidate rules (run monthly or after a big release).
---
1. Run `pwsh scripts/powershell/Export-PrComments.ps1 -Since ${input:since:YYYY-MM-DD}` then
   `python scripts/python/extract_comments.py --in reports/mining/pr_comments.jsonl --out-dir reports/mining` and
   `python scripts/python/cluster_comments.py --in reports/mining/comments.filtered.jsonl --out-dir reports/mining`.
   (Skip steps whose output already exists and the user confirms it is current.)
2. Run the **rule-curator agent** procedure in `.github/agents/rule-curator.agent.md` on `reports/mining/clusters.md`.
3. Show the decision table. Remind the user that an architect must review `guidelines/candidates/` before promotion.
