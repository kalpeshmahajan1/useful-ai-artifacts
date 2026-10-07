#!/usr/bin/env python3
"""Group similar filtered comments and rank them as rule candidates (lexical, not semantic).

Output: clusters.md (input for the rule-curator agent) + clusters.json
Singletons from configured reviewers are listed separately: one strong architect comment can still be a rule.
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fwcommon import repo_root, load_config  # noqa: E402

STOP = set("a an the and or but if then else of to in on for with without is are be been was were it this that these those as at by from can could should would will shall may might "
           "we you i they he she them our your their not no yes do does did done have has had here there so just also very more most any some into than too use used using please "
           "code method class file line change changes".split())


def tokens(text):
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"https?://\S+|`[^`]*`", " ", text)
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    out = set()
    for w in re.findall(r"[A-Za-z]{3,}", text.lower()):
        if len(w) > 4:
            w = re.sub(r"(ing|ed|es|s|n)$", "", w)
            w = re.sub(r"([^aeiou])\1$", r"\1", w)
        if w not in STOP:
            out.add(w)
    return out


def jac(a, b):
    return len(a & b) / len(a | b) if a and b else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True); ap.add_argument("--out-dir", required=True)
    a = ap.parse_args()
    root = repo_root(); cfg = load_config(root); mc = cfg["mining"]
    reviewers = {r.lower() for r in cfg["reviewer_logins"]}
    items = [json.loads(l) for l in Path(a.inp).read_text(encoding="utf-8").splitlines() if l.strip()]
    for it in items:
        it["tok"] = tokens(it["body"])
    items.sort(key=lambda x: -x["signal"])
    clusters = []
    for it in items:
        best, bs = None, 0.0
        for c in clusters:
            s = max(jac(it["tok"], c["rep"]), jac(it["tok"], c["core"]))
            if s > bs: best, bs = c, s
        if best is not None and bs >= mc["similarity"]:
            best["members"].append(it)
            cnt = Counter(t for m in best["members"] for t in m["tok"])
            best["core"] = {t for t, n in cnt.items() if n >= max(2, len(best["members"]) // 2)} or best["rep"]
        else:
            clusters.append({"rep": it["tok"], "core": set(it["tok"]), "members": [it]})
    out = []
    for i, c in enumerate(clusters, 1):
        m = c["members"]
        prs, authors = {x["pr"] for x in m}, {x["author"] for x in m}
        acc = sum(1 for x in m if x["accepted"]) / len(m)
        arch = sum(1 for x in m if (x["author"] or "").lower() in reviewers)
        out.append({"id": "C%03d" % i, "size": len(m), "distinct_prs": len(prs), "authors": sorted(a for a in authors if a),
                    "accepted_ratio": round(acc, 2), "reviewer_comments": arch,
                    "exts": dict(Counter(x["ext"] for x in m)), "categories": dict(Counter(cat for x in m for cat in x["categories"])),
                    "keywords": [t for t, _ in Counter(t for x in m for t in x["tok"]).most_common(8)],
                    "rank": len(prs) * 2 + round(acc * 3) + arch, "members": m})
    cands = sorted([c for c in out if c["distinct_prs"] >= mc["min_distinct_prs"]], key=lambda c: -c["rank"])
    singles = sorted([c for c in out if c["distinct_prs"] < mc["min_distinct_prs"] and c["reviewer_comments"] > 0], key=lambda c: -c["rank"])[:25]
    L = ["# Rule candidate clusters", "",
         "Lexical grouping only. Merge semantically equal clusters, and reject non-generalizable ones, in the curation step.",
         "Thresholds: >= %d distinct PRs. Clusters: %d, candidates: %d" % (mc["min_distinct_prs"], len(out), len(cands)), ""]
    def dump(c, n):
        L.append("## %s - %d comments / %d PRs / accepted %.0f%% / keywords: %s" % (c["id"], c["size"], c["distinct_prs"], c["accepted_ratio"] * 100, ", ".join(c["keywords"])))
        L.append("categories: %s | file types: %s | reviewers: %s" % (c["categories"], c["exts"], ", ".join(c["authors"])))
        for x in c["members"][:n]:
            L.extend(["", "- %s (%s, PR #%s)" % (x["url"], x["path"], x["pr"]), "  > " + x["body"][:400].replace("\n", "\n  > ")])
            if x["diff_hunk"]: L.extend(["  ```", "  " + x["diff_hunk"][-500:].replace("\n", "\n  "), "  ```"])
        L.append("")
    L.append("# Candidates (repeated across PRs)\n")
    for c in cands: dump(c, 5)
    L.append("# Single strong reviewer comments (read, may still be rules)\n")
    for c in singles: dump(c, 1)
    od = Path(a.out_dir); od.mkdir(parents=True, exist_ok=True)
    (od / "clusters.md").write_text("\n".join(L), encoding="utf-8")
    (od / "clusters.json").write_text(json.dumps([{k: v for k, v in c.items() if k != "members"} for c in out], indent=2), encoding="utf-8")
    print("clusters: %d, candidates: %d, reviewer singletons: %d -> %s" % (len(out), len(cands), len(singles), od / "clusters.md"))


if __name__ == "__main__":
    main()
