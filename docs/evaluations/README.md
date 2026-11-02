# Evaluations

What AEC has been measured on, including results that didn't favour it. Each entry links to its full write-up.

| Evaluation | Question | Result |
|---|---|---|
| [probe-001](probe-001-results.md) ([pre-registration](probe-001.md), [materials](probe-001/)) | Does AEC's structural briefing change what a coding agent does on dependency-sensitive tasks? | No signal: 18/18 trials succeeded in every condition. Briefings raised token use on 2 of 3 tasks. It exposed a caller-resolution gap. Exploratory pilot. |
| [resolver-001](resolver-001.md) | How many unresolved calls does the C-11 fix (`x = C(...); x.m()`) resolve on Data-Guide, and are they right? | 25 of 874 resolved, including probe-001's missed caller; 25/25 correct by hand check; ambiguous locals left unresolved; about 20% slower; five edge cases found in review fixed. Tool accuracy, not an outcome result. |
| [walkthrough-001](walkthrough-001.md) | Can a newcomer go from the README to a `stale` report? (v0.4.0 README) | Not from the README alone. It led to the install and quickstart sections. |
| [walkthrough-002](walkthrough-002.md) | The same question for the reorganised README. | Yes for the commands. It found gaps in record guidance and the worked-example command, both fixed. |
| [MtG pilot](mtg-pilot.md) | Do the change-impact dispositions reproduce what reviewers concluded by hand? (v0, 2026-10-26) | Yes on six scenarios, but they were encoded after the fact by the session that wrote the tool. |

Walkthroughs were done by AI agents, not human strangers.
