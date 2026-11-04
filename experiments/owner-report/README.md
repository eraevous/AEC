# Experiment: decisions and human control report (EXP-owner-report)

**Why.** Zach, 2026-11-03 08:53 CT: "We really need to add some functional support for a 'decisions and
human control' report - I frequently have no idea what levers I actually need to pull or what choices I'm
making." It serves the ambition AMB-owner-reporting.

**What it is.** `owner_report.py` reads the project's records where they already are: open pull requests,
relay-kit decisions, handoffs and candidates, and Telosmith's records. It prints one Markdown report:
1. **Your levers:** every item waiting on the owner (land, merge, route, decide, authorise, confirm, investigate),
   the choice it is, and **what happens if you do nothing**. Stacked PRs are listed in merge order.
2. **Choices you're making by default:** items that have waited long enough that no action is the decision.
3. **What you decided recently**, in your own recorded words.
4. **Standing ambitions**, kept open but not commitments.

It's read-only and uses the standard library; GitHub is read through `gh`.

**Experiment, not feature (DEC-033).** It commits to nothing and needn't be supported. Under the build gates
(DEC-032) it is an **adoption unlock** and **cost reducer**:

| Gate | |
|---|---|
| Cheapest alternative | `status.py` in the relay kit (open handoffs, proposed decisions), plus reading GitHub and the ledgers by hand |
| Result that promotes it into Telosmith | Over about a week of real use, Zach finds and acts on what's waiting faster, and misses fewer items, than with the alternative. Also: at least one "choice by default" he hadn't noticed |
| Result that drops it | He doesn't use it, or `status.py` plus GitHub's own lists serve as well |

**Found in use (2026-11-03).** Stacked PRs #43 and #44 were merged into `pi/toolchain`, which was never
retargeted to `main`. The work looked merged but wasn't on main. The report now flags merged PRs whose base
branch is still ahead of the default branch (lever **land**), unless a PR to land it is already open.

**Known gaps.**
- It recommends nothing: the levers are facts, and judgement stays with the reader or an agent annotating the report.
- Owner actions with no record (for example "paste this prompt into Copilot") are invisible.
- DEC-020 (a decision queue kept by agents, trialled for a month) is the natural home for those, and for recommendations.

```bash
python3 experiments/owner-report/owner_report.py --telosmith . --relay ../relay-kit-private \
    --repo eraevous/Telosmith --repo eraevous/relay-kit-private -o owner-report.md
```
