"""Records location as a setting (HO-RK-20261103-5J0W): fixtures for a configured
non-default location, a decoy for the default sibling layout, and degradation to
`unavailable` when the location is missing."""
import hashlib
import io
import json
import os
import re
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))
from aec.__main__ import main
from aec.records import Record, Store, check
from aec.sources import DEFAULT_RECORDS_ROOT, RECORDS_ENV, SourceContext, render_search

LEDGER = b'{"id": "DEC-001", "text": "one canonical decision"}\n'
DECOY = b'{"id": "DEC-001", "text": "a decoy that must not be read"}\n'
PIN = 'a7fa03a362ca1c0cd6dc911bec4d9f0b54f9bf7e'


class RecordsLocation(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name)
        self.repo = self.base / 'repo'
        (self.repo / '.aec').mkdir(parents=True)
        self.mine = self.base / 'elsewhere' / 'my-records'          # a non-default location
        self.sibling = self.base / 'relay-kit-private'              # the default layout, as a decoy
        for folder, raw in ((self.mine, LEDGER), (self.sibling, DECOY)):
            (folder / 'governance').mkdir(parents=True)
            (folder / 'governance/decisions.jsonl').write_bytes(raw)
        env = patch.dict(os.environ)
        env.start()
        self.addCleanup(env.stop)
        os.environ.pop(RECORDS_ENV, None)

    def config(self, **data):
        (self.repo / '.aec/sources.json').write_text(json.dumps(data))

    def state(self, root, raw=LEDGER):
        anchor = {'root': root, 'path': 'governance/decisions.jsonl',
                  'sha256': hashlib.sha256(raw).hexdigest(), 'locator': 'q:"id": "DEC-001"'}
        rec = Record('DEC-001', 1, 'decision', text='projection', data={'anchors': [anchor]})
        ctx = SourceContext(self.repo)
        return ctx.inspect_record(rec)[0].state, check(Store([rec]), sources=ctx)

    # configured non-default location
    def test_env_points_the_records_root_at_a_non_default_location(self):
        os.environ[RECORDS_ENV] = str(self.mine)
        self.assertEqual(self.state(DEFAULT_RECORDS_ROOT), ('verified', []))

    def test_env_relative_path_resolves_from_the_working_directory_like_relay_kit(self):
        os.environ[RECORDS_ENV] = 'elsewhere/my-records'
        cwd = Path.cwd()
        os.chdir(self.base)
        self.addCleanup(os.chdir, cwd)
        self.assertEqual(self.state(DEFAULT_RECORDS_ROOT)[0], 'verified')

    def test_config_names_which_root_holds_the_records(self):
        self.config(roots={'kit': '../elsewhere/my-records'}, records_root='kit')
        self.assertEqual(self.state('kit')[0], 'verified')

    def test_env_takes_precedence_over_the_configured_path(self):
        self.config(roots={'relay-kit-private': '../relay-kit-private'}, records_root='relay-kit-private')
        os.environ[RECORDS_ENV] = str(self.mine)
        self.assertEqual(self.state('relay-kit-private')[0], 'verified')
        self.assertEqual(self.state('relay-kit-private', DECOY)[0], 'mismatch')  # the sibling was not read

    def test_env_does_not_move_other_roots(self):
        self.config(roots={'relay-kit-private': '../relay-kit-private'}, records_root='relay-kit-private')
        os.environ[RECORDS_ENV] = str(self.mine)
        self.assertEqual(self.state(DEFAULT_RECORDS_ROOT)[0], 'unavailable')

    def test_search_includes_the_env_records_root(self):
        os.environ[RECORDS_ENV] = str(self.mine)
        out = render_search(Store([]), 'one canonical decision', SourceContext(self.repo))
        self.assertIn(f'root="{DEFAULT_RECORDS_ROOT}"', out)
        self.assertNotIn('decoy', out)

    # the default (Zach's sibling layout) and its decoy
    def test_sibling_layout_still_works_when_configured(self):
        self.config(roots={'relay-kit-private': '../relay-kit-private'}, records_root='relay-kit-private')
        self.assertEqual(self.state('relay-kit-private', DECOY), ('verified', []))

    def test_decoy_unconfigured_sibling_is_never_read_implicitly(self):
        for root in ('relay-kit-private', DEFAULT_RECORDS_ROOT):
            with self.subTest(root=root):
                state, findings = self.state(root, DECOY)
                self.assertEqual(state, 'unavailable')
                self.assertEqual([f.level for f in findings], ['warning'])

    def test_empty_env_is_ignored(self):
        self.config(roots={'relay-kit-private': '../relay-kit-private'}, records_root='relay-kit-private')
        os.environ[RECORDS_ENV] = '  '
        self.assertEqual(self.state('relay-kit-private', DECOY)[0], 'verified')

    # a missing or unusable location degrades to unavailable, never a crash
    def test_missing_location_is_unavailable_not_a_crash(self):
        for value in (str(self.base / 'nowhere'), 'https://example.com/records', 'bad\npath'):
            with self.subTest(value=value):
                os.environ[RECORDS_ENV] = value
                state, findings = self.state(DEFAULT_RECORDS_ROOT)
                self.assertEqual(state, 'unavailable')
                self.assertEqual([f.rule for f in findings], ['anchor-unavailable'])

    def test_check_cli_exits_zero_with_a_missing_location(self):
        os.environ[RECORDS_ENV] = str(self.base / 'nowhere')
        anchor = {'root': DEFAULT_RECORDS_ROOT, 'path': 'governance/decisions.jsonl',
                  'sha256': hashlib.sha256(LEDGER).hexdigest(), 'locator': 'L1'}
        records = self.repo / '.aec/records.jsonl'
        records.write_text(json.dumps({'id': 'C', 'version': 1, 'type': 'claim', 'text': 'x',
                                       'anchors': [anchor]}) + '\n')
        out, err = io.StringIO(), io.StringIO()
        cwd = Path.cwd()
        os.chdir(self.repo)
        self.addCleanup(os.chdir, cwd)
        with redirect_stdout(out), redirect_stderr(err):
            code = main(['check', str(records)])
        self.assertEqual(code, 0, err.getvalue())
        self.assertIn('unavailable', out.getvalue())

    def test_malformed_records_root_is_a_config_error_like_other_roots(self):
        self.config(roots={}, records_root=['not', 'a', 'name'])
        with self.assertRaises(ValueError):
            SourceContext(self.repo).roots


class RepositoryDefaults(unittest.TestCase):
    def test_this_repository_keeps_the_owners_sibling_layout(self):
        data = json.loads((ROOT / '.aec/sources.json').read_text())
        self.assertEqual(data['records_root'], 'relay-kit-private')
        self.assertEqual(data['roots']['relay-kit-private'], '../relay-kit-private')

    def test_relay_kit_is_pinned_to_one_ref_everywhere(self):
        refs = {}
        for path in [ROOT / 'README.md', *(ROOT / 'docs').rglob('*.md'), ROOT / '.github/workflows/ci.yml']:
            if 'evaluations' in path.parts or 'history' in path.parts:
                continue
            for ref in re.findall(r'github\.com/eraevous/relay-kit(?:\.git)?@([\w.\-]+)', path.read_text()):
                refs.setdefault(ref, []).append(path.relative_to(ROOT).as_posix())
        self.assertEqual(set(refs), {PIN}, refs)
        doc = (ROOT / 'docs/integrations/relay-kit.md').read_text()
        self.assertIn(f'pip install "relay-kit @ git+https://github.com/eraevous/relay-kit@{PIN}"', doc)

    def test_architecture_names_relay_kit_private_only_as_the_owners_instance(self):
        for line in (ROOT / 'docs/architecture.md').read_text().splitlines():
            if 'relay-kit-private' in line:
                self.assertIn("Zach's", line, line)


if __name__ == '__main__':
    unittest.main()
