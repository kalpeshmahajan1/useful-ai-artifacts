#!/usr/bin/env python3
"""Compile active/seed rule summaries into the GENERATED blocks of Copilot instruction files.

Blocks look like:  <!-- GENERATED:RULES scope=csharp --> ... <!-- /GENERATED -->
Files are checked against instruction_char_budget (Copilot code review reads only the first
~4,000 characters of an instruction file). Highest severity rules are written first.

  compile_instructions.py            rewrite blocks
  compile_instructions.py --check    exit 1 if blocks are stale or over budget (CI)
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fwcommon import repo_root, load_config, load_rules, read_text  # noqa: E402

BLOCK = re.compile(r"(<!-- GENERATED:RULES scope=([\w,]+) -->)(.*?)(<!-- /GENERATED -->)", re.S)
ORDER = {"blocker": 0, "major": 1, "minor": 2, "nit": 3}


def render(rules, scopes):
    sel = [r for r in rules.values() if r.get("status") in ("active", "seed") and r.get("scope") in scopes]
    sel.sort(key=lambda r: (ORDER[r["severity"]], r["id"]))
    return "\n" + "\n".join("- [%s] (%s) %s" % (r["id"], r["severity"], r["summary"]) for r in sel) + "\n"


def main():
    check = "--check" in sys.argv
    root = repo_root(); cfg = load_config(root); rules = load_rules(root)
    budget = cfg.get("instruction_char_budget", 3800)
    bad = 0
    files = [root / ".github" / "copilot-instructions.md"] + sorted((root / ".github" / "instructions").glob("*.instructions.md"))
    for f in files:
        if not f.exists():
            continue
        text = read_text(f)
        new = BLOCK.sub(lambda m: m.group(1) + render(rules, m.group(2).split(",")) + m.group(4), text)
        if len(new) > budget:
            print("OVER BUDGET %s: %d > %d chars. Shorten summaries, deprecate rules, or split scope." % (f.name, len(new), budget)); bad = 1
        if new != text:
            if check:
                print("STALE %s (run compile_instructions.py)" % f.name); bad = 1
            else:
                f.write_text(new, encoding="utf-8"); print("updated %s (%d chars)" % (f.name, len(new)))
        else:
            print("ok %s (%d chars)" % (f.name, len(new)))
    return bad


if __name__ == "__main__":
    sys.exit(main())
