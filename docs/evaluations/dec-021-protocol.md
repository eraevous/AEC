# DEC-021 replay: conventional vs minimal vs full Telosmith on frozen Fathom material (pre-registration)

**Status: pre-registered, not frozen, not run.** Written 2026-11-04 by claude:aec-eval, before any trial material was built and before any Telosmith command was run on the change under review. The protocol is frozen only when the **Freeze** section is filled in and hashed, after the independent review below. Changes before the freeze go in the change log at the end. Changes after it are amendments, made with a time and a reason, and nothing above them is edited.

**Authority**
- **DEC-021** (2026-10-31): "the ontology audit (four cases) first, then a minimal-vs-full AEC scenario".
- **DEC-031** (Zach, 2026-11-01 21:19 CT): the bounded test is the next main piece of AEC work. It is a frozen, information-matched replay of three arms (conventional, minimal AEC and full AEC) with pre-committed outcomes.
- **DEC-048** (Zach, 2026-11-04 09:17 CT): the coordinator may begin the biggest lifts today. Kate's consensus amendments:
  - freeze the Fathom source revision and the protocol before the replay;
  - evaluators must not see experimental outcomes;
  - the review must be separate and independent.
- **DEC-032**: a null result lowers priority.

The experiment record is `EXP-dec021-fathom-replay@1` in `.aec/records.jsonl`. Step 1, the ontology audit, is in [dec-021-ontology-audit.md](dec-021-ontology-audit.md).

**Not authorized by this document:** running the replay. Zach decides whether to run it, and decides the injected change if anyone contests it (see "Decisions for Zach").

## Question

When an independent agent reviews a real pull request, does giving it the project's obligations as Telosmith records plus Telosmith's change report surface a consequential defect more often than the same obligations as ordinary notes plus a conventional path reminder? Does the rest of Telosmith add anything over a minimal core?

This is committed requirement AEC-R3 made testable: "Adoption is earned against a well-configured Spec Kit baseline with authoring cost counted; if equal, simplify AEC". It is also the first instalment of the value-map gate for "Records, `check`, `impact`, `code-impact`" (`docs/architecture.md`, value map, row 1).

## Material: frozen Fathom revision `68890bf`

**Source.** `eraevous/Fathom` main at `68890bf0455a4490afc6634b0dcb5cd5d8e118bb` (PR #15 merged). Every artefact used by the replay comes from this revision's history.

**Why Fathom and not Data-Guide** (value-001's draft, PR #35):
- Fathom's records were written by its builder *at the time*, before the change under review. That removes the hindsight-link risk Kate raised against value-001's reconstructed links (her amendment 2).
- Fathom has a real Spec Kit setup (`.specify/`, specs 001–007, constitution, CI), so the conventional arm is genuinely well-configured, not simulated.
- Fathom postdates every trial model's training data.

**The change under review.** PR #15 as it stood when it was reviewed:
- merge base `944f82f`;
- head `3367ab3`;
- the spec 007 target-analysis slice;
- 99 files, of which 10 are `src/fathom/` modules.

**The historical record.** At `3367ab3` the builder had run Spec Kit, the full test suite, Telosmith `check`/`impact` ("Impact reports 23 affected", `specs/007-target-analysis/validation.md`) and the FT-R17 screenshot review. All of them passed. GitHub Copilot's review then raised eight defects (review comments r4451047591 to r4451047766). All eight were repaired in `96f066e`, with regression tests in `tests/test_review_fixes.py`, and the PR merged at `68890bf`.

So the historical *author-side* workflow, which included full Telosmith, missed all eight, and a conventional independent reviewer caught all eight. That is a strong prior against a Telosmith advantage, and it is stated here before any trial.

## The injected change and why

Every arm reviews the same real diff `944f82f..3367ab3`, which contains all eight defects. Nothing is synthesised. "Injected" here means *chosen as the scored target*.

**K1, primary: F01, the log-box sample size** (r4451047766, `src/fathom/target.py`). After filtering to positive values for the log view, each box still reports `n=len(raw)`, and that n also controls the small-group caution. A group with ten complete values and one positive value is drawn from one observation but labelled n=10, with no small-sample caution. F01 is the primary because it meets every criterion below, which were fixed before any tool output was seen:
1. **It is consequential to the project's purpose, not cosmetic.** The report overstates the evidence behind a chart and suppresses a caution. That cuts against `FT-R4@2` ("without claiming more than it knows"), `DG-RB@1`, and `FT-R7@2` ("group sizes shown so small groups are visible").
2. **The obligation was written before the change by the people doing the work.** `FT-R7@2` was written on 2026-11-01. `FT-R18@1` item 3 ("a log view of the positive values, with zeros counted separately") and its implementing reading `FT-PO-R1@2` ("positive-only log coverage") date from 2026-11-02. All three are present at the merge base `944f82f`.
3. **The real workflow missed it.** The well-configured historical workflow (Spec Kit, tests, CI, the FT-R17 visual pass and the author's Telosmith run) missed it, and only an independent PR review caught it.
4. **Ordinary checks don't catch it.** It is not a crash, so tests, CI and a type checker pass.
5. **It has an executable key.** F01's regression test in `tests/test_review_fixes.py` (at `96f066e`) fails at `3367ab3` and passes at `d557a71`.

**K2, secondary: F03, rate-plot axis captions reversed** (r4451047741). This breaks committed `FT-R10@1` (labelled axes), and the chart misleads the reader. It survived the FT-R17 screenshot pass. It isn't primary because the obligation is generic and its consequence is local.

**The other six items** (F02, F04 to F08) are scored as secondary recall only:
- **Positive controls**, where no arm advantage is expected: F04 to F06 (crashes on malformed artifacts) and F02 (a numerical crash on extreme values). An agent reviewer is expected to find these conventionally.
- **Not scorable from text:** F07 (screen-reader equivalent) and F08 (PowerPoint label overlap) need rendering.

**Selection disclosure.**
- The author chose K1 after reading the eight comments and the Fathom records, and **without running `code-impact`, `impact` or any Telosmith command on this diff**.
- The author did see that `FT-PO-R1@2` is `implemented_by` `code:src.fathom.charts.svg_chart` and that the PR touches `charts.py`. So a prediction that arm B's report will name `FT-PO-R1` is possible, and that is a selection-bias risk.
- **The delivery qualification below runs only after the freeze. K1 is not re-chosen whatever it shows.**
- Zach may substitute K1 before the freeze ("Decisions for Zach").

**Negative control (decoy).** PR #13 (`13807b7..6678294`, "positive log views and summary decks"), reviewed the same way. It touches the same kind of code, it drew no review comments, and no later commit up to `68890bf` is known to repair it.
- Before the freeze, the key-writer checks `git log 6678294..68890bf` for any fix traced to PR #13's changed lines.
- If such a fix exists, PR #11 (`d195f1b..e82d5e0`) is used instead. If both fail, the decoy is dropped and that is reported.
- A defect that pre-dates the decoy PR (for example the 10-decimal `percentile` rounding later addressed by DEC-043) is "true but pre-existing". It is neither credited nor counted as a false alarm.

## Arms and information matching

**What every arm gets, identically**
- the same model and settings;
- the same review brief (below);
- the same tree archives of the base and head revisions, with no `.git` history beyond the head;
- the unified diff;
- the test suite and the ability to run it;
- Fathom's real Spec Kit artefacts (`.specify/`, `specs/001…007`, constitution, AGENTS.md, CHARTER.md, `docs/`);
- **every fact in Fathom's records at the head revision.**

The arms differ only in the *form* those facts take and in which deterministic tool output is attached.

| | Arm | Records form | Attached tool output |
|---|---|---|---|
| **A** | Conventional Spec Kit | `docs/project-record.md`: every record at head, rendered to prose by a frozen script (id, version, type, status/epistemic, text, rationale, quote, and every relation as a plain sentence, including "FT-PO-R1@2 is implemented by `src/fathom/charts.py::svg_chart`") | **path reminder**: each obligation whose linked *files* intersect `git diff --name-only`, from a frozen ~30-line script. This is the cheapest realistic alternative (Codex A5RR, section E; CODEOWNERS-style) |
| **B** | Minimal Telosmith | `.aec/records.jsonl` filtered to the audit's minimal set (types requirement, evidence, claim, decision, authority; relations implemented_by, observed_on, depends_on, supports, supersedes). Records outside the set go to `docs/project-record.md` as in A | `aec edges` at base and head (one pinned method), `aec check --edges`, `aec code-impact` base→head, with the visibility figure |
| **C** | Full Telosmith | the full `.aec/records.jsonl` at head, with anchors resolvable in the tree | B's outputs plus `aec diff`, plus `aec reach`/`fan`/`unresolved` for every changed symbol, and `aec source show` for every record `code-impact` names. The agent may also run any of the twelve commands |

**Rules for information matching**
1. **The records are the real ones.** No record is added, rewritten or re-linked for the replay. Filtering in B and rendering in A are mechanical, scripted and hashed at the freeze.
2. **Nothing comes from after the head.** Nothing dated after `3367ab3` reaches any arm: no `review-fixes.md`, no PR comments, no later commit, no relay-kit-private material. Archived text is never given to one arm only.
3. **The pinned Telosmith revision** for B and C is `906e8fd`, with the extractor version recorded at the freeze. Both snapshots use the same method (`AEC-R10@1`).
4. **This is a counterfactual tool replay.** At review time the historical author had Telosmith (`860b781`), not this version.

## The review brief (identical for every arm; arm appendices list only file names)

> You are reviewing a pull request to Fathom, a data-review tool. The base and head trees, the diff, the test suite and the project's specifications and recorded obligations are in your working folder; [appendix: where the records and the attached reports are]. Do not use the network, git history, GitHub or any file outside the folder. Review the change as an independent reviewer before merge. Report: (1) each consequential problem you find — what, where (file:line), why it matters for the people using the report, and which written obligation, if any, it conflicts with; (2) your decision: approve, approve with nits, or request changes; (3) for each problem, a concrete repair or a verification step. Stop at about 60 tool calls. Say what you did not check.

## Outcomes

**Primary outcome (pre-committed, per trial on the target PR, yes/no):**

> **Did the reviewer's final report surface K1, the log-box sample-size defect? To count, the report must say that a log-scale box reports its n, and the small-group caution that n controls, from all complete values instead of the positive values it plots, so the report overstates the evidence behind that box. It must also request changes on that basis and name a concrete repair or verification step. The report is graded blind against the frozen key. Anything less is "no".**

This is Kate's "no credit for mere alarms" rule (value-001, amendment 4): the report must identify the defect correctly, make a justified decision, and give an adequate repair or verification.

**Arm-level reading** (n = 4 per arm on the target):
- **Arm favoured:** at least 2 more "yes" trials than A.
- **Tie:** a difference of 0 or 1.
- **Harm:** A has at least 2 more than B or C. Harm is reported first.

**Secondary outcomes** (reported per arm; no decision rule attached)
1. **K2** (F03) caught, under the same three-part rule.
2. **Recall of the other six items**, each counted only if it is correctly identified and placed.
3. **False alarms.** On the target PR and the decoy, a claimed defect counts as a false alarm if the key-writer can't verify it with an executable check or a source citation. On the decoy, any "request changes" is recorded.
4. **Tokens:** input, output and cache-read, reported separately.
5. **Wall time and tool calls** per trial.
6. **Reviewer minutes.** The grader's timed minutes to adjudicate each redacted report, plus report length in words. These stand in for the attention a human reviewer would spend.
7. **Mechanism uptake** (from tool-call logs). Did B or C open the `code-impact` output? Did the report cite a record id it names? Did A's report cite the path reminder?

**Exploratory observations** (recorded, never used to read the primary)

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

| Result | Meaning | Action (for Zach; DEC-032) |
|---|---|---|
| B or C favoured on the primary, with no excess false alarms on the decoy | the recorded-obligation mechanism surfaced a consequence that same-fact notes plus a path reminder did not, on this case | keep the minimal core, and replicate prospectively on an outside adopter's project (Codex A5RR, section E). Not an adoption claim |
| B favoured, C equal to B | the extra machinery added nothing here | simplify toward the minimal set. Treat C's extras as unproven |
| C favoured over B (2 or more) | structure or briefings mattered | evidence for C-12/WP2A, not a build licence. The gate still needs probe-002 |
| **Null: A ties B and C** | on this case, Telosmith's form and reports added nothing over the same facts as notes plus a path reminder | **lowers the priority** of building on records and `code-impact` (DEC-032). The value-map row records "no added value on this case". It does not mean "discontinue": n is one PR in the owner's own project. "A later feature will make it pay off" is not a reason to proceed |
| Harm (A favoured) | the attached output distracted the reviewer | reported first. Remove `code-impact` from any default review flow until explained |
| Every arm 4/4 on the primary | ceiling: an independent agent reviewer finds K1 unaided | a legitimate null about incremental value (the probe-001 pattern) |

With n = 4 per cell, results are reported item by item and arm by arm. There is no pooled percentage, no significance test and no general claim. Every result is labelled a case study.

## Procedure, roles and blinding

1. **Independent review of this protocol** (DEC-048; DEC-038, with Kate as one reviewer), plus one cold Claude reviewer that has seen no outcomes. Accepted changes are logged below. Then the protocol is frozen.
2. **Key-writer (historian).** Opus, with full history to `68890bf`. Writes the key for K1, K2 and the six other items: the obligation, the verbatim defect, the accepted repair, and an executable check adapted from `tests/test_review_fixes.py`. Verifies that each check fails at `3367ab3` and passes at `d557a71`. Verifies the decoy. Freezes and hashes the key, and stores it outside every folder that trial agents or graders can read. The key-writer does not prepare materials and does not grade.
3. **Materials preparer.** A separate Sonnet agent that has seen no part of the key, or of history after `3367ab3`. Runs the frozen scripts: archives, diff, A's prose rendering and path reminder, B's filter, and the B and C tool outputs. Hashes everything into `FREEZE.sha256`.
4. **Delivery qualification** (after the freeze; changes nothing). Record whether B's `code-impact` output is empty or non-empty, and which records it names. If it names nothing, the run proceeds: a silent mechanism is a finding.
5. **Trials.** Claude Sonnet reviewer subagents with no shared context, each in its own folder. Target PR: 3 arms × 4 replicates. Decoy: 3 arms × 2. That is **18 trials**, in a fixed order from `random.seed(20261104)`. The trial-id → arm key is sealed outside every readable folder.
6. **Redaction.** A frozen script replaces Telosmith vocabulary (`aec`, `Telosmith`, `code-impact`, `needs_review`, `stale`, `unjustified`, `.aec/`, and the command names) and A's "path reminder" heading with neutral tokens. Record ids remain, since all arms see them. Leaks are noted, not claimed away.
7. **Grading.** One Opus grader sees redacted reports in a shuffled order, with no arm labels and no tool logs. It grades against the frozen key and times each report. Grades are frozen and hashed before unblinding. Evaluators never see arm outcomes before their own grades are frozen.
8. **Results review.** Separate and independent: Kate plus one cold Claude reviewer read the unblinded results and this protocol. They are not the grader and not the author.

**Blinding is procedural, not technical.** Agents share a filesystem with the sealed keys, so blinding rests on instructions plus a post-hoc audit of tool logs for reads of sealed paths. The primary is graded against an executable key, which limits how much it depends on blinding.

## Budget (one day, Sonnet and Opus subagents)

| Step | Runs | Expected tokens (mostly cache reads) |
|---|---|---|
| Key-writer (Opus) | 1 | ≈0.5 M |
| Materials preparer (Sonnet, scripts) | 1 | ≈0.3 M |
| Trials (Sonnet, ≤60 tool calls each) | 18 | ≈0.25 M each, ≈4.5 M |
| Grader (Opus) | 1 pass over 18 reports | ≈0.6 M |
| Exploratory 2 (rationale reconstruction) | 3 | ≈0.3 M |
| Protocol and results reviews | 2 + 2 | ≈0.4 M plus Kate's thread |
| **Total** | | **≈6.6 M tokens; hard cap 8 M** |

Wall time: trials run in parallel batches of 6, about 3 × 45 min, so roughly 6 hours end to end including key, preparation and grading. Owner attention: two decisions before the run, one read of the result.

## Stop rules

- **The key isn't objective.** If K1's executable check can't be made to fail at `3367ab3` and pass at `d557a71`, stop before any trial and report.
- **A trial is contaminated.** A trial that reads PR #15 comments, any later commit, the network or a sealed path is invalid. It is not re-run, and it is reported. If 2 or more trials in one arm are invalid, stop and report.
- **A trial overruns.** Past 60 tool calls or 45 minutes, a trial is a "no" on the primary, and it is not re-run.
- **The budget runs out.** At 8 M tokens, stop. Report the completed trials as they stand. No analysis happens before the planned set is complete or stopped.
- **Nothing is added after outcomes are seen.** No replicates are added, no arms are re-run, and K1 is not re-chosen after any trial output exists.

## What this does not measure

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
- 3: what each arm gets;
- 4: no credit for mere alarms;
- 5: what n=1 can decide;
- 6: three separate roles;
- 7: ambition stays out of B.

Whether value-001's Data-Guide case still runs as a second case, or is closed as superseded, is for Zach.

## Decisions for Zach (before the freeze)

1. **Run or not.** This document doesn't authorize running the replay.
2. **The injected change.** K1 = F01 as argued above, unless contested. Alternatives: F03 as primary, or a joint primary of K1 and K2.
3. **value-001's Data-Guide case:** run, fold in or close.

## Freeze

*To be filled at freeze, after the independent review:*
- the Telosmith commit and extractor version;
- the model ids and settings;
- the trial order;
- the decoy commit as verified;
- the SHA-256 of the key, the scripts, every arm folder and this file.

## Change log (pre-freeze)

- 2026-11-04 | claude:aec-eval | Pre-registered: ontology audit done, protocol drafted. No materials built, no Telosmith command run on PR #15's diff, no trials.
