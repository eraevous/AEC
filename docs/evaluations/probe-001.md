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
