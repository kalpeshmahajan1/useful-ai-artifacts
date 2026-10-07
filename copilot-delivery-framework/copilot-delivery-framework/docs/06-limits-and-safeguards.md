# 6. Limits and safeguards (read before relying on any output)

## What the AI can and cannot do
- LLM review can miss defects and can produce plausible but wrong findings. The framework reduces this (evidence quotes verified against files, rule citation required,
  deterministic checks, human approval) but cannot eliminate it.
- LLMs do not reliably know which .NET Framework 4.8 APIs exist. The reviewer must check `csproj`/`packages.config`; unsure => `confidence: verify`.
- Instruction files are guidance, not enforcement. Only the scripts/CI enforce.
- Model behaviour changes with model versions. Re-run the shadow-mode check after Copilot model changes.

## Safeguards built in
1. Humans approve rules, merges and critical-path changes. AI never merges, never activates rules.
2. Findings need a rule or a demonstrable defect, exact code, and pass the excerpt check.
3. Score and verdict are computed by a script from configuration.
4. `verify`-confidence findings never block automatically.
5. Skipped steps are reported as SKIPPED, never as passed.
6. Critical paths are flagged mechanically from file globs.

## Healthcare-specific cautions
- Never paste patient data, real DICOM files, screenshots of real studies, or production logs into prompts, rules, tests or reports. Use synthetic data.
- Review reports and mined comments can contain internal information; keep `reports/` out of git (default) and treat artifacts as internal (14-day retention).
- AI-assisted changes are subject to the same quality-management, traceability and change-control process as other changes. Check with your quality/regulatory
  function how AI-assisted development must be documented in your quality system.
- A passing review score is not evidence of clinical safety.

## Known technical limits
- `static_checks.py` is regex-based: it ignores comments/strings but is not a parser. Hence `confidence` levels. Roslyn analyzers/StyleCop/ESLint/SonarQube remain the right tools for deep analysis; keep them.
- Clustering is lexical. Multi-language comments, screenshots, and long discussions are not understood.
- Copilot code review reads about the first 4,000 characters of each instruction file; the compiler enforces a 3,800 budget.
- `--mode pr` requires the PR head to be checked out so excerpts can be verified.
- Prompt/agent file support differs by IDE and version (see integration matrix).
