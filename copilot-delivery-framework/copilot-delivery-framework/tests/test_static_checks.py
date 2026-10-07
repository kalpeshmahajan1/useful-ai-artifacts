import sys, tempfile, unittest, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "python"))
import static_checks as sc
from fwcommon import load_config, load_rules

ROOT = Path(__file__).resolve().parents[1]
CFG = load_config(ROOT)
CHECKS = sc.build_checks(ROOT, CFG)


def scan(name, text):
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / name).write_text(text, encoding="utf-8")
        return {f["check_id"] for f in sc.scan_file(Path(d), name, None, CHECKS, {}, CFG)}


class T(unittest.TestCase):
    def test_csharp_new_syntax_flagged(self):
        src = """namespace A;
class C { void M(string? s, int[] a) {
  var r = x switch { 1 => 2, _ => 3 };
  y ??= 1;
  using var f = Open();
  var z = a[^1]; var w = a[1..3];
  if (o is not null) {} if (o is { }) {}
  List<int> l = new();
  var p = q!.Name;
} }
public record P(int X);
public class Q { public int V { get; init; } }
"""
        got = scan("a.cs", src)
        for cid in ["switch-expression", "null-coalescing-assign", "using-declaration", "index-range",
                    "nullable-reference-type", "is-not", "property-pattern", "target-typed-new",
                    "null-forgiving", "record", "init-accessor", "file-scoped-namespace"]:
            self.assertIn("csharp73." + cid, got, cid)

    def test_csharp73_valid_code_clean(self):
        src = """using System; using Alias = System.Text.StringBuilder;
namespace A { class C<T> where T : class, new() {
  int? n; string s = "switch { ?? = x[^1] }"; // y ??= 1; record R
  void M(int[] a, object o) {
    switch (n) { case 1: break; }
    using (var f = Open()) { }
    if (!(o is string)) { } if (n != null && a[a.Length - 1] != 2) { }
    var t = new List<int>(); var u = new Foo(1);
    int k = a[1 ^ 2];
  } } }
"""
        got = {c for c in scan("a.cs", src) if c.startswith("csharp73")}
        self.assertEqual(got, set())

    def test_cs_robustness(self):
        src = """class C { async void Run() { }  async void Button_Click(object s, EventArgs e) { }
  void M() { try { A(); } catch (Exception) { } try { B(); } catch { /* ignore */ }
    var x = t.Result; t.Wait();
    var q = "SELECT * FROM T WHERE id=" + id;
    var r = "update the label " + name; } }"""
        got = scan("a.cs", src)
        self.assertIn("cs.async-void", got); self.assertIn("cs.empty-catch", got)
        self.assertIn("cs.async-blocking", got); self.assertIn("cs.sql-concat", got)
        self.assertIn("cs.sql-select-star", got)

    def test_async_void_handler_ok_and_english_not_sql(self):
        got = scan("a.cs", 'class C { async void Button_Click(object s, EventArgs e) { } void M(){ var r = "update the label " + n; } }')
        self.assertNotIn("cs.async-void", got); self.assertNotIn("cs.sql-concat", got)

    def test_js(self):
        src = """Foo.prototype = { a: function(){} };
Bar.prototype = { constructor: Bar, a: function(){} };
Array.prototype.x = function(){};
if (a == b) {} if (a === b) {} if (a != b) {}
eval("1"); el.innerHTML = s; var s = "// eval(x) ==";
"""
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "a.js").write_text(src, encoding="utf-8")
            f = sc.scan_file(Path(d), "a.js", None, CHECKS, {}, CFG)
        by = {}
        for x in f: by.setdefault(x["check_id"], []).append(x["line_start"])
        self.assertEqual(by["js.prototype-literal"], [1])
        self.assertIn("js.builtin-prototype", by); self.assertEqual(by["js.loose-equality"], [4, 4])
        self.assertIn("js.eval", by); self.assertIn("js.innerhtml", by)

    def test_cpp_sql_ts(self):
        self.assertIn("cpp.unsafe-c-function", scan("a.cpp", "void f(char*a){ strcpy(a,b); }"))
        self.assertNotIn("cpp.unsafe-c-function", scan("a.cpp", "void f(){ obj.sprintf(1); }"))
        self.assertIn("sql.select-star", scan("a.sql", "SELECT * FROM T"))
        self.assertNotIn("sql.select-star", scan("a.sql", "IF EXISTS (SELECT * FROM T) SELECT COUNT(*) FROM T"))
        self.assertIn("ts.any", scan("a.ts", "let x: any = 1;"))
        self.assertNotIn("ts.any", scan("a.spec.ts", "let x: any = 1;"))

    def test_added_lines_filter(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "a.cs").write_text("class C {\n void A(){ try{}catch{} }\n void B(){ try{}catch{} }\n}\n", encoding="utf-8")
            f = sc.scan_file(Path(d), "a.cs", {3}, CHECKS, {}, CFG)
            self.assertEqual([x["line_start"] for x in f], [3])

    def test_secret_and_todo(self):
        got = scan("a.cs", 'class C { string password = "hunter2hunter2"; // TODO fix\n // TODO ABC-123 fix\n }')
        self.assertIn("gen.hardcoded-secret", got); self.assertIn("gen.todo-no-ticket", got)

if __name__ == "__main__":
    unittest.main()
