# How AEC governs itself

AEC is designed and owned by Zach Rhodes and built with AI agents (Claude, Codex and ChatGPT)
working from written handoffs. "Kate" in these documents is the maintainer's name for ChatGPT, which serves as an independent reviewer. It is developed with Spec Kit (`specs/`) and governs itself with
its own records (`.aec/records.jsonl`), which makes the project its own longest-running test case.
What is public and what isn't: the specs, records, PR descriptions and evaluation write-ups here
are public. The coordination handoffs and the owner's decision log are kept in a private
repository. Where a public record cites them, it says so, and you are taking that citation on the
maintainer's word.


## Which source governs which question

`.aec/records.jsonl` governs purpose and authority (`AEC-P0@1`, `AU-zach@1`).
The engineering principles live in `.specify/memory/constitution.md`, applied by
`CHARTER.md`; `AGENTS.md` governs agent behavior. When a project uses Spec Kit,
Spec Kit owns its specification workflow. Purpose files in `codex_++/purpose_files/` are semantic contracts whose
claims are candidates, and `codex_++/intents/` contains provisional reasoning.
Generated edges are static structural facts, not a competing authority. If a
purpose file disagrees with a committed record, report the conflict for review;
the file cannot silently revise the record. Only Zach or an explicitly authorized
decision-maker for that subject may accept a commitment.
Reviews of PRs that touch a contract, a check or authority tag findings with the names in
[`review-vocabulary.md`](review-vocabulary.md).
