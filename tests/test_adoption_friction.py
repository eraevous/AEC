"""DEC-095 adoption friction (pilot report, 2026-11-05): `init --purpose/--purpose-anchor`, no hook or CI for
repositories without Python code, and `aec append` to add a record with computed anchor hashes.

Written before the code (each test failed first)."""
import hashlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
FIX = Path(__file__).resolve().parent / "fixtures"
from aec import edges as E  # noqa: E402
from aec.__main__ import main  # noqa: E402
from aec.init import init  # noqa: E402
from aec.records import Store, check  # noqa: E402
from aec.sources import SourceContext  # noqa: E402

SNIPPETS = (".aec/snippets/claude-settings.json", ".aec/snippets/aec-ci.yml")


def code_repo():
    d = Path(tempfile.mkdtemp()) / "repo"
    shutil.copytree(FIX / "purpose_repo", d)
    return d


def docs_repo():
    d = Path(tempfile.mkdtemp()) / "docs"
    d.mkdir()
    (d / "README.md").write_text("# Notes\n\nThis repo holds the umbrella purpose.\n", encoding="utf-8")
    return d


def run(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            rc = main(argv)
        except SystemExit as e:  # argparse usage errors
            rc = e.code
    return rc, out.getvalue(), err.getvalue()


class TestNoCodeRepo(unittest.TestCase):
    def test_repo_without_python_gets_no_hook_or_ci(self):
        d = docs_repo()
        rep = init(d, owner="Zach")
        for s in SNIPPETS:
            self.assertNotIn(s, rep["created"])
            self.assertFalse((d / s).exists(), s)
        self.assertIn("no Python", rep["next_steps"])
        self.assertIn(".aec/records.jsonl", rep["created"])

    def test_hooks_true_writes_them_anyway(self):
        d = docs_repo()
        rep = init(d, owner="Zach", hooks=True)
        for s in SNIPPETS:
            self.assertIn(s, rep["created"])

    def test_code_repo_still_gets_them(self):  # decoy: the default for code is unchanged
        d = code_repo()
        rep = init(d, owner="Zach")
        for s in SNIPPETS:
            self.assertIn(s, rep["created"])

    def test_hooks_false_skips_them_for_code(self):
        d = code_repo()
        rep = init(d, owner="Zach", hooks=False)
        for s in SNIPPETS:
            self.assertNotIn(s, rep["created"])

    def test_cli_flags(self):
        d = docs_repo()
        rc, out, _ = run(["init", str(d), "--owner", "Zach", "--hooks"])
        self.assertEqual(rc, 0)
        self.assertIn("created .aec/snippets/aec-ci.yml", out)
        d2 = code_repo()
        rc, out, _ = run(["init", str(d2), "--owner", "Zach", "--no-hooks"])
        self.assertEqual(rc, 0)
        self.assertNotIn("aec-ci.yml", out.split("Next steps")[0])


class TestInitPurpose(unittest.TestCase):
    def test_purpose_text_replaces_the_stub(self):
        d = code_repo()
        init(d, owner="Zach", purpose="Turn raw tables into understanding.")
        p0 = Store.load(d / ".aec" / "records.jsonl").latest["P0"]
        self.assertEqual(p0.text, "Turn raw tables into understanding.")
        self.assertEqual(p0.get("epistemic"), "provisional")  # still the owner's to commit

    def test_purpose_anchor_is_hashed_and_verifies(self):
        d = docs_repo()
        init(d, owner="Zach", purpose="Hold the umbrella purpose.", purpose_anchor="README.md#q:umbrella purpose")
        st = Store.load(d / ".aec" / "records.jsonl")
        p0 = st.latest["P0"]
        (anchor,) = p0.get("anchors")
        self.assertEqual(anchor["sha256"], hashlib.sha256((d / "README.md").read_bytes()).hexdigest())
        states = [i.state for i in SourceContext(d).inspect_record(p0)]
        self.assertEqual(states, ["verified"])
        self.assertEqual([f for f in check(st, sources=SourceContext(d)) if f.level == "error"], [])

    def test_bad_anchor_writes_nothing(self):
        d = docs_repo()
        with self.assertRaises(ValueError):
            init(d, owner="Zach", purpose="x", purpose_anchor="README.md#q:not in the file")
        self.assertFalse((d / ".aec").exists())

    def test_anchor_without_purpose_is_refused(self):
        d = docs_repo()
        with self.assertRaises(ValueError):
            init(d, owner="Zach", purpose_anchor="README.md#L1")
        self.assertFalse((d / ".aec").exists())

    def test_cli_purpose(self):
        d = docs_repo()
        rc, out, err = run(["init", str(d), "--owner", "Zach", "--purpose", "Hold the umbrella purpose.",
                            "--purpose-anchor", "README.md#L3"])
        self.assertEqual(rc, 0, err)
        self.assertNotIn("Replace the purpose stub", out)
        rc, _, err = run(["init", str(docs_repo()), "--purpose", "x", "--purpose-anchor", "nope.md#L1"])
        self.assertEqual(rc, 2)
        self.assertIn("nope.md", err)


class TestAppend(unittest.TestCase):
    def setUp(self):
        self.d = code_repo()
        init(self.d, owner="Zach")
        self.records = self.d / ".aec" / "records.jsonl"
        (self.d / "docs").mkdir(exist_ok=True)
        (self.d / "docs" / "why.md").write_text("# Why\n\nTables must load in under a second.\n", encoding="utf-8")

    def req(self, **kw):
        r = {"id": "R-1", "version": 1, "type": "requirement", "subject": "purpose", "epistemic": "provisional",
             "text": "Tables load in under a second.", "relations": [{"rel": "serves", "to": "P0@1"}]}
        r.update(kw)
        return json.dumps(r)

    def test_appends_with_computed_anchor(self):
        before = self.records.read_bytes()
        rc, out, err = run(["append", str(self.records), self.req(), "--anchor", "docs/why.md#q:under a second"])
        self.assertEqual(rc, 0, err)
        after = self.records.read_bytes()
        self.assertTrue(after.startswith(before))  # append-only
        st = Store.load(self.records)
        r = st.latest["R-1"]
        self.assertEqual(r.get("anchors")[0]["sha256"],
                         hashlib.sha256((self.d / "docs" / "why.md").read_bytes()).hexdigest())
        self.assertEqual([i.state for i in SourceContext(self.d).inspect_record(r)], ["verified"])
        self.assertIn("R-1@1", out)

    def test_rationale_anchor(self):
        rc, _, err = run(["append", str(self.records), self.req(), "--rationale-anchor", "docs/why.md#L3"])
        self.assertEqual(rc, 0, err)
        self.assertEqual(Store.load(self.records).latest["R-1"].get("anchors")[0]["for"], "rationale")

    def test_reads_stdin(self):
        sys_stdin = sys.stdin
        try:
            sys.stdin = io.StringIO(self.req())
            rc, _, err = run(["append", str(self.records), "-"])
        finally:
            sys.stdin = sys_stdin
        self.assertEqual(rc, 0, err)
        self.assertIn("R-1", Store.load(self.records).latest)

    def test_existing_id_version_is_refused(self):
        run(["append", str(self.records), self.req()])
        before = self.records.read_bytes()
        rc, _, err = run(["append", str(self.records), self.req(text="different")])
        self.assertEqual(rc, 1)
        self.assertIn("R-1@1 already exists", err)
        self.assertEqual(self.records.read_bytes(), before)

    def test_record_that_check_rejects_is_refused(self):
        before = self.records.read_bytes()
        rc, _, err = run(["append", str(self.records), self.req(relations=[{"rel": "serves", "to": "P9@1"}])])
        self.assertEqual(rc, 1)
        self.assertIn("P9@1", err)
        self.assertEqual(self.records.read_bytes(), before)

    def test_unresolved_anchor_is_refused(self):
        before = self.records.read_bytes()
        rc, _, err = run(["append", str(self.records), self.req(), "--anchor", "docs/why.md#q:not there"])
        self.assertEqual(rc, 1)
        self.assertIn("does not resolve", err)
        self.assertEqual(self.records.read_bytes(), before)

    def test_not_json_is_a_usage_error(self):
        rc, _, err = run(["append", str(self.records), "{not json"])
        self.assertEqual(rc, 2)

    def test_dry_run_writes_nothing(self):
        before = self.records.read_bytes()
        rc, out, _ = run(["append", str(self.records), self.req(), "--dry-run"])
        self.assertEqual(rc, 0)
        self.assertEqual(self.records.read_bytes(), before)
        self.assertIn('"id": "R-1"', out)

    def test_missing_final_newline_is_repaired_not_merged(self):
        self.records.write_bytes(self.records.read_bytes().rstrip(b"\n"))
        rc, _, err = run(["append", str(self.records), self.req()])
        self.assertEqual(rc, 0, err)
        self.assertEqual(len(Store.load(self.records).records), 3)

    def test_append_only_source_gets_prefix_bytes(self):
        ledger = self.d / "ledger.jsonl"
        ledger.write_text('{"id": "DEC-1", "decision": "load fast"}\n', encoding="utf-8")
        (self.d / ".aec" / "sources.json").write_text(json.dumps({"roots": {}, "append_only": {".": ["ledger.jsonl"]}}))
        rc, _, err = run(["append", str(self.records), self.req(), "--rationale-anchor", 'ledger.jsonl#q:"DEC-1"'])
        self.assertEqual(rc, 0, err)
        anchor = Store.load(self.records).latest["R-1"].get("anchors")[0]
        self.assertEqual(anchor["prefix_bytes"], ledger.stat().st_size)
        with ledger.open("a", encoding="utf-8") as f:
            f.write('{"id": "DEC-2", "decision": "later"}\n')
        r = Store.load(self.records).latest["R-1"]
        self.assertEqual([i.state for i in SourceContext(self.d).inspect_record(r)], ["appended"])

    def test_alias_root(self):
        other = Path(tempfile.mkdtemp()) / "ledgers"
        other.mkdir()
        (other / "d.md").write_text("decided: load fast\n", encoding="utf-8")
        (self.d / ".aec" / "sources.json").write_text(json.dumps({"roots": {"led": str(other)}}))
        rc, _, err = run(["append", str(self.records), self.req(), "--rationale-anchor", "led=d.md#L1"])
        self.assertEqual(rc, 0, err)
        anchor = Store.load(self.records).latest["R-1"].get("anchors")[0]
        self.assertEqual((anchor["root"], anchor["path"]), ("led", "d.md"))

    def test_appended_record_passes_check_with_edges(self):
        run(["append", str(self.records), self.req()])
        st = Store.load(self.records)
        self.assertEqual([f for f in check(st, edges=E.load(self.d / ".aec" / "edges.jsonl")) if f.level == "error"], [])


if __name__ == "__main__":
    unittest.main()
