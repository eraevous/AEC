# eval-design: does Telosmith enhance or outperform framework X? (pre-registration draft)

**Status: DRAFT. Not frozen, not reviewed, no materials built, no trials run.** Written 2026-11-04 by
claude:aec#usecases. It is frozen only when the [Freeze](#freeze) section is filled in and hashed. Until then,
anything here may change, and changes go in the change log at the end.

**Authority and context.**
- Zach, 2026-11-04 16:37 CT: *"The primary evaluation of Telosmith will be in the context of an existing Agentic
  Coding framework that does not implement SpecKit. Telosmith should either enhance or outperform that
  implementation, with the caveat that my company might balk at the compute budget I've gotten used to."*
- `AEC-R3@1` (committed): adoption is earned against a baseline, with authoring cost counted; "if equal, simplify".
  That requirement names Spec Kit as the baseline. This design uses framework X instead. Whether `AEC-R3` gets a
  version 2 is Zach's decision ([use-cases.md](../use-cases.md), last section).
- Prior designs this borrows from: [probe-001](probe-001.md) and [its results](probe-001-results.md), and
  `dec-021-protocol.md` (PR #50, unmerged), in particular its info-parity rule, its mechanism precondition and
  Kate's power review.

**Not authorized by this document:** building materials, running trials, or spending compute. Zach decides
[the open parameters](#decisions-for-zach).

## Question

> On small code changes to a repository whose reasons are written down, does adding Telosmith's computed change
> report to framework X make the review (agent or human) **catch an endangered recorded claim** more often, or
> sooner, **without** more false alarms, and at what extra compute?

What this does **not** ask:
- **Whether Telosmith gives better first builds.** fathom-002 already gave negative evidence there (39 against
  44/45, confounded), and nothing here revisits it.
- **Whether the records themselves help.** Both arms get the same written reasons (see
  [info parity](#arms)). That isolates the tool's *computed, delivered report*, which is the part X does not
  already have. It also means a positive result cannot be credited to the act of writing records down.

Hypotheses, stated so that each can fail:
- **H1 (catch).** B catches more endangered claims than A.
- **H2 (noise).** B raises no more false alarms on decoys than A.
- **H3 (cost).** B's median tokens per trial are within +25% of A's.

## Framework X is a parameter

X is whatever the evaluating team already runs. The design holds X fixed (model, harness, rules files, tools,
caps) and changes only the Telosmith layer. [How each common shape changes the design](#how-the-shape-of-x-changes-the-design)
is below. Until X is known, the default is **X = Claude Code with a `CLAUDE.md` and no Spec Kit**, because that is
the shape Telosmith's generated hook targets.

## Arms

| Arm | Gets | Delivery of the Telosmith report |
|---|---|---|
| **A: X alone** | X as configured, plus a reasons file in X's native form (`docs/reasons.md`, linked from `CLAUDE.md` / the rules file): a prose rendering of the **same** records, with `code:` targets written as plain dotted names | none |
| **B: X + Telosmith** | A's inputs, plus `.aec/records.jsonl` (same content), the rules-file text from [without-spec-kit.md, Path 4](../integrations/without-spec-kit.md#path-4-rules-file-text-an-agent-reads), and the delivery path for X's shape (hook, git hook or CI summary) | computed `code-impact` report, delivered automatically |

**Info parity (from DEC-021, Kate 1).** A's `docs/reasons.md` is generated mechanically from B's records file by a
frozen script: one paragraph per record, with id, version, text, relations and linked names. A manifest check
confirms that every record and relation appears in both arms. The only intended difference is that B is *told*
which records a change touched, and when.

**Instruction parity.** B's rules text also tells the agent how to read the output, which is an instruction
effect as well as a tool effect. A's rules file gets a matched instruction: "before finishing, check
`docs/reasons.md` for any reason your change might affect, and say which ones you re-checked." Without it, a B
win could come from the instruction alone.

**Optional arm A0 (no written reasons), only if the budget allows.** This is what adopting Telosmith compares
against in practice, but it confounds the tool with the authoring. Report it separately. No decision rule reads it.

## Repository and changes

**Repository.** A frozen slice of a real repository with existing records: Fathom (`FT-*` records) or Data-Guide,
cut to about 1,500–3,000 lines of Python so a trial fits the [budget](#budget-per-trial). It needs at least 8
committed requirements or claims with `code:` links, and it must pass `aec check` with `--edges` at the freeze. A toy
repository like the one in `demo.md` is rejected: grep finds everything in it, which is the probe-001 ceiling.

**Changes: N = 8 single-change tasks**, each a frozen patch or instruction:

| # | Kind | Endangers a recorded claim? | Telosmith mechanism expected |
|---|---|---|---|
| E1 | edit inside a linked function that breaks its requirement | yes | `stale` (direct link) |
| E2 | edit a helper one call from a linked function, breaking its requirement | yes | pointer (depth 1) |
| E3 | edit inside a module-linked file, breaking its requirement | yes | `stale` (module link) |
| E4 | edit a constant or helper **two** calls away, breaking a requirement | yes | **none at default depth** (mechanism-negative item: tests false reassurance) |
| D1 | behaviour-preserving rewrite of a linked function | no | `stale` (expected Telosmith false alarm) |
| D2 | edit unlinked code near linked code | no | none |
| D3 | comment or docstring only | no | none |
| D4 | module-linked file, unrelated function changed | no | `stale` (module-link coarseness; expected false alarm) |

That is four endangering items and four decoys, with the decoys chosen so that Telosmith's known false-alarm
shapes (D1, D4) are included rather than avoided. The key for every item says which record(s) are endangered and
why, with the Oracle-style evidence: a failing hidden test or a stated counterexample.

**Who writes the items.** Not the session that wrote Telosmith or this design. Ideally Kate or a fresh reviewer,
from the repository's records, without running `code-impact`. This repeats the selection-disclosure rule from
DEC-021.

**Mechanism precondition (deterministic, run before any trial).** For each item, run `aec code-impact` at the
frozen Telosmith commit, between the base snapshot and the patched snapshot, and record whether it names the
key's endangered record. Publish the table before any trial. Items where the precondition fails (expected: E4,
possibly others) are analysed as **presentation/false-reassurance items**, never as evidence about reach. If fewer
than 2 of E1–E3 pass, stop: the question as posed cannot be answered on this repository.

## Trial procedure

Two task modes. X's shape picks the primary one.

- **Implement mode (primary for hook-shaped X).** The agent is asked to make the change. It is phrased as a normal
  request that does not mention reasons or records. Hooks fire as they would in practice. The agent ends with a
  short report. Tool-call cap: 12.
- **Review mode (primary for CI-gated X, and cheapest).** The agent is given the frozen patch as a PR diff plus
  repository access. B also gets the CI job summary text. The agent writes a review. Tool-call cap: 8.

Each (item, arm) pair runs **r = 2** times in a fresh session, so there are 8 × 2 × 2 = **32 trials** per mode.
Order is interleaved by a seeded schedule, so a budget stop leaves the arms at equal n.

## Outcomes

**Primary: catch (per endangering item).** The final report or review (i) names the endangered record by id, or
unambiguously by content, **and** (ii) says the change may violate it, or says what was checked. A grader applies
this from the key. Mentioning a record without connecting it to the change is not a catch.

**Secondary (reported per arm; no decision rule unless noted):**
1. **False alarm (per decoy).** The report says a decoy endangers a record. H2 reads this.
2. **Time to catch.** The index of the first tool call or turn at which the endangered record is named, plus wall
   time. Wall time is reported but not compared if trials ran concurrently (probe-001 queuing).
3. **Tokens.** Total, uncached input, cache reads and output, reported separately. H3 reads median **total
   tokens** for the cost rule if X bills on it. Otherwise it reads whatever X's organisation pays for; this is
   fixed at the freeze.
4. **False reassurance (E4 and any precondition-failed item).** The report cites Telosmith's silence ("0
   affected", no hook output) as a reason the change is safe. This is a harm measure, and it is reported even if
   rare.
5. **Uptake.** In B: whether the agent saw the report (hook fired, CI text present) and whether its report
   mentions it. In A: whether it opened `docs/reasons.md`.
6. **Record harm.** Any in-place edit to records or `reasons.md`, or any weakening of a claim's text to fit the
   change. The append-only guard from without-spec-kit.md is run on every final tree.
7. **Correctness of the change (implement mode).** Hidden tests pass or fail. This is reported only, because the
   question is review, not building.

**Grading.** One grader per mode, blind to arm. Strip `aec`, `Telosmith`, `.aec` and the hook's footer line from
reports, replacing them with a neutral token. This is imperfect: B reports may still be recognisable by style. As
in DEC-021, run a blind arm-identification audit and report the grader's guess rate. A second grader takes every
judgment the first marks ambiguous.

## Budget per trial

Target: **under 50k tokens per trial per arm.** The number is this design's (the coordinator's brief for this
draft), not Zach's. Zach's constraint is qualitative: his company "might balk at the compute budget I've gotten
used to". He sets the real cap ([Decisions for Zach](#decisions-for-zach)).

Prior measurement says this is **not** achievable inside a full Claude Code session if cache reads count. probe-001
trials used 0.55–1.54 M total tokens each, with 88–97% of that cache reads, on a 3,200-line repository with 4–14
tool calls. Its harness context is re-read on every turn. So the design fixes the metric and the harness first:

The two cheap rows assume a **proposed minimal harness** (a direct API loop with a small system prompt and the
repository's tools) that **does not exist yet** and would have to be built and frozen. It is **not** the default X
(Claude Code + `CLAUDE.md` + hook). In it, the hook does not fire by itself: the harness would inject the
report after an edit. So the minimal harness **does not test hook delivery**, only whether a delivered report
changes the review. Testing delivery in the default X means the third row's cost.

| Setting | Estimate per trial | Basis (all inference unless noted) |
|---|---|---|
| Review mode, proposed minimal harness (direct API loop, ~2k system prompt, 8-call cap) | **~15–25k total tokens** in A; B adds the summary (~0.2–0.7k) re-read on later turns, **+~1–3k** | Diff ~1k; 2–4 file reads of ~2k each; context grows to ~10k by the last turn; ~5 turns. The 695-character report measured here is ~175 tokens. |
| Implement mode, proposed minimal harness (12-call cap; report injected, not hook-delivered) | **~35–45k** in A; B **+~2–5k** (1–3 hook firings, each re-read on later turns; the hook re-reports until commit) | ~6–8 turns averaging ~5–6k context, plus ~3k output |
| Implement mode inside Claude Code, counting cache reads | **~0.5–1.5 M** (measured in probe-001) | Over budget by 10–30×. Count **uncached input + output** instead (probe-001 output alone was 2–9k per trial), or use the minimal harness. |

Telosmith's own commands add **zero model tokens**: about 0.4 s per hook firing on a toy repo, and about 2 s on a
63-file repo (measured 2026-11-04, [use-cases.md](../use-cases.md)). Whole run, review mode, proposed minimal harness:
32 trials × ~25k ≈ **0.8 M tokens**. Implement mode: 32 × ~45k ≈ **1.4 M**. Both are under the 8 M cap DEC-021
kept, and both are an order of magnitude below one probe-001 condition. **A stop-at-cap rule is still needed:**
pick the cap at the freeze, and stop at the end of an interleaved block.

**What the company would pay in use (separate from the experiment).** It is the B-minus-A token delta per change,
times changes per day. On these estimates that is about 1–5k tokens per change, depending on how many times the
hook fires before a commit. The experiment measures this; the estimate is not a claim.

## Sample-size honesty

This is a **diagnostic**, not a superiority test, as Kate's review of PR #50 insists (`dec-021-protocol.md`,
"How many trials, and what the counts can show"). That protocol's error rates for a "B ahead by ≥ 2 at equal n"
heuristic at n = 4 per arm combine two reviewers' figures:

- **Kate's:** with no effect (p = 0.5), a false "B ahead" happens **14.5%** of the time. With a true effect from
  0.3 to 0.7, the heuristic misses it **44.8%** of the time.
- **The cold Claude reviewer's:** with a true effect from 0.3 to 0.6, it misses **57.3%** of the time.

This design's rules count more than 4 per arm, so the rates must be stated at the n each rule uses. Recomputed
2026-11-04 (two independent binomials, margin ≥ 2; reproduces `dec-021-power.py` at n = 4; illustrative, because
within-item correlation makes every row worse):

| n per arm | Used by | P(false "B ahead"), p = 0.5 | p = 0.3 | Miss, 0.3 → 0.6 | Miss, 0.3 → 0.7 |
|---|---|---|---|---|---|
| 4 | (DEC-021 reference) | 0.145 | 0.120 | 0.573 | 0.448 |
| **6** | **primary rule**: E1–E3 × r = 2 | 0.194 | 0.170 | 0.416 | 0.276 |
| **8** | all endangering items, E1–E4 × r = 2 (descriptive) | **0.227** | 0.205 | **0.311** | 0.175 |

At a fixed margin of 2, a larger n buys power by raising the false-favour rate. The margin should scale with n.
Choosing it is a [freeze](#freeze) decision, and the table is re-run with `dec-021-power.py` at that point.

The ceiling rule (A catches ≥ 5 of 6) is met by chance with probability 0.11 if A's true rate is 0.5, 0.42 at 0.7,
and 0.89 at 0.9.

The 6 or 8 trials per arm are **not independent**. They come from 3 or 4 items, each run twice with the same model,
so the effective n is nearer the item count. Therefore:

- A null result is **weak** evidence against even a moderate advantage. It is reported as "inconclusive at
  3–4 items", and never as "Telosmith does not help".
- A B-ahead result is reported as "signal on this repository and model; replicate", never as "outperforms X".
- Results are reported **per item** as well as summed, because one item can carry the whole difference.

## Decision rules

Pre-stated, applied to the primary outcome on precondition-passing items (E1–E3, plus any others that pass):

| Result | Reading | Action |
|---|---|---|
| **Ceiling:** A catches ≥ 5 of 6 on E1–E3 | X already catches these. This repeats probe-001 | **Drop "outperforms X on small changes"** for this repository class. Keep only "candidate for cases search can't find", which needs a new design (dynamic dispatch, larger repo, budget-capped model) |
| B ahead by ≥ 2, H2 holds, H3 holds | diagnostic signal for "enhances X" | replicate on a second repository and model before any README sentence |
| B ahead, but H2 fails (more false alarms) or H3 fails (> +25% tokens) | catches bought with noise or compute | report as a trade-off; Zach decides whether the trade is acceptable for his company |
| Tie, no ceiling | inconclusive | no claim; report n and the miss rate above |
| A ahead by ≥ 2 | Telosmith's report may distract (as probe-001's irrelevant briefings did) | investigate presentation; do not remove `code-impact` on this alone (DEC-021 rule) |
| False reassurance observed in ≥ 2 B trials | the silence of "0 affected" is read as safety | treat it as a harm finding whatever the catch result is; change the hook and rules text before any adoption |

**What would make Zach drop the claim "Telosmith enhances or outperforms X at change review"** (proposed here;
Zach accepts or edits it at the freeze):
1. The ceiling row, on a repository the item writer judged representative, **or**
2. Two independent replications (different repositories or models) that both come out tie-or-worse, with A off
   the ceiling, **or**
3. H3 failing by more than +50% in every replication, with no catch gain.

Dropping the claim means: no README or pitch sentence claims better review against X. The mechanism claims stay,
because they rest on [use-cases.md](../use-cases.md)'s demonstrated tier. Following `AEC-R3`, the default
response is to simplify toward the minimal set (`check` + `code-impact` + one delivery path).

## Confounds and how each is handled

| Confound | Handling |
|---|---|
| **Search ceiling.** Capable agents grep their way to the answer (probe-001) | a real, non-toy slice; the ceiling row in the decision rules; E4 and D-items are not searchable by name alone |
| **Records vs tool.** B's win could come from having records | info parity: A gets the same reasons in prose |
| **Instruction vs tool.** B's rules text tells the agent to check | instruction parity: A gets a matched "check reasons.md" line |
| **Item author = tool author** | items written by someone other than this session, without running Telosmith; selection disclosed |
| **Grader leakage.** B reports name the tool | redaction, blind identification audit, second grader |
| **Model nondeterminism and within-item correlation** | r = 2; per-item reporting; no claim beyond a diagnostic |
| **Hook re-report noise** inflates B's context | measured as tokens (H3) and uptake; not corrected |
| **Concurrency** distorts wall time | wall time descriptive only |
| **Harness differences between X shapes** | X is held fixed within a run; results do not transfer across shapes without rerunning |
| **Shared machine state** (fathom-002: arms overwrote each other's entry point) | each trial in its own venv and worktree; the install is checked before the trial starts |
| **Telosmith version drift** | pin one commit; record `tool_version` and the edge method in the freeze |

## How the shape of X changes the design

**1. Claude Code + `CLAUDE.md` + hooks** (the default).
- B's delivery is the generated `PostToolUse` hook (exit 2, stderr to the agent) plus the Path 4 rules text.
- Implement mode is primary. The report enters context right after the edit, which is the demonstrated moment.
- Measure hook firings per trial: re-reporting until commit is a known cost.
- If X already has hooks, merge Telosmith's into the same `PostToolUse` list. Hook order is not a variable.

**2. Cursor, Copilot agent or Codex CLI with a rules file.**
- These may have no post-edit hook surface; check the harness version at the freeze.
- B's delivery is the rules-file text, which asks the agent to *run* the four commands, plus the pre-commit hook
  if the agent commits.
- **Uptake becomes the main secondary outcome.** If the agent never runs `aec`, B equals A plus noise. Report the
  share of B trials in which `code-impact` ran.
- Tool-call caps must count the `aec` calls. Raise the cap by 4 in B, or give both arms the same raised cap
  (preferred, for parity).

**3. In-house orchestrator with CI gates.**
- Review mode is primary. B's reviewer agent (or a human reviewer) gets the job-summary text alongside the diff,
  exactly as CI would attach it.
- This is the cheapest shape: no implementation turns. It is also the closest to "my company's budget".
- A **human-reviewer variant** fits here: the same 8 patches, two reviewers per arm, timed. This is the only shape
  where "human or agent" review can be compared within budget (zero tokens; reviewer minutes instead).
- If the orchestrator already posts structured findings, B's summary is appended in the same format. Inventing a
  new surface would test presentation, not Telosmith.

## Decisions for Zach

1. **Which X**, and its exact configuration (model, harness version, rules files, caps).
2. **The token metric for H3 and for the budget:** total including cache reads, or uncached input + output.
3. **The budget cap** for the whole run, and the per-trial cap.
4. **The repository slice** (Fathom, Data-Guide or another) and **who writes the 8 items and the key.**
5. **Whether A0 (no written reasons) runs.**
6. **The drop criteria above:** accept, edit or replace them.
7. **Whether `AEC-R3` is re-versioned** to name X instead of Spec Kit as the baseline.

## Freeze

Not frozen. To freeze: fill in the X configuration, the pinned Telosmith commit and extractor `tool_version`, the
repository slice commit, item and key hashes (in an encrypted key outside agent-readable folders, as in DEC-021),
the precondition table, the re-run power table, the budget cap and the token metric. Then hash everything into
`FREEZE.sha256`, commit, and append an `experiment` record (`EXP-framework-x-review@1`).

## Change log

- 2026-11-04, claude:aec#usecases: first draft.
- 2026-11-04, claude:aec#usecases, after a fresh-context review of PR #54:
  - the 50k target is attributed to this design, not to Zach;
  - the minimal harness is labelled as proposed, and as not testing hook delivery;
  - the power figures are attributed to each reviewer and recomputed at n = 6 and n = 8.
