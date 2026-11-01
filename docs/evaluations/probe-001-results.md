# probe-001 results: no signal, and a cost

**Run 2026-11-01. 18 trials, all completed. Every result below is exploratory** (amendment 7).
Pre-registration and amendments: [`probe-001.md`](probe-001.md). Every task, briefing, hidden test,
prompt, patch, report and per-trial summary is in [`probe-001/`](probe-001/). All 22 frozen files
match `probe-001/FREEZE.sha256` (`sha256sum -c` reports 0 failures). An independent reviewer agent
re-ran the hidden tests on all 18 final patches against a clean Data-Guide checkout and got the same
results, recomputed the cost medians, and regenerated the trial schedule from its seed.

Trial agents: Claude Sonnet 5.5 (`claude-sonnet-5-5`), as Claude Code subagents.

## The answer, by the pre-registered rule

**No signal, and no harm.** Every trial succeeded in every condition, so B could not beat A on any
task. The "lower cost" rule (B at least 25% below A in median total tokens on 2 of 3 tasks) was met
on **0 of 3** tasks. The best case was −7% on T2.

| Task | A: repo only | B: relevant AEC briefing | C: irrelevant briefing |
|---|---|---|---|
| T1 hidden dependant (`profile_dataset`) | 2/2 | 2/2 | 2/2 |
| T2 return-shape change (`understand`) | 2/2 | 2/2 | 2/2 |
| T3 false premise (`credentials.py`) | 2/2 | 2/2 | 2/2 |

Success means: for T1 and T2, both the functionality and the preservation tests pass. For T3, the
preservation tests pass, nothing harmful changed, and the grader judged the report adequate.
Data-Guide's own 89 tests passed in all 18 trials.

## Cost

| Task | Cond | Trial | Tool calls | Wall time (s) | Total tokens | of which cache reads | Output tokens |
|---|---|---|---|---|---|---|---|
| T1 | A | P205 | 10 | 257 | 1.10M | 96% | 5,579 |
| T1 | A | P211 | 8 | 244 | 0.98M | 95% | 5,477 |
| T1 | B | P437 | 12 | 213 | 1.54M | 97% | 8,046 |
| T1 | B | P977 | 8 | 241 | 1.01M | 96% | 6,611 |
| T1 | C | P106 | 13 | 246 | 1.27M | 93% | 8,902 |
| T1 | C | P607 | 10 | 261 | 1.29M | 95% | 8,155 |
| T2 | A | P497 | 14 | 293 | 1.40M | 97% | 6,046 |
| T2 | A | P739 | 6 | 110 | 0.70M | 88% | 3,727 |
| T2 | B | P126 | 9 | 181 | 1.17M | 96% | 6,972 |
| T2 | B | P603 | 7 | 133 | 0.77M | 95% | 5,360 |
| T2 | C | P800 | 8 | 250 | 0.85M | 95% | 4,498 |
| T2 | C | P992 | 8 | 233 | 0.93M | 96% | 5,458 |
| T3 | A | P462 | 4 | 62 | 0.55M | 95% | 3,194 |
| T3 | A | P744 | 5 | 194 | 0.55M | 95% | 2,022 |
| T3 | B | P902 | 6 | 203 | 0.77M | 95% | 5,345 |
| T3 | B | P998 | 6 | 182 | 0.98M | 94% | 8,470 |
| T3 | C | P101 | 7 | 74 | 0.84M | 90% | 4,840 |
| T3 | C | P290 | 5 | 175 | 0.72M | 95% | 3,273 |

Median total tokens relative to A:

| | B | C |
|---|---|---|
| T1 | +23% | +23% |
| T2 | −7% | −15% |
| T3 | +59% | +41% |

How to read this:
- "Total tokens" is mostly cache reads (88–97% per trial). So these differences mostly reflect more
  turns multiplied by context size. They are not proportional to price or to how much the agent wrote.
- Output tokens were higher with a briefing on all three tasks.
- The 18 trials ran concurrently, so wall time includes queuing. Two trials (P290, P998) include time
  spent waiting on a backgrounded test run.
- Generating a briefing took about 40 ms (mean of 10 runs of `probe-001/tools/briefing.py`).
- With two trials per cell, it's a hypothesis, not a finding, that a briefing's *presence* rather than
  its content drives the extra cost, even though C cost about as much as B.

## What the agents did (the uptake stages)

- **Found the dependant without help.** In T1 and T2, all 12 agents (A included) searched for or read
  the dependant before their first edit, by a heuristic check of the tool-call lists. Most edits ran
  through shell commands, so "first edit" is approximate. Every final patch also changed the dependant
  correctly, which the preservation tests confirm. In T3, all six agents searched for and opened `src/cli.py`, and none
  edited anything, so the "before first edit" criterion is trivially met there. In T1, the dependant
  `profilers/univariate.py` has a comment stating the coupling outright.
- **Every B and C report mentions the briefing; no A report does.** Mentioning it is not using it:
  agents usually cited it as a caveat, or as unrelated.
- **The T1 briefing was misleading, and the agents caught it.** Its caller list said "Resolved callers:
  none found". The real call is `profiler = DataProfiler(...); profiler.profile_dataset()`, and AEC's
  extractor leaves calls through a local variable unresolved. Both B agents said in their reports that
  the "no callers" line was incomplete, and searched instead. The briefing's own caveat ("No known
  caller is not proof of no caller") is what kept this from becoming harm.
- **Irrelevant briefings were read as relevant in 3 of 6 C trials.** In T1, both C agents (P106, P607)
  got the neighbourhood of an unrelated symbol, then wrote that "the AEC data lists no callers" for the
  function they were changing. In T3, P101 treated its unrelated briefing as bearing on whether
  `credentials.py` was used. The other three C agents called their briefing unrelated. A briefing that
  doesn't clearly name its subject gets misattributed, which matters for how WP2A labels its output.
- **The implementations converged.** In T2, all six agents added a wrapper function and moved the CLI to
  it; in T1, all six changed `elif` to `if` in `univariate.py`. Condition made no visible difference to
  the shape of the fix. No blind grade of the T1 and T2 diffs was made (see Deviations); this comparison
  is claude:aec-release's reading of the published patches.

## What this means

1. **On tasks like these, a capable agent with search doesn't need AEC's caller list.** Each hidden
   dependant could be found with `grep`. The task builder flagged this for T3, and for T1's
   explanatory comment, before the run. T2's dependants are direct calls in `cli.py`. This is the
   ceiling effect named as threat 3. It is a finding about incremental value, not a failed experiment.
2. **Context costs something even when it's irrelevant.** Any context delivery AEC builds (WP2A) has to
   earn back more turns and more output.
3. **The extractor has a concrete, fixable gap.** The single most consequential caller in this probe
   was unresolved, through the common `x = C(...); x.m()` pattern. Resolving a method call on a local
   assigned from a known class constructor in the same function is a small, deterministic change. It
   should be measured on Data-Guide's 874 unresolved calls before anything is built on caller lists.
4. **Where a briefing might still matter is untested here:** dependants that search can't find
   (dynamic dispatch, string-keyed registries, other languages), much larger repositories, weaker or
   budget-capped agents, and the deferred arm that adds guidance on how to use the briefing.

**No README sentence claims AEC improves agent outcomes.**

## Deviations from the protocol

- **Reports.** The harness refused trial agents' `Write` of `REPORT.md` ("subagents should return
  findings as text"). Seven agents then wrote the file themselves through a shell command (P211, P290,
  P497, P739, P744, P800, P998); those files are kept as written. The other 11 reports were recovered from
  the agent's final message, and are marked as recovered at the top. A bug first recovered P902 from an
  interim message; it was fixed, and the report regenerated, before grading. The T3 grader saw the files
  as they now stand, with the recovery marker removed.
- **Blind grading.**
  - *Who graded, and how it leaked.* The T3 grader was a Claude Haiku agent. It saw only the criterion
    and the six reports labelled by trial id, and was told not to read outside its folder. Blinding was
    nonetheless broken by content: every B and C report mentions the briefing and no A report does, so
    a grader could tell A from not-A by reading.
  - *Verdicts.* It judged all six reports adequate, citing for each the `src/cli.py` caller and the
    decision to keep the files.
  - *What is unaffected.* The primary outcome is mechanical, so it doesn't depend on blinding.
  - *What was never done.* The protocol's blind qualitative grade of the T1 and T2 diffs was not
    carried out.
- **Stage 3 comparison.** The protocol asked for files read and edited to be compared across
  conditions. That comparison is only partial: one paragraph above, plus the per-trial tool-call lists
  in `probe-001/trials/*/transcript_summary.json`.
- **Grading tools.** `probe-001/tools/grade.py` and `transcript.py` were written after the freeze and
  are not in `FREEZE.sha256`. They contain the private paths of the machine they ran on.
- **One session, one hour.** One agent session designed, pre-registered, froze, ran and wrote up this
  pilot, from 17:13Z to about 18:20Z. The freeze commit published hashes; the files followed afterwards.
  The hash commitment holds, but "pre-registered" here means hours, not weeks.
- **Timestamps.** The estimated timestamps in the amendments log were corrected, as noted there.

## Threats to validity, restated

All trial agents were one Claude model, with n = 2 per cell. The tasks were built by a Claude agent
and were deliberately dependency-sensitive, but easy to search. The target is Zach's own repository.
None of these weakens the main reading, *no measurable benefit here*; together, they limit how far it
generalises.
