"""US2 tests (T012, T013): code changes -> affected conclusions; dangling code references."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
FIX = Path(__file__).resolve().parent / "fixtures"
from aec import edges as E  # noqa: E402
from aec.code_impact import code_impact  # noqa: E402
from aec.records import Store, check  # noqa: E402


class TestCodeImpact(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = Store.load(FIX / "code_impact" / "records.jsonl")
        cls.v1, cls.v2 = E.snapshot(FIX / "edges_pkg_v1"), E.snapshot(FIX / "edges_pkg_v2")
        cls.rep, cls.events = code_impact(cls.store, cls.v1, cls.v2)
        cls.st = {k: v.status for k, v in cls.rep.impacts.items()}

    def test_changed_symbol_reaches_requirement_claim_and_decision(self):  # FR-007, US2-1
        self.assertEqual(self.st["REQ-load@1"], "stale")
        self.assertEqual(self.st["CL-load@1"], "stale")
        self.assertEqual(self.st["D-ship@1"], "needs_review")
        self.assertIn("code:pkg.core.Worker.step", self.rep.impacts["REQ-load@1"].because[0])

    def test_deleted_symbol_leaves_requirement_unjustified(self):  # US2-2
        self.assertEqual(self.st["REQ-fetch@1"], "unjustified")

    def test_unchanged_linked_code_is_not_flagged(self):  # decoy, SC-004
        self.assertNotIn("REQ-extras@1", self.st)

    def test_no_change_no_impact(self):  # US2-3
        rep, events = code_impact(self.store, self.v1, self.v1)
        self.assertEqual((events, rep.impacts), ([], {}))


class TestDanglingCodeRefs(unittest.TestCase):  # T013 / FR-006
    def test_dangling_and_valid(self):
        f = Path(tempfile.mkdtemp()) / "r.jsonl"
        f.write_text("\n".join(json.dumps(x) for x in [
            {"id": "R1", "version": 1, "type": "requirement", "relations": [{"rel": "implemented_by", "to": "code:pkg.core.load"}]},
            {"id": "R2", "version": 1, "type": "requirement", "relations": [{"rel": "implemented_by", "to": "code:pkg.core.lod"}]},
        ]))
        fs = check(Store.load(f), edges=E.snapshot(FIX / "edges_pkg_v1"))
        bad = {(x.rule, x.ref) for x in fs if x.level == "error"}
        self.assertIn(("code-reference", "R2@1"), bad)
        self.assertNotIn(("code-reference", "R1@1"), bad)

    def test_code_refs_without_snapshot_are_not_errors(self):
        f = Path(tempfile.mkdtemp()) / "r.jsonl"
        f.write_text(json.dumps({"id": "R", "version": 1, "type": "requirement",
                                 "relations": [{"rel": "implemented_by", "to": "code:x.y"}]}))
        self.assertEqual([x for x in check(Store.load(f)) if x.level == "error"], [])


class TestObservedOn(unittest.TestCase):  # feature 002 US4 / FR-010 (T004)
    """Evidence observed on code: a code change asks for an applicability review, never invalidates."""

    @classmethod
    def setUpClass(cls):
        f = Path(tempfile.mkdtemp()) / "r.jsonl"
        f.write_text("\n".join(json.dumps(x) for x in [
            {"id": "EV-step", "version": 1, "type": "evidence", "evidence_kind": "behavioral_observation",
             "relations": [{"rel": "observed_on", "to": "code:pkg.core.Worker.step"}, {"rel": "supports", "to": "CL-a@1"}]},
            {"id": "EV-fetch", "version": 1, "type": "evidence",
             "relations": [{"rel": "observed_on", "to": "code:pkg.core.fetch"}, {"rel": "supports", "to": "CL-b@1"}]},
            {"id": "EV-extras", "version": 1, "type": "evidence",
             "relations": [{"rel": "observed_on", "to": "code:pkg.extras.helper"}, {"rel": "supports", "to": "CL-c@1"}]},
            {"id": "CL-a", "version": 1, "type": "claim"},
            {"id": "CL-b", "version": 1, "type": "claim"},
            {"id": "CL-c", "version": 1, "type": "claim"},
        ]))
        rep, _ = code_impact(Store.load(f), E.snapshot(FIX / "edges_pkg_v1"), E.snapshot(FIX / "edges_pkg_v2"))
        cls.st = {k: v.status for k, v in rep.impacts.items()}

    def test_changed_code_puts_evidence_and_its_claim_under_review(self):
        self.assertEqual(self.st["EV-step@1"], "needs_review")
        self.assertEqual(self.st["CL-a@1"], "needs_review")

    def test_deleted_code_still_only_review(self):
        self.assertEqual(self.st["EV-fetch@1"], "needs_review")
        self.assertEqual(self.st["CL-b@1"], "needs_review")
        self.assertNotIn("unjustified", self.st.values())

    def test_unrelated_code_flags_nothing(self):  # decoy, SC-005
        self.assertNotIn("EV-extras@1", self.st)
        self.assertNotIn("CL-c@1", self.st)


if __name__ == "__main__":
    unittest.main()
