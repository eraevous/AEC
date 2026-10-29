# WP0 implementation intent — 2026-10-29

@ai-intent: Implement frozen spec 003 from repository evidence; preserve authorization boundaries.

## Starting understanding (T001; repository sources only)
- AEC extends specification-driven development with purpose, authority, evidence and versioned criteria (README).
- Records govern purpose and authority; the constitution governs engineering principles (.specify/memory/constitution.md).
- The six built commands are check, impact, edges, code-impact, init and import-purpose (CLI).
- Runtime AEC code is Python standard library only and reports structural findings (constitution).
- WP0 repairs import fidelity and AEC's own documentation/history; the architecture beyond WP0 remains proposed (spec 003).

## Intake and limits

Implementation starts from main's merged PR #12, cfbe10e. The owner corrected an
incorrect initial attachment (HO-20261029-001, a relay-kit pilot) with
HO-20261029-002. The pilot already ran; its untracked scratch/ and outputs/ files
are retained locally and excluded from this feature's commits. The earlier context
cannot be erased, so this is repository-only implementation, not a claim of a
pristine cold implementer. No source chat thread will be fetched or used. The
fresh usability agent will receive repository evidence only.

The corrected handoff requests a summary named handoffs/outputs/HO-20261029-001.md
despite its new ID 002. Follow that explicit path, identifying both IDs in the
summary rather than silently renaming it or overwriting the unrelated pilot.

## Questions, assumptions, discrepancies and rework (append as encountered)

- Q: Does merging proposed architecture authorize later packages? A: no; implement
  WP0 only, no accepted reconstructed decisions, no changes to existing record lines,
  no legacy-code deletion and no merge of the eventual PR.
- Q: Which governing rules apply while replacing inherited AGENTS/CHARTER?
  A: use the constitution and frozen spec's narrower AEC rules; the spec explicitly
  authorizes removal of non-AEC subsystem requirements. Record module-contract
  discrepancies instead of changing purpose files (T016).
- Q: Is an available Data-Guide checkout acceptable for SC-002? A: use a disposable
  copy pinned to its git HEAD; do not mutate the working checkout.

## Verification and authoring cost

Start: 2026-10-29 (UTC timestamps in subsequent entries). Cost is elapsed model
work, not owner attention. Spec Kit is pinned but not required to implement WP0;
no claim of a new analyze/converge run or comparative benefit will be made.

- T002 baseline: 65 tests pass, one optional Spec Kit install/remove test skipped
  (CLI missing); record/edge check 0 errors, 0 warnings. First test attempt failed
  only because the packaging test needed sandbox network permission; rerun with
  network enabled passed. Baseline command output saved in /tmp during the session.
- Import representation choice: keep legacy declared_text semantics (minus cap)
  for compatibility and add declared_raw with the entire exact source text. Keep
  repeated headers as ordered lists in declared_fields while the first declaration
  continues to drive legacy link/intent behavior. This prevents losing repeated
  bottom-of-file Tags without changing which source/intent declaration is primary.
- T003/T004: added singular-prefix, dual-source, structured and >5,000-character
  fixtures; old tests remain the compatibility decoy. New checks fail against the
  old parser as expected, before implementation.

- T005 importer suite: 18 tests pass, including all old assertions. Unknown section
  bodies and the full exact source are retained; nested integration text is kept
  with its parent, and direct section text remains keyed by normalized heading.
- T006 disposable AEC copy: 5 imports, 1 template skipped; exactly 3 code links
  (impact, records, legacy extractor); exactly 2 missing-source findings (driftdiff,
  semantic_chunk). All imported raw text matches source; record check 0 errors.
  Canonical AEC records were not modified by the trial.
- T007 locally cloned Data-Guide at 173c56108a27bf85b1c928a7a9a43b3a96a6f02b,
  isolated from the owner's checkout. 26 imports, 1 template skipped. All 25
  imported files with Inputs/Outputs headings have structured IO; the headerless
  Design_Document has none. Checked every heading/table inventory entry; all full
  text retained and record check 0 errors. The skipped template has IO headings
  but is intentionally not an imported claim, so SC-002's denominator excludes it.
- T008 doc-truth tests written before doc edits: inherited AGENTS fails on missing
  VISION.md and unrelated config. Test fixtures separately prove bad paths and
  unregistered commands fail, while real paths/commands and filename examples pass.
  Backticked bare extension conventions are not repository file references; fenced
  shell filenames are examples, but their command names are still checked.

- T009–T011: root AGENTS is now <120 lines with AEC rules, governing roles,
  commands, checks and visibility limits. Old AGENTS is archived verbatim after a
  historical label; CHARTER defers to the constitution and describes only AEC.
  README and architecture distinguish built, partial and planned capabilities.
- Rework/precision for T008: actual old-doc failures were the fake example intent
  path and backticked Run/Drift, plus README's *external* Data-Guide source path.
  VISION.md was plain prose and thus not matched by the specified backtick rule.
  Removed the old instructions; clarified the external path rather than creating
  a fake local file. Doc checks now only await the real T014 generated artifacts.
- T012: reconstructed 21 one-sentence decisions, including all R1–R6 and D1–D9,
  the historical deleted-obligation rule and T022 reversal, plus Kate review fixes.
  Each input has an exact source quote and section. No source chat is consulted.
- Source discrepancy: research R1's prose suggests unresolved builtins/locals
  are emitted and dropped in the same paragraph. Reconstruct only its stable
  five-edge/no-type-inference decision; current code is the source for behavior.
- Authority discrepancy: historical logs say "provisionally accepted" but that is
  not a new authorization for reconstructed records. All reconstructed decisions
  stay proposed/candidate, including corrections already shipped in the code.
- Architecture status prose had become stale after importer repair; updated only
  implementation-status descriptions, retaining proposed/pending-owner direction.

- T013/T014 reconstruction: five tests written before the script existed (red),
  then passed. They cover candidate provenance, byte-prefix preservation, explicit
  reversals, idempotence, changed-source append versions, acceptance refusal,
  duplicate IDs, authority-field refusal, false quotes/sections and dangling links.
  Canonical run appended 42 records: 21 sources + 21 proposed/candidate decisions.
  Exact source hashes match current source files. Second run appends 0 records.
  docs/decisions-to-confirm.md has an empty owner-confirmation column for each.
- Source stability: finalized the feature-003 log entry before reconstructing
  decisions sourced from that log; do not change it after hashing. Final timing
  and follow-up verification live here to avoid making those source pins stale.
- T015: installed Spec Kit v1.2.3 in a disposable /tmp tool environment, then ran
  all 80 tests with no skips (including extension install/remove and packaging).
  Canonical record/edge check and example record check: 0 errors, 0 warnings.
  CI-equivalent init/import/check on the extended fixture copy: 12 imports, clean.
- Snapshot rework: first manual regeneration command omitted PYTHONPATH and failed
  before writing anything. Reran with PYTHONPATH=src successfully (41 files, 1676
  edges). The unrelated pilot scratch/outputs were temporarily moved aside with
  finally-restoration during extraction so the snapshot describes product files,
  not untracked experiments. No extractor default exclusions were changed.
- T016: left every purpose file unchanged. Two describe nonexistent source modules
  (core.driftdiff, core.parsing.semantic_chunk). aec.records declares dependencies
  "none" despite stdlib imports (possibly shorthand for no external dependencies;
  the declaration does not specify that distinction); its module-name and version
  metadata are historical. aec.impact describes old status vocabulary and
  lists only records despite additional stdlib imports. Neither purpose file lists
  actual callers, which explains reported observed-not-declared findings. The
  legacy extractor's described dependency set also differs from current imports.
  These are candidate contract discrepancies, not authorization to revise them.
- Parser limit: structured IO recognizes Markdown tables, as plan P2 specifies.
  Bullet-form IO declarations (for example core.driftdiff) remain verbatim in raw
  sections/full text rather than inventing a schema for unsupported prose.
- Handoff calibration: no spec change or outside-WP0 work was needed. The fresh
  agent will assess repository usability only; its answers/verdict are candidate
  evidence, not Claude's technical review, Kate's purpose review or Zach's consent.

- Final parser review found that stripping all boundary pipes drops a compact IO
  row whose final description is empty. Added a failing compact-table fixture
  (with a union type containing a pipe), then fixed removal to exactly one boundary
  delimiter per side. Escaped pipes and code pipes are also covered; 19 importer
  tests pass. This is genuine rework after the initial 80-test verification.

- SC-003 fresh agent completed ten repository-only answers, checked against code:
  10/10, recorded in docs/wp0-cold-agent-review.md. I graded these as implementer;
  that is not independent human approval. The source repository copy excluded
  pilot artifacts and no chat threads were provided.
- Fresh-agent finding/rework: frozen question 6 says impact where code-impact is
  needed to synthesize deletion targets/events. The agent correctly qualified it.
  Do not rewrite the frozen questions to improve the score. A second finding:
  current _dependents invalidates evaluations and some necessary relation types
  more broadly than the vocabulary's intended exception. Added a factual known-
  implementation-limit note without changing code semantics, vocabulary or the
  narrower intended invariant. This is a review issue rather than WP1–WP5 work.

## SC-002 per-file inventory (final parser, disposable clone)

Data-Guide revision: 173c56108a27bf85b1c928a7a9a43b3a96a6f02b. Template excluded because it is skipped.

| Imported source | IO heading present | Structured IO rows |
| --- | --- | --- |
| Design_Document.md | no | 0 |
| ast_dependency_cli.purpose.md | yes | 6 |
| bivariate_profiler.purpose.md | yes | 4 |
| combine_scripts.purpose.md | yes | 4 |
| config.purpose.md | yes | 3 |
| data_pipeline.pipeline.purpose.md | yes | 2 |
| data_profiler.purpose.md | yes | 5 |
| data_transform.purpose.md | yes | 4 |
| docs_usage_guide.purpose.md | yes | 2 |
| etl-data_from_pdf.purpose.md | yes | 4 |
| inline_html.purpose.md | yes | 2 |
| main_pipeline.purpose.md | yes | 2 |
| md_to_html.purpose.md | yes | 2 |
| notebooks_ar_and_collections.purpose.md | yes | 3 |
| notebooks_data_munging.purpose.md | yes | 2 |
| notebooks_insurance_plan_profitability.purpose.md | yes | 2 |
| notebooks_scheduling_optimization.purpose.md | yes | 2 |
| notebooks_tighted_ar_collections.purpose.md | yes | 2 |
| pipeline.purpose.md | yes | 4 |
| pipeline_transformed.purpose.md | yes | 2 |
| profiler.purpose.md | yes | 2 |
| profiler_cli.purpose.md | yes | 4 |
| project.purpose.md | yes | 2 |
| reconciliation_plan.purpose.md | yes | 2 |
| run_profiler.purpose.md | yes | 2 |
| typer_cli.purpose.md | yes | 4 |

25 matching IO-heading/structured-IO imports; Design_Document is the headerless decoy.

## Final verification before PR

81 tests pass, no skips, with pinned Spec Kit v1.2.3 and network-enabled packaging
checks. After compact-cell rework, reran AEC/Data-Guide import trials; SC-001 and
25/25 SC-002 counts still hold. Final product snapshot: 41 files, 1681 edges.
Canonical and example record checks: 0 errors, 0 warnings. Existing canonical
records are a byte-for-byte prefix; all 42 new records are proposed reconstructions
and source hashes match current files. Purpose files, legacy code and constitution
are unchanged. git diff --check passes. No WP1–WP5 features were implemented.

Outstanding: external technical review by Claude, purpose review by Kate, and any
owner confirmation of reconstructed history. A pristine cold-implementer condition
cannot be claimed after the owner's handoff correction; the usability agent was
fresh and repository-only. No owner outcome/comparative benefit is established.
