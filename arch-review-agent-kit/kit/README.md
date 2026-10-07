# Architect Review Agent Kit (GitHub Copilot)

Learns your architect's review taste from historical PRs, then uses it to **generate** compliant code and to **review** code with a scored markdown report.

## Install
Copy `.github/`, `scripts/` and `.gitignore` entries into the repo root. Requirements: VS Code + GitHub Copilot Chat (agent mode, custom agents/prompt files/instruction files enabled), `git`, `gh` CLI (`gh auth login`), PowerShell 5.1+ or `pwsh`.
Tool names in `tools:` can differ by Copilot version; adjust in `.github/agents/*.agent.md` if VS Code flags one.

## Flow
```
PR history --Get-PrReviewComments.ps1 / workflow--> harvest/
   --/learn-from-prs (pr-review-miner)--> candidates.md (+ rejected.md for one-offs)
   --/curate-rules (rule-curator, architect approves)--> architect-rules.md + learned-*.instructions.md
learned-*.instructions.md ----> every Copilot chat/generation (auto, by file type)
/generate-code (arch-code-generator) ----> code + compliance note + self score
/review* (arch-code-reviewer) ----> report .md + .json
/calibrate-reviewer ----> recall/precision vs. architect's real comments ----> new candidates
```

## Day-1 steps
1. Fill the TODOs in `.github/review-knowledge/design-philosophy.md` (15 minutes with the architect pays off most).
2. `pwsh scripts/Export-SonarContext.ps1 -SonarUrl <url> -ProjectKey <key>` (needs `SONAR_TOKEN`).
3. `pwsh scripts/Get-PrReviewComments.ps1 -Reviewer <architect-login> -Limit 50`
4. Chat: `/learn-from-prs` then `/curate-rules` (architect approves in batches). Repeat weekly; it is incremental.
5. Chat: `/calibrate-reviewer` on the newest PRs; tune.

## Review inputs
| Want | Prompt | Collector mode |
|---|---|---|
| GitHub PR | `/review-pr 482` | `PR` |
| Staged files | `/review-staged` | `Staged` |
| Working `git diff` | `/review-diff` | `WorkingDiff` |
| Branch vs base | `/review-branch` | `Branch` (merge-base) |
| Branch A vs B | `/review` "branch A vs B" | `BranchDiff` |
| Commit / range | `/review` "commit abc" | `Commit` / `Range` |
| Single / many files | `/review-files a.cs b.cs` | `Files` |
| File listing paths | `/review-file-list files.txt` | `FileList` |
| Whole folder | `/review-files src/Services` | `Folder` |
Or just use `/review` and describe the target in words.

## Reports
`.github/review-knowledge/reports/review-<timestamp>.md` (+ `.json`): scorecard, per-finding file, code block, issue, justification, severity, fix, "acceptable if not fixed", Sonar pre-check. Scoring: `review-knowledge/severity-and-scoring.md`.

## Tuning
- Rule too noisy -> narrow its `Scope` or lower Severity in `architect-rules.md`, then re-run the curator to regenerate compiled lines.
- Reviewer misses something -> add a candidate (or let the calibrator propose it).
- Change score weights/thresholds in `severity-and-scoring.md`.

## Limits to know
- The reviewer predicts Sonar findings from rules; it does not run Sonar. Keep your real scan in CI.
- Copilot's built-in PR code review also reads `.github/copilot-instructions.md` and `*.instructions.md`, but only a limited amount of text, so keep learned rule lines short.
- Never commit PHI. Harvested snippets can contain code only; the miner strips identifiers, but skim `harvest/` before pushing.
