# Enforcement audit: governing instructions as executable dependencies

**Status: draft for owner review.** Docs only. Nothing here changes a rule, a check, a hook or CI;
every fix is proposed, not applied. Asked for by the external review CH-035 §6 and DEC-120
(enforcement audit), taken under the DEC-136 idle policy.

Audited on 2026-11-06 against `origin/main` at `265c2aa`. Sources read: `AGENTS.md`, `CHARTER.md`,
`CONTRIBUTING.md`, `.specify/memory/constitution.md`, `.github/workflows/ci.yml`,
`.github/pull_request_template.md`, `.claude/settings.json`, `tools/preflight.py`,
`tools/record_touch.py`, `tests/`, `src/aec/records.py`.

## Labels

| Label | Meaning |
| --- | --- |
| `enforced` | a hook, CI job, test or script fails when the rule is broken; the path is named |
| `procedural` | relies on a person (or an agent) doing it; nothing fails if they don't |
| `advisory` | guidance or an epistemic stance; not the kind of thing a check can fail on |
| `planned` | names a mechanism that does not exist yet |
| `obsolete` | contradicted by the current records or code |

Where a rule is `enforced` only for part of its scope, the row says which part.

## What was run (read-only)

- `PYTHONPATH=src python3 -m unittest discover -s tests` (with `AEC_SKIP_INSTALL_TEST=1`): 317 tests, OK, 2 skipped.
- `PYTHONPATH=src python3 -m aec edges . -o <scratch>` then `python3 -m aec check .aec/records.jsonl --edges <scratch>`: 0 errors, 23 warnings (structural).
- `PYTHONPATH=src python3 -m aec check examples/mtg-pilot/records.jsonl`: 0 errors, 1 warning.
- `python3 tools/record_touch.py --base origin/main`: passes (no `src/` changes on this branch).
- `ruff check .`: all checks passed (ruff 0.17.x installed locally; CI does not run it).
- `python3 -m aec --help`: 14 registered subcommands.

## Rules and their enforcement

| # | Rule (short quote) | Where stated | Enforcing mechanism | Label | Evidence |
| --- | --- | --- | --- | --- | --- |
| 1 | "No runtime dependencies beyond Python 3.10+" / "Standard library only" | AGENTS.md (intro, cadence), CHARTER 1, CONTRIBUTING rule 1, constitution II | `tests/test_stdlib_only.py` walks `src/aec/*.py` imports against `sys.stdlib_module_names`; CI runs the unit suite | `enforced` | ran the suite; read the test |
| 2 | "Deterministic ordering" / "same input gives byte-identical output" | AGENTS.md, CHARTER 2, CONTRIBUTING rule 1, constitution II | No dedicated determinism test (no run-twice-and-compare fixture); individual tests assert sorted output in places | `procedural` (reviewed) | grep `tests/` for repeat-run comparisons: none |
| 3 | "Never edit existing record lines" / "Append-only records" | AGENTS.md, CHARTER 4, CONTRIBUTING "may not", constitution II and Governance | `aec check` fails on a changed version with the same id (`unique`, `version` errors in `src/aec/records.py`); `tests/test_ledger_hygiene.py::test_records_file_is_never_rewritten` checks the tool itself never rewrites. No CI diff against the base for rewritten lines of `.aec/records.jsonl` | `enforced` for same-id/version conflicts; `procedural` for a silent rewrite that keeps id/version valid | read `records.py` finding rules; CI `ci.yml` has no append-only git diff step |
| 4 | "An accepted decision must name a governing authority with `decided_by`" | AGENTS.md | `aec check` error `authority` (`records.py` line ~242: accepted but `decided_by` does not govern the subject); `tests/test_no_transitive_authority.py` | `enforced` | read `records.py`; ran suite |
| 5 | "Reconstructed decisions remain proposed" / "never accept a reconstructed decision" | AGENTS.md, CHARTER 3–4 | `tools/reconstruct_decisions.py` writes `status: proposed`; `tests/test_reconstruct_decisions.py`. Nothing stops a human appending an accepted version later: that is by design (owner's call) | `enforced` for the tool's own output; `procedural` for people | read tool + test |
| 6 | "A typed `authorized_by` is a claim, not verified consent" | AGENTS.md, CHARTER 4 | None possible; `aec check` warns when a revision lacks `authorized_by` (`authority` warning) | `advisory` | read `records.py` |
| 7 | "Never hand-edit `.aec/edges.jsonl`" | AGENTS.md, CHARTER 2, CONTRIBUTING | CI regenerates edges before every check (`ci.yml` "Edge snapshot"); the file is git-ignored (`.aec/.gitignore`), so a hand edit cannot reach main | `enforced` | read `ci.yml`; `git check-ignore .aec/edges.jsonl` |
| 8 | "Each new check/classifier needs a violating fixture and a clean decoy, written before implementation" | AGENTS.md, CHARTER 5, CONTRIBUTING rule 2, constitution III (NON-NEGOTIABLE) | No meta-test enumerates checks and asserts a violating + decoy fixture per check; the convention is followed in the test files (`# violating` / `# decoy` comments) but review is what catches a missing pair. "Written before" is unobservable after the fact | `procedural` | grep `tests/` for "decoy": many per-test; no enumerating test |
| 9 | "Before opening a PR ... run `python3 tools/preflight.py` ... say in the PR body that it passed" | AGENTS.md | `tools/preflight.py` exists and mirrors CI; the PR template has a checkbox. CI runs the same steps, so the *outcome* is enforced; the *saying so* is not | `enforced` (outcome via CI); `procedural` (the PR-body statement) | ran preflight's components; read `pull_request_template.md` |
| 10 | "A src/ change appends a record or says why not" | `ci.yml` step, `tools/record_touch.py` docstring (implicit in AGENTS "purpose files change only in their authorized task scope; log discrepancies") | `tools/record_touch.py` in CI on pull requests; `tests/test_record_touch.py` | `enforced` (PR events only; a direct push to main is not checked) | read `ci.yml` `if: github.event_name == 'pull_request'`; ran the script |
| 11 | "Records check against the snapshot fails on dangling code references" | AGENTS.md "Checks", CHARTER 5 | `ci.yml` "Records check" step; `aec check --edges` error `code-reference`; the Claude Code hook in `.claude/settings.json` runs the same after every Edit/Write | `enforced` | ran `aec check`; read hook |
| 12 | "Docs tell the truth: every path and `aec` command named in README.md, AGENTS.md and this file must exist" | CONTRIBUTING rule 4 | `tests/test_docs_truth.py::test_readme_and_agents_tell_the_truth` | `enforced` for existence of named paths/commands; `procedural` for completeness (a command the docs omit is not caught, see mismatch 3) | read the test |
| 13 | "Structural ≠ semantic: outputs and docs say what records and code show, never that a conclusion is true" | AGENTS.md, CHARTER 3, CONTRIBUTING rule 3, constitution IV | `tests/test_docs_truth.py::TestAnchorOutputTruth` forbids "supports/proves/verifies the claim/authorized" in `aec.sources.OUTPUT_TEMPLATES`; `TestGraphVisibilityTruth` requires visibility denominators and the caveat. Prose in README/docs is not scanned | `enforced` for anchor/graph output templates; `procedural` for prose | read the test |
| 14 | "Keep the CLI thin; `__main__.py` only parses arguments" | CHARTER 1, CONTRIBUTING rule 5 | No test measures logic in `__main__.py` | `procedural` | grep `tests/` for `__main__` size/branch checks: none |
| 15 | "No new service / graph database without an owner decision" | CHARTER 1, constitution II | None; stdlib-only test (row 1) would catch a client library but not a subprocess call | `procedural` | read tests |
| 16 | "Mark a proposed decision as accepted ... only the maintainer" | CONTRIBUTING "may not", AGENTS.md | `aec check` enforces that `decided_by` governs the subject (row 4) but cannot verify *who typed it*; repository protection (branch rules, CODEOWNERS) not present in the repo | `procedural` | no CODEOWNERS; no branch-protection file visible from the checkout |
| 17 | "Tick the CLA box ... an agent must never tick the box on a contributor's behalf" | CONTRIBUTING | PR template checkbox only; no CLA bot or CI check | `procedural` | read `.github/`; no CLA workflow |
| 18 | "Say in the PR that it was written with AI agents" | CONTRIBUTING | None | `procedural` | — |
| 19 | "Pre-commit hooks run ruff" / lint | CONTRIBUTING, `.pre-commit-config.yaml` | Optional local pre-commit; `tools/preflight.py` runs ruff only when installed; CI does not run ruff | `procedural` (documented as optional) | read `ci.yml`, `preflight.py` |
| 20 | "Spec Kit is pinned (v1.2.3)" / extension integration never edits Spec Kit core templates | constitution Additional Constraints, AGENTS.md | CI installs `specify-cli` at `v1.2.3`; `tests/test_extension.py` skips when the CLI is absent (so locally it is often not run) | `enforced` in CI; `procedural` locally | read `ci.yml`; suite reported 2 skips locally |
| 21 | "A feature spec MUST cite the AEC purpose or requirement it serves by `id@version`" | constitution I | No test scans `specs/*/spec.md` for an `id@version` citation | `procedural` | grep `tests/` for `specs/`: none |
| 22 | "`python -m aec check` MUST pass before implementation and after convergence" | constitution Development Workflow | CI runs `aec check` on every push/PR (row 11); the "before implementation" timing is a workflow step nothing observes | `enforced` (at PR time); `procedural` (timing) | read `ci.yml` |
| 23 | "A PR that adds a subsystem includes a dissent review" | constitution Development Workflow; AGENTS.md Drift | None; PR template has no dissent section | `procedural` | read `pull_request_template.md` |
| 24 | "Every PR review verifies compliance with Principles I–VI" | constitution Governance | None automated | `procedural` | — |
| 25 | "Amendments [to the constitution] require a recorded decision event approved by `AU-zach@1` with a semantic version bump" | constitution Governance | No test ties `constitution.md` changes to a records entry | `procedural` | grep tests for `constitution`: none |
| 26 | "Record authoring/maintenance cost and what Spec Kit caught in `docs/speckit-log.md`" | CHARTER 6, constitution V | None; the file exists and is maintained by hand | `procedural` | file present; no check |
| 27 | "Run / Drift ... today this is an agent practice, not an automated trigger" | AGENTS.md, CHARTER closing | Honestly labelled as practice; automation is listed as planned | `planned` (automation) / `procedural` (practice) | read AGENTS.md "Built, partial and planned" |
| 28 | "Legacy `src/core/` is excluded from the shipped package" | CHARTER 1, AGENTS.md | `pyproject.toml` package config; `tests/test_install.py` installs the package (skipped offline via `AEC_SKIP_INSTALL_TEST`) and the stdlib test only walks `src/aec` | `enforced` in CI (install test runs there) | read `pyproject.toml`; suite skipped it locally |
| 29 | "Purpose files are candidate claims; they cannot override committed purpose or authority records" | AGENTS.md, CHARTER closing | `aec import-purpose` imports as provisional with source links (`tests/test_import_purpose.py`); nothing prevents a human treating them as policy | `enforced` for the import's epistemic label; `advisory` otherwise | read test names |
| 30 | "Never infer a justificatory dependency from an import/call edge alone" | AGENTS.md, CHARTER 2 | `aec code-impact` output is labelled structural; report-only CI step | `advisory` | read `ci.yml` code-impact step (`exit 0`) |

Counts by primary label (30 rules): `enforced` 14 (rows 1, 3, 4, 5, 7, 9, 10, 11, 12, 13, 20, 22, 28, 29; eight of these carry a `procedural` remainder for part of their scope), `procedural` 13 (rows 2, 8, 14–19, 21, 23–26), `advisory` 2 (rows 6, 30), `planned` 1 (row 27, automation of Run/Drift), `obsolete` 0 rules, though three documents cite a superseded purpose version (mismatch 1).

## Mismatches found

Each is a docs-vs-records or docs-vs-code disagreement, with a proposed fix. None applied.

1. **Stale purpose version in three governing documents.** `AGENTS.md` names `AEC-P0@3` as the current purpose, and `.aec/records.jsonl` holds `AEC-P0` at versions 1, 2 and 3. `CHARTER.md` (line 5), `.specify/memory/constitution.md` (Principle I) and `docs/governance.md` (line 14) still say `AEC-P0@1`. `docs/gates.md` line 97 already notes 17 records pointing at `@1`. CH-035 §6 raised this for AGENTS.md; AGENTS.md was fixed, the others were not.
   *Proposed fix:* cite `AEC-P0@3` (or "the latest version of `AEC-P0`") in CHARTER, constitution and `docs/governance.md`; since the constitution's own Governance section requires a PATCH bump and a recorded decision for wording changes, do it as one decision event. Owner's call whether the `@1` citations in `docs/speckit-log.md` and `docs/use-cases.md` are historical and should stay.
2. **No `v0.5.0` tag although 0.5.0 is described as released.** `pyproject.toml` says `0.5.0`, `CHANGELOG.md` has `## [0.5.0] - 2026-11-04`, `AGENTS.md` says the WP1A commands were "first released in 0.5.0". `git tag` lists only `v0.4.0` and `v0.4.1`. Downstream, relay-kit's and Cognitive-Scaffolding's `telosmith.yml` say "change the ref only to a release >= v0.5.0", which cannot be followed.
   *Proposed fix:* tag the release commit `v0.5.0` (owner action), or reword the CHANGELOG entry and the two downstream comments to "commit" until a tag exists.
3. **AGENTS.md "Built commands" table is incomplete and the count is wrong.** It lists 12 commands and says "Built: the twelve commands above"; `python -m aec --help` registers 14 (`anchor` and `append` are missing from the table). `tests/test_docs_truth.py` checks that named commands exist, not that all registered commands are named, so this passes CI.
   *Proposed fix:* add `anchor` and `append` rows and say "fourteen"; optionally extend `test_docs_truth.py` with a reverse check (every registered subcommand appears in AGENTS.md).
4. **Constitution III says a check without a failing fixture is "planned", never "enforced", but nothing checks that.** Rows 8 and 21–25 are rules the constitution states with MUST that have no test. The gap is between the constitution's standard for *AEC's checks* and the standard applied to *the constitution's own rules*.
   *Proposed fix:* none needed to code; this audit is the honest label. If the owner wants, a `tests/test_governance_claims.py` could assert the two cheapest items: every `specs/*/spec.md` cites an `id@version`, and `constitution.md`'s version string changes only alongside a `.aec/records.jsonl` append (via git diff in `tools/record_touch.py` style).
5. **`record_touch` and the code-impact report run only on `pull_request` events.** A push straight to `main` (owner workflow) bypasses the record-touch gate. Consistent with "only Zach accepts", but worth stating in AGENTS.md so an agent does not assume every `src/` commit on main was gated.
   *Proposed fix:* one sentence in AGENTS.md "Checks" noting the PR-only steps, or run `record_touch.py` on push with `--base HEAD~1`.
6. **CHARTER 4 / CONTRIBUTING "may not edit existing lines" is enforced only when the edit changes id or version.** A rewrite of a line's `text` that keeps `id@version` passes `aec check` (same-id duplicates are a `unique` error only when the content *differs between two present lines*; a single rewritten line has no twin). Only a git-history comparison would catch it, as relay-kit's `relay-kit ledger check --git --base` does for its ledgers.
   *Proposed fix:* add a CI step that diffs `.aec/records.jsonl` against the PR base and fails if any pre-existing line changed or vanished (stdlib: `git diff --unified=0` parsing). Label the rule `procedural` until then.
7. **`.specify/memory/constitution.md` says "the AEC drift checks once they exist" run on every PR.** No drift check exists as a CI step; `code-impact` is report-only (`exit 0`). This is correctly `planned`, but the constitution's Development Workflow reads as if it were part of the gate.
   *Proposed fix:* add "(planned; report-only today)" where the constitution mentions drift checks, as part of the same PATCH bump as mismatch 1.

## What this audit did not do

- It did not read `docs/` beyond the governance-bearing files named above; skill files and spec folders were not audited rule by rule.
- It did not run `tests/test_install.py` (needs network) or the Spec Kit extension test (needs `specify-cli` v1.2.3); CI runs both.
- It did not judge whether any rule is *right*; that is the owner's question. It only asked what would fail if the rule were broken.
