"""WP0 doc-truth checks: real paths/CLI names, with broken-doc violations and clean decoys."""
import argparse
import re
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))


def registered_commands():
    from aec.__main__ import main
    commands = set()

    class Captured(Exception):
        pass

    def capture(parser, *args, **kwargs):
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                commands.update(action.choices)
        raise Captured

    with patch.object(argparse.ArgumentParser, 'parse_args', autospec=True, side_effect=capture):
        try:
            main([])
        except Captured:
            pass
    return commands


def doc_findings(text, root, commands):
    findings = []
    # Fenced blocks contain example filenames, while inline path tokens name repo artifacts.
    prose = re.sub(r'^```[^\n]*\n.*?^```\s*$', '', text, flags=re.M | re.S)
    for token in re.findall(r'(?<!`)`([^`\n]+)`(?!`)', prose):
        if re.fullmatch(r'\.[\w-]+\.md', token):  # suffix conventions, not file names
            continue
        if re.fullmatch(r'[\w.+/-]+', token) and ('/' in token or token.endswith(('.md', '.jsonl', '.py', '.toml', '.yml'))):
            if not (root / token).exists():
                findings.append('missing path: ' + token)
    for command in re.findall(r'\baec\s+([a-z][a-z-]*)\b', text):
        if command not in commands:
            findings.append('unknown command: ' + command)
    return findings


class TestDocsTruth(unittest.TestCase):
    def test_missing_path_violation_and_existing_path_decoy(self):
        self.assertEqual(doc_findings('Read `docs/no-such-contract.md`.', ROOT, set()),
                         ['missing path: docs/no-such-contract.md'])
        self.assertEqual(doc_findings('Read `README.md` and `.purpose.md` files.', ROOT, set()), [])

    def test_unregistered_command_violation_and_real_commands_decoy(self):
        commands = registered_commands()
        self.assertTrue(commands)
        self.assertEqual(doc_findings('Run `python -m aec imagined`.', ROOT, commands),
                         ['unknown command: imagined'])
        for command in commands:
            self.assertEqual(doc_findings('Run `python -m aec '+command+'`.', ROOT, commands), [])

    def test_examples_are_not_repository_artifacts(self):
        text = '```bash\npython -m aec edges --diff old.jsonl new.jsonl\n```\nRead `src/aec/`.'
        self.assertEqual(doc_findings(text, ROOT, registered_commands()), [])
        # Commands are still checked in fenced examples.
        self.assertIn('unknown command: imaginary', doc_findings('```sh\naec imaginary\n```', ROOT, registered_commands()))

    def test_readme_and_agents_tell_the_truth(self):
        for name in ['README.md', 'AGENTS.md']:
            with self.subTest(document=name):
                self.assertEqual(doc_findings((ROOT / name).read_text(), ROOT, registered_commands()), [])


class TestAnchorOutputTruth(unittest.TestCase):
    def test_output_templates_make_only_integrity_observations(self):
        from aec.sources import OUTPUT_TEMPLATES
        forbidden = re.compile(r'\bsupports\b|\bverifies the claim\b|\bproves\b|\bauthorized\b',re.I)
        self.assertIsNone(forbidden.search('\n'.join(OUTPUT_TEMPLATES.values())))
        # Violation: the same check catches overclaiming; neutral source-state text is the decoy.
        self.assertIsNotNone(forbidden.search('This anchor proves the claim.'))
        self.assertIsNone(forbidden.search('artifact bytes and locator match'))


if __name__ == '__main__':
    unittest.main()
