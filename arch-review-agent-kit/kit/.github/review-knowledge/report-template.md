# Code Review Report

| | |
|---|---|
| **Target** | {mode}: {PR #/branch/range/files} |
| **Base -> Head** | {base} -> {head} |
| **Reviewed** | {n} files, {changed lines} changed lines ({diff-only / full-file}) |
| **Date** | {YYYY-MM-DD HH:mm} |
| **Rules applied** | architect-rules ({n} approved), design-philosophy, language instructions, Sonar guidance |

## Scorecard
**Score: {NN}/100 - {Approve | Approve with comments | Request changes}**

| Blocker | Critical | Major | Minor | Info |
|---|---|---|---|---|
| {n} | {n} | {n} | {n} | {n} |

| Dimension | /10 |
|---|---|
| Correctness | |
| SOLID / OOP | |
| Simplicity | |
| Style & guideline conformance | |
| Design-philosophy fit | |
| Architect-rule compliance | |
| Sonar cleanliness | |
| Security / PHI | |
| Tests | |

**Can merge if unfixed items are accepted?** {Yes/No - list the "No" items that block}

## Top issues to fix first
1. {F-001 one line}
2. ...

## Findings
Ordered by file, then severity.

### `{path/to/File.cs}`

#### F-001 · {Severity} · {Category}
- **Location:** `{path}:{line-range}`
- **Rule / basis:** {ARC-0xx | Sonar S#### | SOLID-SRP | Simplicity | Style}
- **Confidence:** {High/Med/Low} · **Architect-likelihood:** {High/Med/Low}

**Code**
```csharp
{offending code with line numbers}
```

**Issue:** {what is wrong}

**Justification:** {why it matters here, tied to rule/principle/product}

**Suggested fix** (simplest option that matches existing style)
```csharp
{fixed code}
```

**Acceptable if not fixed?** {Yes | Conditional | No} - {reason / condition}

---

## Sonar pre-check
{Likely Sonar issues, rule keys, severity, and whether they would fail the quality gate}

## Positive observations
{Max 3 bullets: things done well that follow the rules}

## Not reviewed / limitations
{Skipped files (generated/binary), missing context, assumptions}

## Suggested follow-ups
{Ticket-worthy items for deferred findings; candidate new rules if a recurring pattern appeared}
