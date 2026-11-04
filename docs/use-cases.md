# Use cases

What Telosmith is for, ranked by how strong the evidence is. Each entry says what it does, how you run it, what
you see, what it does **not** do, and what it costs.

Written 2026-11-04 by claude:aec#usecases. The owner asked for it (Zach, 2026-11-04): *"The primary evaluation
of Telosmith will be in the context of an existing Agentic Coding framework that does not implement SpecKit…
Use cases for Telosmith are also required."* For the setup without Spec Kit, see
[integrations/without-spec-kit.md](integrations/without-spec-kit.md). For the planned comparison, see
[evaluations/eval-design-framework-comparison.md](evaluations/eval-design-framework-comparison.md).

## How to read the tiers

| Tier | Meaning |
|---|---|
| **Demonstrated** | The mechanism was run end to end on 2026-11-04 (in `docs/demo.md`, or in the scratch project for this page), and the output is pasted. It shows that the mechanism works, **not that it helps**. |
| **Qualified** | An entry in `docs/evaluations/` measured coverage, delivery or noise. Still not an outcome result. |
| **Plausible, untested** | The commands exist and run, but no one has used this for its stated purpose. |

**No use case below has outcome evidence.** The evidence that exists points the other way, or is null:

- [probe-001](evaluations/probe-001-results.md): agents found hidden dependants without Telosmith (18/18 trials
  in every condition), and briefings raised token use on 2 of 3 tasks.
- fathom-002 (run 2026-11-04; materials in the private relay-kit repository, see
  [governance.md](governance.md)): a first build with Spec Kit and Telosmith scored 39 against 44 and 45 for
  Spec Kit alone and for a plain `AGENTS.md`. It is confounded: the Spec Kit + Telosmith arm was a different
  builder (Codex, reviewed by Zach), while the other two were single Opus sessions. **Do not claim that
  Telosmith gives better first builds.**
- DEC-021 precondition P1 (`docs/evaluations/dec-021-protocol.md`, PR #50, not merged): on a real Fathom PR,
  `code-impact` did **not** name the committed obligations that the PR's defect broke. It named only a
  provisional reading that a plain file-level reminder also names.

The claim still untested, and the one the use cases rest on, is **better change review**: a change that
endangers a recorded reason gets noticed. Use case 1 is how that is supposed to happen.

## Summary

| # | Use case | Tier | Runs | LLM tokens |
|---|---|---|---|---|
| 1 | Change review in the agent loop (hook, exit 2) | Demonstrated + qualified | after every Edit/Write | none to compute; ~175 to read a 3-record report |
| 2 | PR gate: impact report in the CI job summary | Demonstrated (emulated) + qualified | per push/PR | none |
| 3 | Refactor safety: module links and reach pointers | Demonstrated + qualified (noise measured) | same as 1 and 2 | none |
| 4 | "Why does this code exist?" lookup | Demonstrated (mechanics only; no dedicated command) | on demand | none |
| 5 | Audit trail: claims → evidence → decisions, append-only, authority-checked | Mechanics demonstrated; use untested | on demand, CI | none |
| 6 | Experiment registry for data-science work | Mechanics demonstrated; used in Telosmith's own records; use untested | on demand | none |
| 7 | Knowledge artifacts beyond code (definitions, assumptions) | **Exploratory**: one after-the-fact pilot + anchor check | on demand | none |

Considered, not kept: **onboarding** ("a newcomer reads the records before the code"). Nothing does this
except opening `.aec/records.jsonl`. [walkthrough-001](evaluations/walkthrough-001.md) and
[-002](evaluations/walkthrough-002.md) tested whether a newcomer could *set Telosmith up*, not whether the records
help them understand a codebase. As a use case it would be a claim about prose quality, not about Telosmith.
Use case 4 is the part of it that the tool actually supports.

Every Telosmith command is deterministic and offline. None of them calls a model. The only token costs are
(a) a model **writing** records, and (b) a model **reading** a report. Both are noted where they apply.

---

## 1. Change review in the agent loop

**Tier: demonstrated + qualified.** [demo.md §4](demo.md); [code-impact-qual-001](evaluations/code-impact-qual-001.md)
(delivery table, tests `TestDelivery.test_hook_tells_the_agent_...` and decoy `test_hook_quiet_...`);
records `AEC-R6@1` ("A code change is traced to the conclusions that rely on it") and `AEC-R5@1`.

**Situation.** An agent edits a function that a written requirement rests on. The tests still pass. The
README's itsdangerous example is the shape: `hmac.compare_digest` "simplified" to `==`, 297 of 297 tests green.

**What Telosmith does.** After each edit, the hook refreshes the edge snapshot, runs `check`, snapshots `HEAD`,
and runs `code-impact --exit-code`. If a linked symbol changed, or a definition one call away changed, it
writes the report to stderr and exits 2, which Claude Code hands back to the agent. If nothing linked moved,
it says nothing.

**Path.** `aec init` → copy `.aec/snippets/claude-settings.json` into `.claude/settings.json`. For other
harnesses, use the git hooks or the rules-file text in
[without-spec-kit.md](integrations/without-spec-kit.md).

**What the agent sees** (scratch project, 2026-11-04, `apply_discount` edited; `R-1` is linked to it, `C-1`
depends on `R-1@1`, and decision `D-1` depends on `C-1@1`):

```text
- change: revise code:shop.pricing.apply_discount (by code, authorized_by None)

[stale] R-1@1: Discounts never make a price negative.
    via code:shop.pricing.apply_discount -> R-1@1
[needs_review] C-1@1: Checkout totals are never negative.
    via code:shop.pricing.apply_discount -> R-1@1 -> C-1@1
[needs_review] D-1@1: Ship the checkout with the never-negative guarantee.
    via code:shop.pricing.apply_discount -> R-1@1 -> C-1@1 -> D-1@1

3 affected, 2 conclusions with no status change
(Telosmith: stale/needs_review lines are status changes; structural pointer lines are candidates for attention and change no status.)
exit 2
```

**What it does not do.** It does not say whether `R-1` still holds, and it does not run or write tests. It
cannot see what no record links to (an edit to unlinked code reports nothing). It does not reach two calls
away by default: in the same scratch project, changing the constant `LIMIT` that `clamp` reads
(`apply_discount → clamp → LIMIT`) printed `0 affected`. It cannot see calls it cannot resolve (dynamic
dispatch, string registries, non-Python code). On the one real-PR case checked (DEC-021 P1, above), it
missed the obligations that mattered. Nothing is acknowledged or cleared: the report repeats on every edit
until the change is committed (code-impact-qual-001, "Noise cost").

**Cost.** Four deterministic commands per edit. About 0.4 s on the toy project and about 2.1 s on Telosmith
itself (63 files, 4,619 edges); measured 2026-11-04. Zero tokens to compute. The agent reads the report:
695 characters for the three-record report above, roughly 175 tokens (an estimate at about 4 characters per
token). probe-001 found that context the agent did not need still cost turns, which is the risk here.

## 2. PR gate: impact report in the CI job summary

**Tier: demonstrated (emulated locally) + qualified.** code-impact-qual-001, delivery table
(`test_ci_puts_the_report_in_the_job_summary`, decoy `test_ci_summary_says_nothing_affected_...`).
Telosmith's own CI runs the same step (`.github/workflows/ci.yml`, "Code impact against the PR base").

**Situation.** A human reviews a PR, possibly one an agent wrote, and wants to know which written reasons it
touches without reading every diff hunk.

**What Telosmith does.** `aec check` fails the job on record errors (a dangling `code:` reference, for
example). Then the impact step snapshots the merge-base, runs `code-impact` against the checkout, and appends
the report to `$GITHUB_STEP_SUMMARY`. **The impact step never fails the job.**

**Path.** `aec init` → copy `.aec/snippets/aec-ci.yml` into `.github/workflows/aec.yml`.

**What the reviewer sees** (the generated step's script, run locally with `GITHUB_STEP_SUMMARY` set to a file
and `AEC_BASE` set to `origin/main`):

````text
## Telosmith code-impact (structural, report-only) vs 13b185ddcfea49386d1ab7c08f9fe26452ffddeb
```
# derived 1 change event(s) from the structural diff
...
[stale] R-1@1: Discounts never make a price negative.
...
3 affected, 2 conclusions with no status change
```
````

**What it does not do.** It posts no PR comment. A reviewer sees the report only by opening the run, and
nobody has measured whether reviewers do (code-impact-qual-001, "Limit"). It does not block on impact. It does
not check that records are append-only (see use case 5 for a script that does). Not tested on GitHub's runners
in this pass. One gotcha found here: `aec init` run from a source checkout pins the snippet to `v0.5.0`, and
that tag does not exist yet (only `v0.4.0` and `v0.4.1` on 2026-11-04). Until it does, replace the ref with a
commit SHA.

**Cost.** One job: install, snapshot twice, check, and code-impact. The Telosmith commands take about 2 s on
a repo of Telosmith's size; the job is dominated by setup. Zero tokens.

## 3. Refactor safety: module links and reach pointers

**Tier: demonstrated + qualified, with noise measured.** code-impact-qual-001, coverage tables (before and
after) and "Noise on real history"; `docs/reasoning-vocabulary.md`, "Code references".

**Situation.** A refactor changes the inside of a module, or a helper that a linked function calls, without
touching the linked symbol itself. This is also what `AMB-radical-restructuring@1` hopes for ("refactoring or
completely restructuring a project while still fulfilling the commitments"). That record is an ambition, not
a commitment.

**What Telosmith does.** A link to a module (`code:shop.tax`, the form `import-purpose` writes) is revised by
*any* change inside the module. A link to a function is revised by changes to its own body. A changed
definition one resolved call or reference away becomes a `structural: ... reaches changed ...` pointer, which
assigns no status. If a linked symbol is renamed or moved, `check` errors on the dangling reference, and
`code-impact` marks the dependants `needs_review`, with "recorded implementation path ... no longer exists".

**What you see** (scratch project):

```text
# shop/tax.py: only label() changed, but R-2 links the whole module
[stale] R-2@1: Tax is computed at the published 8% rate.
    via code:shop.tax -> R-2@1

# clamp() edited; R-1 links apply_discount, which calls clamp
[finding] structural: code:shop.pricing.apply_discount reaches changed code:shop.pricing.clamp (calls, depth 1); no status change; candidate for attention: R-1@1

# shop/pricing.py moved to shop/core/pricing.py
[ERROR] code-reference: R-1@1: implemented_by -> code:shop.pricing.apply_discount: no such symbol in the edge snapshot (renamed or deleted?)
[finding] recorded implementation path R-1@1 -> code:shop.pricing.apply_discount no longer exists: the satisfaction claim is unjustified; the requirement itself stands
```

**What it does not do.** Module links are coarse: the `label()` decoy flags `R-2` exactly as a rate change
would. Behaviour-preserving rewrites still count as revisions (code-impact-qual-001, item 3). On a move, `check`
offered no near-miss suggestion for `shop.core.pricing.apply_discount` (observed here); you re-link by hand.
On real history, pointers added items on 11 of 16 code-changing Telosmith merges, and **their precision was not
judged**.

**Cost.** Same commands as use cases 1 and 2. `--reach-depth 2` widens the pointers (36 at depth 2 against 22 at
depth 1 on Telosmith's history). Zero tokens.

## 4. "Why does this code exist?" lookup

**Tier: demonstrated, mechanics only.** There is no dedicated command. It takes three steps, and each one works.
`docs/reference/source-anchors.md`; `AEC-R9@1`.

**Situation.** You are about to change `round_cents` and want to know what written reason, if any, rests on it.

**What you do.**

```bash
grep -n '"code:shop.pricing.round_cents"' .aec/records.jsonl                 # is it linked directly? (here: no)
aec reach shop.pricing.round_cents --direction callers --depth 2              # which symbols reach it?
#   "reachable": ["shop.pricing.apply_discount", "shop.pricing.clamp"]
grep -n '"code:shop.pricing.apply_discount"' .aec/records.jsonl               # R-1 is linked to a caller
aec source show R-1@1                                                         # the passage R-1's rationale came from
```

```text
record-directed R-1@1 anchor[0] for=rationale state=verified source="docs/pricing.md" locator="L3-4"
...
3 | Refunds are issued as negative line items elsewhere,
4 | so a discount must never push a price below zero.
```

**What it does not do.** It is a manual join of `grep`, `reach` and `source show`. Nothing goes from a symbol
to its records in one step, and `reach` takes the bare name (passing `code:` errors with "symbol is not present
in the snapshot"). A missing record means nobody wrote one, not that there is no reason. Unresolved callers are
invisible, and `reach` prints a caveat saying so.

**Cost.** Three or four sub-second commands. Zero tokens, unless an agent reads the output.

## 5. Audit trail for compliance-minded teams

**Tier: mechanics demonstrated; use untested.** `docs/reasoning-vocabulary.md` (the ADR, change-request and
rebaselining mappings, and the `revise` authorization rule); the MtG pilot, scenarios 3 and 4
([mtg-pilot.md](evaluations/mtg-pilot.md)).

**Situation.** Someone has to answer, later, "what was concluded, on what evidence, who decided, and did the
basis change afterwards?". That is a controls-review question, and Zach's background is audit and compliance.

**What Telosmith does.**
- Chains `evidence -supports-> claim -depends_on-> decision`, pinned by `id@version`.
- `check` errors on an accepted decision that names no governing authority.
- `impact` labels a revision as authorized or not, by whether `authorized_by` governs the subject:

  ```text
  [finding] unauthorized revision of committed requirement DEF-active@1: by='analyst', authorized_by=None does not govern subject 'definitions'. This is a proposal, not a revision.
  ```

- Retracting evidence propagates: in the scratch data-science example, the claim it supported became
  `unjustified` and the decision that depended on that claim became `needs_review`.

**What it does not do.**
- **`check` does not enforce append-only.** An in-place edit of an evidence line's text passed `check` with
  0 errors (tested here). The trail is git history. [without-spec-kit.md](integrations/without-spec-kit.md#append-only-guard)
  has a stdlib CI guard, tested here, that fails when the records file stops starting with its base-revision
  bytes.
- It does not verify that `authorized_by` is real consent: "a typed `authorized_by` is a claim, not verified
  consent" (`AGENTS.md`).
- It does not judge evidence quality.
- One gap observed here: appending `R-1@2` while `C-1` still pins `R-1@1` gives no warning. After that, a code
  change marked only `R-1@2` stale, and `C-1@1` was no longer reached. Re-pin dependants when you revise a record.

**Cost.** Writing records is the cost. A model writing them spends tokens; Telosmith spends none. `docs/speckit-log.md`
logs authoring time (for example, "~3 hours of agent time" for feature 001 including Spec Kit stages). That is
not a records-only figure.

## 6. Experiment registry for data-science work

**Tier: mechanics demonstrated; used in Telosmith's own ledger; use untested.** DEC-033 (types defined,
`docs/reasoning-vocabulary.md`); `EXP-owner-report@1` in `.aec/records.jsonl`; `EXP-dec021-fathom-replay@2`
(PR #50).

**Situation.** An analyst tries two feature sets, keeps one, and ships a model decision on the result. Later
the holdout turns out to have leaked.

**What Telosmith does.** An `experiment` record names its variants and `produced` the evidence. The decision
cites the claim, not the experiment. Retracting the evidence flags the chain. The experiment itself is never
reported, because it is not a conclusion. Scratch run:

```text
- change: retract E-auc@1 (by dana, authorized_by None)

[unjustified] C-usage@1: Usage features add predictive value for churn.
    via E-auc@1 -> C-usage@1
[needs_review] D-ship@1: Ship the tenure+usage model.
    via E-auc@1 -> C-usage@1 -> D-ship@1
```

**What it does not do.**
- The change event (`{"change":"retract","target":"E-auc@1",...}`) is written by hand. Nothing derives it from
  a notebook, a dataset or an MLflow run.
- Notebooks are not in the edge snapshot (Python files only).
- There is no command to list experiments or their status. Use `grep '"experiment"'`.
- Nothing checks whether a commitment forecloses an ambition. Mechanising that is undecided (vocabulary, DEC-033).

**Cost.** `impact` ran in about 0.06 s on the MtG pilot. Zero tokens.

## 7. Knowledge artifacts beyond code (exploratory)

**Tier: exploratory.** The [MtG pilot](evaluations/mtg-pilot.md) is the only real non-code case: deck
reasoning, six scenarios, encoded after the fact by the session that wrote the tool. The anchor check below was
run here. This is input for Zach's "Knowledge Engine" intake, not a supported mode.

**Situation.** A docs or analytics repository holds definitions ("active customer = ordered in the last 90
days") and assumptions, and reported numbers rest on them. Someone edits the glossary.

**What Telosmith does.**
- A record anchored to the glossary passage (`anchors`: path, sha256, locator) makes `check` warn when the file
  changes:

  ```text
  [WARNING] anchor-mismatch: DEF-active@1: ... state=mismatch source="glossary.md" locator="q:Active customer": file bytes changed; the earlier observation is not falsified; applicability needs review
  ```

- After someone writes the revise event by hand, `impact` marks the dependent figure stale and flags the
  unauthorized revision:

  ```text
  [stale] C-retention@1: Q3 retention was 62% of active customers.
  ```

**What it does not do.**
- The anchor warning does not become a change event. There is no `code-impact` equivalent for documents, so
  someone has to connect "the glossary changed" to "DEF-active was revised".
- `check` exits 0 on warnings.
- It cannot tell a typo fix from a definitional change.

**Cost.** `check` and `impact`, each under a second. Zero tokens.

---

## Where this leaves the claim

All seven use cases rely on records that someone wrote and keeps up to date (review-001, "Architectural dissent";
`AEC-R3@1`). The strongest one, change review in the loop, is qualified for **delivery**, not for **value**. It has
one real-PR miss on record (DEC-021 P1). [The evaluation draft](evaluations/eval-design-framework-comparison.md)
tests it directly against a framework without Spec Kit.

**For Zach to decide (raised here, not resolved).** `AEC-P0@1` (committed) describes Telosmith "as a measurable
extension to spec-driven development (Spec Kit)", and `AEC-R3@1` measures adoption "against a well-configured
Spec Kit baseline". The evaluation context stated on 2026-11-04 is a framework **without** Spec Kit. Nothing in the
check/impact loop depends on Spec Kit (verified in
[without-spec-kit.md](integrations/without-spec-kit.md#what-spec-kit-adds-and-what-is-lost-without-it)), so this
is a question of wording and baseline, not of code. Whether to append `AEC-P0@2` and `AEC-R3@2` is Zach's call.
