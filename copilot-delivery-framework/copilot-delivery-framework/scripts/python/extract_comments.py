#!/usr/bin/env python3
"""Filter exported PR review comments down to rule-worthy signal.

Input : JSON-lines from Export-PrComments.ps1 (GitHub 'pulls/comments' objects)
Output: comments.filtered.jsonl + extract_summary.md
Heuristic signals only: the Copilot rule-curator agent and a human architect make the final call.
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fwcommon import repo_root, load_config  # noqa: E402

APPROVAL = re.compile(r"^\W*(lgtm|looks good|approved?|thanks?|thank you|ok|okay|\+1|nice|great|done|fixed)\W*$", re.I)
DIRECTIVE = re.compile(r"\b(should|must|need to|needs to|don'?t|do not|avoid|prefer|instead|use|never|always|move|extract|rename|remove|replace|violates?|consider|why not|please)\b", re.I)
CATEGORIES = [
    ("async-threading", r"\b(async|await|deadlock|thread|lock|race|concurren|task)\b"),
    ("error-handling", r"\b(exception|catch|throw|error|null|fail)\b"),
    ("security", r"\b(inject|xss|sanitiz|secret|password|auth|permission|csrf|escape)\b"),
    ("data-access", r"\b(sql|query|transaction|stored proc|index|repository|entity)\b"),
    ("design-solid", r"\b(solid|single responsibility|interface|abstraction|coupling|layer|dependency|inject|responsibilit)\w*"),
    ("testing", r"\b(test|mock|assert|coverage|fixture)\b"),
    ("performance", r"\b(performance|allocation|memory|leak|dispose|loop|cache|slow)\b"),
    ("naming-style", r"\b(name|naming|rename|format|style|comment|typo|spelling)\b"),
    ("frontend", r"\b(angular|component|subscribe|observable|template|rxjs|typescript)\b"),
]


def pr_number(c):
    m = re.search(r"/pulls/(\d+)", c.get("pull_request_url", "") or c.get("html_url", ""))
    return int(m.group(1)) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True); ap.add_argument("--out-dir", required=True)
    a = ap.parse_args()
    root = repo_root(); cfg = load_config(root); mc = cfg["mining"]
    bots = {b.lower() for b in cfg["bot_logins"]}; reviewers = {r.lower() for r in cfg["reviewer_logins"]}
    comments = [json.loads(l) for l in Path(a.inp).read_text(encoding="utf-8-sig").splitlines() if l.strip()]
    replies = {}
    for c in comments:
        if c.get("in_reply_to_id"):
            replies.setdefault(c["in_reply_to_id"], []).append(c)
    kept, dropped = [], Counter()
    for c in comments:
        if c.get("in_reply_to_id"):
            continue
        user = ((c.get("user") or {}).get("login") or "").lower()
        body = (c.get("body") or "").strip()
        if user in bots or user.endswith("[bot]"): dropped["bot"] += 1; continue
        if len(body.split()) < mc["min_words"]: dropped["too short"] += 1; continue
        if APPROVAL.match(body): dropped["approval only"] += 1; continue
        rs = replies.get(c["id"], [])
        accepted = any(any(m in (r.get("body") or "").lower() for m in mc["accepted_markers"])
                       and ((r.get("user") or {}).get("login", "").lower() != user) for r in rs)
        directive = bool(DIRECTIVE.search(body))
        question_only = body.rstrip().endswith("?") and not directive
        is_reviewer = (user in reviewers) if reviewers else True
        sig = (2 if directive else 0) + (2 if (reviewers and is_reviewer) else 0) + (1 if accepted else 0) \
            + (1 if c.get("position") is None else 0) + (1 if "```suggestion" in body else 0) - (2 if question_only else 0)
        if sig < mc["min_signal_score"]: dropped["low signal"] += 1; continue
        cats = [n for n, rx in CATEGORIES if re.search(rx, body, re.I)] or ["other"]
        kept.append({"id": c["id"], "pr": pr_number(c), "author": (c.get("user") or {}).get("login"), "path": c.get("path"),
                     "ext": Path(c.get("path") or "").suffix.lower(), "url": c.get("html_url"), "created_at": c.get("created_at"),
                     "body": body, "diff_hunk": "\n".join((c.get("diff_hunk") or "").splitlines()[-8:]),
                     "accepted": accepted, "outdated": c.get("position") is None, "directive": directive,
                     "categories": cats, "signal": sig})
    out = Path(a.out_dir); out.mkdir(parents=True, exist_ok=True)
    (out / "comments.filtered.jsonl").write_text("\n".join(json.dumps(k) for k in kept), encoding="utf-8")
    cat = Counter(c for k in kept for c in k["categories"])
    summ = ["# Extraction summary", "", "Input comments: %d | kept: %d" % (len(comments), len(kept)), "",
            "Dropped: " + ", ".join("%s=%d" % kv for kv in dropped.most_common()), "",
            "Kept by category (heuristic keywords): " + ", ".join("%s=%d" % kv for kv in cat.most_common()), "",
            "Distinct PRs: %d | Distinct authors: %d" % (len({k["pr"] for k in kept}), len({k["author"] for k in kept}))]
    (out / "extract_summary.md").write_text("\n".join(summ), encoding="utf-8")
    print("\n".join(summ))


if __name__ == "__main__":
    main()
