# Severity and scoring rubric

## Severity
| Severity | Meaning | Examples |
|---|---|---|
| **Blocker** | Must not merge. Data loss, PHI exposure, security hole, crash/deadlock in normal use, broken build. | PHI in logs, SQL injection, `.Result` deadlock in ASP.NET request path, wrong pixel/UID handling corrupting images |
| **Critical** | Very likely bug or serious violation of an approved architect rule / design principle. | Swallowed exception hiding failure, resource leak (undisposed stream), layer violation |
| **Major** | Real maintainability/correctness cost; architect would almost certainly request change. | SRP violation (god method), over-engineering, Sonar Major/Critical issue, missing tests for new logic |
| **Minor** | Worth fixing, low risk. | Naming, small duplication, dead code, style drift |
| **Info** | Suggestion/nit. Never blocks. | Optional readability tweak |

## Score (0-100)
Start at 100 and deduct per finding (confidence **Low** counts half):

| Severity | Deduction |
|---|---|
| Blocker | -20 |
| Critical | -10 |
| Major | -5 |
| Minor | -2 |
| Info | 0 |

Caps: any Blocker -> max 59. Any Critical -> max 79. For diffs > 400 changed lines, total deduction from Minor+Info is capped at 20. Floor is 0.

## Verdict
- **Approve**: score >= 90 and no Major+
- **Approve with comments**: 75-89, no Blocker/Critical
- **Request changes**: < 75, or any Blocker/Critical

## Dimension scores (0-10 each, reported beside the total)
Correctness · SOLID/OOP · Simplicity · Style & guideline conformance · Design-philosophy fit · Architect-rule compliance · Sonar cleanliness · Security/PHI · Tests

## "Acceptable if not fixed"
Every finding carries one of:
- **Yes** - safe to defer/ignore; state why (e.g. pre-existing, cosmetic, no behavior impact).
- **Conditional** - acceptable only if a stated condition holds (e.g. "if tracked in a follow-up ticket", "if this path is never called with >1 series").
- **No** - must fix before merge.
Defaults: Blocker/Critical = No. Architect rule with `Defer-OK` uses that value. Major defaults to Conditional. Minor/Info default to Yes.

## Architect-likelihood
For each finding: High / Medium / Low = how likely the architect would raise it in a real review (rule-backed + recurring = High). Used by the calibrator.

## Coding score (generated code)
The generator self-checks with the same rubric. Delivery target: **score >= 90, zero Major+**. Anything lower must be fixed before presenting, or explicitly listed as a known deviation.
