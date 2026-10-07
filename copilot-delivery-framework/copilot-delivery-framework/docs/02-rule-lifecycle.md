# 2. Rule lifecycle: from review comment to enforced guideline

1. **Export** (`Export-PrComments.ps1`): inline review comments, PRs and reviews for a period.
2. **Filter** (`extract_comments.py`): drops bots, approvals, very short comments; scores signal (directive wording, configured reviewer,
   author replied "fixed", line later changed, ```suggestion block). Question-only comments are down-weighted.
3. **Cluster** (`cluster_comments.py`): groups lexically similar comments; ranks by distinct PRs, acceptance and reviewer weight.
   *Limit:* wording-based. Two comments with different words but the same meaning may sit in different clusters; the curator merges them.
4. **Curate** (rule-curator agent): applies the generalisation test, drafts `guidelines/candidates/<ID>.md` with real evidence URLs, or records a rejection with a reason.
5. **Approve** (architect, via normal PR): reads the evidence, edits wording/severity, moves the file to `guidelines/rules/`, sets `status: active`, `approved_by`, `review_by`.
6. **Compile** (`Update-Rules.ps1`): lint, regenerate instruction blocks, run tests. CI re-checks this on every PR.
7. **Enforce**: Copilot (chat, agent mode, code review) reads the instructions; the reviewer agent cites rule IDs; static checks enforce what can be a regex.
8. **Measure and retire**: rules with high false-positive rates or no hits for two review periods are deprecated at `review_by`.

## Promoting a rule to a deterministic check
Only when a regex is reliable enough to produce few false positives: add a `Check` in `static_checks.py`, a unit test with good and bad samples in
`tests/test_static_checks.py`, and list the check id in the rule's `checks`. Start with `confidence: verify`; raise to `likely` after a clean trial period.

## Conflict handling
If reviewers disagree, no rule is created; the cluster goes to the architect as a decision. If a mined rule contradicts an ADR, the ADR wins until superseded.
