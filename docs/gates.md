# Gate register

Every point where a Telosmith record changes state, or where a check stops or passes something, with:
- who or what decides (the evaluator);
- what it takes (the threshold);
- what the gate protects against;
- whether it can be undone.

"Owner judgement" means no rule decides: a person with authority does.

The register exists to make hidden thresholds visible. Its exit test (from the owner's private decision log, adopting
a prior-framework alignment study): writing it must surface at least one undocumented threshold or contradiction, or
the register is not maintained. It found four. They are under [Findings](#findings) and have not been fixed here.

Reversibility is the same everywhere: records are append-only, so nothing is undone in place. "Append" below means a
correcting version is appended and the earlier one stays in the history.

## Record states (`check`)

`check` gates nothing by itself: it reports. An error fails the command (exit 1); a warning never does. The hook and CI
snippets decide what a failure blocks.

| Transition | Evaluator | Threshold | Protects against | Reversibility | Where |
|---|---|---|---|---|---|
| A line becomes a record | `check` | Parses as JSON (otherwise `check` stops with a parse error); `version` a positive JSON integer (otherwise an error, and the line is not loaded); a known `type`; `id@version` not already used (an exact repeat of a line is a warning and is read once) | Lost or reused history | A malformed line can only be fixed by editing the file, which is an exception to append-only and so an owner decision | `records.py` `Store.load`, `check` |
| Record version bump (`@n` → `@n+1`) | `check`, `aec append` | Same `id`, a version not yet used. Nothing else: see finding F1 | Rewritten history | Append | `records.py` `check` (`unique`) |
| `provisional` → `committed` | Nobody | Appending a version with `"epistemic": "committed"`; no authority or revision is checked. See F1 and F2 | (intended: unreviewed baselines) | Append a provisional version | not enforced |
| Record names its author | `check` | `authored_by` is a non-empty string; `author_role`, if present, is `owner`, `independent` or `implementer` and has an author; an unusual actor spelling only warns | Authorship claims that cannot be compared (the independence test) | Append | `records.py` `_authorship_findings` (error; warning for spelling) |
| Decision `status: accepted` | `check` | `decided_by` names an `authority` whose latest version lists the decision's `subject` in `governs` | A model's report of a decision treated as the decision | Append | `records.py` `_decision_findings` (error) |
| `revision` record counts as a revision | `check` | Has `authorized_by`; otherwise a warning says it is a proposal | Unauthorised change presented as authorised | Append with `authorized_by` | `records.py` (`authority` warning) |
| Claim/evidence tier `observed` | `check` | At least one supporting evidence record is `produced` by an evaluation | Observation claimed without a run | Append | `records.py` `_tier_findings` (error) |
| Tier `prospective` | `check` | `frozen_sha256` is a 64-character lowercase SHA-256 | Predictions written after the outcome | Append | `_tier_findings` (error) |
| Purpose-outcome claim is supported | `check` | Not every supporting evidence record is `contract_conformance` (warning if all are) | Conformance mistaken for outcome | Append evidence or narrow the claim | `_evidence_kind_findings` (warning) |
| Reference moves to a newer version | `check` | A latest record that is not evidence or a decision, pointing at `id@n` when `id@n+1` exists, warns | Changes that never reach a record still pinned to an old version | Append a version that references the newer one. There is no way to say the old pin is intended: see F3 | `_superseded_reference_findings` (warning) |
| Evidence and decisions keep old references | Rule by type | Type is `evidence` or `decision` | Re-pointing history to support nobody checked | Owner judgement on any later change to the rule | `records.py` `HISTORICAL` |
| Source anchor still matches | `check --sources` | sha256 of the file (or its declared append-only prefix) matches, and the locator resolves | A cited source changing under a record | Append a re-anchored version | `sources.py` `record_findings` (warning: `anchor-mismatch`, `anchor-locator_invalid`; `appended` passes) |
| Dangling `code:` reference gets suggestions | `check --edges` | Up to two names ending in the whole name; else up to three by last segment, spelling-close at difflib ratio ≥ 0.75. See F4 | Silent link rot when code moves | n/a (advice only) | `records.py` `_near` |

## Conclusion statuses (`impact`, `code-impact`)

A conclusion keeps the most severe status it reaches, in this order: exploratory < rebaseline < weakened < contested <
needs_review < stale < unjustified. Only latest versions take a status. Statuses are a report and are not stored:
running again on later records gives the new answer.

| Transition | Evaluator | Threshold | Protects against | Reversibility | Where |
|---|---|---|---|---|---|
| Linked code changed → `stale` | `code-impact` | The body hash of a symbol a record links to differs between the two snapshots. Code changes carry no authority, so every linked committed record goes `stale` | Rationale silently outliving the code it describes | Owner judgement: re-examine, then append | `code_impact.py`, `impact.py` (`revise`) |
| Revision of a `provisional` record → dependents `exploratory` | `impact` | `"epistemic": "provisional"` exactly. Anything else counts as committed: see F2 | Discovery reported as drift | Append | `impact.py` |
| Authorised revision → dependents `rebaseline` | `impact` | `authorized_by` names an authority governing the subject | Authorised change reported as drift | Append | `impact.py` |
| Unauthorised revision of a committed purpose, criterion or requirement → `stale`, plus a finding | `impact` | No governing authority on the change | A proposal treated as a revision | Owner judgement | `impact.py` |
| Downstream of a `stale` or `contested` record → `needs_review` | `impact` | Any dependency path | Conclusions resting on something under question | Owner judgement | `impact.py` |
| Necessary dependency on an `unjustified` record → `unjustified` | `impact` | A `necessary` relation, and the dependent is not a decision (decisions only ever get `needs_review`) | Conclusions without remaining support | Owner judgement | `impact.py` |
| Support-only dependency on an `unjustified` record → `weakened` | `impact` | The claim still has another live support | Over-invalidation | Owner judgement | `impact.py` |
| New contradicting evidence → `contested` | `impact` (`add`) | A `contradicts` relation to a resolving record | Evidence against a conclusion going unread | Owner judgement | `impact.py` |
| Linked code deleted | `impact` (`retract`) | Obligations → `needs_review` with a finding; claims or evidence that `depends_on` the code → `unjustified`; others → `needs_review` | Deleted implementations counted as satisfied | Owner judgement | `impact.py` |
| Changed code reached from a link → pointer | `code-impact` | A changed definition within `--reach-depth` steps (default 1) of a linked symbol. No status changes | Changes one step away going unseen | n/a (a pointer, not a status) | `code_impact.py` `reached_changes` |
| Changes just past the depth → note | `code-impact` | Changed definitions at exactly depth + 1 are counted in a `[note]` | A quiet report hiding what it stopped short of | n/a | `code_impact.py` `unexamined_beyond` |

## Delivery (`init` snippets)

| Transition | Evaluator | Threshold | Protects against | Reversibility | Where |
|---|---|---|---|---|---|
| Hook tells the agent | Claude Code hook | `code-impact --exit-code` exits 1 (anything affected or a finding). The hook then exits 2 and the report goes to the agent. A `[note]` alone stays quiet | Edits that reach records going unseen during the session | Remove the hook | `init.py` hook snippet |
| Hook stops on bad records | Claude Code hook | `check` exits 1 | Building on broken records | Fix and append | hook snippet |
| CI fails on bad records | CI job | `check` exits 1 | Merging broken records | Fix and append | `init.py` `ci_snippet` |
| CI reports impact | CI job | Always runs; the `code-impact` step never fails the job; writes the job summary | Reports nobody reads | Remove the job | `init.py` `ci_snippet` |
| `init` writes the hook and CI | `init` | On only when the first snapshot has code files (`--hooks` / `--no-hooks` override) | Hooks that can never fire, in repos without code | Re-run with the flag | `init.py` |
| `append` writes a record | `aec append` | Refuses an `id@version` already in use, and any new `check` error (it runs a trial file first) | A bad line entering an append-only file | Append | `append.py` |

## Owner gates outside the tool

| Transition | Evaluator | Threshold | Protects against | Reversibility |
|---|---|---|---|---|
| Purpose or contract adoption (a new `AEC-P0` version, a check's semantics) | Owner judgement, after an independent review | The owner's own words, recorded with a locator in the private decision log | Agents redefining what the project is for | Owner judgement |
| Merge to `main` | Owner, or the coordinator after review where a handoff allows it | Tests and lint pass, plus an independent review | Unreviewed change | Revert by a new PR (no force-pushes) |

## Findings

These are what writing the register surfaced. None is fixed here: each needs an owner decision on whether it is a bug,
a missing rule, or a rule to write down.

- **F1. A committed record can be changed by a plain append.** `docs/reasoning-vocabulary.md` says a committed record
  "changes only through an authorized `revision`". Nothing checks that. Appending `P-1@2` with new text under a
  committed `P-1@1` gives no error and no warning from `check` or `aec append`. The authority test exists only in
  `impact` (the rules list in that doc does assign this rule, rule 4, to `impact`), and only when someone files a
  `revise` change with `authorized_by`. Nothing files one for a plain append. Reproduction: a committed purpose at
  versions 1 and 2 with different text and no revision record; `check` reports 0 errors and 0 warnings for it.
  Options: (a) a `check` warning when a committed record's latest version has no authorised `revision` pointing at it;
  (b) reword the vocabulary doc to say the rule is procedural; (c) leave it.
- **F2. `epistemic` is not validated, and anything other than `provisional` counts as committed.** `"epistemic":
  "comitted"` (a typo) passes `check`. `impact` treats it as committed, which fails safe (the stricter treatment) but
  is not written down. Unlike `tier` and `evidence_kind`, there is no list of allowed values. The same gap applies to
  records that are not purposes, which a pilot repo raised separately (labels for non-purpose records).
- **F3. `superseded-reference` cannot be acknowledged.** The warning says "the old version may be intentional", but
  there is no way to record that intent. The owner adopted the by-type exemption (evidence and decisions) and not a
  per-relation `version_pinned` marker. So a claim or requirement that deliberately pins an old version warns for as
  long as it exists. On 2026-11-05 this repo's own `check` carried 17 of them pointing at `AEC-P0@1`. Options: re-point them, accept
  permanent warnings, or revisit the marker.
- **F4. The suggestion cutoff is undocumented.** The spelling-closeness ratio (0.75) that decides which near-miss names
  `check` suggests appears only in the code. It is advice, not a verdict, so it changes no outcome. Recorded here so the
  register is complete; documenting it in the reference is enough.

Threshold disclosure in `check` output, which shows rule, threshold, measured value and state for verdict-governing
thresholds, is separate work and not part of this page.
