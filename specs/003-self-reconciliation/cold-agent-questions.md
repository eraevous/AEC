# Cold-agent usability check (SC-003)

After WP0 is implemented, a **fresh agent**, not the implementer, answers these questions using only a checkout of the repository: no chat history, no web search about AEC. The reviewer grades each answer against the code. Correct means specific and true. "The docs don't say" is an honest answer and counts as a documentation failure, not an agent failure.

1. What is AEC for, in one or two sentences, and where is that purpose recorded authoritatively?
2. List every `python -m aec` subcommand and say in one line what each does.
3. What are AEC's runtime dependencies?
4. If a purpose file and a record in `.aec/records.jsonl` disagree about what a module is for, which governs, and why?
5. Who may accept a decision about AEC's scope, and how would the repository show that a decision was accepted rather than proposed?
6. What does `aec impact` report when a requirement's implementing function is deleted? What does it report for a claim that `depends_on` that function?
7. What does a passing `aec check` establish, and what does it not establish?
8. Which capabilities in `docs/architecture.md` are built today, and which are only planned?
9. How do you run the full test suite and the record checks locally, exactly as CI does?
10. Name two known limitations of the AST edge graph that an agent should keep in mind before relying on "no callers found".
