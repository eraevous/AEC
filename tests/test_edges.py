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


if __name__ == "__main__":
    unittest.main()
