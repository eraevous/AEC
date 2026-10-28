"""Feature 002 US2 (T009): import Codex++ .purpose.md files as provisional, provenance-linked records.

The fixture repo (tests/fixtures/purpose_repo) has one purpose file per edge case: correct (core),
caller drift both ways (util), deleted source (report), template (template), notebook source
(notebook), no headers (freeform), ambiguous basename (helpers).
"""
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
FIX = Path(__file__).resolve().parent / "fixtures"
from aec import edges as E  # noqa: E402
from aec.init import init  # noqa: E402
from aec.purpose_import import import_purpose  # noqa: E402
from aec.records import Store, check  # noqa: E402

PURPOSE_DIR = "codex_++/purpose_files"


def setup_repo():
    d = Path(tempfile.mkdtemp()) / "repo"
    shutil.copytree(FIX / "purpose_repo", d)
    init(d, owner="Zach")
    return d


def run(d, dry_run=False):
    return import_purpose(d, d / PURPOSE_DIR, d / ".aec" / "records.jsonl", E.snapshot(d), dry_run=dry_run)


def findings(rep, file):
    return {(f["kind"], f.get("detail", "")) for f in rep["findings"] if f["file"].endswith(file)}


class TestImport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = setup_repo()
        cls.rep = run(cls.d)
        cls.store = Store.load(cls.d / ".aec" / "records.jsonl")

    def rec(self, rid):
        return self.store.latest[rid]

    def test_records_are_provisional_with_provenance(self):  # FR-003, SC-002
        src, claim = self.rec("PF-core"), self.rec("PC-core")
        raw = (self.d / PURPOSE_DIR / "core.purpose.md").read_bytes()
        self.assertEqual(src.type, "source")
        self.assertEqual(src.get("ref"), f"{PURPOSE_DIR}/core.purpose.md")
        self.assertEqual(src.get("sha256"), hashlib.sha256(raw).hexdigest())
        self.assertEqual((src.get("ai_generated"), src.get("ai_verified")), (True, False))
        self.assertEqual(claim.type, "claim")
        self.assertEqual((claim.get("tier"), claim.get("epistemic")), ("candidate", "provisional"))
        self.assertIn("Run the cleaning step", claim.get("declared_text"))
        self.assertIn("Orchestrate cleaning through util", claim.get("declared_text"))
        rels = {(e["rel"], e["to"]) for e in claim.relations}
        self.assertIn(("depends_on", "PF-core@1"), rels)
        self.assertIn(("depends_on", "code:pkg.core"), rels)

    def test_import_never_creates_authority(self):  # FR-004
        imported = [r for r in self.store.records if r.id.startswith(("PF-", "PC-"))]
        self.assertTrue(imported)
        self.assertFalse(any(r.type == "authority" for r in imported))
        self.assertTrue(all(r.get("epistemic") == "provisional" for r in imported if r.type == "claim"))
        f = self.d / "probe.jsonl"
        f.write_text((self.d / ".aec" / "records.jsonl").read_text() + json.dumps(
            {"id": "D", "version": 1, "type": "decision", "subject": "design", "status": "accepted",
             "decided_by": "PC-core"}) + "\n")
        bad = {(x.rule, x.ref) for x in check(Store.load(f)) if x.level == "error"}
        self.assertIn(("authority", "D@1"), bad)

    def test_declared_vs_observed_callers(self):  # FR-006, US2-2
        fs = findings(self.rep, "util.purpose.md")
        self.assertIn(("declared-not-observed", "report"), fs)
        self.assertIn(("observed-not-declared", "pkg.cli"), fs)
        self.assertNotIn(("declared-not-observed", "core"), fs)  # core really imports util
        self.assertEqual(findings(self.rep, "core.purpose.md"), {("non-code-consumer", "developer")})

    def test_missing_source_still_imported(self):  # US2-3
        self.assertIn(("missing-source", "report.py"), findings(self.rep, "report.purpose.md"))
        claim = self.rec("PC-report")
        self.assertFalse(any(e["to"].startswith("code:") for e in claim.relations))

    def test_template_is_skipped(self):  # edge case
        self.assertNotIn("PC-template", self.store.latest)
        self.assertIn(f"{PURPOSE_DIR}/template.purpose.md", [s["file"] for s in self.rep["skipped"]])

    def test_notebook_source_has_no_code_link(self):  # edge case
        self.assertIn(("not-code", "src/notebooks/Demo.ipynb"), findings(self.rep, "notebook.purpose.md"))
        self.assertFalse(any(e["to"].startswith("code:") for e in self.rec("PC-notebook").relations))

    def test_headerless_file_is_text_only(self):  # edge case
        self.assertIn(("no-headers", ""), findings(self.rep, "freeform.purpose.md"))
        self.assertIn("nobody wrote headers", self.rec("PC-freeform").get("declared_text"))

    def test_ambiguous_name_is_not_guessed(self):  # FR-005
        fs = findings(self.rep, "helpers.purpose.md")
        self.assertIn(("ambiguous-source", "helpers.py: pkg/a/helpers.py, pkg/b/helpers.py"), fs)
        self.assertFalse(any(e["to"].startswith("code:") for e in self.rec("PC-helpers").relations))

    def test_records_check_clean_after_import(self):  # SC-001
        errors = [x for x in check(self.store, edges=E.snapshot(self.d)) if x.level == "error"]
        self.assertEqual(errors, [])


class TestIdempotence(unittest.TestCase):  # FR-007, US2-5
    def test_rerun_appends_nothing_and_change_makes_version_2(self):
        d = setup_repo()
        first = run(d)
        self.assertGreater(first["appended"], 0)
        records = (d / ".aec" / "records.jsonl").read_text()
        again = run(d)
        self.assertEqual(again["appended"], 0)
        self.assertEqual((d / ".aec" / "records.jsonl").read_text(), records)
        p = d / PURPOSE_DIR / "util.purpose.md"
        p.write_text(p.read_text().replace("Never mutate input", "Never mutate input; trim tabs too"))
        third = run(d)
        self.assertEqual(third["appended"], 2)
        st = Store.load(d / ".aec" / "records.jsonl")
        self.assertEqual((st.latest["PF-util"].version, st.latest["PC-util"].version), (2, 2))
        self.assertEqual(st.latest["PC-core"].version, 1)
        self.assertTrue((d / ".aec" / "records.jsonl").read_text().startswith(records))  # append-only

    def test_dry_run_writes_nothing(self):
        d = setup_repo()
        before = (d / ".aec" / "records.jsonl").read_text()
        rep = run(d, dry_run=True)
        self.assertGreater(rep["appended"], 0)  # what *would* be appended
        self.assertEqual((d / ".aec" / "records.jsonl").read_text(), before)


class TestCli(unittest.TestCase):
    def test_cli_import_and_missing_dir(self):
        import io
        from contextlib import redirect_stderr, redirect_stdout
        from aec.__main__ import main
        d = setup_repo()
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(main(["import-purpose", str(d)]), 0)
        self.assertIn("record(s) appended", out.getvalue())
        self.assertIn("[declared-not-observed]", out.getvalue())
        err = io.StringIO()
        with redirect_stderr(err), redirect_stdout(io.StringIO()):
            self.assertEqual(main(["import-purpose", str(d), "--dir", "nope"]), 2)
        self.assertIn("no purpose-file directory", err.getvalue())


if __name__ == "__main__":
    unittest.main()
