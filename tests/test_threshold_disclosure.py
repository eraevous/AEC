"""Threshold disclosure: a check finding whose verdict turns on a threshold shows the threshold and what was measured.

Every verdict-governing threshold in `check` output shows rule, threshold, measured value and state (the level).
Findings that turn on no threshold (an unknown type, a dangling reference) show none: the decoys.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from aec.records import Store, check  # noqa: E402


def findings(*recs: dict):
    p = Path(tempfile.mkdtemp()) / "records.jsonl"
    p.write_text("".join(json.dumps(r) + "\n" for r in recs))
    return check(Store.load(p))


def one(fs, rule):
    hits = [f for f in fs if f.rule == rule]
    assert len(hits) == 1, [f.line() for f in fs]
    return hits[0]


EV = {"id": "EV-1", "version": 1, "type": "evidence", "text": "seen", "evidence_kind": "contract_conformance",
      "relations": [{"rel": "supports", "to": "C-1@1"}]}


class Disclosed(unittest.TestCase):
    def test_observed_tier(self):
        f = one(findings({"id": "C-1", "version": 1, "type": "claim", "tier": "observed", "text": "c"}, EV), "tier")
        self.assertEqual((f.threshold, f.measured), (">= 1 supporting evidence record produced by an evaluation", "0 of 1"))
        self.assertTrue(f.line().endswith("[threshold: >= 1 supporting evidence record produced by an evaluation; "
                                          "measured: 0 of 1]"))

    def test_prospective_digest(self):
        for digest, measured in [(None, "missing"), ("ABC", "3 characters, not all lowercase hex"), (7, "a JSON int")]:
            rec = {"id": "C-1", "version": 1, "type": "claim", "tier": "prospective", "text": "c"}
            if digest is not None:
                rec["frozen_sha256"] = digest
            f = one(findings(rec), "tier")
            self.assertEqual(f.measured, measured)
            self.assertEqual(f.threshold, "frozen_sha256 is 64 lowercase hex characters")

    def test_outcome_sufficiency(self):
        claim = {"id": "C-1", "version": 1, "type": "claim", "claim_category": "purpose_outcome", "text": "c"}
        f = one(findings(claim, EV), "outcome-sufficiency")
        self.assertEqual(f.measured, "0 of 1")

    def test_superseded_reference(self):
        r = {"id": "R-1", "version": 1, "type": "requirement", "text": "r"}
        f = one(findings(r, dict(r, version=2), dict(r, version=3),
                         {"id": "C-1", "version": 1, "type": "claim", "text": "c",
                          "relations": [{"rel": "depends_on", "to": "R-1@1"}]}), "superseded-reference")
        self.assertEqual((f.threshold, f.measured), ("referenced version is the latest", "@1; latest @3"))


class NotDisclosed(unittest.TestCase):
    def test_rule_without_threshold_shows_none(self):
        fs = findings({"id": "X-1", "version": 1, "type": "nonsense", "text": "x"},
                      {"id": "C-1", "version": 1, "type": "claim", "text": "c",
                       "relations": [{"rel": "depends_on", "to": "Q-9@1"}]})
        self.assertTrue(fs)
        for f in fs:
            self.assertIsNone(f.threshold, f.line())
            self.assertNotIn("[threshold:", f.line())


if __name__ == "__main__":
    unittest.main()
