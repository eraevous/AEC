# AEC reasoning vocabulary v0.3

A small vocabulary for the *work and its justification*. The point is the meaning of the relationships, not the boxes: evidence supporting a claim does not establish it; a passing test does not satisfy a requirement; a satisfied requirement does not show the purpose was achieved. Those are the steps an AI tends to collapse into "done".

**Organizing question (the one capability v0 must earn):** *Something changed. Which conclusions are no longer justified, and which changes were legitimate revisions?*

This is deliberately not a graph platform. Records are plain JSON lines, versioned, append-only. If simple records stop being enough, that is a finding to report, not a reason to build infrastructure first.

## Record types

| type | meaning | typical fields |
|---|---|---|
| `purpose` | the outcome someone wants | `owner`, `epistemic` |
| `requirement` | an obligation the system must satisfy | `epistemic` |
| `criterion` | how "good enough" is judged | `epistemic` (`provisional` or `committed`) |
| `assumption` | a condition relied on | |
| `source` | an external artifact or record (a spec, an Oracle text, a dataset) | `ref` |
| `claim` | something asserted about the system or world | `tier` |
| `evidence` | an observation offered for or against a claim | `tier`, `method`, `limits` |
| `evaluation` | a procedure that examines a claim under stated conditions | `conditions` |
| `decision` | a choice made on a recorded basis | `status`, `decided_by` |
| `authority` | who or what governs a subject | `governs` (list of subjects) |
| `revision` | an authorized change to an earlier commitment | `authorized_by`, `reason` |

**Code references** (v0.2): a relation target `code:<dotted.symbol>` points at code. It is unversioned; the edge snapshot (`aec edges`) supplies its current state, `aec check --edges` reports dangling ones, and `aec code-impact` turns code changes into change events.

Every record has `id`, `version` (int), `type`, `text`, optional `subject` (what it is about, for authority checks) and `relations`. A reference is `id@version`. Pinning the version is what lets a later change be detected.

**Epistemic status** (`epistemic`) separates purpose *discovery* from purpose *preservation*. A `provisional` purpose, criterion or requirement may be reframed during exploration without that being drift. The history is still kept. A `committed` one changes only through an authorized `revision`.

**Evidence kind and claim category** (v0.3, optional). `evidence_kind` is one of `contract_conformance` (the implementation meets its declared contract: tests pass, the report renders), `behavioral_observation` (what the system was seen to do under stated conditions), `outcome_observation` (whether the intended effect happened). `claim_category` is `requirement_satisfaction` or `purpose_outcome`. They exist so the check can tell "it passes" from "it works": a `purpose_outcome` claim whose supporting evidence is *all* `contract_conformance` gets an `outcome-sufficiency` warning. That is an unsupported inference, not a finding that the outcome failed, and adding one outcome observation clears it. Evidence with no kind is not treated as conformance. **This is a necessary-evidence-type check, not a sufficiency test**: it does not judge whether the outcome observation is relevant, reliable, independent or broad enough for the claim. Missing evidence and inadequate evidence stay distinct; the second is a review question.

**Evidence tiers** (`tier`): `candidate` (unreviewed or machine-produced), `reviewed` (a qualified reviewer checked it), `observed` (an outcome actually seen under recorded conditions), `prospective` (a prediction frozen before the outcome). A tier label never establishes validity by itself.

## Relations (from → to)

| relation | from → to | meaning, and what it does **not** mean |
|---|---|---|
| `serves` | requirement → purpose | meeting the requirement is intended to advance the purpose. It does not mean the purpose is achieved |
| `implements` | any → requirement | the artifact is meant to meet the requirement. It does not mean it does |
| `implemented_by` | requirement → `code:<symbol>` | the requirement's *satisfaction* is claimed through this code. If the code changes, satisfaction must be re-examined, not the obligation itself (added in v0.2) |
| `depends_on` | claim, decision, requirement, evaluation → anything | the conclusion relies on this. If it changes, the conclusion must be re-examined |
| `supports` | evidence → claim | counts toward the claim. It does not establish it |
| `contradicts` | evidence → claim | counts against the claim |
| `tests` | evaluation → claim | the evaluation examines the claim under its `conditions` |
| `produced` | evaluation → evidence | where the evidence came from |
| `selects` | decision → claim or alternative | what the decision adopted |
| `supersedes` | revision or record → record@version | the newer commitment replaces the older one. The old one is kept |
| `observed_on` | evidence → `code:<symbol>` | the observation was made against this code. If the code changes, whether the evidence still *applies* needs review. It does not mean the observation was wrong (v0.3) |

## A code dependency is not a justificatory dependency

This is a governing invariant (Kate, MtG coordination, 2026-10-27). The edge graph says what code calls, imports or refers to what; the records say what conclusions rest on what. They inform each other but their edges mean different things. If module A imports B, changing B may change how A runs, yet a conclusion supported by A is not thereby unjustified. Conversely a conclusion can rest on a changed assumption with no import changing at all. So:

- An edge in `edges.jsonl` never becomes a justification by itself. Only a record's explicit relation to `code:<symbol>` connects code to a conclusion.
- A code change produces **review statuses only** (`stale`, `needs_review`). One exception: a **claim or evidence** record whose explicit `depends_on` names code that was **deleted** is `unjustified`, because its recorded justification names something that no longer exists. `depends_on` is a strong declaration; it is never inferred from imports.
- **Obligations are never invalidated by code** (Kate, AEC round 4). If the code implementing a requirement, purpose or criterion is deleted, what breaks is the recorded *satisfaction*, not the obligation: the record gets `needs_review` and a finding says the implementation path is gone. Decisions are only flagged.
- `observed_on` evidence is never invalidated by a code change: an edit is not proof that observed behaviour changed.

### Current implementation limits (WP0 observation)

For code deletion analysis, use `aec code-impact` with old/new snapshots. It creates
synthetic code records and explicit events for the impact engine. Plain `aec impact`
does not discover deletions or create those records: an event naming an absent
`code:` target is reported as unresolved, with no impact inferred.

The deletion branch is broader than the intended exception above: the current
`_dependents` implementation treats explicit `depends_on`, `selects` and
`implemented_by` links as necessary for any record type. A non-obligation,
non-decision record (including an evaluation) can therefore become `unjustified`
when such a code target is deleted. `observed_on` still requests review. WP0
records this discrepancy without changing propagation semantics or the vocabulary;
review is needed before treating the narrower invariant as fully enforced.

## Changes

A change is an event, not an edit:

```json
{"change": "retract" | "revise" | "add", "target": "A-census@1", "new": "A-census@2", "by": "kate",
 "authorized_by": "zach" | null, "revision": "R-0002" | null, "reason": "..."}
```

- `retract`: the target is no longer believed (an assumption found false, or evidence found invalid).
- `add`: a new record arrives, typically evidence. Evidence that `contradicts` a claim starts a reassessment; new supporting evidence changes nothing.
- `revise`: a new version replaces the old one. It counts as **authorized** only if `authorized_by` names an authority whose `governs` covers the target's `subject`.

## What `aec impact` reports for each affected conclusion

| status | when |
|---|---|
| `unjustified` | it relied on the retracted or changed record, and no remaining support of that kind holds it up |
| `contested` | new evidence contradicts it. Whether the contradiction outweighs the support is a review question |
| `weakened` | it lost one support but keeps others |
| `stale` | it pins an old version after an unauthorized change. Investigate before relying on it |
| `rebaseline` | it pins an old version after an **authorized** revision. Re-examine it against the new version; this is not drift |
| `exploratory` | the changed record was `provisional`. Expected during discovery; it is recorded but not flagged |
| `needs_review` | it depends transitively on something that became `unjustified` or `stale` |

Everything else is reported as unaffected. Over-flagging is a failure too.

**These are review dispositions, not truth values** (Kate, PR #8 review). The tool computes dependency propagation; it does not judge justificatory adequacy. `unjustified` means the *recorded* justification no longer holds under the declared dependencies, not that the conclusion is false. `weakened` means some support was lost and the adequacy of what remains is unassessed: one strong observation can outweigh several weak ones, and counting supports cannot tell. A `decision` is never marked `unjustified`, whether the dependency changed directly or transitively; it is flagged `needs_review` for the authority that made it.

**Known limits.** Authorization is *claimed*, not verified: the tool checks that the named authority governs the subject, not that the person actually approved. Evidence has no applicability conditions yet (version, scope, setting), so evidence that stopped applying is invisible until someone retracts it. Retracting a contradicting record does not restore anything.

## Semantics this encoding enforces

0. Unknown record types, relations, tiers, evidence kinds and claim categories are errors.
1. A `decision` with `status: accepted` must have `decided_by` set to an authority that governs its subject.
2. A claim with `tier: observed` must be supported by evidence that an evaluation `produced`. A claim with `tier: prospective` must reference a frozen source (`frozen_sha256`).
3. Every `id@version` reference must resolve.
4. A committed criterion or purpose changed without an authorized revision is flagged. A provisional one is not.

5. A `purpose_outcome` claim supported only by `contract_conformance` evidence is warned about (`outcome-sufficiency`).

`aec check` covers rules 0–3 and 5; `aec impact` covers rule 4 and change propagation. Both are deterministic. Neither decides whether evidence is *good*. That remains review.
