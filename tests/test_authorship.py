"""Authorship of semantic records (Dual-Channel Coding correspondence test with independence).

Two optional fields say who wrote a record and how that author stands to the code it describes:
`authored_by` (an actor such as `zach`, `claude:aec` or `chatgpt:kate`, optionally `#session`) and
`author_role` (`owner`, `independent` or `implementer`: the agent that wrote the code). They are a field, not a
workflow: `check` only validates their shape. Violating cases first, then decoys that must stay clean.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from aec.records import Store, check  # noqa: E402


def findings(**extra):
    rec = {"id": "R-1", "version": 1, "type": "requirement", "text": "r", **extra}
    p = Path(tempfile.mkdtemp()) / "records.jsonl"
    p.write_text(json.dumps(rec) + "\n")
    return [(f.level, f.rule) for f in check(Store.load(p))]


class Violations(unittest.TestCase):
    def test_unknown_role_is_an_error(self):
        self.assertEqual(findings(authored_by="claude:aec", author_role="reviewer"), [("error", "authorship")])

    def test_role_without_author_is_an_error(self):
        self.assertEqual(findings(author_role="owner"), [("error", "authorship")])

    def test_non_string_or_empty_author_is_an_error(self):
        for bad in (7, "", ["claude:aec"], None):
            with self.subTest(bad=bad):
                self.assertEqual(findings(authored_by=bad), [("error", "authorship")])

    def test_malformed_actor_is_a_warning(self):
        self.assertEqual(findings(authored_by="Claude Code"), [("warning", "authorship")])


class Decoys(unittest.TestCase):
    def test_no_fields_is_clean(self):
        self.assertEqual(findings(), [])

    def test_valid_actors_and_roles_are_clean(self):
        for author, role in [("zach", "owner"), ("claude:aec", "implementer"), ("chatgpt:kate", "independent"),
                             ("claude:aec#01GZK2Kne8fYjfQJjz1kDge9", "implementer"), ("codex:aec", None)]:
            with self.subTest(author=author):
                extra = {"authored_by": author} if role is None else {"authored_by": author, "author_role": role}
                self.assertEqual(findings(**extra), [])


if __name__ == "__main__":
    unittest.main()
