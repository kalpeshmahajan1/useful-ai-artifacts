---
agent: agent
description: Review uncommitted, staged, branch or PR changes against repository rules.
---
Run the **reviewer agent** procedure in `.github/agents/reviewer.agent.md`.
Scope: ${input:scope:staged | unstaged | working | branch | diff | pr}. If scope is `branch` or `diff` also ask for base (default `origin/main`); for `pr` ask for the number.
Finish by showing `reports/review.md`.
