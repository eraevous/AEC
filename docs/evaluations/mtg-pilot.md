# The MtG pilot: the one capability v0 had to earn

Historical: the first demonstration of `aec impact`, on real events from the MtG project (2026-10-26). Kept for the record; for current usage see the README.

> **Something changed. Which conclusions are no longer justified, and which changes were legitimate revisions?**

```bash
PYTHONPATH=src python3 -m aec check  examples/mtg-pilot/records.jsonl
PYTHONPATH=src python3 -m aec impact examples/mtg-pilot/records.jsonl examples/mtg-pilot/scenario1_duty_timing.jsonl
PYTHONPATH=src python3 -m unittest discover -s tests
```

Each conclusion that relied on the changed record is classified:
- `unjustified`: its support broke.
- `weakened`: it lost one support but keeps others.
- `stale`: it pins an old version after an unauthorized change.
- `rebaseline`: an authorized revision; re-examine it, but it is not drift.
- `exploratory`: the changed record was provisional, which is expected during purpose discovery.
- `contested`: new evidence contradicts it (change kind `add`).
- `needs_review`: it sits downstream of a broken, stale or contested conclusion, or it is a decision whose basis changed.

These are review dispositions, not truth values. Decisions are never declared unjustified by the tool. They belong to a human authority, so they are flagged for review.

On the MtG pilot, the six scenarios reproduce what the reviewers concluded by hand that day:
- Kate's catch on Duty Beyond Death's timing breaks the "recovery improved" claim. It leaves the receiver hypothesis alone, and flags the Vraska decision for review.
- Downgrading the receiver census only weakens the hypothesis, because Zach's observed game account still supports it.
- The P-01 amendment is `stale` and reported until Zach authorizes it, and `rebaseline` once he does.
- Rewording the provisional success criterion is `exploratory`.
- An unrelated inventory change flags nothing.
