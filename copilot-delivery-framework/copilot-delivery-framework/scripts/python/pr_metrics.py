#!/usr/bin/env python3
"""Baseline review-cycle metrics from Export-PrComments.ps1 output (prs.jsonl, reviews.jsonl, pr_comments.jsonl).

  pr_metrics.py --dir reports/mining
Reports medians for review rounds (CHANGES_REQUESTED reviews), comments per PR and hours to merge.
Run before introducing the framework and monthly afterwards; compare like with like.
"""
import argparse
import json
import statistics as st
from datetime import datetime
from pathlib import Path


def jl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8-sig").splitlines() if l.strip()] if Path(p).exists() else []


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dir", required=True); a = ap.parse_args()
    d = Path(a.dir)
    prs = [p for p in jl(d / "prs.jsonl") if p.get("merged_at")]
    rv, cm = jl(d / "reviews.jsonl"), jl(d / "pr_comments.jsonl")
    rounds, comments, hours = [], [], []
    for p in prs:
        n = p["number"]
        rounds.append(sum(1 for r in rv if r.get("pr") == n and r.get("state") == "CHANGES_REQUESTED"))
        comments.append(sum(1 for c in cm if str(n) in (c.get("pull_request_url", "")).rsplit("/", 1)[-1:]))
        hours.append((ts(p["merged_at"]) - ts(p["created_at"])).total_seconds() / 3600)
    if not prs:
        print("no merged PRs found"); return
    f = lambda xs: "median %.1f | mean %.1f | p90 %.1f" % (st.median(xs), st.mean(xs), sorted(xs)[int(0.9 * (len(xs) - 1))])
    print("merged PRs: %d" % len(prs)); print("changes-requested rounds per PR: " + f(rounds))
    print("review comments per PR: " + f(comments)); print("hours open -> merged: " + f(hours))


if __name__ == "__main__":
    main()
