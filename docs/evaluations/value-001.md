# value-001: does AEC's minimal core earn its cost? (pre-registration, DRAFT)

**Status: draft, not frozen.** Authorised by Zach as the next main piece of work (DEC-031, 2026-11-01
21:19 CT), implementing DEC-021 as bounded by Kate (2026-11-01). Nothing below is final until the
freeze section is filled in and hashed. Changes before the freeze are recorded in the change log at
the end. Changes after it are amendments.

## Question

**What is the smallest set of AEC records and checks that catches a consequential change a
well-configured conventional workflow would miss, and is it worth its authoring and maintenance cost?**

This is committed requirement AEC-R3 made testable: "Adoption is earned against a well-configured Spec
Kit baseline with authoring cost counted; if equal, simplify AEC."

Two separate judgements follow from the result (DEC-031):
- **worth it to Zach**, in several ways: research, a tool he uses, and a portfolio;
- **Zach's ambition that others find it useful.**

This study speaks mainly to the second. Its outcome rules are about usefulness to someone maintaining
code, not about the first.

## Step 1: bounded ontology audit

Kate limited the audit to the question above, not the whole possible vocabulary.

**What exists.** Version 0.4.1 plus main:
- 11 record types: purpose, requirement, criterion, assumption, source, claim, evidence, evaluation,
  decision, authority and revision.
- 11 relations: serves, implements, implemented_by, depends_on, supports, contradicts, tests,
  produced, selects, supersedes and observed_on.
- Optional fields: epistemic status, tier, evidence kind, claim category and source anchors.

**What AEC's own records use** (102 records on main @9f57e19):

| | Used | Never used |
|---|---|---|
| Types | decision 52, source 21, requirement 11, evidence 8, claim 7, authority 2, purpose 1 | criterion, assumption, evaluation, revision |
| Relations | depends_on 64, supersedes 25, serves 14, observed_on 14, implemented_by 11, supports 8 | implements, contradicts, tests, produced, selects |

The MtG pilot uses criterion, assumption and evaluation, plus produced and selects; that's the
reasoning-only, non-code domain. The itsdangerous demo shows the smallest code-impact case: one
requirement `implemented_by` a `code:` symbol, and one claim that `depends_on` it.

**What code-impact needs** to flag a recorded obligation when code changes:
- a requirement (the obligation) and its link to code (`implemented_by` → `code:`);
- whatever rests on it (`depends_on`: claims, decisions);
- the edge snapshots before and after, from the extractor;
- `check` (references resolve) and `code-impact` (propagation).

That is about 1,100 of AEC's roughly 2,300 lines (records, impact, code_impact, edges). Source anchors,
commit snapshots and graph queries, purpose import and init are outside it.

**Minimal AEC, as a candidate definition (condition B):**
- record types requirement, claim and decision (plus authority only if a scenario needs an accepted decision);
- relations implemented_by, depends_on and supports;
- commands `edges`, `check --edges` and `code-impact`.

Kate's candidate list adds "a review finding" and "the source or rationale for the obligation". Both can
be carried in a requirement's `rationale` field or a `source` record. Whether either is needed is
decided by the scenarios, not assumed.

**Ambition (C-19).** Zach proposed `ambition` as a record type "like decision". For this study an
ambition doesn't enter condition B, because code-impact never propagates from one. It is the yardstick
the outcome is judged against: his ambition that others find AEC useful is what the outcome rules
below serve. Whether it becomes a record type, and how it differs from `purpose` (purposes are
committed and govern requirements; an ambition is broader and less testable), is a vocabulary
decision for Zach. It is not settled here.

## Step 2: scenarios

Requirements for a scenario:
- a real past change in AEC, Data-Guide or Fathom;
- an obligation written down *before* the change;
- consequence evidence;
- a record of how, and whether, it was noticed.

Plus at least one real decoy: a change to the same kind of code that endangered nothing consequential.

**Search.** About 320 commits across AEC, Data-Guide and relay-kit-private (2026-11-01, a separate
agent with a strict brief). I checked the primary scenario against the commits myself. Only Data-Guide's
2025 history gives clean events where the obligation was written before the change. AEC and relay-kit
are young (from 2026-10-26) and heavily reviewed. Their defects were caught in the same PR, or had no
earlier written obligation.

**Primary scenario: DG-097c307, profiler consolidation (Data-Guide, 2025-07-21).**
- **The change.** Codex PR #7 (`097c307`, merged 46 seconds later) deleted `src/profiler.py` and
  `profiler_update.py`. It switched three pipelines from `from profiler import DataProfiler` to
  `from data_profiler import DataProfiler`. The old class took `output_dir`
  (`097c307^:src/profiler.py:421`); the new one doesn't (`097c307:src/data_profiler.py:18`).
  `src/pipeline.py:54` still passes `output_dir=`, so every pipeline run raises TypeError. The same
  commit deleted `test_profiler.py`.
- **Obligations written before the change:**
  - `docs/RECONCILIATION_PLAN.md` (`3b2f110`, 2025-07-20): "Merge useful features from `profiler.py`
    and `profiler_update.py` then delete those modules." The PR deleted, but didn't merge.
  - `src/pipeline.purpose.md` (`e877113`, 2025-07-19): the pipeline "orchestrates DataProfiler … and
    writes reports".
- **How it was noticed:** never as a defect. It was repaired incidentally three months later (`d435bd7`,
  2025-10-21). Harm was latent: work had moved to the CLI the same day.

**Control scenario: DG-d435bd7, CLI broken by a profiler rewrite (2025-10-21).**
- `d435bd7` changed `generate_report(format, dataset)` to `generate_report(format, output_filename)`.
  `src/typer_cli.py:56` still passed `dataset=`, so every CLI run failed.
- Obligation: `typer_cli.purpose.md` (`4e7445f`, 2025-07-21), "Write profiling reports to an output
  directory".
- Zach caught and fixed it about an hour later (`37426e7`), presumably by running the CLI. This tests
  whether the conditions tie when the problem is quick to surface.

**Decoys:**
- AEC #20 (`860b781`). It changed `records.check`; `code-impact` flags AEC-R8, yet the R8 rules were
  unchanged (CL-R8-check). This is a real AEC false alarm.
- Data-Guide `d1e614c`. It moved CLI options into config, deliberately, by the owner. The purpose holds;
  only the docs drifted.

**Considered and set aside:**
- A third Data-Guide event: `37426e7` silently disabled report writing. Its obligation was only an hour
  old, and the affected callers were dormant.
- AEC's untagged release pin (C-14). It depends on release tagging, not on code. AEC flagged AEC-R7 stale,
  but a claim still asserted R7 held, so the flag didn't lead to the catch.
- Ledger CH-012. It's data, not code.
- C-11's wrong edges. Copilot caught them before merge.
- Reconstructed HIST-* records, the staged itsdangerous demo, probe-001's built tasks, and the MtG pilot
  (real, but not code).

**What the scarcity means.** Three qualifying events in about 320 commits, all in one area of one repository.
- Real cases of "a change broke a written obligation and slipped through" are uncommon here.
- Both strong cases would plausibly be caught by a smoke test or a type checker, and their history had
  neither tests nor review. The conventional condition is therefore strong, and a gap between A and C
  could just reflect that original weakness.
- At n=1 in the owner's own repository, this study is a case report. A positive result motivates the
  outside-adopter replication. A null result doesn't show AEC has no value, but under AEC-R3 it does
  argue for simplifying.

**What AEC can and can't see here.** For condition B to flag anything, the obligation must already be a
record linked to code: for example, the pipeline requirement `implemented_by` `code:src.profiler.DataProfiler`.
- Deleting that class makes `code-impact` mark the requirement for review.
- AEC does not check call signatures. So B can say "this obligation's code was deleted; look again", not
  "TypeError".
- Whether that prompt leads a reviewer to the broken call is exactly what the replay measures.

**If no real scenario qualifies,** that is a finding in its own right. It would mean the failure AEC
guards against is rare at this project's scale, or invisible in its history. The study then reports
that and stops before Step 3. A staged scenario is not substituted.

## Step 3: replay (conditions, measures, outcomes)

**Conditions.** All three get the same underlying facts: the obligation, its rationale and where it
applies.

| | What the agent or reviewer has |
|---|---|
| **A. Conventional** | the repository at the pre-change commit, the change as a PR diff, tests, Spec Kit artefacts where the project had them, and the obligation written as an ordinary note or ADR in the repo |
| **B. Minimal AEC** | A, plus the obligation as minimal AEC records and the `code-impact` report for the change |
| **C. Full AEC** | A, plus the project's full applicable records and AEC's other relevant commands (anchors, snapshots, graph queries). No new capability is built |

Each condition reviews the scenario change and the decoy, with the order counterbalanced. The model
and settings are fixed and named at freeze. Trials per cell are set at freeze; probe-001 used 2, and
this study should use at least 3.

**Measures**
1. The consequential issue is identified correctly. This is the primary measure, graded blind against
   a key written at freeze.
2. The finding changed the decision or action: approve, request changes, or revise the obligation.
3. False alarms and unnecessary work, including on the decoy.
4. Cost: authoring time to write the records for B and C, review time, tokens, and turns.
5. Durability: whether the recorded understanding stays correct after a later real change, where the
   history allows it.

**Pre-committed outcomes** (Kate, 2026-11-01):
- **Positive:** B or C catches the consequential issue and A does not, without disproportionate false
  alarms. Keep the minimal capability, and replicate on an unfamiliar project with an outside adopter.
- **Equivalent at higher cost:** A does as well. Simplify toward conventional tools, per AEC-R3, keeping
  only parts that demonstrably contribute.
- **B equals C:** simplify toward minimal AEC, and treat C's extra machinery as unproven.
- **Inconclusive:** keep the alpha available, but don't expand the architecture on the assumption of benefit.

**Not built for this study:** any new subsystem. The study uses existing tools, a frozen scenario, a
short protocol and a recorded result.

## Independent views gathered alongside

The same cold question ("is AEC worth it?") is going to Codex (HO-AEC-20261102-A5RR) and GitHub
Copilot without Kate's or Claude's framing. Their answers are inputs to how this design is reviewed
before the freeze, not results of the study.

## Freeze

*[Model and settings, trials per cell, scenario and decoy commits, grading key, and SHA-256 of the
frozen materials. To be filled at freeze.]*

## Change log (pre-freeze)

- 2026-11-01: first draft (claude:aec-release). Ontology audit filled in; scenarios pending.
- 2026-11-01: scenarios from the history search; primary scenario verified against Data-Guide commits (097c307, 3b2f110, e877113).
