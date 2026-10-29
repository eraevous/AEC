"""WP0 history reconstruction: append-only candidate records, safe refusal and decoys."""
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))
from aec.records import Store, check


class TestReconstruction(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / '.aec/reconstructed').mkdir(parents=True)
        (self.root / 'docs').mkdir()
        self.source = self.root / 'docs/log.md'
        self.source.write_text('# History\nOriginal choice.\nCorrection.\n')
        self.records = self.root / '.aec/records.jsonl'
        self.prefix = b'// existing bytes, deliberately no final newline\n{"id":"P","version":1,"type":"purpose","text":"Keep"}'
        self.records.write_bytes(self.prefix)
        self.input = self.root / '.aec/reconstructed/2026-10-history.jsonl'
        self.rows = [dict(id='OLD', text='Original', source_path='docs/log.md', source_section='History', source_quote='Original choice.'),
                     dict(id='NEW', text='Correction', source_path='docs/log.md', source_section='History', source_quote='Correction.', supersedes='OLD@1')]
        spec = importlib.util.spec_from_file_location('reconstruct_decisions', ROOT / 'tools/reconstruct_decisions.py')
        self.tool = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.tool)

    def run_(self):
        self.input.write_text(''.join(json.dumps(r)+'\n' for r in self.rows))
        return self.tool.reconstruct(self.root)

    def test_hash_candidate_reversal_prefix_and_confirmation_list(self):
        self.run_()
        self.assertTrue(self.records.read_bytes().startswith(self.prefix))
        store = Store.load(self.records)
        for id in ['OLD', 'NEW']:
            d = store.latest[id]
            self.assertEqual((d.get('origin'), d.get('status'), d.get('tier')), ('reconstructed', 'proposed', 'candidate'))
            src = store.by_ref[next(r['to'] for r in d.relations if r['rel']=='depends_on')]
            self.assertEqual(src.get('sha256'), hashlib.sha256(self.source.read_bytes()).hexdigest())
            self.assertEqual(src.get('section'), 'History')
            self.assertTrue(src.get('quote'))
            self.assertEqual(src.get('origin'), 'reconstructed')
        self.assertIn({'rel':'supersedes','to':'OLD@1'}, store.latest['NEW'].relations)
        self.assertEqual(check(store), [])
        table = (self.root / 'docs/decisions-to-confirm.md').read_text()
        self.assertIn('OLD@1', table)
        self.assertIn('NEW@1', table)
        self.assertIn('|  |', table)  # confirmation deliberately empty

    def test_idempotence_and_changed_source_append_versions(self):
        self.run_()
        first = self.records.read_bytes()
        table = (self.root / 'docs/decisions-to-confirm.md').read_bytes()
        self.assertEqual(self.run_()['appended'], 0)
        self.assertEqual(self.records.read_bytes(), first)
        self.assertEqual((self.root / 'docs/decisions-to-confirm.md').read_bytes(), table)
        self.source.write_text(self.source.read_text()+'Additional context.\n')
        self.run_()
        self.assertTrue(self.records.read_bytes().startswith(first))
        store = Store.load(self.records)
        self.assertEqual(store.latest['OLD'].version, 2)
        self.assertIn({'rel':'supersedes','to':'OLD@1'}, store.latest['OLD'].relations)

    def test_accepted_input_is_refused_atomically(self):
        self.rows[1]['status'] = 'accepted'
        with self.assertRaisesRegex(ValueError, 'proposed'):
            self.run_()
        self.assertEqual(self.records.read_bytes(), self.prefix)
        self.assertFalse((self.root / 'docs/decisions-to-confirm.md').exists())

    def test_false_quote_bad_section_and_dangling_reversal_are_refused(self):
        for key, value in [('source_quote','Not in the source'), ('source_section','Imaginary'), ('supersedes','MISSING@1')]:
            with self.subTest(key=key):
                original = self.rows[1].copy()
                self.rows[1][key] = value
                with self.assertRaises(ValueError):
                    self.run_()
                self.assertEqual(self.records.read_bytes(), self.prefix)
                self.rows[1] = original

    def test_duplicate_ids_and_authority_fields_are_refused(self):
        self.rows.append(self.rows[0].copy())
        with self.assertRaises(ValueError):
            self.run_()
        self.rows.pop()
        self.rows[0]['decided_by'] = 'AU-zach'
        with self.assertRaises(ValueError):
            self.run_()
        self.assertEqual(self.records.read_bytes(), self.prefix)


if __name__ == '__main__':
    unittest.main()
