# 1. Overview: a small system of agents with deterministic anchors

**Principle:** use AI only where judgement is needed, and surround it with deterministic checks that can be tested.
Nothing here is "autonomous": every rule enters the system through human architect approval, and every AI finding is
verified against the actual file before it is counted.

```
 PR review comments ──► Export (gh) ──► extract + cluster (scripts) ──► rule-curator agent ──► candidate rules
                                                                                                   │ architect review (PR)
                                                                                                   ▼
 guidelines/rules/*.md (active) ──► lint_rules.py ──► compile_instructions.py ──► .github/copilot-instructions.md
        │                                                                          .github/instructions/*.instructions.md
        │                                                                                   │ (Copilot chat, agent mode, code review read these)
        ▼                                                                                   ▼
 static_checks.py (regex facts) ◄── review_scope.py (git → files + changed lines)      implementer agent  ──► code
        │                                                                                   │ self-review
        ▼                                                                                   ▼
 reviewer agent (LLM judgement, rule-cited) ──► review.json ──► review_report.py ──► review.md (verified, scored, verdict)
        ▲
 design-guardian agent ◄── design/DESIGN-CONSTRAINTS.md + ADRs
```

## Components
| Part | Type | Job |
|---|---|---|
| `guidelines/rules/` | data | The single source of truth for standards. One rule per file, with severity, evidence and approval. |
| `compile_instructions.py` | script | Writes rule summaries into Copilot instruction files within the 4,000-character review budget. |
| `static_checks.py` | script | Deterministic checks: C# 7.3 ceiling, async/exception pitfalls, SQL concatenation, JS prototype pitfalls, unsafe C calls, secrets (heuristic), plus project patterns. Tested. |
| `review_scope.py` | script | Turns staged / branch / diff / files / list / PR into exact files and changed line numbers. |
| reviewer agent | Copilot agent | Finds rule violations and defects in changed code. Must cite rules and quote code. |
| `review_report.py` | script | Validates findings, verifies excerpts against files, merges static findings, computes score and verdict. |
| implementer agent | Copilot agent | Writes the smallest compliant change, runs preflight, self-reviews. |
| design-guardian agent | Copilot agent | Checks fit with `DESIGN-CONSTRAINTS.md`; "cannot determine" is an allowed answer. |
| rule-curator agent | Copilot agent | Converts clustered review comments into candidate rules with evidence; cannot activate rules. |
| PowerShell | scripts | Windows-friendly entry points: scope, preflight (MSBuild via vswhere, tests, npm), export, rule update, hooks. |
| GitHub Actions | CI | Deterministic gate on PRs; monthly mining job. |

## What is deliberately NOT here
No auto-merge, no auto-fix commits, no model fine-tuning, no vector database, no AI-generated score, no agent that
changes rules unsupervised. Each would add risk without being needed to reduce review cycles.
