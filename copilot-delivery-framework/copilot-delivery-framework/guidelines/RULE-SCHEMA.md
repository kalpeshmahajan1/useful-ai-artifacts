# Rule file schema

One rule per file: `guidelines/rules/<ID>.md` (active/seed/deprecated) or `guidelines/candidates/<ID>.md` (mined, unapproved).
Validated by `scripts/python/lint_rules.py`. Summaries are compiled into Copilot instruction files.

```
---
id: CS-021                     # PREFIX-NNN; prefix = scope family (GEN HC CS NG JS SQL CPP TST DES)
title: Short name
status: candidate              # candidate -> active -> deprecated   (seed = shipped starter rule, treated as active, must be confirmed)
scope: csharp                  # all csharp typescript javascript sql cpp tests design process
severity: major                # blocker | major | minor | nit
detect: llm                    # static | llm | both | manual
checks: []                     # static_checks.py check ids (required for static/both)
summary: One line, max 150 chars, imperative. This is what Copilot sees.
acceptable_if_unfixed: never   # never | debt | yes   (blocker/major can only be 'never' or 'debt')
origin: mined                  # mined | seed | standard | adr
evidence: [https://.../pull/1#discussion_r1, ...]   # real PR comment URLs; 'seed' for starter rules
approved_by:                   # architect name; REQUIRED when status: active
added: 2026-10-07
review_by: 2027-04-07          # rules are re-confirmed or retired by this date
---
## Rationale     (why; only what evidence supports)
## Bad           (minimal anonymised example)
## Good
## Notes         (exceptions, how to verify, detection ideas)
```

Severity guide
- **blocker**: wrong clinical behaviour, security/privacy hole, build/compile break, data loss. Must fix.
- **major**: defect risk or architecture violation likely to cause rework or incidents. Must fix unless architect waives.
- **minor**: maintainability/consistency issue. May be tracked as debt.
- **nit**: cosmetic. Never blocks.

Confidence guide: `certain` provable from shown code; `likely` strong signal; `verify` depends on something not visible (a human confirms before acting).
