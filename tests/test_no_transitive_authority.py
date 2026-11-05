"""No transitive authority: an authority governs only the subjects its own latest record lists.

A chain of locally valid grants (owner -> coordinator -> builder) does not make a global authority path. Telosmith
has no delegation relation, so a grant can only be recorded as another authority with its own `governs` list; an
authority record that names a governing one (`authorized_by`, or a `depends_on` relation) gains nothing from it.
These tests pin that: the violating cases try to borrow scope through such a link, the decoys use direct scope.
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

OWNER = {"id": "AU-owner", "version": 1, "type": "authority", "text": "owner", "governs": ["scope-a"]}
# a grant recorded the only way the vocabulary allows: a second authority that cites the first
COORD = {"id": "AU-coord", "version": 1, "type": "authority", "text": "coordinator, started by the owner",
         "governs": ["scope-b"], "authorized_by": "AU-owner", "relations": [{"rel": "depends_on", "to": "AU-owner@1"}]}
BUILDER = {"id": "AU-builder", "version": 1, "type": "authority", "text": "builder, started by the coordinator",
           "governs": [], "authorized_by": "AU-coord", "relations": [{"rel": "depends_on", "to": "AU-coord@1"}]}


def store(*recs: dict) -> Store:
    p = Path(tempfile.mkdtemp()) / "records.jsonl"
    p.write_text("".join(json.dumps(r) + "\n" for r in (OWNER, COORD, BUILDER, *recs)))
    return Store.load(p)


def decision(by: str, subject: str) -> dict:
    return {"id": f"D-{by}-{subject}", "version": 1, "type": "decision", "subject": subject,
            "status": "accepted", "decided_by": by, "text": "decided"}


def authority_errors(s: Store) -> list[str]:
    return [f.ref for f in check(s) if f.rule == "authority" and f.level == "error"]


class AcceptedDecisions(unittest.TestCase):
    def test_coordinator_cannot_decide_in_the_owners_scope(self):
        self.assertEqual(authority_errors(store(decision("AU-coord", "scope-a"))), ["D-AU-coord-scope-a@1"])

    def test_builder_cannot_decide_in_either_upstream_scope(self):
        s = store(decision("AU-builder", "scope-a"), decision("AU-builder", "scope-b"))
        self.assertEqual(sorted(authority_errors(s)), ["D-AU-builder-scope-a@1", "D-AU-builder-scope-b@1"])

    def test_decoy_direct_scope_passes(self):
        s = store(decision("AU-owner", "scope-a"), decision("AU-coord", "scope-b"))
        self.assertEqual(authority_errors(s), [])


class Revisions(unittest.TestCase):
    REQ = {"id": "R-1", "version": 1, "type": "requirement", "subject": "scope-a", "epistemic": "committed",
           "text": "r"}
    REQ2 = dict(REQ, version=2, text="r, revised")

    def status(self, by: str) -> str:
        s = store(self.REQ, self.REQ2, {"id": "C-1", "version": 1, "type": "claim", "text": "c",
                                        "relations": [{"rel": "depends_on", "to": "R-1@1"}]})
        rep = impact(s, [{"change": "revise", "target": "R-1@1", "new": "R-1@2", "by": "agent", "authorized_by": by}])
        return rep.impacts["C-1@1"].status

    def test_revision_authorized_down_the_chain_is_not_authorized(self):
        self.assertEqual(self.status("AU-coord"), "stale")
        self.assertEqual(self.status("AU-builder"), "stale")

    def test_decoy_owner_authorizes(self):
        self.assertEqual(self.status("AU-owner"), "rebaseline")


if __name__ == "__main__":
    unittest.main()
