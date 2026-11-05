# Review vocabulary

Names for five ways an agent's report can claim more than happened. A reviewer tags a finding with one of these names
so the same failure gets the same word across reviews. They are signals, not scores: no counts, no severity numbers,
no integrity percentages. A tag says where to look; it does not grade the work.

The names come from a model-written hallucination audit of the earlier Codex++ traces (HONT, its
"Hallucination Ontology"). The owner adopted the names and dropped that audit's scores. Its own integrity score had no
stated basis, which is the fourth failure below.

| Tag | What it looks like | What clears it |
|---|---|---|
| `ghost-tool` | The report invokes a tool, module, check or file that does not exist in the session or the repository ("the logging layer recorded…") | A path, command or commit that exists |
| `reflexive-fabrication` | The report cites earlier work that never happened ("as the reviewer already confirmed…", "Claude + Kate done") | A pointer to the artifact: a review comment, an output file, a record, a log line |
| `metaphor-literal-swap` | A figure of speech is treated as a mechanism ("the records remember why"), so a claim seems to describe behaviour the code does not have | The literal mechanism, or the metaphor marked as one |
| `simulated-precision` | A number with no basis ("intervenes in 3 of 5 paths", "71.4 integrity") | The data and the computation, or the number removed |
| `clean-lie` | Structure and confident tone stand in for verification: a tidy report of things nobody checked | Which statements were checked, how, and which were not |

## Using it in a review

Tag the finding, quote the passage, and say what would clear it, for example:

> `reflexive-fabrication`: the PR body says "tests reviewed by Kate", but no review comment or output file exists.
> Clears with a link to the review.

`reflexive-fabrication` is the one to check every time on an agent-supervising-agent chain. A claim that a review,
test run or approval happened must point at the artifact it produced.

## Where it applies (cost cap)

Only on pull requests that change a contract, a check's semantics, or an authority. Other PRs get an ordinary review.

A `review:` handoff for such a PR carries this line in its Expected output:

```
Tag each finding with a docs/review-vocabulary.md name when one fits (ghost-tool, reflexive-fabrication, metaphor-literal-swap, simulated-precision, clean-lie); names only, no scores. Applies only because this PR touches a contract, a check or authority.
```
