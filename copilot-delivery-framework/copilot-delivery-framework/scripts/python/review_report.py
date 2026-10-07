#!/usr/bin/env python3
"""Validate an agent review JSON, verify code excerpts against the files, merge static findings,
compute the score deterministically and render Markdown.

  review_report.py --in reports/review.json [--static reports/static.json] [--out reports/review.md]

The model finds issues; this script decides what is verified, what the score is, and what the verdict is.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fwcommon import repo_root, load_config, read_text, lang_of  # noqa: E402

SEV = ["blocker", "major", "minor", "nit"]
CONF = {"certain", "likely", "verify"}
REQ = ["file", "line_start", "line_end", "code", "issue", "justification", "severity", "confidence", "fix", "acceptable_if_unfixed"]
FENCE = {"csharp": "csharp", "typescript": "typescript", "javascript": "javascript", "sql": "sql", "cpp": "cpp", "html": "html", "powershell": "powershell"}


def norm(s):
    return re.sub(r"\s+", "", s)


def verify(root, f):
    p = root / f["file"]
    if not p.exists():
        return "file not found: %s" % f["file"]
    lines = read_text(p).splitlines()
    s, e = int(f["line_start"]), int(f["line_end"])
    if s < 1 or e < s or s > len(lines):
        return "line range %s-%s outside file (%d lines)" % (s, e, len(lines))
    window = norm("".join(lines[max(0, s - 3):e + 2]))
    ex = [norm(l) for l in f["code"].splitlines() if l.strip()]
    if not ex:
        return "empty code excerpt"
    missing = [l for l in ex if l not in window]
    return ("excerpt not found near lines %d-%d" % (s, e)) if missing else None


def validate(f, i):
    errs = [("missing '%s'" % k) for k in REQ if k not in f or f[k] in (None, "")]
    if f.get("severity") not in SEV: errs.append("bad severity")
    if f.get("confidence") not in CONF: errs.append("bad confidence")
    au = f.get("acceptable_if_unfixed")
    if not (isinstance(au, dict) and au.get("value") in ("never", "debt", "yes") and au.get("reason")):
        errs.append("acceptable_if_unfixed needs {value: never|debt|yes, reason}")
    if not f.get("rule_id") and f.get("severity") in ("minor", "nit"):
        errs.append("minor/nit findings must cite a rule_id (no unmapped opinions)")
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True); ap.add_argument("--static")
    ap.add_argument("--out"); ap.add_argument("--json-out")
    a = ap.parse_args()
    root = repo_root(); cfg = load_config(root); sc = cfg["scoring"]
    data = json.loads(Path(a.inp).read_text(encoding="utf-8"))
    meta, raw = data.get("meta", {}), list(data.get("findings", []))
    if a.static and Path(a.static).exists():
        st = json.loads(Path(a.static).read_text(encoding="utf-8"))["findings"]
        seen = {(f["file"], f["line_start"], f.get("rule_id")) for f in raw}
        raw += [f for f in st if (f["file"], f["line_start"], f.get("rule_id")) not in seen]

    ok, rejected, unverified = [], [], []
    for i, f in enumerate(raw, 1):
        errs = validate(f, i)
        if errs:
            rejected.append((f, errs)); continue
        if f.get("source") != "static":
            why = verify(root, f)
            if why:
                unverified.append((f, why)); continue
        ok.append(f)
    ok.sort(key=lambda f: (SEV.index(f["severity"]), f["file"], int(f["line_start"])))
    for n, f in enumerate(ok, 1):
        f["id"] = "F-%03d" % n

    deduct = 0.0
    for f in ok:
        d = sc["deductions"][f["severity"]]
        deduct += d * (sc["verify_multiplier"] if f["confidence"] == "verify" else 1)
    score = max(0, round(100 - deduct))
    firm_blockers = [f for f in ok if f["severity"] == "blocker" and f["confidence"] in ("certain", "likely")]
    crit = [x for x in meta.get("critical_files", [])]
    if firm_blockers: verdict = "BLOCK - fix blockers before merge"
    elif score < sc["pass_score"] or any(f["severity"] == "major" and f["confidence"] != "verify" and f["acceptable_if_unfixed"]["value"] == "never" for f in ok): verdict = "REWORK - must-fix findings or score below %d" % sc["pass_score"]
    else: verdict = "PASS - advisory; human approval still required"
    must = [f for f in ok if f["acceptable_if_unfixed"]["value"] == "never"]
    can = [f for f in ok if f["acceptable_if_unfixed"]["value"] != "never"]

    L = ["# Code review report", "",
         "**Verdict:** %s  " % verdict, "**Score:** %d / 100 (computed by script, not by the model)  " % score,
         "**Findings:** %s" % ", ".join("%d %s" % (sum(1 for f in ok if f["severity"] == s), s) for s in SEV), ""]
    if crit:
        L += ["> **Human sign-off required** - critical-path files changed: " + ", ".join("`%s`" % c for c in crit), ""]
    L += ["**Scope:** %s | base `%s` | head `%s`" % (meta.get("mode", "?"), meta.get("base", "?"), meta.get("head", "?")),
          "**Reviewed files:** %s" % (", ".join("`%s`" % x for x in meta.get("reviewed_files", [])) or "none listed"),
          "**Not reviewed:** %s" % (", ".join("`%s`" % x for x in meta.get("not_reviewed", [])) or "none"),
          "**Tools run:** %s" % (", ".join("%s=%s" % (k, v) for k, v in meta.get("tools_run", {}).items()) or "none recorded"), "",
          "Must fix: %d | Can be deferred: %d | Unverified (excluded): %d | Rejected (malformed): %d" % (len(must), len(can), len(unverified), len(rejected)), ""]
    for sev in SEV:
        grp = [f for f in ok if f["severity"] == sev]
        if not grp: continue
        L += ["## %s (%d)" % (sev.capitalize(), len(grp)), ""]
        for f in grp:
            lang = FENCE.get(lang_of(f["file"]) or "", "")
            au = f["acceptable_if_unfixed"]
            L += ["### %s `%s:%s-%s` %s" % (f["id"], f["file"], f["line_start"], f["line_end"], "[%s]" % f.get("rule_id", "no-rule")),
                  "```%s" % lang, f["code"].rstrip(), "```",
                  "- **Issue:** %s" % f["issue"], "- **Why (rule / evidence):** %s" % f["justification"],
                  "- **Severity / confidence:** %s / %s%s" % (f["severity"], f["confidence"], " (human must confirm)" if f["confidence"] == "verify" else ""),
                  "- **Possible fix:** %s" % f["fix"],
                  "- **Acceptable if not fixed:** %s - %s" % ({"never": "No", "debt": "Yes, as tracked debt", "yes": "Yes"}[au["value"]], au["reason"]), ""]
    if unverified:
        L += ["## Unverified - location or excerpt does not match the file (do not act without checking)", ""]
        for f, why in unverified:
            L.append("- `%s:%s` %s - *%s*" % (f.get("file"), f.get("line_start"), f.get("issue"), why))
        L.append("")
    if rejected:
        L += ["## Rejected - malformed findings", ""] + ["- %s: %s" % (f.get("issue", "?"), "; ".join(e)) for f, e in rejected] + [""]
    out = "\n".join(L)
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True); Path(a.out).write_text(out, encoding="utf-8")
    if a.json_out:
        Path(a.json_out).write_text(json.dumps({"score": score, "verdict": verdict, "findings": ok}, indent=2), encoding="utf-8")
    print(out if not a.out else "review: score %d, %s -> %s" % (score, verdict, a.out))
    return 1 if firm_blockers else 0


if __name__ == "__main__":
    sys.exit(main())
