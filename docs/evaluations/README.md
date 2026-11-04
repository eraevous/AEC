# Evaluations

What AEC has been measured on, including results that didn't favour it. Each entry links to its full write-up.

| Evaluation | Question | Result |
|---|---|---|
| [probe-001](probe-001-results.md) ([pre-registration](probe-001.md), [materials](probe-001/)) | Does AEC's structural briefing change what a coding agent does on dependency-sensitive tasks? | No signal: 18/18 trials succeeded in every condition. Briefings raised token use on 2 of 3 tasks. It exposed a caller-resolution gap. Exploratory pilot. |
| [resolver-001](resolver-001.md) | How many unresolved calls does the C-11 fix (`x = C(...); x.m()`) resolve on Data-Guide, and are they right? | 25 of 874 resolved, including probe-001's missed caller; 25/25 correct by hand check; ambiguous locals left unresolved; about 20% slower; five edge cases found in review fixed. Tool accuracy, not an outcome result. |
| [review-001](review-001.md) ([protocol](review-protocol.md)) | What does an independent model find when it audits the architecture, implementation and code? (GitHub Copilot) | Four findings, three of them reproducible defects, all fixed in PR #33. The fourth: AEC's value over its cost is unproven. |
| [code-impact-qual-001](code-impact-qual-001.md) ([materials](code-impact-qual-001/)) | Do Codex's helper, constant and module cases (A5RR) now produce a `code-impact` report, and does it reach anyone? | Yes on the fixture: module links fixed, helpers/constants reported as status-free pointers, hook and CI deliver it. Pointers add items on 11 of 16 code-changing Telosmith merges, precision unjudged. A cheap coverage/delivery qualification, not a value win. |
| [walkthrough-001](walkthrough-001.md) | Can a newcomer go from the README to a `stale` report? (v0.4.0 README) | Not from the README alone. It led to the install and quickstart sections. |
| [walkthrough-002](walkthrough-002.md) | The same question for the reorganised README. | Yes for the commands. It found gaps in record guidance and the worked-example command, both fixed. |
| [MtG pilot](mtg-pilot.md) | Do the change-impact dispositions reproduce what reviewers concluded by hand? (v0, 2026-10-26) | Yes on six scenarios, but they were encoded after the fact by the session that wrote the tool. |

Walkthroughs were done by AI agents, not human strangers.
