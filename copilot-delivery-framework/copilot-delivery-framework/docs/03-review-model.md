# 3. Review model: findings, severity, score, verdict

## Finding (reports/review.json)
```json
{
  "meta": {
    "mode": "branch", "base": "origin/main", "head": "HEAD",
    "reviewed_files": ["src/A.cs"], "not_reviewed": [{"path": "src/Big.cs", "reason": "generated"}],
    "critical_files": ["src/Rendering/Window.cs"],
    "tools_run": {"static_checks": true, "build": false, "tests": false}
  },
  "findings": [{
    "rule_id": "CS-005",
    "file": "src/A.cs", "line_start": 42, "line_end": 44,
    "code": "exact code copied from the file",
    "issue": "what is wrong, one sentence",
    "justification": "why it matters here; cite the rule or the demonstrable defect",
    "severity": "major",
    "confidence": "certain",
    "fix": "smallest change that resolves it",
    "acceptable_if_unfixed": { "value": "never", "reason": "hides failures in a clinical path" }
  }]
}
```
`rule_id` may be null only for `blocker`/`major` defects with a demonstrated mechanism. Minor/nit without a rule is rejected by the script.

## Verification
`review_report.py` checks that each LLM finding's `code` appears in the file within a few lines of the cited range. Findings that fail are listed as **Unverified**
and excluded from the score. This is the main defence against hallucinated findings. (The branch/PR must be checked out locally.)

## Score (deterministic)
`score = max(0, 100 - sum(deductions))` with blocker 25, major 10, minor 3, nit 1; findings with confidence `verify` count 50%. Values live in `framework.config.json`.

## Verdict
- **BLOCK**: any certain/likely blocker.
- **REWORK**: score below `pass_score` (80) or any certain/likely major that is "never acceptable".
- **PASS (advisory)**: otherwise. A human approval is always required; critical-path files add an explicit sign-off banner.

## Acceptable if not fixed
Defaults come from the rule (`never` for blocker/major). The reviewer may only override with a reason in the finding.
`debt` = can merge if tracked as a work item; `yes` = purely optional.
