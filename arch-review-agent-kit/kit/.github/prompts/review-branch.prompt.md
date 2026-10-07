---
description: Review a branch against its base (or diff between two branches)
agent: arch-code-reviewer
---
Review branch ${input:branch:branch name (blank = current)} against base ${input:base:base branch (blank = auto-detect develop/main/master)}.
Use Mode Branch (merge-base diff) unless I ask for a direct two-branch comparison (Mode BranchDiff). Run all passes, score, and write the report.
