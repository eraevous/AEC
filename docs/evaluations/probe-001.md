# probe-001: does AEC's structural context change what a coding agent does?

**Status: pre-registered pilot, not yet run.** Written 2026-11-01 by claude:aec before any task
was built or any trial run. Changes after this point go in the amendments log at the end, with
time and reason; nothing above it is edited.

This is the first, small version of WP2-probe in `docs/architecture.md`. It is a drift-mode
pilot (DEC-019: drift includes pilots and feasibility tests): its results are evidence for
Zach to weigh, not a decision. It runs before WP1A, using the existing `aec edges` snapshot,
because the question it asks needs no commit-addressed snapshots.

## The question

When a coding agent is asked to change code it has never seen, does giving it AEC's structural
neighbourhood of the code it was asked to change alter:
1. what it looks at,
2. what it changes,
3. whether the result still works for the code that depended on the old behaviour,
4. and at what cost?

It also asks the counter-question: does an accurate but **irrelevant** structural briefing change
behaviour just as much? If so, any effect is the briefing's presence, not its content.

Constitution IV forbids claiming AEC improves outcomes without a recorded comparison. This is a
pilot: it can show a signal worth a full study, no signal, or harm. It cannot establish that AEC
helps in general, and no README sentence will say it does.

## Target repository

`eraevous/Data-Guide` at commit `0607401` (46 Python files, 2,427 static edges). Chosen because
it is real code not built for this probe, has its own test suite, and is unlikely to be
memorised by the models under test. It is Zach's repository, which is a limitation (below).

## Tasks

Three tasks, built **before any trial** by a fresh agent that has not seen this conversation,
from these rules only:

- **T1, hidden dependant.** A plausible change request to a function F, phrased as a user would
  phrase it, where at least one caller of F in a *different* file relies on the behaviour being
  changed, and nothing in F's own file mentions that caller.
- **T2, hidden dependant, different shape.** As T1, but the change alters F's signature or return
  shape rather than its internal behaviour.
- **T3, change nothing.** A request resting on a false premise about the code (for example "X is
  unused, remove it" when X has a caller). The correct outcome is to decline or to make no
  harmful change, and say why.

For each task the builder writes **hidden acceptance tests** that pass on the unmodified code
and fail if a dependant breaks. Trial agents never see them. The builder also confirms that
Data-Guide's own test suite passes on the unmodified checkout.

Tasks and hidden tests are hashed (SHA-256) and the hashes are appended to the amendments log
before the first trial.

## Conditions

Every trial gets the same task text, a fresh copy of the repository, and the same tools (read,
search, edit, run tests). Conditions differ only in one appended block:

| | Condition | Appended block |
|---|---|---|
| **A** | repository only (control) | none |
| **B** | accurate, relevant structural briefing | AEC neighbourhood of every symbol the task names |
| **C** | accurate, irrelevant structural briefing | AEC neighbourhood of a different symbol, chosen by rule |

The briefing is generated **mechanically** from `aec edges` output by a script committed with the
results, with no hand editing:
- for each named symbol: its definition site, resolved callers and importers (file:line),
  callees, and base or derived classes;
- the repository-wide count of unresolved calls, with the sentence "No known caller is not proof
  of no caller."

C's symbol is chosen by rule: the function in a different module whose resolved-caller count is
closest to the task symbol's (ties broken alphabetically).

A fourth arm, B plus brief guidance on how to reason with structural information, is deferred to
the full probe. It is the "information alone vs information plus how to use it" split from the
2026-10-31 coordination thread.

## Agents and replication

- Trial agents: Claude Sonnet subagents with no shared context, each working in its own
  repository copy.
- 3 tasks × 3 conditions × 2 replicates = 18 trials, run in a fixed randomised order.
- All trial agents are Claude models, so shared model biases are not controlled.

## Outcomes (the five stages)

| Stage | Measure | How |
|---|---|---|
| 1. Received | briefing present | by construction (B, C) |
| 2. Used | did the agent read or cite a dependant named in the B briefing? Recorded for A too: did it find that dependant by itself? | mechanical, from the agent's tool calls and final report |
| 3. Did something different | files read and files edited, compared across conditions | mechanical |
| 4. Better result (**primary**) | hidden acceptance tests pass; Data-Guide's own suite still passes | mechanical (test run) |
| 5. Worth the cost | tokens and tool calls per trial | from run metadata |

A secondary, qualitative grade (did the agent explain the dependency risk correctly?) is given
by a separate grader agent that sees only the diffs and final reports, with condition labels
removed. The unblinding key is kept outside every repository the grader can reach until grades
are frozen, a lesson from representation-001.

## How results will be read

Decided now, before any data:
- **Signal worth the full WP2-probe:** B passes more hidden tests than A on at least 2 of 3 tasks,
  and C does not match B on those tasks. Or: B matches A on results at lower cost.
- **No signal:** none of the above. Reported as plainly as a positive result.
- **Harm:** B or C passes fewer hidden tests than A on any task, or the T3 agent is pushed into
  removing code it should keep. Any harm is reported first.
- With two replicates per cell, every result is reported task by task. No pooled percentage, no
  significance test, no claim of overall superiority.

## Known threats

1. **Small n.** 18 trials is a pilot.
2. **Tasks built by a Claude model** for Claude trial agents; the builder could write tasks that
   suit the briefing. Mitigated by the fixed rules above and a fresh builder, not removed.
3. **Ceiling effects.** A capable agent may find every caller with ordinary search, leaving
   nothing for the briefing to add. That is a legitimate finding about incremental value.
4. **Zach's own repository.** Not adversarial, and its style may differ from typical code.
5. **The briefing's form is one choice among many** (the 2026-10-31 thread's levels 1 to 3). This
   pilot tests level 2, the neighbourhood, only.

## Amendments log (append-only)

- 2026-11-01 | claude:aec | Pre-registered. No tasks built, no trials run.
- 2026-11-01T17:50Z | claude:aec | Task building started: a fresh general-purpose agent, given only the task rules above. Its brief already asked for one test per T1/T2 showing the requested change was made, but not the full separation in amendment 1 below. Recorded here because Kate's review asks that amendments precede task generation, and this one did not.
- 2026-11-01T18:45Z | claude:aec, adopting Kate's review (HO-20261101-001; relay-kit-private `handoffs/outputs/HO-20261101-001.md`). Made before any trial; tasks are not yet frozen.
  1. **Two kinds of hidden test.** *Requested-functionality* tests fail on the original checkout and pass when the request is correctly implemented. *Dependency-preservation* tests pass on the original checkout and must still pass afterwards. For T1 and T2, a trial succeeds only if both pass, so making no change is a failure. For T3, a trial succeeds if the preservation tests pass, no harmful change was made, and the final report identifies or investigates the false premise. The last part is graded by the blind grader against a criterion frozen with the task.
  2. **Each task is shown feasible and its dependency shown to matter** before freezing. The record states: what the user wants, what must stay intact and why, that a satisfactory solution exists (a reference solution passes both test kinds), and how success differs from an unchanged checkout. For T3, it states evidence of runtime use, not only a static caller.
  3. **C's irrelevance is checked.** The mechanically chosen symbol is rejected if its briefing names any file or symbol that the task's dependency path touches (the target's module, its callers' files, or the dependants). The next deterministic candidate is then taken, and each rejection is logged. B and C briefings are reported with their lengths in characters. If they differ by more than a factor of two, that is reported as a threat; it is not padded.
  4. **Uptake recorded as four separate observations:** inspected the dependant (from tool calls); referred to the briefing (from the report); implementation accounted for the dependant (from the diff, graded blind); and, in A, whether the dependant was found independently. None of these alone is read as causal uptake; only the randomised comparison is.
  5. **Behavioural observations:** whether the dependant was opened before the first edit; whether the implementation was adjusted for compatibility; whether T3 left the target in place; and any unnecessary or harmful change. These explain the primary outcome; they do not replace it.
  6. **Cost:** input and output tokens, wall time and tool calls per trial, plus briefing generation time. Cap: each trial agent is told to stop at about 40 tool calls. A trial that times out, errors or exceeds the cap is a failure, and is not re-run.
  7. **Operational signal rule** (replaces "How results will be read", first bullet). The primary outcome is per-replicate task success, as defined in 1. A task favours B when B has more successful replicates than A, out of 2. *Exploratory signal:* B is favoured on at least 2 of 3 tasks and C does not equal B on those tasks. *Lower cost:* B is at least 25% below A in median total tokens with equal success, on at least 2 of 3 tasks. Every result is labelled exploratory.
  8. **Scope stated plainly.** Tasks are deliberately enriched for dependency sensitivity. The pilot asks whether graph information helps on such tasks, not how often it would help across ordinary work. The unblinding key (`schedule.private.json`, trial id → condition) is kept outside every repository and every location the grader can read until grades are frozen.
  9. **Reproducibility identifiers** are recorded at freeze: the Data-Guide commit, the AEC commit and extractor `tool_version`, the extractor settings, the edge-snapshot SHA-256, and the briefing script's SHA-256.
  10. **Sequencing:** Zach approved running this pilot before WP1A (DEC-024, 2026-11-01), answering a direct question after Kate flagged that DEC-019 alone did not settle the order.
- 2026-11-01T19:40Z | claude:aec | **Frozen before any trial.** The SHA-256 of every task, hidden test, reference patch, briefing, script and the edge snapshot is in `probe-001/FREEZE.sha256`; the files are published with the results.
  - Data-Guide: `0607401`. AEC: `4779429`, extractor `tool_version` 0.3.0, default settings, 46 files, 2,427 edges, 0 skipped.
  - Targets: T1 `DataProfiler.profile_dataset` (dependant `profilers/univariate.py`); T2 `understanding.workflow.understand` (dependants `cli.understand` and `cli.demo`); T3 `connectors.credentials` (dependant `cli._build_connector`).
  - The builder's checks: the unmodified checkout fails T1/T2 functionality and passes all preservation tests; each naive patch passes the repo's 89 tests but fails its preservation test; each reference patch passes both test kinds.
  - **Weaknesses the builder reported, not corrected:** (a) T1's dependant calls `profile_dataset` through an unresolved method call, so the B briefing does *not* list it as a caller. It names `univariate.py` only as an importer of the module. This tests AEC as it is, gaps included. (b) A comment in `univariate.py` states T1's coupling outright, for anyone who opens that file. (c) T2's preservation test treats "the CLI prints each output path" as the contract, so a careful solution that changes what the CLI prints would fail it. (d) T3's caller is found by a plain `grep`, so T3 mainly measures whether the agent checks before deleting.
  - **Decoys (C)**, chosen by rule with the irrelevance check: T1 `ast_dependency_cli.ASTDependencyExtractor.__init__`; T2 `connectors.credentials.CredentialsValidationError`; T3 `understanding.annotations.load`. One candidate was rejected for T1 (`cli._build_connector`, which names `src/cli.py`). *Deviation:* the rule said "function", and the generator also admits classes, so T2's decoy is a class. Briefing lengths (characters, B/C): T1 943/558, T2 1186/1221, T3 1558/1716, all within a factor of 2.
  - Trial order: fixed, `random.seed(20261101)`; the opaque trial-id → condition key is held outside the repositories. Blinding is procedural, not technical: trial and grader agents share a filesystem with the sealed key, so blinding rests on their instructions. The primary outcome is mechanical, so it does not depend on blinding.
- 2026-11-01T18:06Z | claude:aec | **Correction to the timestamps above.** claude:aec wrote them from estimates, not a clock, and they run 35 to 95 minutes late. Commit times on this branch give the actual order: pre-registered 17:13Z; task building started ≈17:14Z; Kate's review adopted 17:30Z (her reply ≈17:23Z, Zach's sequencing answer ≈17:28Z); frozen 18:05Z; first trials launched 18:05Z. The order of events, and therefore the claim that every amendment preceded the freeze and the trials, is unchanged.
