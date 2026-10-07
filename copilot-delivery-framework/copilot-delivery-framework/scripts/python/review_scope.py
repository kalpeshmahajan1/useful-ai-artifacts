#!/usr/bin/env python3
"""Build a review scope JSON (files + added line numbers) from git. Standard library only.

Modes: staged | unstaged | working | branch | diff | files | list-file | file | pr
Examples:
  review_scope.py --mode staged
  review_scope.py --mode branch --base origin/main
  review_scope.py --mode diff --base v1.0 --head HEAD
  review_scope.py --mode files --paths a.cs b.ts
  review_scope.py --mode list-file --list-file files.txt
  review_scope.py --mode pr --pr 123      (needs GitHub CLI 'gh', and the PR head checked out)
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fwcommon import repo_root, load_config, match_any, lang_of, is_test_path  # noqa: E402

HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def run(cmd, root, check=True):
    r = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode != 0:
        raise SystemExit("command failed: %s\n%s" % (" ".join(cmd), r.stderr.strip()))
    return r.stdout


def parse_unified_diff(text):
    """Return {path: [added line numbers]} from a unified diff (new-file line numbers)."""
    files, cur = {}, None
    for line in text.splitlines():
        if line.startswith("+++ "):
            p = line[4:].strip().strip('"')
            if p == "/dev/null":
                cur = None
            else:
                cur = p[2:] if p.startswith("b/") else p
                files.setdefault(cur, [])
            continue
        m = HUNK.match(line)
        if m and cur is not None:
            start = int(m.group(1))
            count = int(m.group(2)) if m.group(2) is not None else 1
            files[cur].extend(range(start, start + count))
    return files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True,
                    choices=["staged", "unstaged", "working", "branch", "diff", "files", "list-file", "file", "pr"])
    ap.add_argument("--base"); ap.add_argument("--head", default="HEAD")
    ap.add_argument("--paths", nargs="*"); ap.add_argument("--list-file"); ap.add_argument("--pr")
    ap.add_argument("--out", default=None, help="default: <reports_dir>/scope.json")
    a = ap.parse_args()

    root = repo_root(); cfg = load_config(root)
    warnings, base, head, files = [], a.base, a.head, {}
    g = ["git", "-c", "core.quotepath=off", "diff", "-U0", "--no-color", "--diff-filter=ACMR"]

    if a.mode == "staged":
        files = parse_unified_diff(run(g + ["--cached"], root))
    elif a.mode == "unstaged":
        files = parse_unified_diff(run(g, root))
    elif a.mode == "working":
        files = parse_unified_diff(run(g + ["HEAD"], root))
    elif a.mode == "branch":
        base = a.base or "origin/main"
        mb = run(["git", "merge-base", base, a.head], root).strip()
        files = parse_unified_diff(run(g + [mb, a.head], root)); base = mb
    elif a.mode == "diff":
        if not a.base:
            raise SystemExit("--base required for mode diff")
        files = parse_unified_diff(run(g + [a.base, a.head], root))
    elif a.mode == "pr":
        if not a.pr:
            raise SystemExit("--pr required for mode pr")
        out = run(["gh", "pr", "view", a.pr, "--json", "headRefOid,baseRefName"], root)
        info = json.loads(out)
        local = run(["git", "rev-parse", "HEAD"], root).strip()
        if local != info["headRefOid"]:
            warnings.append("Local HEAD (%s) is not the PR head (%s). Check out the PR branch first "
                            "(gh pr checkout %s) or code excerpts will not match." % (local[:8], info["headRefOid"][:8], a.pr))
        files = parse_unified_diff(run(["gh", "pr", "diff", a.pr], root))
        base, head = info["baseRefName"], info["headRefOid"]
    else:
        paths = []
        if a.mode == "file" or a.mode == "files":
            paths = a.paths or []
        elif a.mode == "list-file":
            paths = [l.strip() for l in Path(a.list_file).read_text(encoding="utf-8-sig").splitlines()
                     if l.strip() and not l.strip().startswith("#")]
        files = {p.replace("\\", "/"): None for p in paths}  # None = whole file

    out_files, skipped = [], []
    for path in sorted(files):
        norm = path.replace("\\", "/")
        if match_any(norm, cfg["excluded_globs"]):
            skipped.append({"path": norm, "reason": "excluded_globs"}); continue
        if not (root / norm).exists():
            skipped.append({"path": norm, "reason": "not found in working tree"}); continue
        added = files[path]
        out_files.append({
            "path": norm, "language": lang_of(norm), "is_test": is_test_path(norm),
            "critical": match_any(norm, cfg.get("critical_paths", [])),
            "added_lines": sorted(set(added)) if added is not None else None,
        })
    if not out_files:
        warnings.append("No reviewable files in scope.")
    scope = {"mode": a.mode, "base": base, "head": head,
             "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "files": out_files, "skipped": skipped, "warnings": warnings}
    out = Path(a.out) if a.out else root / cfg["paths"]["reports_dir"] / "scope.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(scope, indent=2), encoding="utf-8")
    print("scope: %d file(s), %d skipped -> %s" % (len(out_files), len(skipped), out))
    for w in warnings:
        print("WARNING: " + w, file=sys.stderr)


if __name__ == "__main__":
    main()
