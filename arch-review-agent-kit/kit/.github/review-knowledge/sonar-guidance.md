# SonarQube guidance for review and generation

> Generic baseline. **Run `scripts/Export-SonarContext.ps1`** to replace the assumptions below with your real quality profile, quality gate and top recurring issues (written to `.github/review-knowledge/sonar/`). When those files exist they take precedence over this document.

## How the reviewer uses Sonar knowledge
- Predict which Sonar rules the changed code would trigger; cite the key (e.g. `S3776`). Do not claim a scan was run.
- New-code focus: Sonar quality gates usually fail on **new code** (new bugs/vulnerabilities/hotspots, coverage on new code, duplication on new code, maintainability rating). Weigh these when scoring.
- Sonar finding severity maps: Blocker/Critical -> Critical (or Blocker if security/PHI); Major -> Major; Minor/Info -> Minor.
- Unreviewed Security Hotspots in changed code -> flag as Major with "needs review" note.

## C# rules to check (verify against your profile)
| Key | Topic | Guidance |
|---|---|---|
| S3776 | Cognitive complexity | Keep methods simple; extract only to remove nesting, not to hide logic |
| S138 | Method too long | Split by responsibility |
| S107 | Too many parameters | Introduce a parameter object only if the codebase already does |
| S1172 / S1481 / S1854 | Unused param / local / dead store | Remove |
| S1144 | Unused private member | Remove |
| S125 | Commented-out code | Delete |
| S1135 | TODO tags | Acceptable only with ticket reference per team convention |
| S1066 / S3358 | Mergeable ifs / nested ternary | Simplify |
| S1192 | Duplicated string literals | Constant if reused 3+ times |
| S112 | Throwing generic exceptions | Throw specific types |
| S1696 | Catching NullReferenceException | Never |
| S2259 | Possible null dereference | Guard or restructure |
| S2930 / S3881 | IDisposable not disposed / bad dispose pattern | `using` blocks (C# 7.3 braces form) |
| S2068 | Hard-coded credentials | Blocker |
| S3649 / S2077 | SQL injection / formatted SQL | Parameterize always |
| S5131 / S5145 | XSS / log injection | Encode / sanitize |
| S4423 / S5542 | Weak TLS / weak crypto | Use platform defaults / strong algorithms |
| S1215 | GC.Collect | Do not call |
| S2325 | Method could be static | Only apply if consistent with codebase style |
| S1118 | Utility class public ctor | Static class or protected ctor |
| S101 / S100 | Naming | Follow existing convention first |

## TypeScript / JavaScript
S3776 (complexity), S1186 (empty function), S4325 (unnecessary assertion), S1128 (unused import), S1854 (dead store), S2589 (always-true/false condition), S6544 (misused promise), S3735 (`void` operator), S125 (commented code), S1192 (duplicated literal), S2814 (redeclaration), plus any Angular-specific rules enabled in the profile.

## SQL (T-SQL)
Parameterize; avoid `SELECT *`; avoid implicit conversions on indexed columns; avoid scalar UDFs in hot queries; set-based over cursor unless justified; explicit column lists on INSERT.

## C++
Sonar C/C++ rules: RAII for resources, no raw owning pointers, bounds checks, no unchecked casts, const-correctness; follow the project's existing C++ standard level.

## Generation rule
When generating code, avoid every pattern above by construction. If a Sonar rule conflicts with an existing codebase convention or an approved architect rule, the architect rule wins; mention the conflict in the compliance note.
