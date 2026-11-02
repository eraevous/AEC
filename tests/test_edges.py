"""US1 tests for aec.edges (T004-T007). Written before the implementation (Constitution III)."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
FIX = Path(__file__).resolve().parent / "fixtures"

from aec import edges as E  # noqa: E402


def idents(snapshot, kind):
    return {(e["src"], e["dst"]) for e in snapshot["edges"] if e["kind"] == kind}


class TestExtraction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snap = E.snapshot(FIX / "edges_pkg_v1")
        cls.expected = json.loads((FIX / "edges_pkg_v1" / "expected_edges.json").read_text())

    def test_labelled_kinds_match_exactly(self):  # T004 / SC-001 / FR-001
        for kind in ("defines", "imports", "inherits", "calls", "references"):
            with self.subTest(kind=kind):
                self.assertEqual(idents(self.snap, kind), {tuple(x) for x in self.expected[kind]})

    def test_every_edge_has_location_and_resolution(self):  # FR-002
        for e in self.snap["edges"]:
            self.assertIn("file", e)
            self.assertIsInstance(e["line"], int)
            self.assertEqual(e["resolved"], not e["dst"].startswith("?"))

    def test_explicit_import_after_star_wins(self):
        self.assertIn(("pkg.core.Worker.step", "pkg.util.helper"), idents(self.snap, "calls"))
        self.assertNotIn(("pkg.core.Worker.step", "pkg.extras.helper"), idents(self.snap, "calls"))

    def test_dynamic_call_is_unresolved_not_guessed(self):  # T007
        calls = idents(self.snap, "calls")
        self.assertIn(("pkg.core.load", "?getattr(...)"), calls)
        self.assertFalse(any(dst in ("os.getcwd",) for _, dst in calls))

    def test_syntax_error_file_is_skipped_others_still_processed(self):  # T005
        self.assertEqual([s["file"] for s in self.snap["header"]["skipped"]], ["pkg/broken.py"])
        self.assertIn(("pkg.core", "pkg.core.main"), idents(self.snap, "defines"))


class TestDeterminism(unittest.TestCase):
    def test_byte_identical_runs(self):  # T005 / SC-003 / FR-003
        a = E.dumps(E.snapshot(FIX / "edges_pkg_v1"))
        b = E.dumps(E.snapshot(FIX / "edges_pkg_v1"))
        self.assertEqual(a, b)
        lines = a.splitlines()
        self.assertTrue(json.loads(lines[0]).get("aec_edges"))
        self.assertEqual(lines[1:], sorted(lines[1:], key=lambda l: E.sort_key(json.loads(l))))

    def test_roundtrip(self):
        s = E.snapshot(FIX / "edges_pkg_v1")
        self.assertEqual(E.loads(E.dumps(s))["edges"], s["edges"])


class TestDiff(unittest.TestCase):
    def test_diff_is_exactly_the_labelled_changes(self):  # T006 / FR-004
        d = E.diff(E.snapshot(FIX / "edges_pkg_v1"), E.snapshot(FIX / "edges_pkg_v2"))
        added = {(e["kind"], e["src"], e["dst"]) for e in d["added"]}
        removed = {(e["kind"], e["src"], e["dst"]) for e in d["removed"]}
        self.assertEqual(added, {("calls", "pkg.core.Worker.step", "pkg.core.load")})
        self.assertEqual(removed, {("defines", "pkg.core", "pkg.core.fetch"), ("calls", "pkg.core.fetch", "pkg.core.load")})
        self.assertEqual(d["defs_removed"], ["pkg.core.fetch"])
        self.assertEqual(d["defs_added"], [])
        self.assertEqual(d["defs_changed"], ["pkg.core.Worker", "pkg.core.Worker.step", "pkg.util.helper"])

    def test_comment_and_whitespace_change_is_not_a_diff(self):  # decoy
        d = E.diff(E.snapshot(FIX / "edges_pkg_v1"), E.snapshot(FIX / "edges_pkg_v2"))
        touched = {e["src"] for e in d["added"] + d["removed"]} | set(d["defs_changed"])
        self.assertFalse(any(s.startswith("pkg.base") for s in touched))


class TestLegacyCsv(unittest.TestCase):
    def test_legacy_csv_has_source_call_header(self):
        csv = E.legacy_csv(E.snapshot(FIX / "edges_pkg_v1"))
        self.assertTrue(csv.startswith("Source,Call\n"))
        self.assertIn("pkg.core.load,json.loads", csv)


class TestSourceRootAliases(unittest.TestCase):  # feature 002: code run with src/ on sys.path
    def snap(self):
        import tempfile
        d = Path(tempfile.mkdtemp())
        (d / "src").mkdir()
        (d / "src" / "prof.py").write_text("def f():\n    return 1\n")
        (d / "src" / "json.py").write_text("X = 1\n")
        (d / "src" / "use.py").write_text("from prof import f\nimport json\n\ndef g():\n    return f()\n")
        return E.snapshot(d)

    def test_bare_import_resolves_to_the_source_root_module(self):
        s = self.snap()
        self.assertIn(("src.use", "src.prof.f"), idents(s, "imports"))
        self.assertIn(("src.use.g", "src.prof.f"), idents(s, "calls"))
        self.assertEqual(s["header"]["source_roots"], ["src"])

    def test_stdlib_names_are_never_aliased(self):  # decoy
        self.assertIn(("src.use", "json"), idents(self.snap(), "imports"))


LOCAL_CTOR_MODELS = '''\
class Base:
    def run(self):
        return 1


class Model(Base):
    def fit(self):
        return 2


class Odd:
    def __new__(cls):
        return object.__new__(cls)

    def run(self):
        return 3


def make():
    return Model()
'''

LOCAL_CTOR_USE = '''\
from pkg.models import Model, Odd, make


def resolves(flag):
    m = Model()
    m.fit()
    m.run()
    a: Model = Model()
    a.fit()
    cb = m.fit
    return cb


def stays_unresolved(flag, p):
    r = Model()
    r = make()
    r.fit()
    if flag:
        s = Model()
    s.fit()
    p = Model()
    p.fit()
    n = Odd()
    n.run()
    w = make()
    w.fit()
    k = Model()
    k.missing()
    k.data.fit()
    for t in []:
        pass
    t = Model()
    t.fit()
    try:
        e = Model()
    except Exception as e:
        pass
    e.fit()
    q = Model()

    def inner():
        q.fit()
    return inner


def global_name():
    global g
    g = Model()
    g.fit()


class Holder:
    h = Model()
    h.fit()
'''


class TestLocalConstructorCalls(unittest.TestCase):
    """C-11 (probe-001): `x = C(...); x.m()` resolves when the local has exactly one possible value,
    assigned from a known class in the same function. Everything else stays unresolved, never guessed."""

    @classmethod
    def setUpClass(cls):
        import tempfile
        d = Path(tempfile.mkdtemp())
        (d / "pkg").mkdir()
        (d / "pkg" / "__init__.py").write_text("")
        (d / "pkg" / "models.py").write_text(LOCAL_CTOR_MODELS)
        (d / "pkg" / "use.py").write_text(LOCAL_CTOR_USE)
        cls.snap = E.snapshot(d)
        cls.calls = idents(cls.snap, "calls")

    def test_method_on_local_from_known_class_resolves(self):  # violation: was ?m.fit
        self.assertIn(("pkg.use.resolves", "pkg.models.Model.fit"), self.calls)
        self.assertNotIn(("pkg.use.resolves", "?m.fit"), self.calls)

    def test_inherited_method_resolves_through_bases(self):
        self.assertIn(("pkg.use.resolves", "pkg.models.Base.run"), self.calls)

    def test_annotated_assignment_resolves(self):
        self.assertNotIn(("pkg.use.resolves", "?a.fit"), self.calls)

    def test_bound_method_reference_resolves(self):
        self.assertIn(("pkg.use.resolves", "pkg.models.Model.fit"), idents(self.snap, "references"))

    def test_ambiguous_locals_stay_unresolved(self):  # decoys
        src = "pkg.use.stays_unresolved"
        for dst in ("?r.fit", "?s.fit", "?p.fit", "?n.run", "?w.fit", "?k.missing", "?k.data.fit", "?t.fit", "?e.fit"):
            with self.subTest(dst=dst):
                self.assertIn((src, dst), self.calls)
        resolved = {d for s, d in self.calls if s == src and not d.startswith("?")}
        self.assertFalse(resolved & {"pkg.models.Model.fit", "pkg.models.Odd.run", "pkg.models.Base.run"}, resolved)

    def test_no_resolution_through_closures_globals_or_class_bodies(self):  # decoys
        self.assertIn(("pkg.use.stays_unresolved.<locals>.inner", "?q.fit"), self.calls)
        self.assertNotIn(("pkg.use.global_name", "pkg.models.Model.fit"), self.calls)
        self.assertNotIn(("pkg.use.Holder", "pkg.models.Model.fit"), self.calls)



LOCAL_CTOR_REVIEW_MODELS = '''\
from abc import ABC


class Model:
    def fit(self):
        return 1


class AssignedNew:
    __new__ = staticmethod(lambda cls: Model())

    def run(self):
        return 2


class Meta(type):
    def __call__(cls, *a, **k):
        return Model()


class ViaMeta(metaclass=Meta):
    def run(self):
        return 3


class Child(ViaMeta):
    pass


class Abstract(ABC):
    def go(self):
        return 4


class Concrete(Abstract):
    pass


def make():
    return Model()
'''

LOCAL_CTOR_REVIEW_OTHER = '''\
class Model:
    def fit(self):
        return 5
'''

LOCAL_CTOR_REVIEW_USE = '''\
from pkg.models import AssignedNew, Child, Concrete, Model, ViaMeta, make


def nonlocal_write():
    m = Model()

    def reset():
        nonlocal m
        m = make()
    reset()
    m.fit()


def rebound_import():
    from pkg.models import Model as M
    m = M()
    from pkg.other import Model as M
    m.fit()


def lambda_param():
    m = Model()
    cb = lambda m: m.fit()
    return cb(make())


def odd_construction():
    n = AssignedNew()
    n.run()
    v = ViaMeta()
    v.run()
    c = Child()
    c.run()


def abc_still_resolves():
    a = Concrete()
    a.go()
'''


class TestLocalConstructorReviewCases(unittest.TestCase):
    """Cases from the Copilot review of PR #32: each would have produced a wrong resolved edge."""

    @classmethod
    def setUpClass(cls):
        import tempfile
        d = Path(tempfile.mkdtemp())
        (d / "pkg").mkdir()
        (d / "pkg" / "__init__.py").write_text("")
        (d / "pkg" / "models.py").write_text(LOCAL_CTOR_REVIEW_MODELS)
        (d / "pkg" / "other.py").write_text(LOCAL_CTOR_REVIEW_OTHER)
        (d / "pkg" / "use.py").write_text(LOCAL_CTOR_REVIEW_USE)
        cls.calls = idents(E.snapshot(d), "calls")

    def resolved_from(self, fn):
        return {d for s, d in self.calls if s == f"pkg.use.{fn}" and not d.startswith("?")}

    def test_nonlocal_write_in_nested_function_disqualifies(self):
        self.assertNotIn("pkg.models.Model.fit", self.resolved_from("nonlocal_write"))

    def test_constructor_name_rebound_by_local_import_disqualifies(self):
        r = self.resolved_from("rebound_import")
        self.assertFalse({"pkg.models.Model.fit", "pkg.other.Model.fit"} & r, r)

    def test_lambda_parameter_shadowing_disqualifies(self):
        self.assertNotIn("pkg.models.Model.fit", self.resolved_from("lambda_param"))

    def test_assigned_new_and_custom_metaclass_call_disqualify(self):
        r = self.resolved_from("odd_construction")
        self.assertFalse({"pkg.models.AssignedNew.run", "pkg.models.ViaMeta.run"} & r, r)

    def test_ordinary_abc_subclass_still_resolves(self):  # decoy: don't over-exclude metaclasses
        self.assertIn("pkg.models.Abstract.go", self.resolved_from("abc_still_resolves"))


class TestModuleNameCollision(unittest.TestCase):
    """From Copilot's repository review: `foo.py` beside `foo/__init__.py` both mapped to module `foo`, and
    one file's calls vanished without a trace. Python imports the package, so the package is analysed and
    the module file is reported as skipped (shadowed), not silently merged or dropped."""

    def test_package_wins_and_shadowed_module_is_reported(self):
        import tempfile
        d = Path(tempfile.mkdtemp())
        (d / "foo").mkdir()
        (d / "foo.py").write_text("def a():\n    b()\n\n\ndef b():\n    pass\n")
        (d / "foo" / "__init__.py").write_text("def c():\n    d()\n\n\ndef d():\n    pass\n")
        (d / "bar.py").write_text("def e():\n    pass\n")
        s = E.snapshot(d)
        self.assertIn(("foo.c", "foo.d"), idents(s, "calls"))
        self.assertNotIn(("foo", "foo.a"), idents(s, "defines"))
        skipped = {x["file"]: x["reason"] for x in s["header"]["skipped"]}
        self.assertIn("foo.py", skipped)
        self.assertIn("shadowed", skipped["foo.py"])
        self.assertNotIn("bar.py", skipped)  # decoy: an unrelated module is untouched


class TestFileChangedDuringExtraction(unittest.TestCase):
    """From Copilot's repository review: a file edited between the two passes produced a snapshot mixing
    both versions. Extraction now fails rather than return a snapshot that looks complete."""

    def test_change_between_passes_raises(self):
        import tempfile
        d = Path(tempfile.mkdtemp())
        f = d / "demo.py"
        f.write_text("def old():\n    pass\n")
        ex = E._Extractor(d, set(E.DEFAULT_IGNORE))
        ex.load()
        f.write_text("def new():\n    old()\n")
        ex.build_module_bindings()
        ex.collect_bases()
        with self.assertRaises(E.SourceChanged):
            ex.scan_bodies()

    def test_unchanged_tree_extracts(self):  # decoy
        import tempfile
        d = Path(tempfile.mkdtemp())
        (d / "demo.py").write_text("def old():\n    pass\n")
        self.assertIn(("demo", "demo.old"), idents(E.snapshot(d), "defines"))

if __name__ == "__main__":
    unittest.main()
