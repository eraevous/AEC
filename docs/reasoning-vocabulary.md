# AEC reasoning vocabulary v0

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

## Changes

A change is an event, not an edit:

```json
{"change": "retract" | "revise", "target": "A-census@1", "new": "A-census@2", "by": "kate",
 "authorized_by": "zach" | null, "revision": "R-0002" | null, "reason": "..."}
```

- `retract`: the target is no longer believed (an assumption found false, or evidence found invalid).
- `revise`: a new version replaces the old one. It counts as **authorized** only if `authorized_by` names an authority whose `governs` covers the target's `subject`.

## What `aec impact` reports for each affected conclusion

| status | when |
|---|---|
| `unjustified` | it relied on the retracted or changed record, and no remaining support of that kind holds it up |
| `weakened` | it lost one support but keeps others |
| `stale` | it pins an old version after an unauthorized change. Investigate before relying on it |
| `rebaseline` | it pins an old version after an **authorized** revision. Re-examine it against the new version; this is not drift |
| `exploratory` | the changed record was `provisional`. Expected during discovery; it is recorded but not flagged |
| `needs_review` | it depends transitively on something that became `unjustified` or `stale` |

Everything else is reported as unaffected. Over-flagging is a failure too.

## Semantics this encoding enforces

1. A `decision` with `status: accepted` must have `decided_by` set to an authority that governs its subject.
2. A claim with `tier: observed` must be supported by evidence that an evaluation `produced`. A claim with `tier: prospective` must reference a frozen source (`frozen_sha256`).
3. Every `id@version` reference must resolve.
4. A committed criterion or purpose changed without an authorized revision is flagged. A provisional one is not.

`aec check` covers rules 1–3; `aec impact` covers rule 4 and change propagation. Both are deterministic. Neither decides whether evidence is *good*. That remains review.
