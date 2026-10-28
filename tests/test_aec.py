"""Tests for aec check and aec impact.

  PYTHONPATH=src python3 -m unittest discover -s tests

The MtG pilot scenarios are real events from 2026-10-26, so the expected outcomes are the conclusions
the human and model reviewers actually reached. Any change to them is a behavior change to justify.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from aec.impact import impact  # noqa: E402
from aec.records import Store, check  # noqa: E402

PILOT = ROOT / "examples" / "mtg-pilot"


def changes(name):
    return [json.loads(l) for l in (PILOT / name).read_text().splitlines() if l.strip() and not l.startswith("//")]


def statuses(rep):
    return {k: v.status for k, v in rep.impacts.items()}


def store_from(lines):
    f = Path(tempfile.mkdtemp()) / "r.jsonl"
    f.write_text("\n".join(json.dumps(x) for x in lines))
    return Store.load(f)


class TestPilot(unittest.TestCase):
    def setUp(self):
        self.store = Store.load(PILOT / "records.jsonl")

    def test_pilot_records_check_clean(self):
        self.assertEqual([f for f in check(self.store) if f.level == "error"], [])

    def test_duty_timing_breaks_recovery_claim_not_the_receiver_hypothesis(self):
        s = statuses(impact(self.store, changes("scenario1_duty_timing.jsonl")))
        self.assertEqual(s["CL-duty-rebuild@1"], "unjustified")
        self.assertEqual(s["CL-recovery-improved@1"], "unjustified")
        self.assertEqual(s["D-0003@1"], "needs_review")      # decisions are flagged, never invalidated by the tool
        self.assertNotIn("CL-binding-receivers@1", s)       # the other line of the decision still stands

    def test_census_overclaim_only_weakens_the_hypothesis(self):
        s = statuses(impact(self.store, changes("scenario2_census_overclaim.jsonl")))
        self.assertEqual(s, {"CL-binding-receivers@1": "weakened"})  # Zach's observed account still supports it

    def test_unauthorized_amendment_is_stale_and_reported(self):
        rep = impact(self.store, changes("scenario3_p01_amendment_unauthorized.jsonl"))
        self.assertEqual(statuses(rep), {"CL-boundary-rule@1": "stale", "D-0002@1": "stale"})
        self.assertTrue(any("unauthorized revision of committed requirement P-01@1" in f for f in rep.findings))

    def test_authorized_amendment_is_rebaseline_not_drift(self):
        rep = impact(self.store, changes("scenario4_p01_amendment_authorized.jsonl"))
        self.assertEqual(statuses(rep), {"CL-boundary-rule@1": "rebaseline", "D-0002@1": "rebaseline"})
        self.assertEqual(rep.findings, [])

    def test_provisional_criterion_change_is_exploratory(self):
        rep = impact(self.store, changes("scenario5_criterion_exploratory.jsonl"))
        self.assertEqual(statuses(rep), {"D-0003@1": "exploratory"})
        self.assertEqual(rep.findings, [])

    def test_decoy_change_flags_nothing(self):
        rep = impact(self.store, changes("scenario6_decoy_inventory.jsonl"))
        self.assertEqual(rep.impacts, {})


class TestSemantics(unittest.TestCase):
    BASE = [
        {"id": "AU", "version": 1, "type": "authority", "governs": ["s"]},
        {"id": "A", "version": 1, "type": "assumption", "subject": "s"},
        {"id": "C", "version": 1, "type": "claim", "relations": [{"rel": "depends_on", "to": "A@1"}]},
        {"id": "C2", "version": 1, "type": "claim", "relations": [{"rel": "depends_on", "to": "C@1"}]},
        {"id": "E1", "version": 1, "type": "evidence", "relations": [{"rel": "supports", "to": "K@1"}]},
        {"id": "E2", "version": 1, "type": "evidence", "relations": [{"rel": "supports", "to": "K@1"}]},
        {"id": "K", "version": 1, "type": "claim"},
    ]

    def test_transitive_necessary_dependency(self):
        s = statuses(impact(store_from(self.BASE), [{"change": "retract", "target": "A@1"}]))
        self.assertEqual(s, {"C@1": "unjustified", "C2@1": "unjustified"})

    def test_last_support_removed_is_unjustified(self):
        st = store_from(self.BASE)
        s = statuses(impact(st, [{"change": "retract", "target": "E1@1"}, {"change": "retract", "target": "E2@1"}]))
        self.assertEqual(s["K@1"], "unjustified")

    def test_authority_must_govern_the_subject(self):
        lines = self.BASE + [{"id": "AU2", "version": 1, "type": "authority", "governs": ["other"]}]
        s = statuses(impact(store_from(lines), [{"change": "revise", "target": "A@1", "authorized_by": "AU2"}]))
        self.assertEqual(s["C@1"], "stale")
        s = statuses(impact(store_from(lines), [{"change": "revise", "target": "A@1", "authorized_by": "AU"}]))
        self.assertEqual(s["C@1"], "rebaseline")

    def test_direct_retraction_never_invalidates_a_decision(self):
        # Kate, PR #8 review: decisions are flagged for review, never declared unjustified by the tool.
        lines = self.BASE + [{"id": "D", "version": 1, "type": "decision", "subject": "s",
                              "relations": [{"rel": "depends_on", "to": "A@1"}]}]
        s = statuses(impact(store_from(lines), [{"change": "retract", "target": "A@1"}]))
        self.assertEqual(s["D@1"], "needs_review")
        self.assertEqual(s["C@1"], "unjustified")  # claims still are

    def test_new_contradicting_evidence_contests_the_claim(self):
        # Kate, PR #8 review: counter-evidence must start a reassessment without a manufactured retraction.
        lines = self.BASE + [
            {"id": "X", "version": 1, "type": "evidence", "relations": [{"rel": "contradicts", "to": "K@1"}]},
            {"id": "D", "version": 1, "type": "decision", "subject": "s", "relations": [{"rel": "selects", "to": "K@1"}]},
        ]
        rep = impact(store_from(lines), [{"change": "add", "target": "X@1"}])
        s = statuses(rep)
        self.assertEqual(s["K@1"], "contested")
        self.assertEqual(s["D@1"], "needs_review")
        self.assertEqual(len(s), 2)  # supporting evidence E1, E2 untouched

    def test_new_supporting_evidence_flags_nothing(self):  # decoy
        lines = self.BASE + [{"id": "E3", "version": 1, "type": "evidence", "relations": [{"rel": "supports", "to": "K@1"}]}]
        self.assertEqual(statuses(impact(store_from(lines), [{"change": "add", "target": "E3@1"}])), {})

    def test_check_rules(self):
        bad = [
            {"id": "AU", "version": 1, "type": "authority", "governs": ["s"]},
            {"id": "D", "version": 1, "type": "decision", "subject": "s", "status": "accepted", "decided_by": "nobody"},
            {"id": "O", "version": 1, "type": "claim", "tier": "observed"},
            {"id": "P", "version": 1, "type": "claim", "tier": "prospective"},
            {"id": "X", "version": 1, "type": "claim", "relations": [{"rel": "depends_on", "to": "missing@1"}]},
        ]
        rules = {(f.rule, f.ref) for f in check(store_from(bad)) if f.level == "error"}
        self.assertIn(("authority", "D@1"), rules)
        self.assertIn(("tier", "O@1"), rules)
        self.assertIn(("tier", "P@1"), rules)
        self.assertIn(("reference", "X@1"), rules)


class TestOutcomeSufficiency(unittest.TestCase):  # feature 002 US3 / FR-008, FR-009 (T003)
    def run_check(self, extra):
        base = [{"id": "C", "version": 1, "type": "claim", "claim_category": "purpose_outcome",
                 "text": "Reports let the analyst see the real data"},
                {"id": "T", "version": 1, "type": "evidence", "evidence_kind": "contract_conformance",
                 "text": "report tests pass", "relations": [{"rel": "supports", "to": "C@1"}]}]
        return check(store_from(base + extra))

    def test_outcome_claim_on_conformance_only_warns(self):
        fs = [f for f in self.run_check([]) if f.rule == "outcome-sufficiency"]
        self.assertEqual([(f.level, f.ref) for f in fs], [("warning", "C@1")])
        self.assertIn("unsupported inference", fs[0].msg)
        self.assertIn("T@1", fs[0].msg)

    def test_outcome_observation_makes_it_pass(self):
        extra = [{"id": "O", "version": 1, "type": "evidence", "evidence_kind": "outcome_observation",
                  "relations": [{"rel": "supports", "to": "C@1"}]}]
        self.assertEqual([f for f in self.run_check(extra) if f.rule == "outcome-sufficiency"], [])

    def test_requirement_satisfaction_on_conformance_is_fine(self):  # decoy
        lines = [{"id": "C", "version": 1, "type": "claim", "claim_category": "requirement_satisfaction"},
                 {"id": "T", "version": 1, "type": "evidence", "evidence_kind": "contract_conformance",
                  "relations": [{"rel": "supports", "to": "C@1"}]}]
        self.assertEqual([f for f in check(store_from(lines)) if f.level in ("warning", "error")], [])

    def test_unkinded_evidence_is_not_counted_as_conformance(self):  # decoy: unknown is not conformance
        lines = [{"id": "C", "version": 1, "type": "claim", "claim_category": "purpose_outcome"},
                 {"id": "T", "version": 1, "type": "evidence", "relations": [{"rel": "supports", "to": "C@1"}]}]
        self.assertEqual([f for f in check(store_from(lines)) if f.rule == "outcome-sufficiency"], [])

    def test_unknown_kind_or_category_is_an_error(self):
        lines = [{"id": "C", "version": 1, "type": "claim", "claim_category": "vibes"},
                 {"id": "T", "version": 1, "type": "evidence", "evidence_kind": "anecdote"}]
        errs = {(f.rule, f.ref) for f in check(store_from(lines)) if f.level == "error"}
        self.assertEqual(errs, {("claim-category", "C@1"), ("evidence-kind", "T@1")})


if __name__ == "__main__":
    unittest.main()
