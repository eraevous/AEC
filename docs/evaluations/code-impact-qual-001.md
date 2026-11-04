# code-impact-qual-001: coverage and delivery qualification for `code-impact`

**A cheap coverage/delivery qualification, not a value win.** It checks that a frozen link mapping produces a
report for Codex's helper, constant and module cases, and that the report reaches someone. It says nothing
about whether those reports save reviewer time or catch consequential problems that tests and ordinary
review would miss. That is the job of the DEC-031 trial and value-001.

- Handoff: HO-RK-20261104-DN2X (relay-kit-private), replying to Codex's assessment HO-AEC-20261102-A5RR,
  section B ("What I established in scratch experiments") and the qualification step at the end of section E.
- Run by: claude:aec (Claude, session 01GZK2KncnZ4v7e6ZAQ4C1ZH), 2026-11-04, branch `dn2x/code-impact-gaps`.
- Independence: none. The same session wrote the fix and ran this check. Codex's probe scripts weren't
  available, so the fixture was rebuilt from its report.

## Materials (frozen before either run)

[`code-impact-qual-001/`](code-impact-qual-001/): two link mappings and the runner, hashed in `FREEZE.sha256`.

- `mapping-function.jsonl`: `REQ-price` (prices stay between 0 and 10) `implemented_by` `code:pricing.price`;
  `CL-price` `depends_on` `REQ-price@1`.
- `mapping-module.jsonl`: the same, linked to `code:pricing`, the form `import-purpose` writes.
- `run.py`: Codex's fixture, `price(x) = min(LIMIT, helper(x))`, `LIMIT = 10`, `helper(x) = max(0, x)`, and its
  seven edits. Run with `PYTHONPATH=<tool>/src python3 run.py`.

## Coverage

Before: `origin/main` at 906e8fd (`code_impact.py` unchanged since Codex's 9f57e19). Codex's table reproduced
exactly, including the module case.

| change | sample behaviour | function link | module link |
|---|---|---|---|
| no edit | preserved | none | none |
| add a comment | preserved | none | none |
| swap min arguments | preserved | REQ stale, CL needs_review | none |
| price returns its input | broken | REQ stale, CL needs_review | none |
| remove helper's lower bound | broken | **none** | **none** |
| raise LIMIT to 100 | broken | **none** | **none** |
| add an unrelated function | preserved | none | none |

After (this branch):

| change | sample behaviour | function link | module link |
|---|---|---|---|
| no edit | preserved | none | none |
| add a comment | preserved | none | none |
| swap min arguments | preserved | REQ stale, CL needs_review | REQ stale, CL needs_review |
| price returns its input | broken | REQ stale, CL needs_review | REQ stale, CL needs_review |
| remove helper's lower bound | broken | none; pointer: `code:pricing.helper` | REQ stale, CL needs_review |
| raise LIMIT to 100 | broken | none; pointer: `code:pricing.LIMIT` | REQ stale, CL needs_review |
| add an unrelated function | preserved | none | REQ stale, CL needs_review |

Raw outputs: [`before.md`](code-impact-qual-001/before.md), [`after.md`](code-impact-qual-001/after.md).

What changed and what didn't:

1. **Helpers and constants (function link): reported, not classified.** A changed definition one resolved
   `calls`/`references` step from a linked symbol produces a `structural: ... reaches changed ...` pointer naming
   the records to re-check. It assigns no status, so what a link means is unchanged (A5RR warns against letting a
   changed callee make every caller's rationale stale; that option is a proposal for Zach, not built).
   `--reach-depth N` widens it, `0` turns it off. A pointer whose records the report already flags is dropped.
2. **Module links: fixed.** A module's own hash was a placeholder, so `code:pricing` was only ever retracted
   (module deleted), never revised. A module now counts as changed when any definition or statement it contains
   changes, as a class does when a method changes. A package link does not cover its submodules. It is coarse,
   like a file watch: it flags the unrelated-function decoy too.
3. **The harmless reorder still flags.** `min(LIMIT, helper(x))` → `min(helper(x), LIMIT)` changes the body's
   AST. Deciding equivalence is semantic; `code-impact` stays structural (Constitution IV). Measured, not fixed.

## Noise on real history (link mappings frozen at today's records)

Each merge was snapshotted at its parent and itself, with the current records, old logic vs new.

| corpus | commits | with definition changes | linked symbols | commits with ≥1 affected record (old → new) | reach pointers, depth 1 (after folding) | depth 2 |
|---|---|---|---|---|---|---|
| Telosmith, first-parent merges to 906e8fd | 40 | 16 | 22 functions, 0 modules | 14 → 14 | 22 on 11 merges (56 before folding) | 36 (93 before folding) |
| Data-Guide 51d647a, all commits, links from `import-purpose` | 60 | 25 | 6 modules | 4 → 9 | 0 | 0 |

- On Telosmith the pointers add something on 11 of 16 code-changing merges. That is a review cost; whether any
  pointer was worth it was **not judged** (no precision measured).
- On Data-Guide module links now flag 5 more commits. Precision not judged. The mapping is frozen at HEAD, so
  commits before the 097c307 module consolidation under-count (the linked module names didn't exist yet).
- On this branch's own diff, the pointer report named `CL-telosmith-urls@1` and `AEC-R7@1` (via `init.init` →
  the changed `CI`/`HOOK` constants), which the old logic would have missed; both were re-checked and still hold
  (the CI snippet still installs the pinned release by URL; `tests/test_init.py` passes). It also named
  `DEC-036@1` via `__main__.main` → `build_parser` (a new flag), which is noise for that decision.

## Delivery

Before: the hook and CI that `aec init` generates ran `check` only, so `code-impact` reached no one unless run by
hand. After:

| path | recipient | what it does | covering test |
|---|---|---|---|
| Claude Code hook | the agent | after each edit: refresh snapshot, `check`, snapshot `HEAD`, `code-impact --exit-code`; on impact, report to stderr with exit 2; silent otherwise | `TestDelivery.test_hook_tells_the_agent_...` (LIMIT edit → exit 2, pointer in stderr); decoy `test_hook_quiet_...` |
| generated CI job | a human reviewer opening the run | merge-base snapshot, `code-impact`, report into the job summary; never fails the job | `test_ci_puts_the_report_in_the_job_summary`; decoy `test_ci_summary_says_nothing_affected_...` |
| Telosmith's own CI (this PR) | Zach on the PR's checks | the same step, Python 3.12 job, pull requests only | `test_own_ci_runs_the_same_impact_step`; the PR's run is the live check |

Locally, the generated CI step against `origin/main` wrote: `AEC-R6@1` stale and `CL-R6-deletion@1` needs_review
(via `code_impact.code_impact`), and the three pointers above.

Limit: "reaches" here means the report lands where the recipient will see it (agent context; the Actions run
summary). It is not a pull-request comment (a gated adoption item in `docs/architecture.md`), and nothing here
shows that anyone reads it or acts on it.

## Verdict

Qualified for coverage and delivery on this fixture: all three of Codex's missed cases now produce something a
reviewer receives, at the cost of coarser module links and a pointer stream measured above. Not evidence of
value.
