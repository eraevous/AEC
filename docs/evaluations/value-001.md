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

## Step 2: scenarios (to be filled from the history search)

Requirements for a scenario:
- a real past change in AEC, Data-Guide or Fathom;
- an obligation written down *before* the change;
- consequence evidence;
- a record of how, and whether, it was noticed.

Plus at least one real decoy: a change to the same kind of code that endangered nothing consequential.

*[Candidates, evidence and the chosen pair go here.]*

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
