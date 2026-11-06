# Enforcement audit: what holds each rule in AGENTS.md

For each consequential rule in `AGENTS.md` (and the Claude Code hook in `.claude/settings.json`), this page names
the mechanism that enforces it, or labels the rule as one of:

- **mechanical**: a test, CI step, hook or `check` finding fails or reports when the rule is broken;
- **partial**: a mechanism covers part of the rule; the gap is named;
- **procedural**: held by agents and reviewers following the text; nothing fails when it is broken;
- **advisory**: guidance about interpretation; there is nothing to break.

Audited against `main` at 265c2aa (2026-11-06). Nothing here changes a rule. Gaps are listed for a decision, not
fixed. Requested by the idle list (relay-kit-private `kairos/idle-work.md`, DEC-120 enforcement audit).

## Which source governs which question

| Rule | Label | Mechanism, or what is missing |
| --- | --- | --- |
| `.aec/records.jsonl` governs purpose; `AEC-P0@3` is the purpose (latest version) | partial | `check` warns on `superseded-reference` when a record cites an older version. Nothing ties the prose in `AGENTS.md`, `CHARTER.md` or `docs/governance.md` to the latest version: the last two still name `AEC-P0@1`. |
| `AU-zach@1` governs design intent and acceptance, by subject | mechanical | `check` errors on an accepted `decision` whose `decided_by` does not govern its subject (`src/aec/records.py`, `store.governs`). |
| Constitution beats `CHARTER.md` on conflict | procedural | No check compares the two. |
| Spec Kit owns specs, plans and tasks; a Telosmith report is never permission to rewrite them | procedural | The Spec Kit extension's command files tell the agent "Do not modify Spec Kit artifacts" (`extension/commands/`); that is an instruction, not a check. |
| Purpose files are candidate claims and cannot override committed records | mechanical | `import-purpose` writes them as provisional, source-linked claims (`tests/test_import_purpose.py`). Reporting a disagreement instead of choosing a new goal is procedural. |
| `.aec/edges.jsonl` is generated; never hand-edit it | partial | CI regenerates it before `check`, so a hand edit never decides a CI result. A hand-edited snapshot committed to the repo is not detected: CI does not compare the regenerated file with the committed one. |
| Never infer a justificatory dependency from an import or call edge alone | mechanical | `code-impact` labels such reach as structural pointers that "change no status" (`tests/test_code_impact.py`). |

## Authority

| Rule | Label | Mechanism, or what is missing |
| --- | --- | --- |
| Only Zach (or an authorized decider) accepts scope or goal commitments | mechanical for records | Same `decided_by` check as above. Acceptance said in a PR or chat, outside records, is procedural. |
| Reconstructed decisions stay proposed | mechanical | `tools/reconstruct_decisions.py` writes candidates as proposed (`tests/test_reconstruct_decisions.py`). Promoting one by hand is not detected. |
| A typed `authorized_by` is a claim, not verified consent | advisory | By design nothing verifies it; `docs/gates.md` F1 notes the consequence. |
| Authority does not compose (rule 7, `docs/reasoning-vocabulary.md`) | mechanical | `tests/test_no_transitive_authority.py`. |

## Work cadence and boundaries

| Rule | Label | Mechanism, or what is missing |
| --- | --- | --- |
| Run / Drift cadence; record questions and rework in an intent note | procedural | `AGENTS.md` itself says this is "an agent practice, not an automated trigger". |
| Stop on work outside authorization | procedural | — |
| Standard library only, no runtime dependencies | partial | `pyproject.toml` declares `dependencies = []`. CI runs the tests from `src/` without installing the package, so a third-party import in `src/` fails there; nothing fails if a dependency is added to `pyproject.toml` and the import is guarded. |
| Deterministic ordering | partial | Output tests in `tests/` pin many outputs; `tools/golden_master.py` compares runs but is not run in CI. There is no general check. |
| Each new check or classifier gets a violating fixture and a clean decoy, written first | procedural | Reviewers check the PR; "written first" cannot be verified from the merged diff. |
| **Never edit existing record lines** (append-only records) | **procedural (gap)** | No CI step or test checks that the base branch's `.aec/records.jsonl` is a byte prefix of the PR's. `record_touch.py` only checks that the file was touched. `init` writes a reminder comment; `import-purpose` is tested to append only. An in-place edit of a committed line in a PR passes CI. |
| Never treat a passing test as owner approval | procedural | — |
| Purpose files change only within their authorized task scope | procedural | — |
| Run `tools/preflight.py` before opening or marking a PR ready | procedural | The PR template has a checkbox. CI runs the same gating steps after the PR is opened, so a skipped preflight is caught late, not missed. |
| A `src/` change appends a record or gives `AEC-Record: none - <reason>` | partial | CI `tools/record_touch.py`, on `pull_request` events only; a direct push to `main` skips it. |

## Merging and the hook

| Rule | Label | Mechanism, or what is missing |
| --- | --- | --- |
| Merges only with green tests plus an independent review (DEC-048; not in `AGENTS.md`) | procedural | `main` has no branch protection and no rulesets (GitHub API, 2026-11-06). CI runs on every PR and push, but nothing blocks a merge on red CI or without a review. |
| After each Edit/Write, Claude Code re-checks records against fresh edges | mechanical in Claude Code | `.claude/settings.json` PostToolUse hook; exit 2 hands findings to the agent. Other agents (Codex, ChatGPT) do not run it. |

## Gaps, for a decision

None of these is fixed here; each would change behaviour or a gate.

1. **Append-only records are not checked in CI.** A `record_prefix` step (base `records.jsonl` must be a byte
   prefix of head) would make the rule mechanical. Related to `docs/gates.md` F1.
2. **No branch protection on `main`.** Requiring the CI checks (and, if wanted, one review) would make the
   DEC-048 merge rule mechanical.
3. **Committed `edges.jsonl` can drift from the code.** CI could fail when the regenerated snapshot differs.
4. **`record_touch` skips direct pushes.** Only matters if pushes to `main` happen outside PRs.
5. **`CHARTER.md` and `docs/governance.md` still name `AEC-P0@1`.** Already with Zach as a wording decision.
