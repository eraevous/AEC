# probe-001 results: no signal, and a cost

**Run 2026-11-01. 18 trials, all completed.** Pre-registration and amendments:
[`probe-001.md`](probe-001.md). Every task, briefing, hidden test, prompt, patch, report and
per-trial summary is in [`probe-001/`](probe-001/). All frozen files match
`probe-001/FREEZE.sha256` (`sha256sum -c` reports 0 failures).

## The answer, by the pre-registered rule

**No signal, and no harm.** Every trial succeeded in every condition, so B could not beat A on any
task. The pre-registered "lower cost" rule was not met either: B was cheaper than A on 1 of 3 tasks,
and the rule needed 2.

| Task | A: repo only | B: relevant AEC briefing | C: irrelevant briefing |
|---|---|---|---|
| T1 hidden dependant (`profile_dataset`) | 2/2 | 2/2 | 2/2 |
| T2 return-shape change (`understand`) | 2/2 | 2/2 | 2/2 |
| T3 false premise (`credentials.py`) | 2/2 | 2/2 | 2/2 |

Success means: for T1 and T2, both the functionality and the preservation tests pass. For T3, the
preservation tests pass, nothing harmful changed, and a blind grader judged the report adequate.
Data-Guide's own 89 tests passed in all 18 trials.

## Cost

Median total tokens per trial (input, output and cache), relative to A:

| Task | A | B | C |
|---|---|---|---|
| T1 | 1.04M | 1.28M (+23%) | 1.28M (+23%) |
| T2 | 1.05M | 0.97M (−7%) | 0.89M (−15%) |
| T3 | 0.55M | 0.88M (+59%) | 0.78M (+41%) |

Output tokens were higher with a briefing on all three tasks, because the agents discussed it.
C costs about as much as B, so the extra cost comes from having a briefing at all, not from its
content. Generating the briefing itself takes milliseconds.

## What the agents did (the uptake stages)

- **Found the dependant without help.** All 18 agents, A included, opened the dependant file before
  their first edit. In T1, they found `profilers/univariate.py` by search, and that file has a comment
  stating the coupling outright.
- **Every B and C report mentions the briefing**, and no A report does. Mentioning it is not using
  it: agents usually cited it as a caveat, or as unrelated in C.
- **The T1 briefing was misleading, and the agents caught it.** Its caller list said "Resolved callers:
  none found", because the real call is `profiler = DataProfiler(...); profiler.profile_dataset()`
  and AEC's extractor leaves calls through a local variable unresolved. Both B agents said in their
  reports that the "no callers" line was incomplete, and relied on search instead. The briefing's own
  caveat ("No known caller is not proof of no caller") is what kept this from becoming harm.
- **The irrelevant briefing was sometimes read as if it were relevant.** In T1, both C agents got the
  neighbourhood of an unrelated symbol (`ASTDependencyExtractor.__init__`). Both then wrote that "the
  AEC data lists no callers" for the function they were changing, and dismissed it as unreliable. In
  T2 and T3, the C agents correctly called their briefing unrelated. A briefing that doesn't clearly
  say which symbol it describes can be misattributed. That matters for how WP2A labels its output.
- **The implementations converged.** In T2, 6 of 6 agents added a wrapper function and moved the CLI to
  it; in T1, 6 of 6 changed `elif` to `if` in `univariate.py`. Condition made no visible difference
  to the shape of the fix.

## What this means

1. **On tasks like these, a capable agent with search doesn't need AEC's caller list.** Every hidden
   dependant here could be found with `grep`, which the task builder flagged before the run. This is
   the ceiling effect the pre-registration named as threat 3. It is a real finding about incremental
   value, not a failed experiment.
2. **A briefing has a cost even when it's irrelevant:** +23% to +59% total tokens on two of three
   tasks. Any context delivery AEC builds (WP2A) has to earn that back.
3. **The extractor has a concrete, fixable gap.** The single most consequential caller in this probe
   was unresolved, through the common `x = C(...); x.m()` pattern. Resolving a method call on a local
   variable assigned from a known class constructor in the same function is a small, deterministic
   change. It should be measured on Data-Guide's 874 unresolved calls before anything else is built on
   caller lists.
4. **Where a briefing might still matter is untested here:** dependants that search can't find
   (dynamic dispatch, string-keyed registries, other languages), much larger repositories, weaker or
   more budget-limited agents, and the deferred arm that adds guidance on how to use the briefing.
   These are the next probe's conditions, if there is one.

The pre-registration allowed every result in its "how results will be read" section, and this is
one of them. **No README sentence claims AEC improves agent outcomes.**

## Deviations from the protocol

- **Reports were recovered, not written.** The harness refused trial agents' writes of `REPORT.md`
  ("subagents should return findings as text"), so each report was recovered from the agent's final
  message. Two agents later got their own file written through a shell command; those files were
  kept. A bug wrote one T3 report (P902) from an interim message. It was fixed, and the report
  regenerated from the final message, *before* grading.
- **Blind grading was procedural.** The T3 grader (a Claude Haiku agent) saw only the criterion and the
  six reports, labelled by trial id. It shared a filesystem with the sealed key and was told not to read
  outside its folder. It graded all six adequate.
- **Two trial agents left the full test suite running in the background** and reported its result
  afterwards (P290, P998). Neither changed any code, and the mechanical grading re-ran every suite
  anyway.
- **The timestamps were corrected**, as noted in the pre-registration's amendments log.

## Threats to validity, restated

All trial agents were Claude Sonnet, with n = 2 per cell. The tasks were built by a Claude agent and
were deliberately dependency-sensitive, but easy to search. The target is Zach's own repository. None
of these weakens the main reading, *no measurable benefit here*; together, they limit how far it
generalises.
