# 5. Rollout and metrics

## Phase 0 - Baseline (week 1-2)
Run `Export-PrComments.ps1` and `pr_metrics.py` on the last 3-6 months. Record: review rounds per PR, comments per PR, hours to merge.
Fill `design/DESIGN-CONSTRAINTS.md` sections 1-3 and `critical_paths`. Set `reviewer_logins`.

## Phase 1 - Standards (week 2-4)
Architects confirm or edit the seed rules (status `seed` -> `active`, `approved_by`). Delete rules that do not apply. Run `Update-Rules.ps1`.
Run the mining pipeline once; review candidates; promote the few that are clearly right.

## Phase 2 - Shadow mode (week 4-8)
Reviewer agent and Copilot code review are advisory. Authors run Preflight and the implementer/reviewer prompts. Track every finding as accepted / rejected
(a simple shared sheet: PR, rule id, accepted?, reason). Fix or retire rules with frequent false positives. Do not gate yet.

## Phase 3 - Gate what is certain (week 8+)
Enable `framework-gate` as required check. It only fails on certain/likely blocker/major deterministic findings, which have been validated in Phase 2.
Optionally enable the pre-commit hook.

## Phase 4 - Steady state
Monthly mining and curation (1-2 hours for an architect). Quarterly: review `review_by` dates, retire stale rules, re-measure.

## Metrics (compare to baseline)
| Metric | Source | Direction |
|---|---|---|
| Changes-requested rounds per PR | `pr_metrics.py` | down |
| Review comments per PR | `pr_metrics.py` | down (for repeat-type comments) |
| Repeat-comment rate (same rule cited again) | review reports / mining clusters | down |
| Hours open -> merged | `pr_metrics.py` | down |
| Agent finding acceptance rate | shadow-mode sheet | up (target > 70%; below 50% = fix the rule) |
| Escaped defects in critical paths | your defect tracker | down; any increase is investigated first |

Do not publish individual developer statistics from these numbers.
