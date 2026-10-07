---
description: Universal review - describe the target in plain words (PR, branch, diff, staged, files, list file)
agent: arch-code-reviewer
---
Review target: ${input:target:e.g. "PR 482", "staged", "branch feature/x vs develop", "git diff", "src/A.cs src/B.cs", "list in files-to-review.txt"}

Choose the right collector mode, run the complete review procedure (all passes), score it, and write the markdown + JSON report.
