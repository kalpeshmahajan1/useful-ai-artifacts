#!/usr/bin/env python3
"""Validate guidelines/rules/*.md and guidelines/candidates/*.md. Exit 1 on errors."""
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fwcommon import repo_root, load_config, parse_front_matter, read_text  # noqa: E402
import static_checks as sc  # noqa: E402

SEV = {"blocker", "major", "minor", "nit"}
STATUS = {"candidate", "seed", "active", "deprecated"}
SCOPES = {"all", "csharp", "typescript", "javascript", "sql", "cpp", "tests", "design", "process"}
DETECT = {"static", "llm", "both", "manual"}
UNFIXED = {"never", "debt", "yes"}
REQ = ["id", "title", "status", "scope", "severity", "detect", "summary", "acceptable_if_unfixed", "origin", "evidence"]


def main():
    root = repo_root(); cfg = load_config(root)
    known_checks = {c.id for c in sc.build_checks(root, cfg)}
    errors, warns, seen = [], [], {}
    files = sorted((root / "guidelines" / "rules").glob("*.md")) + sorted((root / "guidelines" / "candidates").glob("*.md"))
    for f in files:
        meta, body = parse_front_matter(read_text(f)); rel = f.relative_to(root).as_posix()
        def err(m): errors.append("%s: %s" % (rel, m))
        def warn(m): warns.append("%s: %s" % (rel, m))
        for k in REQ:
            if k not in meta or meta[k] in ("", []):
                err("missing '%s'" % k)
        rid = meta.get("id", "")
        if rid and not re.fullmatch(r"[A-Z]{2,4}-\d{3}", rid): err("id must look like CS-001")
        if rid and f.stem != rid: err("file name must equal id")
        if rid in seen: err("duplicate id (also %s)" % seen[rid])
        seen[rid] = rel
        if meta.get("status") not in STATUS: err("status must be one of %s" % sorted(STATUS))
        if meta.get("severity") not in SEV: err("severity must be one of %s" % sorted(SEV))
        if meta.get("scope") not in SCOPES: err("scope must be one of %s" % sorted(SCOPES))
        if meta.get("detect") not in DETECT: err("detect must be one of %s" % sorted(DETECT))
        if meta.get("acceptable_if_unfixed") not in UNFIXED: err("acceptable_if_unfixed must be one of %s" % sorted(UNFIXED))
        if len(meta.get("summary", "")) > 150: err("summary longer than 150 chars (instruction budget)")
        if meta.get("severity") in ("blocker", "major") and meta.get("acceptable_if_unfixed") == "yes":
            err("blocker/major rules cannot be 'acceptable_if_unfixed: yes'")
        checks = meta.get("checks", []) if isinstance(meta.get("checks", []), list) else []
        if meta.get("detect") in ("static", "both") and rid not in ("DES-001",) and not checks:
            err("detect=%s requires 'checks'" % meta.get("detect"))
        for c in checks:
            if c not in known_checks: err("unknown check id '%s' (run static_checks.py --list-checks)" % c)
        st = meta.get("status")
        if st == "active":
            if not meta.get("approved_by"): err("active rule requires approved_by")
            for h in ("## Rationale", "## Bad", "## Good"):
                if h not in body and meta.get("origin") != "standard": err("active rule needs section '%s'" % h)
        if st == "candidate":
            if meta.get("origin") != "mined": warn("candidate with origin != mined")
            ev = meta.get("evidence", [])
            if not isinstance(ev, list) or len([e for e in ev if e.startswith("http")]) < cfg["mining"]["min_distinct_prs"]:
                warn("candidate has fewer than %d evidence URLs" % cfg["mining"]["min_distinct_prs"])
        if st == "seed":
            warn("seed rule not yet confirmed by an architect (set status: active + approved_by)")
        rb = meta.get("review_by")
        if rb:
            try:
                if date.fromisoformat(rb) < date.today(): warn("review_by date passed (%s)" % rb)
            except ValueError:
                err("review_by must be YYYY-MM-DD")
    for m in errors: print("ERROR  " + m)
    quiet = "--quiet" in sys.argv
    if not quiet:
        for m in warns: print("WARN   " + m)
    print("rules lint: %d file(s), %d error(s), %d warning(s)" % (len(files), len(errors), len(warns)))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
