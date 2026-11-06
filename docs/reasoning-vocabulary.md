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
| `ambition` | a direction the project, or a project derived from it, may take; not a commitment | `owner`, `source` quote |
| `experiment` | trying a few things, to or with the package; not a commitment to a feature or to long-term support | `variants`, `status` |

**Ambitions and experiments** (DEC-033, Zach, 2026-11-02).
- An **ambition** records "we might want to do this at some point". Its main job is to keep the
  implementation limber: before a commitment (a decision, a committed requirement, a design choice) is
  made, the ambitions it could foreclose can be checked. It is not a commitment and creates no obligation.
- An **experiment** codifies trying a couple of different things. It is not a commitment to a feature, a
  full feature or long-term support. Its *results* can be promoted (a decision or requirement may cite the
  evidence it `produced`). The experiment itself needn't be supported later.
- Neither is a conclusion: `impact` never reports an ambition or an experiment for reassessment, and
  `check` applies no obligation rules to them.
- Nothing yet checks whether a commitment forecloses an ambition. That review question is the reason
  the type exists. How to mechanise it is undecided and would itself start as an experiment.

**Code references** (v0.2): a relation target `code:<dotted.symbol>` points at code. It is unversioned; the edge snapshot (`aec edges`) supplies its current state, `aec check --edges` reports dangling ones, and `aec code-impact` turns code changes into change events. A module link now means "flag dependents stale when anything inside the module changes", where before it only reported the module's deletion. Link granularity matters: a link to a function or class is revised when its own body changes (nested definitions and methods included); a link to a module (`code:pkg.mod`, what `import-purpose` writes) is revised when any definition or statement in that module changes, not when a submodule does. A changed definition that a linked symbol reaches through resolved calls or references (one step by default, `--reach-depth`) is reported as a pointer, a candidate for attention rather than a required reassessment, and assigns no status: a changed callee does not make the caller's rationale stale. Behaviour-preserving rewrites (reordered arguments) still revise; comments do not.

Every record has `id`, `version` (a positive JSON integer: `1.9`, `"1"` and `true` are errors, never coerced), `type`, `text`, optional `subject` (what it is about, for authority checks) and `relations`. A reference is `id@version`. Pinning the version is what lets a later change be detected.

**Epistemic status** (`epistemic`) separates purpose *discovery* from purpose *preservation*. A `provisional` purpose, criterion or requirement may be reframed during exploration without that being drift. The history is still kept. A `committed` one changes only through an authorized `revision`.

**Authorship** (optional). `authored_by` names who wrote the record: an actor such as `zach`, `claude:aec` or `chatgpt:kate`, optionally with `#session`. `author_role` says how that author stands to the code the record describes: `owner`, `independent` (an agent that did not write the code) or `implementer` (the agent that did). It exists for one test: whether semantic records written independently of the code catch drift that ones written by the implementer miss. If they catch no more, the independence condition is dropped. It is a field, not a workflow. `check` validates only its shape (an unknown role, or a role without an author, is an error; an actor spelled some other way is a warning), and nothing else reads it. It is not proof of authorship, any more than `authorized_by` is proof of consent.

**Evidence kind and claim category** (v0.3, optional). `evidence_kind` is one of `contract_conformance` (the implementation meets its declared contract: tests pass, the report renders), `behavioral_observation` (what the system was seen to do under stated conditions), `outcome_observation` (whether the intended effect happened). `claim_category` is `requirement_satisfaction` or `purpose_outcome`. They exist so the check can tell "it passes" from "it works": a `purpose_outcome` claim whose supporting evidence is *all* `contract_conformance` gets an `outcome-sufficiency` warning. That is an unsupported inference, not a finding that the outcome failed, and adding one outcome observation clears it. Evidence with no kind is not treated as conformance. **This is a necessary-evidence-type check, not a sufficiency test**: it does not judge whether the outcome observation is relevant, reliable, independent or broad enough for the claim. Missing evidence and inadequate evidence stay distinct; the second is a review question.

**Evidence tiers** (`tier`): `candidate` (unreviewed or machine-produced), `reviewed` (a qualified reviewer checked it), `observed` (an outcome actually seen under recorded conditions), `prospective` (a prediction frozen before the outcome). A tier label never establishes validity by itself.

## Optional source anchors and rationale (WP-S)

Every record type may retain a `rationale` string in Record.data, separate from its
existing `text`, and an `anchors` array. Each anchor names a local root (optional,
repository by default), relative path, raw-byte SHA-256, line/quote locator and an
optional `for` field (text by default, or rationale). No new justificatory relation
is inferred. Shape errors are errors; unavailable/missing/mismatch/invalid-locator
observations are warning findings; verified integrity/locator matches are not
findings. See README for full data/root/CLI contract. This does not change impact,
authority, evidence tiers or propagation. Adding anchors means appending a record
version, never rewriting history. No sources are copied into the repository.

## Relations (from → to)

| relation | from → to | meaning, and what it does **not** mean |
|---|---|---|
| `serves` | requirement → purpose | meeting the requirement is intended to advance the purpose. It does not mean the purpose is achieved |
| `implements` | any → requirement | **Deprecated** (`check` warns; `impact` ignores it). Use `implemented_by` on the requirement |
| `implemented_by` | requirement → `code:<symbol>` | the requirement's *satisfaction* is claimed through this code. If the code changes, satisfaction must be re-examined, not the obligation itself (added in v0.2) |
| `depends_on` | claim, decision, requirement, evaluation → anything | the conclusion relies on this. If it changes, the conclusion must be re-examined |
| `supports` | evidence → claim | counts toward the claim. It does not establish it |
| `contradicts` | evidence → claim | counts against the claim |
| `tests` | evaluation → claim | the evaluation examines the claim under its `conditions` |
| `produced` | evaluation → evidence | where the evidence came from |
| `selects` | decision → claim or alternative | what the decision adopted |
| `supersedes` | revision or record → record@version | the newer commitment replaces the older one. The old one is kept |
| `observed_on` | evidence → `code:<symbol>` | the observation was made against this code. If the code changes, whether the evidence still *applies* needs review. It does not mean the observation was wrong (v0.3) |

## Standard terms

AEC's vocabulary maps onto established practice. Most names are kept because they read plainly to
developers and agents. Where AEC's idea is new, the AEC name is the point.

| AEC term | Nearest established term | Field | Where AEC differs |
|---|---|---|---|
| `requirement` → `implemented_by` → `code:` | requirement *satisfied by* a design element (SysML «satisfy»); requirements traceability | requirements engineering (ISO/IEC/IEEE 29148) | Traces to code symbols resolved from a dependency graph, not to model elements |
| `evaluation` → `tests` → claim | verification («verify»); test case verifies requirement | requirements engineering | Applies to claims as well as requirements |
| `serves` (requirement → purpose) | derived requirement («deriveReqt»), goal refinement | goal-oriented RE (KAOS, i*) | Records intent only; never asserts the purpose is met |
| `decision` with `decided_by` | architecture decision record (ADR) | software architecture | Machine-checked: an accepted decision must name an authority that governs its subject |
| `epistemic: committed` / `provisional` | baselined (under change control) / draft | configuration management | "Provisional" makes exploration explicit, so changing it isn't drift |
| `revision`, disposition `rebaseline` | change request, rebaselining | configuration management | Authorized changes are distinguished from unauthorized ones by `impact` |
| append-only records, `supersedes`, `id@version` | event sourcing; immutable versioned records | software architecture | The current state is the latest version; old ones stay citable |
| `impact` / `code-impact` | change impact analysis | software maintenance | Propagates through *justification* (what rests on what), not only code dependencies |
| disposition `stale` / `needs_review` | suspect link (traceability tools flag links whose ends changed) | requirements management (e.g. DOORS) | Separates the obligation (stands) from its satisfaction (needs re-checking) |
| `tier: prospective` | pre-registered prediction | experimental method | A tier label never establishes validity by itself |
| `evidence_kind` | verification vs validation ("built it right" vs "built the right thing") | systems engineering | Warns when an outcome claim rests only on conformance evidence |
| `.aec/edges.jsonl`, `aec edges` / `snapshot` | dependency graph, call graph (static analysis) | program analysis | Unresolved calls are kept and labelled, never guessed |
| `experiment` | spike; experiment | agile; empirical method | Results can be promoted; the experiment needn't be supported |
| `ambition` | (no close equivalent; nearest are option value and a product vision item) | AEC | Recorded so commitments don't foreclose it; not a commitment |
| purpose discovery vs purpose preservation; drift | requirements elicitation vs change control; architecture drift and erosion | RE; software architecture | AEC's term for a project whose purpose is still being found |

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

Fixed 2026-11-01 (the WP0 finding): on deletion, only a **claim or evidence** record whose explicit
`depends_on` names the deleted code becomes `unjustified`. Evaluations, and `selects` or
`implemented_by` links from records that are not obligations, get `needs_review`. Downstream
propagation is unchanged: a record that necessarily rests on an unjustified claim is itself unjustified.
`check` does not yet reject `implemented_by` on records that aren't obligations. That would touch
`records.py`, which the open v0.4 release PR (#20) also edits, so it is left as a follow-up.

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
2. A claim with `tier: observed` must be supported by evidence that an evaluation `produced`. A claim with `tier: prospective` must reference a frozen source: `frozen_sha256` is the 64-character lowercase hex SHA-256 of that source. The check validates the digest's form, not that it matches a real file or that the freeze happened before the outcome.
3. Every `id@version` reference must resolve.
4. A committed criterion or purpose changed without an authorized revision is flagged. A provisional one is not.

5. A `purpose_outcome` claim supported only by `contract_conformance` evidence is warned about (`outcome-sufficiency`).
6. The latest version of a claim, requirement or other conclusion that references an older version of another record (other than through `supersedes`) is warned about (`superseded-reference`): only latest versions take an impact status, so `code-impact` reaches it only as a `structural: ... references superseded ...` pointer. The old version may be meant; a warning, never an error. Evidence and decisions are history by nature, pinned to the version that existed when they were observed or made, so they are never flagged: re-pointing them would assert support nobody checked.
7. Authority does not compose. An authority governs only the subjects in its own latest record's `governs`; an authority record that cites another (through `authorized_by` or a relation) gains none of that one's scope, so a chain of grants (owner → coordinator → builder) is never an authority path. A sub-grant exists only as its own authority record with its own `governs`, written where the upstream decision says sub-delegation is allowed. Rules 1 and 4 apply this; `tests/test_no_transitive_authority.py` pins it.

`aec check` covers rules 0–3, 5, 6 and 7 (through rule 1); `aec impact` covers rule 4 (and 7 through it) and change propagation. Both are deterministic. Neither decides whether evidence is *good*. That remains review.

When a finding's verdict turns on a threshold (rules 2, 5 and 6), `check` ends the line with what the threshold is and what it measured, for example `[threshold: referenced version is the latest; measured: @1; latest @2]`.
