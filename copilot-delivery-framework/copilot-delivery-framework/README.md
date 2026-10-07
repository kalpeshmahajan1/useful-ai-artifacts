# Copilot Delivery Framework - rule-grounded review and code generation

A small, testable system for GitHub Copilot, Visual Studio / VS Code, PowerShell and Python that
1. **learns** standards from your historical PR review comments (with human approval),
2. **steers** code generation and Copilot code review with those standards,
3. **verifies** changes with deterministic checks and an evidence-checked review report,
4. **measures** whether review cycles actually go down.

Generalised: contains no client, product-internal or patient information. Assumed stack: ASP.NET on **.NET Framework 4.8 / C# 7.3**
(your request said "5.8" - treated as 4.8; if wrong, change `framework.config.json`, `CS-001`, and the `csharp73.*` checks), Angular 21, prototype-style JavaScript, SQL Server, C++.

## Install (15 minutes)
1. Copy the contents of this folder into the **root of your repository** (keep `.github/`, `design/`, `guidelines/`, `scripts/`, `tests/`, `framework.config.json`).
   If your repo already has `.github/copilot-instructions.md`, merge by hand and keep the `<!-- GENERATED -->` block.
2. Requirements: Python 3.8+ (no packages), Git, PowerShell 5.1+ (Windows) or 7, GitHub CLI `gh` (only for PR export / `-Mode pr`).
3. Edit `framework.config.json`: `reviewer_logins` (architects), `critical_paths`, `paths.solution`, `paths.frontend_dir`.
4. Run `scripts\powershell\Update-Rules.ps1` (lint + compile + self-tests) and commit.
5. Architects: complete `design/DESIGN-CONSTRAINTS.md` (every `<<FILL>>`), review the 35 **seed** rules in `guidelines/rules/`
   (set `status: active` + `approved_by`, or delete what does not apply), enable what you need in `design/forbidden-patterns.json`.
6. Optional: `scripts\powershell\Install-Hooks.ps1`; make `framework-gate` a required check; enable automatic Copilot code review (GitHub repo ruleset).

## Daily use
| I want to... | Do this |
|---|---|
| Implement a task | Copilot Chat, agent mode: `/implement-task` (or pick the *implementer* agent) |
| Review my changes before pushing | `/review-changes` (staged, unstaged, working, branch, diff, PR) |
| Review specific files / a list of files | `/review-files` |
| Check an idea against the architecture | `/check-design` |
| Local gate | `.\scripts\powershell\Invoke-Preflight.ps1 -Mode working -Build -Test -Frontend` |
| Learn new rules from PR history (monthly) | `/mine-review-comments`, then architect reviews `guidelines/candidates/` |
| Promote a rule | `/promote-rule` or edit the file; then `Update-Rules.ps1` |

Output: `reports/review.md` (verdict, score, per finding: file, code block, issue, justification, severity, confidence, fix, acceptable-if-not-fixed).

## Layout
```
.github/copilot-instructions.md      always-on instructions (< 3,800 chars; rules block is generated)
.github/instructions/*.md            per-language instructions (applyTo globs)
.github/agents/                      reviewer, implementer, design-guardian, rule-curator
.github/prompts/                     slash-command entry points
.github/workflows/                   framework-gate (PR), mine-rules (monthly)
design/                              DESIGN-CONSTRAINTS.md (fill in), forbidden-patterns.json, decisions/ (ADRs)
guidelines/rules|candidates|rejected rule files, schema (RULE-SCHEMA.md)
scripts/python/                      scope, static checks, lint, compile, report, mining, metrics (stdlib only)
scripts/powershell/                  Windows entry points
tests/                               unit tests for the deterministic checks
docs/                                01 overview .. 06 limits and safeguards
```

## Read first
`docs/06-limits-and-safeguards.md`. AI output here is advisory. A human architect approves rules, merges and any change in critical paths.
