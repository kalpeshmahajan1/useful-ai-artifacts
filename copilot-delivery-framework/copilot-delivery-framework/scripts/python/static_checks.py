#!/usr/bin/env python3
"""Deterministic checks. No AI, no network, standard library only.

Every check is a regex over code (comments/strings blanked) or raw text. Checks carry a
confidence: certain | likely | verify. 'verify' findings never fail a gate; a human confirms them.

Usage:
  static_checks.py --scope reports/scope.json [--out reports/static.json] [--format text|github|json]
  static_checks.py --paths a.cs b.ts
  static_checks.py --list-checks
Exit code: 1 if any blocker/major finding with confidence certain|likely (the gate), else 0.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fwcommon import (repo_root, load_config, load_rules, lang_of, is_test_path,  # noqa: E402
                      match_any, read_text)

SQL_KW = r"(?:SELECT\s+.+?\s+FROM|INSERT\s+INTO|UPDATE\s+\S+\s+SET|DELETE\s+FROM)"


def strip_c_like(text, lang):
    """Blank comments and string/char literal contents, preserving offsets and newlines."""
    out, i, n = [], 0, len(text)
    verbatim = lang == "csharp"
    while i < n:
        c, nx = text[i], text[i + 1] if i + 1 < n else ""
        if c == "/" and nx == "/":
            j = text.find("\n", i); j = n if j < 0 else j
            out.append(" " * (j - i)); i = j
        elif c == "/" and nx == "*":
            j = text.find("*/", i + 2); j = n if j < 0 else j + 2
            out.append("".join(ch if ch == "\n" else " " for ch in text[i:j])); i = j
        elif c in "\"'`" and not (c == "`" and lang not in ("javascript", "typescript")):
            is_verb = verbatim and c == '"' and i > 0 and text[i - 1] == "@" or \
                (verbatim and c == '"' and i > 1 and text[i - 2:i] in ("$@", "@$"))
            q, j = c, i + 1
            while j < n:
                if is_verb:
                    if text[j] == '"':
                        if j + 1 < n and text[j + 1] == '"': j += 2; continue
                        break
                else:
                    if text[j] == "\\": j += 2; continue
                    if text[j] == q: break
                    if text[j] == "\n" and q != "`": break
                j += 1
            seg = text[i + 1:j]
            out.append(c + "".join(ch if ch == "\n" else " " for ch in seg) + (q if j < n and text[j] == q else ""))
            i = j + 1
        else:
            out.append(c); i += 1
    return "".join(out)


class Check:
    def __init__(self, cid, rule, langs, pattern, message, severity, confidence, fix,
                 target="code", flags=re.M, post=None, skip_tests=False, skip_line=None, only_ext=None):
        self.id, self.rule, self.langs = cid, rule, set(langs)
        self.rx = re.compile(pattern, flags)
        self.message, self.severity, self.confidence, self.fix = message, severity, confidence, fix
        self.target, self.post, self.skip_tests = target, post, skip_tests
        self.skip_line = re.compile(skip_line) if skip_line else None
        self.only_ext = only_ext


def _async_void_ok(text, m, line):
    name = m.group(1)
    return not ("_" in name or name.startswith("On"))


def _proto_literal_lacks_ctor(text, m, line):
    depth, i = 1, m.end()          # m ends right after the opening '{'
    while i < len(text) and depth:
        depth += {"{": 1, "}": -1}.get(text[i], 0)
        i += 1
    return not re.search(r"\bconstructor\s*:", text[m.end():i])


def _not_exists_select_star(text, m, line):
    return not re.search(r"EXISTS\s*\(\s*$", text[max(0, m.start() - 30):m.start()], re.I)


CS = ["csharp"]
BUILTIN = [
    # --- C# 7.3 ceiling (CS-001): the product compiles with C# 7.3, newer syntax is a compile error ---
    Check("csharp73.switch-expression", "CS-001", CS, r"\bswitch\s*\{", "Switch expression (C# 8) is not available in C# 7.3.", "blocker", "certain", "Use a switch statement or if/else."),
    Check("csharp73.null-coalescing-assign", "CS-001", CS, r"\?\?=", "'??=' (C# 8) is not available in C# 7.3.", "blocker", "certain", "Use: x = x ?? value;"),
    Check("csharp73.using-declaration", "CS-001", CS, r"^\s*using\s+(?:var|[A-Za-z_][\w.<>,\[\]?]*)\s+[A-Za-z_]\w*\s*=", "'using' declaration (C# 8) is not available in C# 7.3.", "blocker", "certain", "Use: using (var x = ...) { ... }"),
    Check("csharp73.index-range", "CS-001", CS, r"\[\s*(?:\^\s*\w+|\w*\s*\.\.\s*\^?\w*)\s*\]", "Index/range syntax (C# 8) is not available in C# 7.3.", "blocker", "likely", "Use explicit indexes, Substring or LINQ Skip/Take."),
    Check("csharp73.nullable-directive", "CS-001", CS, r"^\s*#nullable\b", "'#nullable' (C# 8) is not available in C# 7.3.", "blocker", "certain", "Remove the directive.", target="raw"),
    Check("csharp73.nullable-reference-type", "CS-001", CS, r"\b(?:string|object|dynamic)\?(?!\?)", "Nullable reference type annotation (C# 8) is not available in C# 7.3.", "blocker", "certain", "Remove the '?' (reference types are already nullable)."),
    Check("csharp73.null-forgiving", "CS-001", CS, r"[\w\)\]]!(?=\s*[.;,)\]\[])", "Null-forgiving operator '!' (C# 8) is not available in C# 7.3.", "blocker", "likely", "Remove it."),
    Check("csharp73.record", "CS-001", CS, r"^\s*(?:(?:public|internal|private|protected|sealed|abstract|partial|static|unsafe)\s+)*record\s+(?:class\s+|struct\s+)?[A-Za-z_]\w*", "'record' (C# 9) is not available in C# 7.3.", "blocker", "certain", "Use a class or struct."),
    Check("csharp73.init-accessor", "CS-001", CS, r"(?:\{|;)\s*init\s*(?:;|\{|=>)", "'init' accessor (C# 9) is not available in C# 7.3.", "blocker", "likely", "Use a constructor with get-only property."),
    Check("csharp73.is-not", "CS-001", CS, r"\bis\s+not\b", "'is not' pattern (C# 9) is not available in C# 7.3.", "blocker", "certain", "Use: !(x is T)"),
    Check("csharp73.property-pattern", "CS-001", CS, r"\bis\s*\{", "Property pattern (C# 8) is not available in C# 7.3.", "blocker", "certain", "Use explicit null/property checks."),
    Check("csharp73.target-typed-new", "CS-001", CS, r"(?:=|return|=>|,|\()\s*new\s*\(", "Target-typed 'new()' (C# 9) is not available in C# 7.3.", "blocker", "likely", "Write the type: new Foo(...)", skip_line=r"\bwhere\b"),
    Check("csharp73.file-scoped-namespace", "CS-001", CS, r"^\s*namespace\s+[\w.]+\s*;", "File-scoped namespace (C# 10) is not available in C# 7.3.", "blocker", "certain", "Use namespace X { ... }"),
    Check("csharp73.global-using", "CS-001", CS, r"^\s*global\s+using\b", "'global using' (C# 10) is not available in C# 7.3.", "blocker", "certain", "Remove; add usings per file."),
    Check("csharp73.await-foreach-using", "CS-001", CS, r"\bawait\s+(?:foreach|using)\b", "'await foreach/using' (C# 8) is not available in C# 7.3.", "blocker", "certain", "Use an explicit loop/try-finally."),
    Check("csharp73.with-expression", "CS-001", CS, r"\bwith\s*\{", "'with' expression (C# 9) is not available in C# 7.3.", "blocker", "likely", "Create a copy explicitly."),
    Check("csharp73.async-streams", "CS-001", CS, r"\bIAsync(?:Enumerable|Enumerator|Disposable)\b", "Async streams (C# 8) are not available in C# 7.3.", "blocker", "likely", "Return Task<IEnumerable<T>> or use a callback."),
    # --- C# robustness ---
    Check("cs.async-blocking", "CS-003", CS, r"\.\s*GetAwaiter\s*\(\s*\)\s*\.\s*GetResult\s*\(\s*\)|\.\s*Wait\s*\(\s*(?:\d+\s*)?\)|\w\.Result\b(?!\s*[(=])", "Blocking on a Task (.Result/.Wait()/GetResult()) can deadlock under the ASP.NET synchronization context.", "major", "verify", "Make the call chain async (await) or use ConfigureAwait(false) at a true sync boundary - confirm this is a Task.", skip_tests=True),
    Check("cs.async-void", "CS-004", CS, r"\basync\s+void\s+([A-Za-z_]\w*)\s*\(", "'async void' swallows exceptions and cannot be awaited.", "major", "likely", "Return Task (async void only for event handlers).", post=_async_void_ok),
    Check("cs.empty-catch", "CS-005", CS, r"\bcatch\b\s*(?:\([^)]*\))?\s*(?:when\s*\([^)]*\)\s*)?\{\s*\}", "Empty catch block hides failures.", "major", "certain", "Handle, log with context, or rethrow. If intentionally ignored, catch the narrowest exception and say why."),
    Check("cs.sql-concat", "CS-006", CS, r"(?:\$@?|@)?\"[^\"\n]*\b" + SQL_KW + r"[^\"\n]*\"\s*\+|\$@?\"[^\"\n]*\b" + SQL_KW + r"[^\"\n]*\{[^}\n]+\}|string\.Format\s*\(\s*@?\"[^\"]*\b" + SQL_KW, "SQL built by concatenation/interpolation: injection risk and plan-cache pollution.", "blocker", "verify", "Use parameterized commands (SqlParameter) or the project's data-access layer.", target="raw", flags=re.M | re.I),
    Check("cs.sql-select-star", "SQL-001", CS, r"\"[^\"\n]*\bSELECT\s+\*", "'SELECT *' in application SQL breaks when columns change and over-fetches.", "minor", "verify", "List the needed columns.", target="raw", flags=re.M | re.I),
    # --- JavaScript / TypeScript ---
    Check("js.prototype-literal", "JS-001", ["javascript", "typescript"], r"\b\w+(?:\.\w+)*\.prototype\s*=\s*\{", "Assigning an object literal to .prototype drops the original 'constructor' property.", "major", "likely", "Add constructor: <Type> to the literal or assign methods individually.", post=_proto_literal_lacks_ctor),
    Check("js.builtin-prototype", "JS-002", ["javascript", "typescript"], r"\b(?:Array|Object|String|Number|Boolean|Function|Date|RegExp|Promise|Map|Set)\.prototype\.\w+\s*=(?!=)", "Modifying a built-in prototype affects every script on the page.", "major", "likely", "Use a helper function/module instead."),
    Check("js.loose-equality", "JS-003", ["javascript", "typescript"], r"(?<![=!<>])==(?!=)|(?<![!=<>])!=(?!=)", "Loose equality (==, !=) performs type coercion.", "minor", "likely", "Use === / !==.", skip_tests=True),
    Check("js.eval", "JS-004", ["javascript", "typescript"], r"\beval\s*\(|\bnew\s+Function\s*\(|\bset(?:Timeout|Interval)\s*\(\s*[\"'`]", "eval/new Function/string timers execute dynamic code.", "major", "certain", "Remove dynamic code execution."),
    Check("js.innerhtml", "JS-005", ["javascript", "typescript"], r"\.(?:innerHTML|outerHTML)\s*\+?=(?!=)|\binsertAdjacentHTML\s*\(|\bdocument\.write\s*\(", "HTML string injection: XSS risk if any part is not a constant.", "major", "verify", "Use textContent / DOM APIs / Angular binding; sanitize if HTML is unavoidable.", skip_tests=True),
    Check("ng.bypass-security", "NG-003", ["typescript"], r"\bbypassSecurityTrust\w+\s*\(", "bypassSecurityTrust* disables Angular sanitization.", "major", "likely", "Remove or document why the value is provably safe.", skip_tests=True),
    Check("ng.html-innerhtml", "NG-003", ["html"], r"\[innerHTML\]", "[innerHTML] binding: ensure the value is sanitized and not user/patient-controlled.", "major", "verify", "Prefer interpolation {{ }}.", target="raw"),
    Check("ts.any", "NG-001", ["typescript"], r":\s*any\b|\bas\s+any\b|<any>|\bArray<any>", "'any' removes type checking.", "minor", "likely", "Use a specific type or 'unknown' with narrowing.", skip_tests=True),
    # --- SQL / C++ ---
    Check("sql.select-star", "SQL-001", ["sql"], r"\bSELECT\s+(?:TOP\s*\(?\d+\)?\s+)?\*", "'SELECT *' breaks when columns change and over-fetches.", "minor", "likely", "List the needed columns.", flags=re.M | re.I, post=_not_exists_select_star),
    Check("cpp.unsafe-c-function", "CPP-001", ["cpp"], r"(?<![\w.>])(?:gets|strcpy|strcat|sprintf|vsprintf)\s*\(", "Unbounded C string function: buffer overflow risk.", "major", "certain", "Use bounded alternatives (snprintf, strncpy_s/strcpy_s) or std::string."),
    # --- general ---
    Check("gen.hardcoded-secret", "GEN-003", ["csharp", "typescript", "javascript", "cpp", "powershell", "python"], r"\b(?:password|passwd|pwd|secret|apikey|api_key|accesskey|access_key|token)\w*\s*[:=]\s*@?\"[^\"\n]{6,}\"|(?:password|pwd)\s*=\s*[^;\"'\s{}]{3,};", "Possible hard-coded credential.", "blocker", "verify", "Move to secure configuration/secret store; rotate if it was real.", target="raw", flags=re.M | re.I, skip_tests=True),
]


def build_checks(root, cfg):
    checks = list(BUILTIN)
    wi = cfg.get("work_item_regex", r"#\d+")
    checks.append(Check("gen.todo-no-ticket", "GEN-004", ["csharp", "typescript", "javascript", "cpp", "sql", "powershell", "python"],
                        r"\b(?:TODO|FIXME|HACK)\b(?!.*(?:%s))" % wi, "TODO/FIXME/HACK without a work-item reference.", "nit", "certain",
                        "Add the work-item id or remove it.", target="raw"))
    pf = root / cfg.get("project_patterns_file", "")
    if cfg.get("project_patterns_file") and pf.exists():
        for e in json.loads(pf.read_text(encoding="utf-8")).get("patterns", []):
            if not e.get("enabled", False):
                continue
            c = Check("project." + e["id"], e.get("rule", "DES-001"), e.get("languages", ["csharp", "typescript", "javascript"]),
                      e["pattern"], e["message"], e.get("severity", "major"), e.get("confidence", "likely"),
                      e.get("fix", "See design/DESIGN-CONSTRAINTS.md"), target=e.get("target", "code"))
            c.applies_to = e.get("applies_to", ["**"])
            checks.append(c)
    return checks


def scan_file(root, rel, added, checks, rules, cfg):
    path = root / rel
    lang, test = lang_of(rel), is_test_path(rel)
    if lang is None or not path.exists():
        return []
    raw = read_text(path)
    code = strip_c_like(raw, lang) if lang in ("csharp", "javascript", "typescript", "cpp") else raw
    raw_lines = raw.splitlines()
    findings = []
    for ck in checks:
        if lang not in ck.langs or (ck.skip_tests and test):
            continue
        applies = getattr(ck, "applies_to", None)
        if applies and not match_any(rel, applies):
            continue
        text = raw if ck.target == "raw" else code
        for m in ck.rx.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            if added is not None and line not in added:
                continue
            if ck.post and not ck.post(text, m, line):
                continue
            src = raw_lines[line - 1] if line - 1 < len(raw_lines) else ""
            if ck.skip_line and ck.skip_line.search(src):
                continue
            end_line = text.count("\n", 0, m.end()) + 1
            rule = rules.get(ck.rule, {})
            unfixed = rule.get("acceptable_if_unfixed", "never" if ck.severity in ("blocker", "major") else "debt")
            findings.append({
                "check_id": ck.id, "rule_id": ck.rule, "file": rel, "line_start": line, "line_end": end_line,
                "code": "\n".join(raw_lines[line - 1:end_line]).strip()[:400],
                "issue": ck.message,
                "justification": "Rule %s: %s" % (ck.rule, rule.get("summary", "see guidelines/rules")),
                "severity": ck.severity, "confidence": ck.confidence, "fix": ck.fix,
                "acceptable_if_unfixed": {"value": unfixed, "reason": "Default for rule %s (%s)." % (ck.rule, ck.severity)},
                "source": "static",
            })
    return findings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scope"); ap.add_argument("--paths", nargs="*")
    ap.add_argument("--out"); ap.add_argument("--format", default="text", choices=["text", "github", "json"])
    ap.add_argument("--list-checks", action="store_true")
    a = ap.parse_args()
    root = repo_root(); cfg = load_config(root); rules = load_rules(root)
    checks = build_checks(root, cfg)
    if a.list_checks:
        for c in checks:
            print("%s\t%s\t%s\t%s" % (c.id, c.rule, c.severity, c.confidence))
        return 0
    if a.scope:
        scope = json.loads(Path(a.scope).read_text(encoding="utf-8"))
        targets = [(f["path"], set(f["added_lines"]) if f["added_lines"] is not None else None) for f in scope["files"]]
    elif a.paths:
        targets = [(p.replace("\\", "/"), None) for p in a.paths]
    else:
        ap.error("--scope or --paths required")
    findings = []
    for rel, added in targets:
        findings += scan_file(root, rel, added, checks, rules, cfg)
    findings.sort(key=lambda f: (f["file"], f["line_start"]))
    result = {"files_scanned": len(targets), "findings": findings}
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(result, indent=2), encoding="utf-8")
    for f in findings:
        if a.format == "github":
            lvl = "error" if f["severity"] in ("blocker", "major") and f["confidence"] != "verify" else "warning"
            print("::%s file=%s,line=%d,title=%s [%s]::%s" % (lvl, f["file"], f["line_start"], f["rule_id"], f["confidence"], f["issue"]))
        elif a.format == "text":
            print("%s:%d  [%s/%s] %s %s  -> %s" % (f["file"], f["line_start"], f["severity"], f["confidence"], f["rule_id"], f["issue"], f["fix"]))
    if a.format == "json":
        print(json.dumps(result, indent=2))
    print("static checks: %d file(s), %d finding(s)" % (len(targets), len(findings)), file=sys.stderr)
    gate = [f for f in findings if f["severity"] in ("blocker", "major") and f["confidence"] in ("certain", "likely")]
    return 1 if gate else 0


if __name__ == "__main__":
    sys.exit(main())
