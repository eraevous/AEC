# DEC-021 pre-registration intent — 2026-11-04

@ai-intent: Pre-register the bounded DEC-021 evaluation authorised by DEC-031: a C-03 ontology audit limited to the minimal record set, and a frozen, information-matched replay of three arms (conventional, minimal Telosmith, full Telosmith) on Fathom at 68890bf. Delivered as documents plus one appended `experiment` record. Nothing is run. Started by claude:aec-eval under DEC-048 (the coordinator may begin the biggest lifts, with Kate's amendments: freeze the revision and the protocol, blind evaluators, separate independent review).

## What changed

- `docs/evaluations/dec-021-ontology-audit.md`: the four C-03 cases (P5; Data Guide findings; WP1A revision, snapshot and method; WP2A fidelity and usefulness). The minimal set has five types:
  - requirement
  - evidence
  - claim
  - decision
  - authority

  It has five relations:
  - implemented_by
  - observed_on
  - depends_on
  - supports
  - supersedes

  `ambition` is not in it.
- `docs/evaluations/dec-021-protocol.md`: the pre-registration. Arms, information matching, the injected change (K1 = Copilot item F01 on Fathom PR #15), the primary outcome, decision rules, roles and blinding, budget, stop rules and what is not measured.
- `.aec/records.jsonl`: appended `EXP-dec021-fathom-replay@1` (status `pre-registered`). It depends on `DEC-021@1`, serves `AEC-R3@1`, `AEC-P0@1` and `AMB-adopted-by-others@1`, and is anchored to both documents by digest.
- `docs/evaluations/README.md`: one row.

## Assumptions (each one is a reading, open to correction)

1. **DEC-048 covers drafting and pre-registering.** It does not cover running the replay. The brief says so, and running needs Zach.
2. **"Injected change" means the scored target within a real diff, not a synthetic edit.** All eight Copilot defects stay in the diff that every arm sees. A synthetic injection would break DEC-048's "frozen Fathom material" and Kate's no-hindsight amendment.
3. **"Information-matched" means every arm gets every fact in Fathom's records.** Arms differ only in form (prose, minimal JSONL or full JSONL) and in the attached deterministic output. So the test isolates the mechanism, not access to facts. The conventional arm gets a file-level path reminder, which is Codex A5RR's cheapest realistic alternative. That makes A stronger than "Spec Kit alone", deliberately (AEC-R3: "well-configured").
4. **Arm B is derived mechanically from the real records** (type and relation filter only). Fathom links its claims only through the deprecated `implements`, so in B its claims arrive unlinked. That is reported, not repaired.
5. **The anchors on the experiment record are expected to go to `mismatch`** when the protocol gains its review amendments and freeze section. That is the intended signal ("the protocol changed since registration"). The freeze appends `EXP-dec021-fathom-replay@2` with the frozen digests. v1 is never edited.
6. **The `status` field is a data field.** `check` does not validate experiment status; the vocabulary has no status enum for experiments yet.
7. **The relationship to value-001 (PR #35, draft) is adoption, not replacement.** The value-001 outcome rules and Kate's seven amendments carry over. Whether its Data-Guide case still runs is left to Zach.

## Risks recorded

- **Selection bias.** The author saw that `FT-PO-R1@2` is linked to `charts.svg_chart` and that the PR touches `charts.py` before choosing K1. No Telosmith command was run on the diff. The delivery qualification runs only after the freeze, and K1 is not re-chosen.
- **A strong prior against a Telosmith advantage.** The historical author-side workflow, which included Telosmith, missed all eight defects, and Copilot caught all eight conventionally. A ceiling (every arm 4/4) is a plausible, legitimate null.
- **Commit attribution.** The coordinator's brief asked for a "Claude Fable 5.1" co-author trailer. The session's attribution rule names Claude Opus 5.5, which is the model that did this work, so commits use that.

## What Zach must still decide

1. **Whether to run the replay** (about 6.6 M tokens, capped at 8 M, about 6 hours; two of his decisions before the run, one read after).
2. **The injected change, if contested:** keep K1 = F01, or make F03 primary, or make K1 and K2 a joint primary.
3. **value-001's Data-Guide case:** run it as a second case, fold it in, or close PR #35 as superseded.
4. **Whether `ambition` stays a record type.** The audit leaves it outside the minimal set and treats it as the yardstick for reading results (C-19).

## Not done

- No materials built, no key written, no Telosmith command run on Fathom PR #15, no trials.
- No independent protocol review yet (Kate plus one cold Claude, before the freeze).
- No change to Telosmith code, specs or earlier records. No change to Fathom, which is read-only here.
