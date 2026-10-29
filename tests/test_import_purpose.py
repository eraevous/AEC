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


class TestContracts(unittest.TestCase):
    """WP0 violations of the old parser; existing TestImport is the clean decoy."""
    @classmethod
    def setUpClass(cls):
        cls.d = setup_repo()
        cls.rep = run(cls.d)
        cls.store = Store.load(cls.d / '.aec/records.jsonl')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.d.parent)

    def test_singular_prefixes_link(self):
        for suffix in ['bare', 'dash', 'hash']:
            with self.subTest(prefix=suffix):
                c = self.store.latest['PC-singular_'+suffix]
                self.assertEqual(c.get('declared_source_files'), ['pkg/core.py'])
                self.assertIn({'rel': 'depends_on', 'to': 'code:pkg.core'}, c.relations)

    def test_source_union_is_deduplicated_and_reported(self):
        c = self.store.latest['PC-both_sources']
        self.assertEqual(c.get('declared_source_files'), ['pkg/core.py', 'pkg/util.py'])
        self.assertEqual(len([e for e in c.relations if e['to'].startswith('code:')]), 2)
        self.assertIn('duplicate-source-field', {k for k, _ in findings(self.rep, 'both_sources.purpose.md')})
        self.assertNotIn('duplicate-source-field', {k for k, _ in findings(self.rep, 'core.purpose.md')})

    def test_structured_fields_and_raw_document(self):
        c = self.store.latest['PC-structured']
        raw = (self.d / PURPOSE_DIR / 'structured.purpose.md').read_text()
        self.assertEqual(c.get('declared_raw'), raw)
        self.assertEqual(c.get('declared_io'), [
            {'direction': 'input', 'name': 'data', 'type': '`str`', 'description': 'raw data', 'extra': 'retained'},
            {'direction': 'output', 'name': 'result', 'type': '`dict`', 'description': 'parsed result', 'extra': 'also kept'}])
        for field, text in [('declared_risks', 'Unverified'), ('declared_dependencies', 'pkg.util'),
                            ('declared_integration', 'Sequential stages'), ('declared_guarantees', 'append-only')]:
            self.assertIn(text, str(c.get(field)))
        fields = c.get('declared_fields')
        self.assertEqual(fields['ai-unknown'], 'keep this')
        self.assertEqual(fields['ai-role'], ['parser', 'reviewer'])
        self.assertEqual(fields['ai-downstream'], 'cli')
        self.assertEqual(fields['ai-cadence'], 'run')
        self.assertIn('intent responsibility', c.get('declared_sections'))
        self.assertIn('Preserve this responsibility.', str(c.get('declared_sections')))

    def test_long_text_not_truncated(self):
        c = self.store.latest['PC-long']
        self.assertGreater(len(c.get('declared_text')), 5000)
        self.assertTrue(c.get('declared_text').endswith('END-OF-DECLARATION'))
        self.assertEqual(c.get('declared_raw'), (self.d / PURPOSE_DIR / 'long.purpose.md').read_text())

    def test_all_heading_variants_and_split_io(self):
        from aec.purpose_import import parse
        for heading in ['Risks', 'Risks & Edge Cases', 'Dialogic Notes & Risks']:
            with self.subTest(heading=heading):
                self.assertIn('risk body', str(parse('### '+heading+'\nrisk body\n')['declared_risks']))
        for heading in ['Dependencies', 'Dependencies & Coordination']:
            self.assertIn('dependency body', str(parse('## '+heading+'\ndependency body\n')['declared_dependencies']))
        for heading in ['Integration & Coordination', '9\u2005Pipeline Integration']:
            self.assertIn('integration body', str(parse('## '+heading+'\nintegration body\n')['declared_integration']))
        for heading in ['Intent & Responsibility', 'Responsibilities']:
            self.assertIn('responsibility body', str(parse('## '+heading+'\nresponsibility body\n')['declared_sections']))
        p = parse('''## Inputs
| Name | Type | Description |
| --- | --- | --- |
| source | `str` | in |
## Outputs
| Name | Type | Description |
| --- | --- | --- |
| report | `str` | out |
''')
        self.assertEqual([x['direction'] for x in p['declared_io']], ['input', 'output'])
        self.assertEqual(parse('## Not a Contract\nplain prose\n')['declared_io'], [])

    def test_compact_io_empty_cells_and_pipe_types(self):
        from aec.purpose_import import parse
        p = parse("## Inputs\n|Name|Type|Description|\n|---|---|---|\n|value|`int | None`||\n")
        self.assertEqual(p['declared_io'], [
            {'direction': 'input', 'name': 'value', 'type': '`int | None`', 'description': ''}])
        p = parse("## Outputs\n|Name|Type|Description|\n|---|---|---|\n|result|int \\| None|plain|\n")
        self.assertEqual(p['declared_io'][0]['type'], r'int \| None')

    def test_singular_template_is_skipped(self):
        from aec.purpose_import import parse
        self.assertEqual(parse('# @ai-source-file: <file.py>')['headers']['ai-source-file'], '<file.py>')
        p = self.d / PURPOSE_DIR / 'singular_template.purpose.md'
        p.write_text('@ai-source-file: <file.py>\n@ai-intent: A template\n')
        try:
            report = run(self.d)
            self.assertIn(str(p.relative_to(self.d)), [s['file'] for s in report['skipped']])
        finally:
            p.unlink()


if __name__ == "__main__":
    unittest.main()
