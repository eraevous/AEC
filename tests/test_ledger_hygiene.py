"""Spec 006 (C-09, C-21): anchors into append-only files and byte-identical duplicate record lines.

Fixtures and decoys were written before the implementation (Constitution III).
Synthetic sources exist only in temporary directories.
"""
import hashlib
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))
from aec.__main__ import main
from aec.records import Record, Store, check
from aec.sources import SourceContext

VALID = b'first\nshared needle\nthird\nshared needle\nlast\n'
FIXTURES = ROOT / 'tests/fixtures'


def run_cli(*args):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            result = main(list(args))
        except SystemExit as e:
            result = e.code
    return result, out.getvalue(), err.getvalue()


class AppendedFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.repo, corpus = base / 'repo', base / 'corpus'
        (self.repo / '.aec').mkdir(parents=True)
        corpus.mkdir()
        (corpus / 'valid.txt').write_bytes(VALID)
        (corpus / 'grown.txt').write_bytes(VALID + b'appended line\n')
        (corpus / 'edited.txt').write_bytes(b'FIRST\n' + VALID[6:] + b'appended line\n')
        (corpus / 'short.txt').write_bytes(VALID[:20])
        self.fixture = json.loads((FIXTURES / 'anchors/appended.json').read_text())
        self.config = {'roots': {'corpus': '../corpus', 'ledger': '../corpus'},
                       'append_only': self.fixture['append_only']}
        self.write_config()
        self.records = self.repo / '.aec/records.jsonl'

    def write_config(self):
        (self.repo / '.aec/sources.json').write_text(json.dumps(self.config))

    def anchor(self, case):
        anchor = {k: v for k, v in case.items() if k not in {'id', 'expected'}}
        anchor.setdefault('root', 'corpus')
        anchor['sha256'] = hashlib.sha256(VALID).hexdigest()
        return anchor


class TestAppendedAnchors(AppendedFixture):
    def test_fixture_cases_states_and_findings(self):
        self.assertEqual(len(VALID), 45)
        for case in self.fixture['cases']:
            with self.subTest(case=case['id']):
                r = Record('C', 1, 'claim', text='A conclusion', data={'anchors': [self.anchor(case)]})
                ctx = SourceContext(self.repo)
                state = ctx.inspect_record(r)[0].state
                fs = check(Store([r]), sources=ctx)
                if case['expected'] == 'error':
                    self.assertIsNone(state)
                    self.assertEqual([(f.level, f.rule) for f in fs], [('error', 'anchor-shape')])
                else:
                    self.assertEqual(state, case['expected'])
                    warned = case['expected'] not in ('verified', 'appended')
                    self.assertEqual([f.level for f in fs], ['warning'] if warned else [])

    def test_appended_is_labelled_distinctly_in_check_and_show_output(self):
        grown = self.anchor({'path': 'grown.txt', 'prefix_bytes': 45, 'locator': 'q:third'})
        self.records.write_text(json.dumps({'id': 'C', 'version': 1, 'type': 'claim', 'text': 'x',
                                            'anchors': [grown]}) + '\n')
        code, out, _ = run_cli('check', str(self.records))
        self.assertEqual(code, 0)
        self.assertIn('state=appended', out)
        self.assertNotIn('state=verified', out)
        self.assertNotIn('state=mismatch', out)
        self.assertIn('0 error(s), 0 warning(s)', out)
        self.assertEqual(out, run_cli('check', str(self.records))[1])
        code, shown, _ = run_cli('source', 'show', 'C@1', '--repo', str(self.repo), '--context', '0')
        self.assertEqual(code, 0)
        self.assertIn('state=appended', shown)
        self.assertIn('3 | third', shown)
        self.assertIn('NOTE:', shown)
        self.assertIn('14 byte(s) appended', shown)
        self.assertNotIn('WARNING', shown)

    def test_appended_detail_does_not_claim_more_than_integrity(self):
        from aec.sources import OUTPUT_TEMPLATES
        text = OUTPUT_TEMPLATES['appended'].lower()
        for word in ('support', 'proves', 'authoriz', 'verifies the claim'):
            self.assertNotIn(word, text)
        self.assertIn('not checked', text)

    def test_declared_append_only_needs_line_boundary_prefix(self):
        # The anchored original must end where a line ended; a mid-line prefix is not searched.
        mid = Path(self.tmp.name) / 'corpus/midline.txt'
        mid.write_bytes(VALID[:-1] + b' continued\n')
        self.config['append_only']['ledger'].append('midline.txt')
        self.write_config()
        anchor = self.anchor({'root': 'ledger', 'path': 'midline.txt', 'locator': 'L1'})
        anchor['sha256'] = hashlib.sha256(VALID[:-1]).hexdigest()
        r = Record('C', 1, 'claim', data={'anchors': [anchor]})
        self.assertEqual(SourceContext(self.repo).inspect_record(r)[0].state, 'mismatch')

    def test_explicit_prefix_ending_mid_line_does_not_pass_growth_of_that_line(self):
        # Fix round (Kate, blocking): appended bytes that extend the anchored final line change it.
        (Path(self.tmp.name) / 'corpus/extended.txt').write_bytes(VALID[:-1] + b' continued\n')
        (Path(self.tmp.name) / 'corpus/unterminated.txt').write_bytes(VALID[:-1])
        cases = [('extended.txt', VALID[:-1], 'L5', 'mismatch'),        # violating: last line grew in place
                 ('extended.txt', VALID[:-1], 'L1', 'mismatch'),        # whatever line the locator names
                 ('grown.txt', VALID, 'L5', 'appended'),                # decoy: newline-ended prefix, then growth
                 ('unterminated.txt', VALID[:-1], 'L5', 'verified')]    # decoy: mid-line prefix, file unchanged
        for path, anchored, locator, expected in cases:
            with self.subTest(path=path, locator=locator):
                anchor = self.anchor({'path': path, 'prefix_bytes': len(anchored), 'locator': locator})
                anchor['sha256'] = hashlib.sha256(anchored).hexdigest()
                r = Record('C', 1, 'claim', data={'anchors': [anchor]})
                ctx = SourceContext(self.repo)
                self.assertEqual(ctx.inspect_record(r)[0].state, expected)
                warned = [f.level for f in check(Store([r]), sources=ctx)]
                self.assertEqual(warned, ['warning'] if expected == 'mismatch' else [])

    def test_appended_note_says_a_later_entry_may_supersede(self):
        from aec.sources import OUTPUT_TEMPLATES
        self.assertIn('may supersede', OUTPUT_TEMPLATES['appended'])
        self.assertNotIn('supersed', OUTPUT_TEMPLATES['verified'])

    def test_malformed_append_only_configuration_is_a_usage_error(self):
        for bad in ([], {'ledger': 'grown.txt'}, {'ledger': ['../escape.txt']}, {'nowhere': ['grown.txt']},
                    {'ledger': ['']}):
            with self.subTest(bad=bad):
                self.config['append_only'] = bad
                self.write_config()
                r = Record('C', 1, 'claim', data={'anchors': [self.anchor({'path': 'valid.txt', 'locator': 'L1'})]})
                with self.assertRaises(ValueError):
                    check(Store([r]), sources=SourceContext(self.repo))
        self.config['append_only'] = {'.': ['notes.md'], 'ledger': []}
        self.write_config()
        r = Record('C', 1, 'claim', data={'anchors': [self.anchor({'path': 'valid.txt', 'locator': 'L1'})]})
        self.assertEqual(check(Store([r]), sources=SourceContext(self.repo)), [])


class TestDuplicateLines(unittest.TestCase):
    def test_byte_identical_copy_is_one_record_and_a_warning(self):
        path = FIXTURES / 'duplicates/identical.jsonl'
        store = Store.load(path)
        self.assertEqual([r.ref for r in store.records], ['AU-o@1', 'R-merge@1', 'C-other@1'])
        fs = check(store)
        self.assertEqual([(f.level, f.rule, f.ref) for f in fs], [('warning', 'duplicate-line', 'R-merge@1')])
        self.assertIn('line 5', fs[0].msg)
        self.assertIn('line 3', fs[0].msg)
        code, out, _ = run_cli('check', str(path))
        self.assertEqual(code, 0)
        self.assertIn('[WARNING] duplicate-line: R-merge@1', out)
        self.assertEqual(out, run_cli('check', str(path))[1])

    def test_differing_duplicates_stay_errors(self):
        for name in ('conflicting.jsonl', 'reformatted.jsonl'):
            with self.subTest(name=name):
                path = FIXTURES / 'duplicates' / name
                fs = check(Store.load(path))
                self.assertEqual([(f.level, f.rule) for f in fs], [('error', 'unique')])
                self.assertEqual(run_cli('check', str(path))[0], 1)

    def test_whitespace_or_line_ending_differences_stay_errors(self):
        # Fix round (both reviewers, blocking): lines are compared as written, not after strip().
        self.assertTrue((FIXTURES / 'duplicates/trailing-space.jsonl').read_bytes().endswith(b'} \n'))
        lines = (FIXTURES / 'duplicates/identical.jsonl').read_bytes().split(b'\n')
        # CRLF is built here, not committed, so a checkout's line-ending conversion cannot change the fixture.
        variants = {'trailing-space': (FIXTURES / 'duplicates/trailing-space.jsonl').read_bytes(),
                    'crlf': b'\n'.join(lines[:4]) + b'\n' + lines[4] + b'\r\n',
                    'leading-space': b'\n'.join(lines[:4]) + b'\n ' + lines[4] + b'\n'}
        with tempfile.TemporaryDirectory() as tmp:
            for name, data in variants.items():
                with self.subTest(name=name):
                    path = Path(tmp) / f'{name}.jsonl'
                    path.write_bytes(data)
                    fs = check(Store.load(path))
                    self.assertIn(('error', 'unique'), [(f.level, f.rule) for f in fs])
                    self.assertNotIn('duplicate-line', [f.rule for f in fs])
                    self.assertEqual(run_cli('check', str(path))[0], 1)
            # decoy: the same file with a byte-identical copy (LF throughout) is still only the warning
            path = Path(tmp) / 'identical.jsonl'
            path.write_bytes(b'\n'.join(lines))
            fs = check(Store.load(path))
            self.assertEqual([(f.level, f.rule) for f in fs], [('warning', 'duplicate-line')])
            # decoy: CRLF on every line is still byte-identical between the two copies
            path.write_bytes(b'\r\n'.join(lines))
            fs = check(Store.load(path))
            self.assertEqual([(f.level, f.rule) for f in fs], [('warning', 'duplicate-line')])

    def test_identical_copy_after_a_conflicting_version_is_still_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = '{"id": "R", "version": 1, "type": "requirement", "text": "one"}\n'
            b = '{"id": "R", "version": 1, "type": "requirement", "text": "two"}\n'
            path = Path(tmp) / 'records.jsonl'
            path.write_text(a + b + a)
            rules = sorted((f.level, f.rule) for f in check(Store.load(path)))
            self.assertIn(('error', 'unique'), rules)

    def test_records_file_is_never_rewritten(self):
        path = FIXTURES / 'duplicates/identical.jsonl'
        before = path.read_bytes()
        run_cli('check', str(path))
        self.assertEqual(path.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
