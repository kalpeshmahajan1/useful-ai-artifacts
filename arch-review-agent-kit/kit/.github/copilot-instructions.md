# Repository-wide Copilot instructions

Product: healthcare imaging (DICOM) viewer. Stack: .NET Framework 4.8, **C# 7.3**, Angular 21 / TypeScript, JavaScript, XML, C++, JSON, SQL Server, hosted on IIS (Windows Server).

## Non-negotiables
1. **Match the existing code.** Before writing anything, open 2-3 sibling files in the same folder/layer and copy their naming, layering, DI, error handling, logging and formatting. `.editorconfig` and existing code beat generic best practice.
2. **Simplest thing that works.** Prefer plain, readable code. No new abstraction, pattern, library, base class, generic or framework feature unless the task cannot be done cleanly without it.
3. **Respect language limits.** C# 7.3 only (no nullable reference types, switch expressions, records, `using` declarations, ranges, async streams, `init`). .NET 4.8 APIs only.
4. **Apply the architect's learned rules** in `.github/instructions/learned-*.instructions.md` and the full registry in `.github/review-knowledge/architect-rules.md`. Cite rule IDs (e.g. `ARC-012`) when relevant.
5. **Follow the design philosophy** in `.github/review-knowledge/design-philosophy.md`.
6. **SOLID / OOP rigor** and **SonarQube cleanliness** (`.github/review-knowledge/sonar-guidance.md`): new code must not introduce Sonar issues.
7. **Healthcare safety:** never log PHI/DICOM patient attributes; never weaken validation, audit or access checks.
8. Do not refactor unrelated code. Keep diffs minimal and focused.

## Agents and prompts
- Generate code: agent `arch-code-generator` / prompt `/generate-code`
- Review code: agent `arch-code-reviewer` / prompts `/review`, `/review-pr`, `/review-staged`, `/review-branch`, `/review-diff`, `/review-files`, `/review-file-list`
- Learn from PR history: `/learn-from-prs`, then `/curate-rules`
- Measure reviewer quality offline: `/calibrate-reviewer`
