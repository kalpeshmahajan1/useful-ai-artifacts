"""Shared helpers. Standard library only (Python 3.8+)."""
import json
import os
import re
from pathlib import Path

LANG_BY_EXT = {
    ".cs": "csharp", ".ts": "typescript", ".js": "javascript", ".mjs": "javascript",
    ".sql": "sql", ".cpp": "cpp", ".cc": "cpp", ".c": "cpp", ".h": "cpp", ".hpp": "cpp",
    ".html": "html", ".cshtml": "razor", ".xml": "xml", ".json": "json",
    ".ps1": "powershell", ".py": "python",
}
TEST_RE = re.compile(
    r"(\.spec\.ts$|\.test\.(ts|js)$|Tests?\.cs$|(^|/)[^/]*\.?Tests?(\.[^/]*)?/|(^|/)__tests__/)", re.I)


def repo_root(start=None):
    p = Path(start or os.getcwd()).resolve()
    for d in [p] + list(p.parents):
        if (d / "framework.config.json").exists():
            return d
    return p


def load_config(root):
    with open(Path(root) / "framework.config.json", encoding="utf-8") as fh:
        return json.load(fh)


def glob_to_regex(glob):
    g = glob.replace("\\", "/")
    out, i = "", 0
    while i < len(g):
        c = g[i]
        if g.startswith("**/", i):
            out += "(?:.*/)?"; i += 3; continue
        if g.startswith("**", i):
            out += ".*"; i += 2; continue
        if c == "*":
            out += "[^/]*"
        elif c == "?":
            out += "[^/]"
        else:
            out += re.escape(c)
        i += 1
    return re.compile("^" + out + "$")


def match_any(path, globs):
    p = path.replace("\\", "/")
    return any(glob_to_regex(g).match(p) for g in globs)


def lang_of(path):
    return LANG_BY_EXT.get(Path(path).suffix.lower())


def is_test_path(path):
    return bool(TEST_RE.search(path.replace("\\", "/")))


def parse_front_matter(text):
    """Tiny parser for flat 'key: value' front matter. Lists: [a, b]. Returns (dict, body)."""
    text = text.lstrip("\ufeff")
    if not text.startswith("---"):
        return {}, text
    parts = text.split("\n---", 1)
    if len(parts) < 2:
        return {}, text
    head = parts[0][3:]
    body = parts[1].lstrip("\r\n")
    meta = {}
    for line in head.splitlines():
        if not line.strip() or line.strip().startswith("#") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        k, v = k.strip(), v.strip()
        if v.startswith("[") and v.endswith("]"):
            inner = v[1:-1].strip()
            meta[k] = [x.strip().strip("'\"") for x in inner.split(",") if x.strip()] if inner else []
        else:
            meta[k] = v.strip("'\"")
    return meta, body


def load_rules(root):
    """Return {rule_id: {meta..., 'body':..., 'path':...}} from guidelines/rules."""
    rules = {}
    rdir = Path(root) / "guidelines" / "rules"
    if not rdir.exists():
        return rules
    for f in sorted(rdir.glob("*.md")):
        meta, body = parse_front_matter(f.read_text(encoding="utf-8"))
        if meta.get("id"):
            meta["body"] = body
            meta["path"] = str(f)
            rules[meta["id"]] = meta
    return rules


def read_text(path):
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with open(path, encoding=enc) as fh:
                return fh.read()
        except UnicodeDecodeError:
            continue
    return ""
