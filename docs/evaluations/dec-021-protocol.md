# DEC-021 replay: conventional vs minimal vs full Telosmith on frozen Fathom material (pre-registration)

**Status: pre-registered (revision 2), not frozen, not run.** Revision 1 was written 2026-11-04 by claude:aec-eval before any trial material was built. Revision 2 (same day, same author) answers two independent reviews (Kate, GPT-6 High; a cold Claude reviewer). It adds the deterministic mechanism precondition, which was run before any trial. No trial, key or grade exists. The protocol is frozen only when the **Freeze** section is filled in and hashed. Changes before the freeze go in the change log at the end. Changes after it are amendments, made with a time and a reason, and nothing above them is edited.

**Authority**
- **DEC-021** (2026-10-31): "the ontology audit (four cases) first, then a minimal-vs-full AEC scenario".
- **DEC-031** (Zach, 2026-11-01 21:19 CT): the bounded test is the next main piece of AEC work. It is a frozen, information-matched replay of three arms (conventional, minimal AEC and full AEC) with pre-committed outcomes.
- **DEC-048** (Zach, 2026-11-04 09:17 CT): the coordinator may begin the biggest lifts today. Kate's consensus amendments:
  - freeze the Fathom source revision and the protocol before the replay;
  - evaluators must not see experimental outcomes;
  - the review must be separate and independent.
- **DEC-032**: a null result lowers priority. This protocol states below which results count as that null. A tie does not.

The experiment record is `EXP-dec021-fathom-replay@2` in `.aec/records.jsonl`. Step 1, the ontology audit, is in [dec-021-ontology-audit.md](dec-021-ontology-audit.md). The parity manifest is in [dec-021-parity/](dec-021-parity/). The precondition's raw outputs are in [dec-021-precondition/](dec-021-precondition/).

**Not authorized by this document:** running the replay. Zach decides whether to run it, the budget cap, and the injected change if anyone contests it (see "Decisions for Zach").

## Question

**As registered in revision 1:** when an independent agent reviews a real pull request, does giving it the project's obligations as Telosmith records plus Telosmith's change report surface a consequential defect more often than the same obligations as ordinary notes plus a conventional path reminder? Does the rest of Telosmith add anything over a minimal core?

**As this case can answer it (revision 2, after the precondition below).** On this PR, `code-impact` does not reach the obligation K1 breaks. Both B's change report and A's path reminder name the same record, the provisional reading `FT-TA-R1@2`. So the replay asks a narrower question: **does the form and salience of a computed change report make a reviewer surface K1 more often than a file-level reminder that names the same record?** It does not test `code-impact`'s reach. Every result is reported as a presentation result.

It remains a first, bounded instalment for committed requirement AEC-R3 ("Adoption is earned against a well-configured Spec Kit baseline with authoring cost counted; if equal, simplify AEC") and for the value-map gate for "Records, `check`, `impact`, `code-impact`" (`docs/architecture.md`, value map, row 1).

**What the replay measures on top of.** K1 is one of eight defects that GitHub Copilot's agent review had already caught on this PR. So the replay measures what Telosmith adds **on top of an agent PR review**. It does not measure what Telosmith adds to defects that Spec Kit plus an agent reviewer miss. That selection is disclosed here and is not corrected for.

## Material: Fathom PR #15 at its reviewed head

**Source.** `eraevous/Fathom`. Arms receive the PR's **reviewed head `3367ab3`** and its merge base. The later merge `68890bf` (PR #15 merged, with repairs) is used only by the key-writer.

**Why Fathom and not Data-Guide** (value-001's draft, PR #35):
- Fathom's records were written by its builder *at the time*, before the change under review. That removes the hindsight-link risk Kate raised against value-001's reconstructed links (her amendment 2).
- Fathom has a real Spec Kit setup (`.specify/`, specs 001–007, constitution, CI), so the conventional arm is genuinely well-configured, not simulated.
- Fathom postdates every trial model's training data.

**The change under review.** PR #15 as it stood when it was reviewed:
- merge base `3b89d7c`. (`944f82f`, named in revision 1, is the merge of PR #14. It has the identical tree `ae208ca`, but it is dated 22:39 CT, after the head's 21:22 CT. Arms get `3b89d7c` and a diff from it.)
- head `3367ab3`;
- the spec 007 target-analysis slice;
- **101 files**: 77 under `specs/`, 10 `src/fathom/` modules, 10 tests, 2 under `.aec/`, plus `README.md` and one `codex_++` file.

**The historical record.** At `3367ab3` the builder had run Spec Kit, the full test suite, Telosmith `check`/`impact` ("Impact reports 23 affected", `specs/007-target-analysis/validation.md`) and the FT-R17 screenshot review. All of them passed. GitHub Copilot's review then raised eight defects (review comments r4451047591 to r4451047766). All eight were repaired in `96f066e`, with regression tests in `tests/test_review_fixes.py`, and the PR merged at `68890bf`.

So the historical *author-side* workflow, which included full Telosmith, missed all eight, and a conventional independent agent reviewer caught all eight. That is a strong prior against a Telosmith advantage, and it is stated here before any trial.

## The injected change and why

Every arm reviews the same real diff `3b89d7c..3367ab3`, which contains all eight defects. Nothing is synthesised. "Injected" here means *chosen as the scored target*.

**K1, primary: F01, the log-box sample size** (r4451047766, `src/fathom/target.py`, `relationship_chart`, line 149 at head). After filtering to positive values for the log view, each box still reports `n=len(raw)`, and that n also controls the small-group caution. A group with ten complete values and one positive value is drawn from one observation but labelled n=10, with no small-sample caution. F01 is the primary because it meets every criterion below, which were fixed before any tool output was seen:
1. **It is consequential to the project's purpose, not cosmetic.** The report overstates the evidence behind a chart and suppresses a caution. That cuts against `FT-R4@2` ("without claiming more than it knows"), `DG-RB@1`, and `FT-R7@2` ("group sizes shown so small groups are visible").
2. **The obligation was written before the change by the people doing the work.** `FT-R7@2` was written on 2026-11-01. `FT-R18@1` item 3 ("a log view of the positive values, with zeros counted separately") and its implementing reading `FT-PO-R1@2` ("positive-only log coverage") date from 2026-11-02. All three are present at the merge base `3b89d7c`. `FT-TA-R1@2`, the reading that links `relationship_chart`, is **created in this PR** (absent at base).
3. **The real workflow missed it.** The historical workflow (Spec Kit, tests, CI, the FT-R17 visual pass and the author's Telosmith run) missed it, and only an independent PR review caught it.
4. **Ordinary checks don't catch it.** It is not a crash, so tests, CI and a type checker pass.
5. **It has an executable key.** F01's regression test in `tests/test_review_fixes.py` (at `96f066e`) fails at `3367ab3` and passes at `d557a71`. The cold reviewer reran it on 2026-11-04 and confirmed this.

**K2, secondary: F03, rate-plot axis captions reversed** (r4451047741). This breaks committed `FT-R10@1` (labelled axes), and the chart misleads the reader. It survived the FT-R17 screenshot pass. It isn't primary because the obligation is generic and its consequence is local.

**The other six items** (F02, F04 to F08) are scored as secondary recall only:
- **Positive controls**, where no arm advantage is expected: F04 to F06 (crashes on malformed artifacts) and F02 (a numerical crash on extreme values). An agent reviewer is expected to find these conventionally.
- **Not scorable from text:** F07 (screen-reader equivalent) and F08 (PowerPoint label overlap) need rendering.

**Selection disclosure.**
- The author chose K1 after reading the eight comments and the Fathom records, and **without running `code-impact`, `impact` or any Telosmith command on this diff** (revision 1, commit `195ffba`).
- The author did see that `FT-PO-R1@2` is `implemented_by` `code:src.fathom.charts.svg_chart` and that the PR touches `charts.py`. So a prediction that arm B's report will name `FT-PO-R1` was possible.
- In revision 2, after the reviews, the precondition below ran `code-impact` on this diff. **K1 is not re-chosen** because of what it showed. Zach may still substitute K1 before the freeze ("Decisions for Zach").

**Negative control (decoy).** PR #13 (`13807b7..6678294`, "positive log views and summary decks"), reviewed the same way. It touches the same kind of code and drew no review comments. That does **not** show it has no defects, so the decoy is **reported descriptively only**: no decision rule reads it, and it cannot bound false alarms at n = 2 per arm. Verification and replacement:
- Before the freeze, the key-writer checks `git log 6678294..68890bf` for any fix traced to PR #13's changed lines.
- If such a fix exists, PR #11 (`d195f1b..e82d5e0`) is used instead. If both fail, the decoy is dropped and that is reported.
- A defect that pre-dates the decoy PR (for example the 10-decimal `percentile` rounding later addressed by DEC-043) is "true but pre-existing". It is neither credited nor counted as a false alarm.
- On the decoy, the key-writer sorts claimed defects into "verified true", "verified false alarm" and "unverified". Only the second is called a false alarm.

## Mechanism precondition (pre-registered; run before any trial)

**Precondition P1, verbatim:**

> **P1 (code-impact reaches the governing obligation).** Before any trial, at the frozen Telosmith commit, `aec code-impact` on Fathom's records at `3367ab3`, between edge snapshots of the merge base and `3367ab3` taken with one pinned method, must name `FT-R7@2` or `FT-R18@1` (the committed obligations K1 breaks) with arm B's records or with arm C's. If it names neither, P1 has failed. The replay then measures presentation only: whether the form and salience of a pointer that arm A also receives changes what a reviewer reports. Every result, positive or null, is then reported as a presentation result and never as evidence about `code-impact`'s reach. P1's result is recorded in this section before the freeze and is not re-run after any trial output exists.

**Delivery qualification (run first).** DN2X's frozen link mapping (`docs/evaluations/code-impact-qual-001/` on PR #51; `sha256sum -c FREEZE.sha256` OK) was run through Codex's helper, constant and module cases at two Telosmith commits:
- **906e8fd (the pin):** helper and constant changes produce nothing, and module links produce nothing. This matches PR #51's `before.md` byte for byte.
- **486da47 (PR #51 head, unmerged):** helper and constant changes produce a status-free pointer, and module links fire. This matches `after.md`.

Both raw tables are in `dec-021-precondition/`. F01 sits inside a directly linked function (`target.relationship_chart`, linked by `FT-TA-R1@2`), so the helper, constant and module gaps do not decide reach for K1.

**P1 result (2026-11-04, claude:aec-eval): P1 FAILS.**

| Telosmith | records | affected | names FT-R7@2 / FT-R18@1 | names FT-TA-R1@2 | names FT-PO-R1@2 | chain to `relationship_chart` shown |
|---|---|---|---|---|---|---|
| 906e8fd | C (full) | 23 | **no / no** | stale, via `charts.svg_chart` | stale, via `charts.svg_chart` | only in the change list |
| 906e8fd | B (filtered) | 23 | **no / no** | same | same | same |
| 486da47 (PR #51) | C / B | 23 + 18 reach pointers | **no / no** | same | same | no pointer reaches it |

- **Why it fails.** No relation in Fathom's records carries a code change to `FT-R7@2` or `FT-R18@1`. Neither has a code link. The readings that implement them (`FT-TA-R1@2`, `FT-PO-R1@2`) link to them only by the deprecated `implements`, which no command propagates. This is a property of the records, not of B's filter. Full records give the same 23 statuses.
- **What reaches the reviewer.** B's and C's change reports list `revise code:src.fathom.target.relationship_chart` among 20 changed definitions, and mark `FT-TA-R1@2` stale. That record's text names FT-R19, not FT-R7. Its chain is printed via `svg_chart`. `FT-TA-C1@1`, marked needs_review, mentions "FT-R7 target ranking" in its text.
- **A's path reminder names the same record.** It covers 21 records, including the obligations `FT-TA-R1@2` and `FT-PO-R1@2`, because `src/fathom/target.py` and `charts.py` are in the diff. B's report names 23 records. B has 6 claims that A's reminder lacks (reached through `supports`). A has 4 evidence records that B lacks. Both sets are listed in `dec-021-parity/`.
- **Consequence, applied now.** The question is restated above. The arm comparison is a presentation comparison. The results table below reads every row that way.

**Mechanism outcomes recorded per report** (Kate's item 2). These locate where the chain from changed code to recorded obligation to reviewer judgement breaks:
1. the report cites `FT-TA-R1@2` (the directly linked reading);
2. the report connects K1 to `FT-R7@2` or `FT-R18@1` (the committed obligation), which no tool output supplies;
3. the report recognises the consequence (overstated evidence, a suppressed caution).

## Arms and information matching

**Equal source evidence: what every arm gets, identically**
- the same model and settings;
- the same review brief (below);
- the same tree archives of base `3b89d7c` and head `3367ab3`, with no `.git` history;
- the unified diff `3b89d7c..3367ab3`;
- the test suite and the ability to run it;
- Fathom's real Spec Kit artefacts (`.specify/`, `specs/001…007`, constitution, AGENTS.md, CHARTER.md, `docs/`);
- **`docs/project-record.md`, byte-identical in all three arms.** It renders every record line at `3367ab3` (92 lines, 74 ids) and every relation (313), from a frozen script, as prose. Each relation is one line naming both ends and the relation, for example "`FT-TA-R1@2` implements `FT-R7@2`". Code ends are rendered as dotted symbols.

In revision 1, arms B and C did not get this file, and B's filter silently dropped relations. Revision 2 gives the prose to every arm. So **every relation B's filter drops reappears, in the same words, in the prose file every arm has.** B drops 152 relation lines from its `records.jsonl`: `serves` 76, `implements` 48, `produced` 18, `tests` 8, and `supersedes` 2 on dropped records. It also drops 14 record lines: evaluation 8, assumption 4, purpose 2. All of them are in the prose.

**Unequal computed guidance, by design.** This is the intervention, not a confound. The replay tests a tooling-and-presentation package, not the ontology alone.

| | Arm | Telosmith-form records (in addition to the shared prose) | Computed guidance attached |
|---|---|---|---|
| **A** | Conventional Spec Kit | none | **path reminder**: each record whose linked *files* intersect `git diff --name-only`, from a frozen ~30-line script. This is the cheapest realistic alternative (Codex A5RR, section E; CODEOWNERS-style). On this diff it names 21 records |
| **B** | Minimal Telosmith | `.aec/records.jsonl` filtered to the audit's minimal set: 78 lines, 161 relations | `aec edges` at base and head (one pinned method), `aec check --edges`, and `aec code-impact` base→head, with the visibility figure. On this diff it names 23 records |
| **C** | Full Telosmith | the full `.aec/records.jsonl` at head (92 lines, 313 relations), with anchors resolvable in the tree | B's outputs, plus `aec diff`, `aec reach`/`fan`/`unresolved` for every changed symbol, and `aec source show` for every record `code-impact` names. The agent may also run any command |

**Machine-checkable parity manifest.** `dec-021-parity/manifest.tsv` has 413 rows: 92 records, 313 relations and 8 guidance outputs. For each row it states whether arm A, B or C receives it as prose or as jsonl. `manifest.py` regenerates the table from the records and checks it (`--check`):
- every record and relation is in every arm's prose;
- B's jsonl is a subset of C's.

After the preparer builds the arm folders, `manifest.py <records> --arms <dir>` checks the following, and the freeze requires it to pass:
- the three prose files are byte-identical;
- every row is present in each arm's prose;
- each arm's jsonl contains exactly the rows marked for it.

**Rules for information matching**
1. **The records are the real ones.** No record is added, rewritten or re-linked for the replay. Filtering in B and rendering for all arms are mechanical, scripted and hashed at the freeze.
2. **Nothing comes from after the head.** Nothing dated after `3367ab3` reaches any arm: no `review-fixes.md`, no PR comments, no later commit, no relay-kit-private material, and no `dec-021-precondition/` output beyond the arm's own attached reports.
3. **The pinned Telosmith revision** for B and C is `906e8fd`. `code_impact.py`, `impact.py` and `edges.py` are unchanged on main at `7387f88`. The extractor version is recorded at the freeze. Both snapshots use the same method (`AEC-R10@1`). If Zach merges PR #51 before the freeze and moves the pin, P1 is re-recorded at the new pin. On 2026-11-04 it also fails at PR #51's head.
4. **This is a counterfactual tool replay.** At review time the historical author had Telosmith `860b781`, not this version.

## The review brief (identical for every arm; arm appendices list only file names)

> You are reviewing a pull request to Fathom, a data-review tool. The base and head trees, the diff, the test suite and the project's specifications and recorded obligations are in your working folder; [appendix: where the records and the attached reports are]. Do not use the network, git history, GitHub or any file outside the folder. Review the change as an independent reviewer before merge. Report: (1) each consequential problem you find — what, where (file:line), why it matters for the people using the report, and which written obligation, if any, it conflicts with; (2) your decision: approve, approve with nits, or request changes; (3) for each problem, a concrete repair or a verification step. Stop at about 60 tool calls. Say what you did not check.

## Outcomes

**Primary outcome (pre-committed, per trial on the target PR, yes/no):**

> **Did the reviewer's final report surface K1, the log-box sample-size defect? To count, the report must say that a log-scale box reports its n, and the small-group caution that n controls, from all complete values instead of the positive values it plots, so the report overstates the evidence behind that box. It must also request changes on that basis and name a concrete repair or verification step. The report is graded blind against the frozen key. Anything less is "no".**

This is Kate's "no credit for mere alarms" rule (value-001, amendment 4): the report must identify the defect correctly, make a justified decision, and give an adequate repair or verification. It is analysed **as intention-to-treat**: every trial counts in its arm, whether or not the reviewer opened the attached output.

**How many trials, and what the counts can show.** The comparison is a **descriptive heuristic**, not a test. "B ahead of A" means B has at least 2 more "yes" trials than A at equal n. It is not evidence of statistical superiority. Assuming independent trials with a fixed per-trial rate (illustrative only; correlated model behaviour makes this worse), the heuristic has these error rates at n = 4 per arm:

| true rates | P(B ahead of A) | P(B or C ahead of A) | P(A ahead of B or C) |
|---|---|---|---|
| all 0.5 (no effect) | 0.145 | 0.234 | 0.234 |
| all 0.3 (no effect) | 0.120 | 0.208 | 0.186 |
| A 0.3, B 0.6 | 0.427 (miss 0.573) | | |
| A 0.3, B 0.7 | 0.552 (miss 0.448) | | |

Kate's figures (p = 0.5; 0.3 vs 0.7) and the cold reviewer's (base 0.3; 0.3 vs 0.6) both reproduce exactly in [`dec-021-power.py`](dec-021-power.py), which also gives the staged figures. At n = 6 with the same margin, the power for 0.3→0.6 rises to 0.58, but the no-effect false-favour rate rises to 0.17, so the margin would have to scale with n. **A null is weak evidence against even a moderate advantage.** Under the staged design below, with no effect and rates of 0.3, a false "B or C ahead" occurs with probability 0.21, a false "A ahead" with probability 0.06, and a ceiling stop with probability 0.22. With A at 0.3 and B at 0.6, B comes out ahead with probability 0.41.

**Secondary outcomes** (reported per arm; no decision rule attached)
1. **K2** (F03) caught, under the same three-part rule.
2. **Recall of the other six items**, each counted only if it is correctly identified and placed.
3. **Mechanism outcomes 1–3** above.
4. **Claimed defects on the target and the decoy**, in three bins: verified true, verified false alarm, unverified. On the decoy, any "request changes" is recorded. Descriptive only.
5. **Tokens:** input, output and cache-read, reported separately.
6. **Wall time and tool calls** per trial.
7. **Reviewer minutes.** The grader's timed minutes to adjudicate each redacted report, plus report length in words. These stand in for the attention a human reviewer would spend.
8. **Mechanism uptake** (from tool-call logs). Did B or C open the `code-impact` output? Did the report cite a record id it names? Did A's report cite the path reminder? Uptake is described. It never re-classifies a trial.

**Exploratory observations** (recorded, never used to read the primary; run last and cut first)

These are the four from the AEC direction map, proposed by Kate and claude:aec-direction (`relay-kit-private/aec-drift/direction-map-2026-11-02.md`, "DEC-021 and the release"; HO-AEC-20261102-AQ66):
1. **Did graph information lead to better decisions at acceptable cost?** The counterfactual is C against B, since only C gets reach/fan/unresolved output. The comparison covers the primary, K2, false alarms and median tokens, and asks whether any C report's decision cites the structural output.
2. **Can a later agent reconstruct the rationale?** After grading, one cold agent per arm gets only that arm's materials, with no reports, and answers three frozen "why" questions, each graded against the key:
   - why log views exclude non-positive values;
   - why group sizes must be shown;
   - who accepted `FT-R7`, and whether `FT-TA-R1@2` is accepted.
3. **Did authority hold when a run exposed a problem with the problem?** For example, a reviewer finding that a provisional reading (`FT-TA-R1@2`, "proposed for Zach to accept") conflicts with a committed requirement. The grader counts the reports that relax or reinterpret an obligation on their own, against those that route the conflict to the owner.
4. **Negative findings, logged as such:**
   - mechanisms present but never used (C's commands not invoked; B's report not opened);
   - a simpler arm equal to a richer one;
   - attached context that the report never used.

## How the result will be read (decided now)

P1 failed, so every row reads as a statement about **presentation of the same pointer**, never about `code-impact`'s reach.

| Result | Meaning | Action (for Zach) |
|---|---|---|
| **Ceiling**: A finds K1 in ≥ 2 of its 3 stage-0 trials | on this case an unaided agent reviewer finds K1, so increment can't be measured here | the DEC-032 null: **lowers the priority** of presentation work on records and `code-impact` as a review aid. It is not "discontinue". The value-map row records "no measurable increment on this case (ceiling)" |
| **Futility**: after stage 1, B and C each have no more "yes" than A, and no B or C "yes" report cites the attached report | presentation added nothing visible on this case | the DEC-032 null, as above, with the n and the miss rates printed beside it |
| B or C ahead of A (heuristic, equal n) | on this case, the computed report's presentation was followed by more K1 catches than a file reminder naming the same record | descriptive. Replicate prospectively on a case where P1 holds, and on an outside adopter's project (Codex A5RR, section E). Not an adoption claim, and not evidence about reach |
| B ahead, C not ahead of B | the extra machinery added nothing visible here | treat C's extras as unproven, and simplify toward the minimal set when building |
| C ahead of B (exploratory only) | structure or briefings may matter | evidence for C-12/WP2A, not a build licence. The gate still needs probe-002 |
| **Tie**: neither ahead, and neither ceiling nor futility | **inconclusive** | no priority change from this case. Report n and the miss rates above |
| A ahead of B or C | reported first, as a description. At these n a chance "A ahead" is likely (0.19–0.23 with no effect) | read the B and C transcripts for distraction. **It never by itself triggers removing `code-impact`** from any flow |

With these n, results are reported item by item and arm by arm. There is no pooled percentage, no significance test and no general claim. Every result is labelled a case study.

**Escape hatches closed now.** A null (ceiling, futility or tie) on this case **cannot afterwards be attributed to**:
- Fathom's use of the deprecated `implements`. That is Telosmith as Fathom actually used it, and P1 already records the consequence;
- Telosmith version differences (pin `906e8fd`, against the historical `860b781`, or against PR #51). P1 was run at both current candidates and fails at both;
- reviewers not opening the tool output. The analysis is intention-to-treat. Uptake is reported as a finding, not as an excuse.

Each is a reason for a *different* experiment, registered separately, never for reading this one differently.

## Procedure, roles and blinding

1. **Independent review of this protocol** (DEC-048; DEC-038): Kate and one cold Claude reviewer reviewed revision 1. Their items and the response to each are in the change log. The revision is re-read by both before the freeze, or by Zach if he waives that.
2. **Key-writer (historian).** Opus, with full history to `68890bf`. Writes the key for K1, K2 and the six other items: the obligation, the verbatim defect, the accepted repair, and an executable check adapted from `tests/test_review_fixes.py`. Verifies that each check fails at `3367ab3` and passes at `d557a71`. Verifies the decoy. The key-writer does not prepare materials and does not grade.
3. **Materials preparer.** A separate Sonnet agent that has seen no part of the key, or of history after `3367ab3`. Runs the frozen scripts: archives, diff, the shared prose rendering, A's path reminder, B's filter, and the B and C tool outputs. Runs `manifest.py --arms`, which must pass. Hashes everything into `FREEZE.sha256`.
4. **Sealing (technical, not procedural).** The key and the trial-id → arm table are each encrypted (`openssl enc -aes-256-cbc -pbkdf2`) by the coordinator. They are stored in a directory outside every trial and grading folder, which no brief or appendix names. The passphrase is never written to disk in any folder an agent can read. It is supplied to the grading step only after the trials have finished, and to the unblinding step only after the grades are frozen. Each trial agent runs with its working folder as its only readable root, so it cannot be pointed at the sealed directory. Tool logs are still audited for any attempt to read outside the folder.
5. **Trials.** Claude Sonnet reviewer subagents with no shared context, each in its own folder, in the staged order below.
6. **Redaction.** A frozen script replaces arm-revealing vocabulary with neutral tokens:
   - `aec`, `Telosmith`, `code-impact`, `needs_review`, `stale`, `unjustified`, `.aec/`, and the command names;
   - `edges`, "visibility figure", `unresolved`, `reach`, `fan`, "structural:" and "path reminder";
   - `code:` prefixes, which are rewritten to plain dotted symbols.

   Record ids remain, since all arms see them in the shared prose. Leaks that survive are noted, not claimed away.
7. **Stopping grader** (for the stage rules only). A separate Opus agent grades only the primary, on redacted reports, with no arm labels. A script (not an agent) combines its grades with the sealed arm table and outputs only the next trial ids to run. Its grades are never used for the primary.
8. **Final grading.** One Opus grader (grader 1) sees **all** redacted reports in one shuffled order, with no arm labels and no tool logs, and grades from scratch against the frozen key:
   - **Criterion-level justification.** For each of the three primary criteria (defect identified correctly; changes requested on that basis; concrete repair or verification), the grader gives a quoted span from the report, a met / not met / partial verdict and one sentence of justification. The same applies to K2.
   - **Ambiguity and second grader.** A primary judgment is *ambiguous* if any criterion is "partial", or if the grader rates its own confidence below "high". Every ambiguous judgment goes to grader 2, an independent Opus agent with the same materials and no access to grader 1's verdict. Agreement stands. Disagreement is recorded as "disputed", counted "no" in the primary, and listed with both justifications.
   - **Blind arm-identification audit.** For every report, grader 1 then guesses the arm (A, B or C) and its confidence. This happens after its grades are frozen and hashed. Accuracy is reported against chance (1/3). If accuracy reaches 2/3 or more, the primary is still reported, labelled "blinding not maintained", with the identifying features the grader names.

   Grades are frozen and hashed before unblinding. Evaluators never see arm outcomes before their own grades are frozen.
9. **Results review.** Separate and independent: Kate plus one cold Claude reviewer read the unblinded results and this protocol. They are not the grader and not the author.

**What blinding rests on.** The primary is a judgment on the report. The executable key verifies the *defect*, not the report, so it does not make the primary independent of the grader's judgment. That is why the second grader and the arm-identification audit exist.

## Staged design and trial order

No outcome-dependent discretionary stopping beyond these rules. No replicates are added and no arm is re-run outside them.

| Stage | Trials | Rule |
|---|---|---|
| 0: ceiling check | A1, A2, A3 | The stopping grader grades them. **If A finds K1 in ≥ 2 of 3, stop** and report a ceiling. |
| 1: three per arm | B1, C1, B2, C2, B3, C3 (A1–A3 complete the blocks) | Blocks *i* = {A*i*, B*i*, C*i*}, run in order *i* = 1, 2, 3. After stage 1, the script computes d = (B or C) − A at n = 3. A pair is **decided** if \|d\| ≥ 3 (ahead or behind) or d = 0 (tie: a 4th trial each cannot reach ±2). It is **undecided** if \|d\| ∈ {1, 2}. Futility is assessed here. |
| 2: fourth trial only where undecided | A4 if either pair is undecided; B4 if B–A is undecided; C4 if C–A is undecided | Final classification at n = 4 on the undecided pairs: ahead if d ≥ 2, behind if d ≤ −2, otherwise tie. Run in the order A4, B4, C4. |
| 3: decoy, descriptive | D-A1, D-B1, D-C1, D-A2, D-B2, D-C2 | Runs only if stages 0–2 finished inside the cap. Cut first. |
| 4: exploratory 2 | one per arm | Runs last. Cut before decoys finish if needed. |

Within each stage the order interleaves arms in complete blocks, as listed. **A block starts only if the remaining budget is at least 1.5 × (number of trials in the block) × the largest per-trial cost observed so far** (before any trial, the central planning rate of 1.5 M). So a cap stop always falls between blocks, and the arms in the primary comparison have equal n. If the cap stops the run inside stage 1 after *k* complete blocks, the primary is reported on A1..A*k*, B1..B*k*, C1..C*k* and labelled "stopped by budget at n = *k*". With no effect at rates 0.3, the expected number of target trials is 9.3 (12 at most).

## Budget

**Basis.** probe-001's 18 trials used **0.55–1.54 M tokens each** (median ≈1.0 M; 88–97 % cache reads) at 4–14 tool calls, about 0.1 M per call. This review allows 60 calls on a 101-file PR, so trials will run longer than probe-001's. Planning rates per trial: **low 0.55 M** (probe-001's minimum), **central 1.5 M** (probe-001's maximum), **high 3.0 M** (≈27 calls). A trial that uses all 60 calls would cost ≈6–7 M at probe-001's per-call rate, so the per-trial ceiling (60 calls or 45 min, then "no") is also a cost ceiling. Grading is ≈0.15 M per report, including justifications and the arm guess. Pre-trial work (key-writer, preparer, the re-read of this revision) is ≈2 M.

| Stage | Low | Central | High | Cumulative (low / central / high) |
|---|---|---|---|---|
| Pre-trial | 2.0 | 2.0 | 2.0 | 2.0 / 2.0 / 2.0 |
| 0: 3 A trials + stopping grade | 2.1 | 5.0 | 9.5 | **4.1 / 7.0 / 11.5** |
| 1: 6 trials + stopping grade | 4.2 | 9.9 | 18.9 | 8.3 / 16.9 / 30.4 |
| 2: expected ≈2 (at most 3) trials | 1.4 (2.1) | 3.3 (5.0) | 6.3 (9.5) | 9.7 / 20.2 / 36.7 |
| Final grading (12) + second grader + results review | 2.8 | 2.8 | 2.8 | **12.5 / 23.0 / 39.5** |
| 3: decoy, 6 trials + grading | 4.2 | 9.9 | 18.9 | |
| 4: exploratory reconstruction | 1.5 | 1.5 | 1.5 | |

Revision 1's ≈6.6 M total assumed 0.25 M per trial, which was about 4–10× too low.

**Cap: 8 M tokens, kept.** Applied with the start rule, the cap covers pre-trial work and stage 0 at the low and central rates, but not at the high rate (there stage 0 itself may not complete, and the ceiling check is reported as incomplete). It does not cover stage 1 at any rate: at the low rate the run stops after block 2 of stage 1 (n = 2 per arm), and at the central rate stage 1 cannot start. Completing the target stages needs ≈12.5 M (low) to ≈23 M (central). **Whether to raise the cap is a decision for Zach before the freeze.** Under the 8 M cap, the realistic run is the ceiling check plus a partial stage 1 with equal-n blocks. Owner attention: three decisions before the run (run or not, cap, K1), and one read of the result.

Wall time: stage 0 in one parallel batch (≈45 min), stage 1 in blocks, run in parallel within a block. Roughly 4–6 hours end to end, including key, preparation and grading.

## Stop rules

- **The key isn't objective.** If K1's executable check can't be made to fail at `3367ab3` and pass at `d557a71`, stop before any trial and report.
- **Parity fails.** If `manifest.py --arms` reports any mismatch, stop before any trial and fix the materials, not the manifest.
- **A trial is contaminated.** A trial that reads PR #15 comments, any later commit, the network, the sealed directory or anything outside its folder is invalid. It is not re-run, and it is reported. If 2 or more trials in one arm are invalid, stop and report.
- **A trial overruns.** Past 60 tool calls or 45 minutes, a trial is a "no" on the primary, and it is not re-run.
- **The budget.** Blocks start only under the rule above. At 8 M tokens, or when the next block cannot start, stop. Report the complete blocks as they stand.
- **The stage rules are the only stopping rules.** Nothing is added after outcomes are seen. K1 is not re-chosen after any trial output exists.

## What this does not measure

- **`code-impact`'s reach to an obligation on this case.** P1 failed. The replay measures presentation.
- **Increment over Spec Kit plus no agent reviewer.** K1 was caught by an agent PR review. The replay measures increment on top of one.
- **Authoring cost.** Fathom's records already existed (a sunk cost), so this replay says nothing about whether writing them pays. Their cost appears only as Fathom's history, not as a measured figure.
- **Whether someone could have chosen these links before knowing the failure** (Codex A5RR, assumption 1). Fathom's builder wrote them for other reasons, which is better than hindsight, but it is one builder.
- **Maintenance over time,** link rot and alert fatigue.
- **Generality** beyond one PR in one Python project owned by Zach, or other languages.
- **Human reviewers.** "Reviewer minutes" is a grader-agent proxy.
- **Planned features** (`aec context`, `drift`, reconciliation, premise checks). They earn no credit.
- **Copilot specifically,** or differences between models. All trial agents are Claude, so shared biases are not controlled.
- **Whether AEC is worth it to Zach** as research, a personal tool or a portfolio piece. That is DEC-031's first judgement, made by him.
- **The four guarantees separately,** or rendered or visual defects (F07, F08).

## Relation to value-001 (PR #35)

value-001 (draft, unmerged) designed this comparison on Data-Guide's 2025 history, using reconstructed links. This protocol adopts value-001's outcome rules and Kate's seven pre-freeze amendments where they apply:
- 1: a well-configured A;
- 2: no hindsight records (met by using real records);
- 3: what each arm gets (now the parity manifest);
- 4: no credit for mere alarms;
- 5: what n=1 can decide;
- 6: three separate roles;
- 7: ambition stays out of B.

Whether value-001's Data-Guide case still runs as a second case, or is closed as superseded, is for Zach.

## Decisions for Zach (before the freeze)

1. **Run or not,** given that P1 failed and the replay now measures presentation only. Not running, and spending the budget on a case where P1 holds, is a legitimate choice.
2. **The cap.** Keep 8 M (ceiling check plus a partial stage 1), or raise it to ≈13–23 M to finish the target stages.
3. **The injected change.** K1 = F01 as argued above, unless contested. Alternatives: F03 as primary, or a joint primary of K1 and K2.
4. **The pin.** `906e8fd`, or PR #51 if it merges first. P1 fails at both.
5. **value-001's Data-Guide case:** run, fold in or close.

## Freeze

*To be filled at freeze, after the re-read of this revision:*
- the Telosmith commit and extractor version;
- the model ids and settings;
- the trial ids for each stage, in order;
- the decoy commit as verified;
- `manifest.py --arms` output (must be clean);
- the SHA-256 of the encrypted key, the encrypted arm table, the scripts, every arm folder and this file.

## Change log (pre-freeze)

- 2026-11-04 | claude:aec-eval | Revision 1 pre-registered (`195ffba`): ontology audit done, protocol drafted. No materials built, no Telosmith command run on PR #15's diff, no trials.
- 2026-11-04 | claude:aec-eval | **Revision 2, after two independent reviews** (Kate, GPT-6 High, verdict "freeze after fixes"; cold Claude reviewer, verdict "redesign (limited)"). No trial, key or grade exists. Changes, by review item:
  - *Information parity* (Kate 1, BLOCKING): every arm now gets one byte-identical prose rendering of all records and relations. B's dropped relations reappear there. Added the machine-checked manifest and a statement of the unequal computed guidance.
  - *K1 mechanism* (Kate 2; Claude B1, BLOCKING): ran the delivery qualification and `code-impact` before any trial. Added precondition P1, which **fails**. The question is restated as a presentation comparison, A's and B's named sets are published, and mechanism outcomes 1–3 are added.
  - *Power and null action* (Kate 3, BLOCKING; Claude B3, BLOCKING): ≥2 is now a descriptive heuristic. Both reviewers' error rates are in the document. A tie is inconclusive. A chance "A ahead" never removes `code-impact`. The DEC-032 null applies only to a ceiling or a pre-stated futility pattern.
  - *Budget* (Kate 5; Claude B2, BLOCKING): re-costed from probe-001's 0.55–1.54 M per trial. The 8 M cap is kept, with blocks interleaved across arms and a start rule, so a cap stop leaves arms at equal n.
  - *Sequential design* (Kate 5; Claude 7): stage 0 (3 A trials, stop on ≥ 2/3), then 3 per arm, then a 4th only where undecided. Decoys and exploratory work run last.
  - *Blinding* (Kate 4; Claude 4): the key and the arm table are encrypted outside agent-readable folders. Added a stopping grader distinct from the final grader, criterion-level justifications, a second grader on ambiguous judgments and a blind arm-identification audit. Widened redaction. Corrected the statement that the executable key protects the primary.
  - *Selection* (Claude 5): stated that K1 comes from defects an agent PR review had already caught.
  - *Escape hatches* (Claude 6): committed now; intention-to-treat.
  - *Decoy* (Kate nit; Claude 10): descriptive only, with true / false-alarm / unverified bins.
  - *Ontology audit* (Claude 8, 9): recounted at `3367ab3`, and argued from the four cases with a removal test. See the audit's change log.
  - *Facts* (Claude nits): the merge base is `3b89d7c` (identical tree to `944f82f`, which is dated after the head). The diff has 101 files. Revision 1 planned 4 target and 2 decoy trials per arm (18 in all), as Kate also noted.
  - *Declined:* Kate's recommendation to retain DEC-032's priority-lowering for every null. A tie is too weak at these n (miss rate 0.45–0.57) to lower priority, so only the ceiling and futility patterns do. Claude 7's "then 6 per arm": the cap cannot fund it, and the margin would need re-scaling.
