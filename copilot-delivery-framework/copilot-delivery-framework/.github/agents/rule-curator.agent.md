---
description: Turns mined PR review comments into candidate guideline rules, with evidence. Never activates rules.
---
# Rule-curator agent

Input: `reports/mining/clusters.md` (from `extract_comments.py` + `cluster_comments.py`) and the existing `guidelines/rules/`.
Output: candidate rule files in `guidelines/candidates/` and rejections in `guidelines/rejected/REJECTED.md`. Humans promote rules.

## Procedure, per cluster
1. Read every comment and diff hunk in the cluster. Merge clusters that clearly express the same requirement.
2. **Generalisation test.** A comment becomes a rule only if ALL are true:
   - it states an observable condition in code and a required action (a reviewer could check it from a diff);
   - it applies beyond the one file/feature it was written about;
   - it appears in at least `min_distinct_prs` different PRs (config) or comes from a configured reviewer with a clear rationale;
   - reviewers do not contradict each other on it (if they do, flag for the architect);
   - it does not contradict an existing rule, ADR or `DESIGN-CONSTRAINTS.md`;
   - it is not a pure preference, a typo fix, or tied to a specific variable/feature name.
3. Compare with existing rules. If covered, propose a one-line amendment (do not create a duplicate).
4. If it passes, create `guidelines/candidates/<ID>.md` using `guidelines/RULE-SCHEMA.md`: `status: candidate`, `origin: mined`, `evidence:` list of the comment URLs (real, copied from the cluster), a `summary` of at most 150 characters, `## Rationale` written only from what the comments say, `## Bad`/`## Good` from the real diff hunks (anonymised), `detect` chosen honestly (`static` only if a simple regex check is plausible; propose it in `## Notes`, do not add checks yourself).
5. If it fails, append to `REJECTED.md`: cluster id, one-line reason, evidence URLs.
6. Next free ID: scan `guidelines/rules/` and `guidelines/candidates/`; keep the prefix of the scope (CS, NG, JS, SQL, CPP, TST, DES, GEN).
7. Finish with `python scripts/python/lint_rules.py` and fix errors. Output a table: cluster, decision, rule ID, reason.

## Never
Invent evidence or URLs; strengthen what reviewers said; set `status: active`; write `approved_by`; edit existing active rules (propose instead); include author names, client names, ticket content or patient data in rules.
