# Architect rules registry (source of truth)

Maintained by `/curate-rules` (agent `rule-curator`). **Only `Status: approved` rules are enforced.** Candidates live in `candidates.md`; non-generalizable comments are logged in `rejected.md`.
Compiled one-line versions are generated into `.github/instructions/learned-*.instructions.md`.

## Entry format
```
### ARC-001 - Short title
- Status: approved | deprecated
- Scope: <glob or layer, e.g. **/Services/**/*.cs>
- Rule: <one imperative sentence, <= 25 words>
- Why: <rationale in the architect's own reasoning>
- Check: <how a reviewer detects a violation from code>
- Severity: Blocker | Critical | Major | Minor | Info
- Defer-OK: Yes | Conditional | No - <condition>
- Principle: SRP | OCP | LSP | ISP | DIP | Simplicity | Style | Philosophy | Security | Performance | Testing | Domain
- Sonar: S#### | none
- Evidence: PR #123 (url), PR #131 (url)
- Confidence: High | Medium | Low
- Bad:  <short snippet>
- Good: <short snippet>
- Added: YYYY-MM-DD | Last-validated: YYYY-MM-DD
```

## Rules
<!-- Entries are appended below by the curator. Next ID: ARC-001 -->
