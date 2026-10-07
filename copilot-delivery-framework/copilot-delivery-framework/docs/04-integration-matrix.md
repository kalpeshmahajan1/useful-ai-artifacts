# 4. Tool integration matrix

| Tool | Role | How it connects | Status/verification |
|---|---|---|---|
| **GitHub Copilot code review** (PR) | First-pass reviewer on every PR | Reads `.github/copilot-instructions.md` and `.github/instructions/*.instructions.md` (first ~4,000 chars of each). Enable automatic review via a repository ruleset or the PR Reviewers menu. | Instruction files documented by GitHub. Auto-review is a GitHub setting, not a repo file. |
| **Copilot Chat / agent mode in VS Code** | Implementation + local review | Same instruction files; `.github/prompts/*.prompt.md` run with `/name`; `.github/agents/*.agent.md` appear in the agent picker. Agent mode can run the PowerShell/Python scripts (terminal approval prompts apply). | Verified against current docs for VS Code. Front-matter keys occasionally change between versions (`agent:` vs `mode:` in prompt files). |
| **Visual Studio 2026** | Same, for .NET developers | Repository instructions (`copilot-instructions.md`, path-specific) are supported. Prompt files and custom agents depend on your VS build: **verify in your installation** (Copilot Chat -> check that the prompt/agent shows up). If not, open the file and paste/attach it, or run the PowerShell scripts from the Package Manager/Developer PowerShell terminal. | Not verified for your exact build. The framework does not depend on it: all enforcement is also available through scripts and CI. |
| **PowerShell** (`scripts/powershell`) | Windows entry points | `Get-ReviewScope`, `Invoke-Preflight` (MSBuild via vswhere, tests, npm), `Export-PrComments` (gh), `Update-Rules`, `Install-Hooks`. PowerShell 5.1 and 7. | Written to be PS 5.1 compatible; run once on a dev machine and adjust paths in `framework.config.json`. |
| **Python** (`scripts/python`) | Analysis and deterministic checks | Standard library only (3.8+), no installs, runs on Windows/Linux/CI. | Unit-tested (`tests/`). |
| **GitHub CLI (`gh`)** | PR data | Used by export and `--mode pr`. | Needs `gh auth login`. |
| **GitHub Actions** | Gate + monthly mining | `framework-gate.yml`, `mine-rules.yml`. | Gate runs deterministic checks only. |
| **Git hooks** | Fast local feedback | `.githooks/pre-commit` via `Install-Hooks.ps1`. | Opt-in per clone. |
| **SonarQube** (existing) | Authoritative static analysis | Not replaced. The reviewer must not duplicate Sonar findings; if you export Sonar issues for a PR you may drop the JSON into `reports/` and reference it in the review. | No integration code shipped (depends on your Sonar setup). |
| **MSBuild / VSTest / npm** | Build and tests | Called by `Invoke-Preflight.ps1` using your existing projects and `package.json` scripts. | Configure `paths.*`. Steps not run are reported as SKIPPED. |

## Which surface for which job
- Author, before pushing: implementer agent -> `Invoke-Preflight` -> reviewer agent on own change.
- PR: Copilot code review (instructions) + framework-gate (deterministic) + human review focused on what automation cannot judge.
- Architect, monthly: mining job -> rule-curator -> promote rules.
