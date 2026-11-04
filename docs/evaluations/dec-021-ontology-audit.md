# DEC-021 step 1: ontology audit (C-03), bounded to the minimal record set

**Status: revision 2, 2026-11-04, by claude:aec-eval, after two independent reviews of revision 1.** Nothing was run against a trial outcome. No trial exists. This audit defines arm B (minimal AEC) of the [DEC-021 replay](dec-021-protocol.md). Zach can still overrule any line of it before the freeze.

**Authority.** DEC-021 queued "the ontology audit (four cases) first". DEC-031 (Zach, 2026-11-01 21:19 CT) limited that audit to "the minimal record set needed to catch a consequential change a well-configured Spec Kit workflow would miss". DEC-048 (2026-11-04) lets the coordinator start the work. The four cases come from drift round 2 (`relay-kit-private/aec-drift/round-2/synthesis.md`, Q2, "Next step"). The list is also candidate C-03 in `relay-kit-private/governance/candidates.md`.

**Bound.** One question only: which record types, relations and fields have to be in *Telosmith form* to catch a consequential change that a Spec Kit workflow holding the same facts as prose would miss? Every arm of the replay gets all project facts as identical prose (protocol, "Arms and information matching"). So the question is never whether a fact is needed, only whether its Telosmith form is.

**How each item is argued (changed in revision 2).** Revision 1 called an item "necessary" when `impact.py` reads it. That is circular: it describes the current tool, not the need. Revision 2 argues each item from the four cases by a **removal test**: what a case would lose if the item were gone from Telosmith form and left only in prose. Where a removal can be run, it was run against the replay's own material:
- Fathom's records at `3367ab3`, filtered to arm B;
- `code-impact` on `3b89d7c..3367ab3` at Telosmith `906e8fd`;
- each item deleted in turn, with the records the report then stops naming counted.

That is case-4 evidence about this diff, not a general proof. Items that the cases need, but that are inert on Fathom, are marked as such.

**Corpora**
- **Telosmith** `.aec/records.jsonl` at `906e8fd`: 112 records.
  - Types: decision 53, source 21, requirement 11, claim 9, evidence 9, ambition 5, authority 2, purpose 1, experiment 1.
  - Relations: depends_on 68, supersedes 25 (2 of them across ids), serves 20, observed_on 15, implemented_by 11, supports 9.
  - Never used: criterion, assumption, evaluation and revision as types; implements, contradicts, tests, produced and selects as relations.
- **Fathom** `.aec/records.jsonl` at the **reviewed head `3367ab3`**, which is what the arms receive. (Revision 1 counted at the later merge `68890bf`, which had 95 lines.)
  - **92 lines, 74 ids.**
  - Types (lines / latest versions): requirement 44 / 31, evidence 18 / 16, decision 8 / 7, evaluation 8 / 7, claim 7 / 7, assumption 4 / 4, purpose 2 / 1, authority 1 / 1.
  - Relations (all lines, 313 in total / on latest versions): serves 76 / 52, observed_on 70 / 61, implemented_by 57 / 57, implements 48 / 30, supersedes 18 / 17, produced 18 / 16, supports 18 / 16, tests 8 / 7.
  - **Zero `depends_on`.** Every Fathom supersession is within one id.
  - **What a code change reaches.** It reaches requirement-level *readings* through `implemented_by`, evidence through `observed_on`, and from evidence the claims it `supports`. On this diff that is 7 readings, 10 evidence records and 6 claims (23 in all). Revision 1 said no claim was reachable. That was wrong: claims are reached through `supports`.
  - It never reaches a committed obligation. `FT-R7@2`, `FT-R18@1`, `FT-R4@2`, `DG-RA` and `DG-RB` have no code link. The readings that implement them link to them only by the deprecated `implements`. At head, `implements` is also every claim's only outgoing link.
  - `target.relationship_chart`, where F01 is, is linked by one record only, `FT-TA-R1@2`, which is created in PR #15. `FT-TA-C2`, which also links it at `68890bf`, was written after the review.

## Case 1: P5, proposal vs decision vs authorization

**The failure** (`docs/failure-modes.md` P5): a model's report of a decision is treated as the decision. Real instances:
- **Fathom.** `FT-TA-R1@2` and `FT-PO-R1@2` are `epistemic: provisional`, with the text "proposed for Zach to accept". They were nevertheless implemented and merged as the governing reading of `FT-R7@2`/`FT-R19@1` and `FT-R18@1` (`specs/007-target-analysis/spec.md`, `specs/006-report-polish/`).
- **Telosmith.** Reconstructed `HIST-*` decisions stay proposed until confirmed (`docs/decisions-to-confirm.md`).
- **relay-kit-private.** DEC-046 and DEC-047: two sessions recorded the same owner words as two decisions.

**What a Spec Kit workflow misses.** Spec Kit's spec header ("Status: Draft") and the clarifications log are free text. Nothing distinguishes "Claude's reading, for Zach to accept" from "Zach accepted", and nothing checks who may accept what.

| Item | Verdict | Removing it from Telosmith form would lose |
|---|---|---|
| `decision` with `status`, `decided_by` | **in** | the only checkable statement that something was accepted, and by whom. Without it, the HIST-* and DEC-046/047 cases are free text again. Inert on the replay diff: removing decisions changes no `code-impact` output (0 records lost) |
| `authority` with `governs` | **in** | the authority-by-subject check (`check` rule 1). A decision accepted by someone who doesn't govern its subject would pass silently. Inert on the replay diff (0 lost) |
| `epistemic` on requirements | **in** | the machine-readable split between `FT-TA-R1@2` (provisional reading) and `FT-R7@2` (committed). The exact P5 confusion in Fathom: a merged provisional reading looks like the obligation itself |
| `supersedes` across ids | **in** | which decision replaced which, when the ids differ. Telosmith has 2 such links. Without them, both decisions read as live. It loses nothing on Fathom (all its supersessions are within one id, and "latest" comes from version numbers): 0 records lost on the replay diff |
| verbatim owner `quote` / `rationale` | fact, not form | a reviewer judges consent from the words, and prose carries them equally well |
| anchors + `source` commands | out | they verify that a quote is intact (P8). Removing them loses tamper evidence, not detection of a misread. A digest is not consent (`docs/reference/source-anchors.md`) |
| `revision` type, `authorized_by` | out | nothing in any case: both are unused in both corpora, and `authorized_by` is a claim, not verified consent (AGENTS.md) |

**Limit.** Rule 1 does not catch a fabricated `decided_by`. relay-kit-private's `governance/decisions.jsonl` (DEC-018) already gives a conventional equivalent. On P5, Telosmith's marginal contribution is the authority-by-subject check and the committed/provisional flag, nothing more.

## Case 2: Data Guide findings (observation, interpretation, hypothesis, action)

**The distinction belongs to the project's domain**, not to Telosmith ("an ontology *of* the work vs ontologies *for* the work", synthesis Q2). In Fathom it is a committed requirement:
- `DG-RA@1` separates observations, interpretations, hypotheses and actions, with evidence and confidence;
- `DG-RB@1` says inference is never presented as fact;
- `FT-R4@2` judges a slice useful "without claiming more than it knows".

It is implemented in Fathom's artifact schema (`src/fathom/models.py`; `specs/001-data-review/data-model.md`), and Spec Kit's data-model artefact holds it well.

**A real consequential failure of this kind.** Data-Guide's naive missingness-by-group test fired on pure noise in 20 of 20 runs, so hypotheses were presented as findings (`relay-kit-private/kairos/dataguide-salvage-2026-11-03.md`; DEC-043 item 2). **The cheapest catch is conventional:** a null-data fixture that must produce zero findings, now a constraint in `relay-kit-private/handoffs/HO-DG-20261104-9B3S.md`. So case 2 argues for *little* Telosmith form. K1 is a case-2 failure (a chart overstating its evidence), and nothing in Telosmith form links it to `DG-RB` or `FT-R4`.

| Item | Verdict | Removing it from Telosmith form would lose |
|---|---|---|
| `requirement` + `implemented_by` to the code that produces findings | **in** | the only route by which a change to finding code puts *any* obligation in front of a reviewer. Removal test on the replay diff: dropping `implemented_by` loses all 7 readings B's report names, including `FT-TA-R1@2` and `FT-PO-R1@2`, so B's report would name no obligation at all |
| `evidence` + `observed_on` | **in** (shared with case 3) | the flag that test evidence about finding behaviour was observed on code that has now changed. Removal test: dropping `observed_on` loses 16 of 23 (10 evidence records and the 6 claims reached through them) |
| `claim` + `supports` | **in** | the step from "this evidence was invalidated" to "this conformance claim no longer stands". Removal test: dropping either loses 6 claims (`FT-TA-C1@1` and others). Revision 1 wrongly called claims unreachable on Fathom |
| `serves` from a requirement to the purpose | out | nothing a command uses: it propagates nothing, and that is why `DG-RA`/`DG-RB`/`FT-R4` are never surfaced. Kept in prose for every arm |
| `evidence_kind` / `claim_category` | out | nothing on the replay: Fathom doesn't use them. On Telosmith, removing them loses the `outcome-sufficiency` warning, which is meta-level, not this case |
| `assumption`, `criterion` | out | nothing: Fathom's `DG-A1`–`A4` are context, and nothing depends on them |
| a Telosmith type per finding kind | **rejected** | (adding it, not removing it, is the risk) it would collapse the two ontologies. Findings live in the artifact |

## Case 3: WP1A revision, snapshot and method

**The obligation** is `AEC-R10@1` (`specs/005-commit-snapshots/spec.md`): a snapshot names exactly what it describes (commit or working tree, plus extraction method), and two snapshots are compared only when their methods match. Two real hazards:
- **Method drift.** Extractor 0.4.1 (C-11, PR #32) changed edges with no change in the target code.
- **Stale evidence reused.** An observation made at one revision gets read as describing HEAD (S10).

**What a Spec Kit workflow misses.** Spec Kit has no notion of which revision a piece of evidence describes. A `validation.md` line ("164 tests pass") reads as current forever.

| Item | Verdict | Removing it from Telosmith form would lose |
|---|---|---|
| snapshot identity (commit + method) on both sides | **in**, as snapshot metadata | the guard against comparing across extractor versions. A method-drift diff would read as a code change (C-11) |
| `evidence` with `observed_on code:` and a `method` naming the revision | **in** | the only applicability rule (S10). "164 tests pass" would read as current after the code it was observed on changed |
| `depends_on` | **in**, inert on Fathom | on Telosmith (68 links), a revised decision or requirement would stop flagging the claims and decisions built on it. Fathom has none, so removing it loses nothing on the replay diff (0 lost) |
| `produced` | out | the propagation from a revised evaluation to the evidence it produced. In the four cases, the evidence's own `method` carries the revision, which covers S10. On this diff, no evaluation is changed by code, so B's and C's reports are identical without it |
| `revision` type | out | nothing: unused in both corpora |
| `diff` / `snapshot` commands as separate outputs | full arm only | an informing view. Neither triggers a review |

## Case 4: WP2A graph fidelity, interpretability and usefulness

**The four claims a representation raises** (synthesis Q2): it exists, it is faithful, an agent can interpret it, and it is useful. The evidence so far:
- probe-001: no outcome effect from structural briefings, and higher tokens on 2 of 3 tasks;
- resolver-001: 25 of 874 unresolved calls resolved;
- Codex A5RR, re-run 2026-11-04 at `906e8fd` (protocol, "Mechanism precondition"): helper and constant changes and module links produce nothing. PR #51 adds pointers and module firing.

**Fidelity on the replay diff.** `code-impact` names `FT-TA-R1@2` stale via `charts.svg_chart`. It lists `target.relationship_chart` (F01's function) only among 20 changed definitions, and it reaches no committed obligation (P1 fails). A new caller of an unchanged helper changes no linked definition, so `code-impact` stays silent; PR #15's reuse of `univariate.percentile` for box geometry (Copilot item F02) is one example.

| Item | Verdict | Removing it from Telosmith form would lose |
|---|---|---|
| `code:` links at symbol granularity (`implemented_by`, `observed_on`) | **in** | the trigger itself (removal test above: 7 or 16 records lost). Module links fire on nothing at the pin (A5RR) |
| the visibility figure (unresolved calls, skipped files) | **in** with any structural answer | the warning that "no known caller is not proof of no caller" (AGENTS.md). Without it, silence reads as safety |
| `reach`, `fan`, `unresolved` briefings | full arm only | no case shows a loss: probe-001 found no outcome effect. The full arm measures them again |
| `edges` as an artefact for an architect agent | out of scope | `AMB-tiered-agents@1` / C-20, a separate experiment |

## Ambition (C-19)

**`ambition` is not in the minimal set, in any of the four cases.** Removing it loses nothing a case needs. An ambition records a direction to keep open (DEC-033). It is not an obligation a change can break. The P5 risk it guards against, an ambition read as a commitment, is avoided by not linking ambitions into propagating relations.

Ambitions do have one role in DEC-021: they are the **yardstick** for reading its result. `AMB-adopted-by-others@1` ("Others find AEC useful") is what the outcome rules serve. The experiment record therefore `serves` that ambition, but no arm receives it. How `ambition` differs from `purpose`:
- a purpose is committed and governs requirements;
- an ambition is uncommitted, broader and less testable, and it governs what must not be foreclosed.

Whether `ambition` stays a type is Zach's vocabulary decision. This audit doesn't settle it.

## Result: the minimal set (arm B)

**Record types:** requirement (with `epistemic` and `rationale`), evidence (with `method`), claim, decision (with `status`, `decided_by` and a quote), authority (with `governs`).

**Relations:** implemented_by and observed_on (to `code:` symbols), supports, depends_on, supersedes.

**Commands:** `edges` (one pinned method for both revisions), `check --edges`, and `code-impact` between the merge-base and head snapshots, with the visibility figure.

**Out, for this question:** the types purpose, assumption, criterion, source, evaluation, revision, ambition and experiment; the relations serves, implements, tests, produced, selects and contradicts; the fields tier, evidence_kind, claim_category and anchors; and the commands `source`, `reach`, `fan`, `unresolved`, `diff`, `snapshot`, `impact` on hand-written events, `import-purpose` and `init`.

**Which items are live on the replay.** Six are live on this diff by the removal test: requirement, evidence, claim, implemented_by, observed_on and supports. Five are argued from cases 1 and 3 but are **inert on Fathom**: decision, authority, `epistemic`, depends_on and supersedes. The replay therefore cannot show whether those five earn their place.

**Mechanical derivation for the replay.** Arm B's records file is Fathom's records file at `3367ab3` with two scripted filters (`dec-021-precondition/filter_b.py`):
- keep only the types above;
- drop every relation not in the list above.

The result is 78 lines and 161 relations. It drops 14 record lines and 152 relation lines (`serves` 76, `implements` 48, `produced` 18, `tests` 8, and `supersedes` 2 on dropped records). **Every dropped line reappears, in the same words, in `docs/project-record.md`, which all three arms receive identically.** The machine-checked table is `dec-021-parity/manifest.tsv`. No record is rewritten and no link is added.

**Observations to log** (not changes made here)
1. Fathom's use of the deprecated `implements` cuts every claim's outgoing link, and every reading's link to the obligation it implements, out of propagation. Fathom's pinned AEC (`860b781`) gave 0 warnings at `3367ab3`. For the Fathom lane: either migrate to `implemented_by`/`depends_on`, or record why not. The replay will not be re-read in the light of this (protocol, "Escape hatches").
2. `serves` propagating nothing means that a purpose-level obligation (`DG-RA`, `DG-RB`, `FT-R4`) is never surfaced by a code change unless a lower requirement restates it with code links.
3. The minimal set is five types, not three, as in value-001's draft. Evidence and `observed_on` come in from case 3, because applicability is one of the four guarantees (DEC-016). Claims and `supports` come in from case 2.

## Change log

- 2026-11-04 | claude:aec-eval | Revision 1 (`195ffba`).
- 2026-11-04 | claude:aec-eval | Revision 2, after the cold Claude review (items 8 and 9) and Kate's item 1:
  - recounted Fathom at the reviewed head `3367ab3` (92 lines) instead of `68890bf`;
  - replaced "read by `impact.py`" with a removal test argued from the four cases, run on the replay diff where possible;
  - corrected "no Fathom claim is reachable" (6 are, through `supports`);
  - marked decision, authority, `epistemic`, depends_on and supersedes as inert on Fathom;
  - stated where B's dropped relations reappear.

  The set itself is unchanged.
