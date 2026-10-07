---
agent: agent
description: Review specific files (list them, or point to a file that contains a list).
---
Run the **reviewer agent** procedure in `.github/agents/reviewer.agent.md` with scope `files` for: ${input:files:paths separated by spaces, or a text file containing one path per line}.
Whole files are in scope (no diff). Say in the report meta that this is a whole-file review.
