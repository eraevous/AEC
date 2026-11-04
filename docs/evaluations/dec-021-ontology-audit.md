# DEC-021 step 1: ontology audit (C-03), bounded to the minimal record set

**Status: complete as a desk audit, 2026-11-04, by claude:aec-eval.** Nothing was run against an outcome. This audit defines arm B (minimal AEC) of the [DEC-021 replay](dec-021-protocol.md). Zach can still overrule any line of it before the freeze.

**Authority.** DEC-021 queued "the ontology audit (four cases) first". DEC-031 (Zach, 2026-11-01 21:19 CT) limited that audit to "the minimal record set needed to catch a consequential change a well-configured Spec Kit workflow would miss". DEC-048 (2026-11-04) lets the coordinator start the work. The four cases come from drift round 2 (`relay-kit-private/aec-drift/round-2/synthesis.md`, Q2, "Next step"). The list is also candidate C-03 in `relay-kit-private/governance/candidates.md`.

**Bound.** One question only: which record types, relations and fields have to be in *Telosmith form*, read by a Telosmith command, to catch a consequential change that a Spec Kit workflow holding the same facts as prose would miss? Every arm of the replay gets all project facts (protocol, "Information matching"). So "necessary" here means the deterministic tooling needs the record in Telosmith form. It does not mean the fact itself is needed. A type that is useful for other reasons, such as provenance, owner reporting or the MtG domain, can still be decoration for this question.

**What "catch" means mechanically** (`src/aec/impact.py`, `_dependents`). A change propagates along `depends_on`, `selects` and `implemented_by` (necessary), along `observed_on` (applicability) and along `supports`/`produced` (support). `serves` and `implements` propagate nothing: `implements` is deprecated (`records.py` `DEPRECATED_RELATIONS`). `code-impact` fires only for `code:` symbols that a record names explicitly and whose definition or outgoing edges changed. It does not traverse callers (Codex, `relay-kit-private/handoffs/outputs/HO-AEC-20261102-A5RR.md`, section B scratch probe). `check` rule 1 requires an accepted decision to name an authority that governs its subject.

**Corpora used as evidence**
- **Telosmith** `.aec/records.jsonl` at `906e8fd`: 112 records.
  - Types: decision 53, source 21, requirement 11, claim 9, evidence 9, ambition 5, authority 2, purpose 1, experiment 1.
  - Relations: depends_on 68, supersedes 25, serves 20, observed_on 15, implemented_by 11, supports 9.
  - Never used: criterion, assumption, evaluation and revision as types; implements, contradicts, tests, produced and selects as relations.
- **Fathom** `.aec/records.jsonl` at the frozen revision `68890bf`: 95 records.
  - Types: requirement 44, evidence 20, claim 8, evaluation 8, decision 8, assumption 4, purpose 2, authority 1.
  - Relations: serves 76, observed_on 79, implemented_by 61, implements 49, supersedes 18, supports 20, produced 18, tests 8.
  - **Zero `depends_on`.** In Fathom, every claim is linked by the deprecated `implements`. A code change therefore reaches requirements (through `implemented_by`) and evidence (through `observed_on`), and stops there. No Fathom claim or decision is reachable by `code-impact`.

## Case 1: P5, proposal vs decision vs authorization

**The failure** (`docs/failure-modes.md` P5): a model's report of a decision is treated as the decision. Real instances:
- **Fathom.** `FT-TA-R1@2` and `FT-PO-R1@2` are `epistemic: provisional`, with the text "proposed for Zach to accept". They were nevertheless implemented and merged as the governing reading of `FT-R7@2`/`FT-R19@1` and `FT-R18@1` (`specs/007-target-analysis/spec.md`, `specs/006-report-polish/`).
- **Telosmith.** Reconstructed `HIST-*` decisions stay proposed until confirmed (`docs/decisions-to-confirm.md`).
- **relay-kit-private.** DEC-046 and DEC-047: two sessions recorded the same owner words as two decisions.

**What a Spec Kit workflow misses.** Spec Kit's spec header ("Status: Draft") and the clarifications log are free text. Nothing distinguishes "Claude's reading, for Zach to accept" from "Zach accepted", and nothing checks who may accept what.

| Item | Verdict | Why |
|---|---|---|
| `decision` with `status`, `decided_by` | **necessary** | the only place acceptance is stated in a checkable form |
| `authority` with `governs` | **necessary** | `check` rule 1 (authority by subject) is Telosmith's one deterministic P5 check |
| `epistemic` on requirements (committed / provisional) | **necessary** | separates a proposed reading (`FT-TA-R1@2`) from a commitment (`FT-R7@2`) |
| verbatim owner `quote` or `rationale` text | **necessary as a fact**, not as Telosmith form | a reviewer judges consent from the words; prose carries them equally well |
| anchors + `source` commands | decoration for detection | they verify the quote's integrity (P8). They don't detect a misread. A digest is not consent (`docs/reference/source-anchors.md`) |
| `revision` type, `authorized_by` | decoration | unused in both corpora, and `authorized_by` is a claim, not verified consent (AGENTS.md) |

**Limit, stated plainly.** Rule 1 catches an acceptance whose authority doesn't govern the subject. It does not catch a fabricated `decided_by`. The conventional equivalent already exists outside Telosmith: relay-kit-private's `governance/decisions.jsonl` quotes the owner, and DEC-018 makes it canonical. On P5, Telosmith's marginal contribution is the authority-by-subject check and the committed/provisional flag, nothing more.

## Case 2: Data Guide findings (observation, interpretation, hypothesis, action)

**The distinction belongs to the project's domain**, not to Telosmith ("an ontology *of* the work vs ontologies *for* the work", synthesis Q2). In Fathom it is a committed requirement:
- `DG-RA@1` separates observations, interpretations, hypotheses and actions, with evidence and confidence;
- `DG-RB@1` says inference is never presented as fact;
- `FT-R4@2` judges a slice useful "without claiming more than it knows".

It is implemented in Fathom's artifact schema (`src/fathom/models.py`; `specs/001-data-review/data-model.md`), and Spec Kit's data-model artefact holds it well.

**A real consequential failure of this kind.** Data-Guide's naive missingness-by-group test fired on pure noise in 20 of 20 runs, so hypotheses were presented as findings (`relay-kit-private/kairos/dataguide-salvage-2026-11-03.md`; DEC-043 item 2). The cheapest catch is conventional: a null-data fixture that must produce zero findings. That fixture is now a constraint in `relay-kit-private/handoffs/HO-DG-20261104-9B3S.md`.

| Item | Verdict | Why |
|---|---|---|
| `requirement` stating the obligation, `implemented_by` the code that produces findings | **necessary** | the only path by which a change to finding generation triggers a Telosmith review. Fathom links `FT-R1@2` and `FT-TA-R1@2` to code, but not `DG-RA`/`DG-RB` themselves, which `serve` the purpose and so propagate nothing |
| `evidence` with `observed_on` | **necessary** (shared with case 3) | test evidence about finding behaviour, observed on code the change touches, is flagged for re-assessment |
| Telosmith's `evidence_kind` / `claim_category` (conformance vs outcome; `outcome-sufficiency` warning) | decoration here | it is the meta-level analogue of the domain split, but Fathom uses neither field, so it can't fire in the replay |
| `assumption`, `criterion` | decoration | Fathom's `DG-A1`–`A4` are context. Nothing depends on them |
| a Telosmith type per finding kind | **rejected** | it would collapse the two ontologies. Findings live in the artifact |

## Case 3: WP1A revision, snapshot and method

**The obligation** is `AEC-R10@1` (`specs/005-commit-snapshots/spec.md`): a snapshot names exactly what it describes (commit or working tree, plus extraction method), and two snapshots are compared only when their methods match. Two real hazards:
- **Method drift.** Extractor 0.4.1 (C-11, PR #32) changed edges with no change in the target code, so comparing across it gives spurious or missing impact.
- **Stale evidence reused.** An observation made at one revision gets read as describing HEAD (S10).

**What a Spec Kit workflow misses.** Spec Kit has no notion of which revision a piece of evidence describes. A `validation.md` line ("164 tests pass") reads as current forever.

| Item | Verdict | Why |
|---|---|---|
| snapshot identity (commit + method) on both sides of a comparison | **necessary**, but it is snapshot metadata, not a record type | without it, `code-impact` output can't be trusted |
| `evidence` with `observed_on code:` and a `method` naming the revision | **necessary** | the only built applicability rule (S10). Fathom uses `observed_on` 79 times |
| `supersedes` | **necessary bookkeeping** | `impact` acts on the latest version only. Without supersession, old versions read as live |
| `revision` type | decoration | unused in both corpora |
| `diff` / `snapshot` commands as separate outputs | full arm only | they inform. They don't trigger review |

## Case 4: WP2A graph fidelity, interpretability and usefulness

**The four claims a representation raises** (synthesis Q2): it exists, it is faithful, an agent can interpret it, and it is useful. The evidence so far:
- probe-001: no outcome effect from structural briefings, and higher tokens on 2 of 3 tasks;
- resolver-001: 25 of 874 unresolved calls resolved;
- Codex A5RR: `code-impact` misses helper and constant changes that aren't explicitly linked, and module-level links fire on nothing.

**Fidelity limit relevant to the replay.** A new caller of an unchanged helper changes no linked definition, so `code-impact` stays silent. One example is PR #15's reuse of `univariate.percentile` for box geometry (Copilot item F02).

| Item | Verdict | Why |
|---|---|---|
| `code:` links at symbol granularity (`implemented_by`, `observed_on`) | **necessary** | the trigger. Module links don't fire (A5RR) |
| the visibility figure (unresolved calls, skipped files) | **necessary** with any structural answer | "No known caller is not proof of no caller" (AGENTS.md) |
| `reach`, `fan`, `unresolved` briefings | decoration for the minimal set | no evidence they change outcomes (probe-001). Kept in the full arm, where the replay measures them again |
| `edges` as an artefact for an architect agent | out of scope | that is `AMB-tiered-agents@1` / C-20, a separate experiment |

## Ambition (C-19)

**`ambition` is not in the minimal set, in any of the four cases.** Nothing propagates from an ambition: no command reads one, and no relation from it is in the propagating set. An ambition records a direction to keep open (DEC-033). It is not an obligation a change can break. The P5 risk it guards against, an ambition read as a commitment, is avoided by not linking ambitions into propagating relations, and that needs no ambition in the replay.

Ambitions do have one role in DEC-021: they are the **yardstick** for reading its result. `AMB-adopted-by-others@1` ("Others find AEC useful") is what the outcome rules serve. The experiment record therefore `serves` that ambition, but no arm receives it. How `ambition` differs from `purpose`:
- a purpose is committed and governs requirements;
- an ambition is uncommitted, broader and less testable, and it governs what must not be foreclosed.

This agrees with value-001's draft (PR #35, step 1). Whether `ambition` stays a type is Zach's vocabulary decision. This audit doesn't settle it.

## Result: the minimal set (arm B)

**Record types**
- requirement, with `epistemic` and `rationale`;
- evidence, with `method`;
- claim;
- decision, with `status`, `decided_by` and a quote;
- authority, with `governs`.

**Relations**
- implemented_by (to `code:` symbols)
- observed_on (to `code:` symbols)
- depends_on
- supports
- supersedes

**Commands:** `edges` (one pinned method for both revisions), `check --edges`, and `code-impact` between the merge-base and head snapshots, with the visibility figure.

**Excluded, as decoration for this question**
- **Types:** purpose, assumption, criterion, source, evaluation, revision, ambition, experiment.
- **Relations:** serves, implements, tests, produced, selects, contradicts.
- **Fields:** tier, evidence_kind, claim_category, anchors.
- **Commands:** `source`, `reach`, `fan`, `unresolved`, `diff`, `snapshot`, `impact` on hand-written events, `import-purpose`, `init`.

The facts these carry still reach arm B as prose.

**Mechanical derivation for the replay.** Arm B's records file is the frozen Fathom records file with two filters applied by a script:
- keep only the types above;
- drop every relation not in the list above.

Nothing else is changed: no record is rewritten, and no link is added. One consequence for Fathom: its claims arrive unlinked, because their only links are `implements`. That is Telosmith as Fathom actually used it, and the protocol reports it.

**Three observations to log** (not changes made here)
1. Fathom's use of the deprecated `implements` cuts every claim out of propagation, and Fathom's pinned AEC (`860b781`) gave 0 warnings at `3367ab3`. A candidate for the Fathom lane: either migrate to `implemented_by`/`depends_on`, or record why not.
2. `serves` propagating nothing means that a purpose-level obligation (`DG-RA`, `DG-RB`, `FT-R4`) is never surfaced by a code change unless a lower requirement restates it with code links.
3. The minimal set is five types, not three, as in value-001's draft. Evidence and `observed_on` come in from case 3, because applicability is one of the four guarantees (DEC-016). Supersession comes in because `impact` reads latest versions.
