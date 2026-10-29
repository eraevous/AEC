# Feature Specification: AEC reconciled with itself (WP0)

**Feature Branch**: `speckit/003-self-reconciliation` (to be created by the implementer)
**Created**: 2026-10-28
**Status**: Frozen for implementation
**Serves**: `AEC-P0@1`, `AEC-R1@1` (no competing authority), `AEC-R2@1` (claim honesty), `AEC-R7@1` (adoption by import)
**Roles**: specified by Claude (AEC); **implemented by Codex**, cold, from this repository only; technical review by Claude; purpose review by Kate; decisions by Zach.
**Input**: AEC coordination thread "Synthesize Compare AEC Documentation", rounds 0–1 (2026-10-28). Kate's gap analysis was checked against `main@9524a24` by Claude; Kate's round-1 review set the scope. Architecture context: `docs/architecture.md`. Evaluation design: `docs/failure-modes.md`.

## Why this comes first

AEC contains the drift it exists to catch:
- its agent instructions describe another project;
- its importer drops fields that AEC's own purpose files use;
- its decision history lives outside its records.

Every later work package (commit-addressed topology, `aec context`, reconciliation) delivers repository knowledge to agents. That knowledge has to be true first.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - An arriving agent learns the truth from the repo (Priority: P1)

An agent with no conversation history opens AEC and reads `README.md` and `AGENTS.md`. It can correctly state:
- what AEC is for;
- which commands exist;
- that it has no runtime dependencies;
- where purpose and authority live;
- how to run the checks;
- what AEC does not yet do.

Nothing it reads describes a different project or points at a file that doesn't exist.

**Why this priority**: every agent, including the one implementing this feature, starts here. Wrong operating instructions are the most expensive kind of drift.

**Independent Test**: a fresh agent answers `cold-agent-questions.md` using only the repository. A reviewer grades the answers against the code. Automated doc-truth tests pass.

**Acceptance Scenarios**:
1. **Given** `AGENTS.md`, **When** every file path and `python -m aec <command>` it mentions is checked, **Then** each path exists and each command is a real subcommand.
2. **Given** `README.md`, `AGENTS.md`, `CHARTER.md` and the constitution, **When** they are read together, **Then** they state one consistent rule for what governs which question: records govern purpose and authority; the constitution governs engineering principles; `AGENTS.md` governs agent behaviour; purpose files are semantic contracts whose claims are candidates; intents are provisional reasoning; generated edges are structural facts.
3. **Given** the inherited Cognitive-Scaffolding rules (Typer, FAISS, S3, Retriever, embeddings), **When** the documents are read, **Then** none of them is presented as an AEC requirement. Inherited material that is kept is labelled as history.

---

### User Story 2 - Old purpose files import without losing their contracts (Priority: P1)

The developer imports Codex++ purpose files from AEC itself, Data-Guide and similar repositories. Every structured field survives the import:
- source files, in singular or plural form;
- role, version, used-by and downstream;
- risks, coordination and cadence;
- declared inputs and outputs;
- dependencies, integration notes and test guarantees.

The full declared text is preserved. The code link is made for singular `@ai-source-file` exactly as for the plural form.

**Why this priority**: today six purpose files (including AEC's own `aec.impact` and `aec.records`) import with no code link, and text over 4,000 characters is silently cut. A reconciliation layer (WP3) cannot compare a declared contract that was never imported.

**Independent Test**: import AEC's own purpose files and the existing fixture repo. Check that the expected fields, links and full text are present and that the previous behaviour is unchanged on the existing fixtures.

**Acceptance Scenarios**:
1. **Given** a purpose file using `@ai-source-file: src/aec/impact.py`, **When** imported, **Then** the claim links to `code:src.aec.impact`.
2. **Given** a purpose file with an Inputs & Outputs table, Risks, Dependencies, Integration and Test Guarantees sections under any of the observed heading variants, **When** imported, **Then** each is stored as structured data on the imported claim (declared IO rows, risks, dependencies, integration, guarantees), with the original text kept verbatim.
3. **Given** a declaration longer than 4,000 characters, **When** imported, **Then** nothing is truncated at ingestion. Display limits belong to the views that render it, and any shortening there is labelled.
4. **Given** the existing `tests/fixtures/purpose_repo`, **When** imported, **Then** all findings and records from feature 002 are unchanged, apart from new fields being added.
5. **Given** a field the importer does not recognise, **When** imported, **Then** it is kept as raw `declared_fields` rather than dropped.

---

### User Story 3 - AEC's own history is in its records, honestly labelled (Priority: P2)

The decisions made while building AEC (feature 001's design decisions R1–R6, feature 002's D1–D9 and T022, Kate's review corrections) are recorded in `.aec/records.jsonl`. Each one is a **reconstructed, candidate** record linked to the source artefact (path and content hash) it was reconstructed from. A generated list names the ones Zach must confirm before any can become committed.

**Why this priority**: the reasoning exists but sits outside the reasoning model. Importing it is also the first real test of whether records can carry a project's history. Reconstructing it is not the same as authorization (Kate, round 1), so nothing imported may look accepted.

**Independent Test**: after the import, `aec check` passes. Every reconstructed record has `origin: reconstructed`, a source link and no `accepted` status. `docs/decisions-to-confirm.md` lists each one with an empty confirmation column.

**Acceptance Scenarios**:
1. **Given** a decision described in `docs/speckit-log.md` or a feature plan, **When** it is reconstructed, **Then** the record names its source file, the source's sha256 and the section, and its status is `proposed`.
2. **Given** reconstructed records, **When** `aec check` runs, **Then** no authority error appears, because none claims acceptance.
3. **Given** a decision that was later reversed (for example, feature 001's "a requirement whose implementing code is deleted is unjustified", reversed by T022), **When** it is reconstructed, **Then** both the original and the reversal are present, linked by `supersedes`.

---

### User Story 4 - The repo says where it is going without claiming it is there (Priority: P3)

`README.md` and `AGENTS.md` point to `docs/architecture.md` (proposed direction) and `docs/failure-modes.md` (evaluation design). Each capability is labelled `built`, `partial` or `planned`, and the labels match the code.

**Independent Test**: every capability that the docs mark `built` maps to a command or module that exists, and every `planned` one maps to nothing yet.

## Edge Cases

- A purpose file has both singular and plural source fields: the union is used and the duplicate is reported.
- A source field lists a path relative to a package directory (`semantic_chunk.py`) while the module lives under `src/core/parsing/`: the existing resolution rules apply (unique basename, or ambiguous, or missing). No guessing.
- Purpose files describing legacy modules (`src/core/*`, inherited from Cognitive-Scaffolding) are imported like any other. Whether that legacy code stays is a decision for Zach, recorded as an open question, not made by the implementer.
- The `VISION.md` reference: resolve it by pointing to what exists (`README.md`, the `AEC-P0` record, the white paper, `docs/architecture.md`). Do not create a new governing document.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The importer MUST accept `@ai-source-file` and `@ai-source-files` (header lines with or without a leading `-` or `#`).
- **FR-002**: The importer MUST store recognised structured content: `declared_io` (direction, name, type, description rows), `declared_risks`, `declared_dependencies`, `declared_integration`, `declared_guarantees`, and every `@ai-*` header in `declared_fields`. Heading variants seen in the AEC and Data-Guide purpose files (emoji or none; "Intent & Responsibility" / "Responsibilities"; "Inputs & Outputs" / "Inputs" + "Outputs"; "Risks" / "Risks & Edge Cases" / "Dialogic Notes & Risks"; "Dependencies" / "Dependencies & Coordination"; "Integration & Coordination" / "Pipeline Integration"; "Test Guarantees") MUST be recognised.
- **FR-003**: The importer MUST NOT truncate at ingestion.
- **FR-004**: Import behaviour from feature 002 MUST be preserved: provisional, candidate-tier, never authority, idempotent, append-only, report-never-correct. New fields are additive.
- **FR-005**: `AGENTS.md` MUST be rewritten for AEC. It is an operating guide for agents in this repo, short enough to read on arrival, and it states:
  - commands and checks;
  - the governing-documents rule (US1-2);
  - Run/Drift as AEC uses it today;
  - what is built vs planned;
  - Zach's authority.

  The inherited Codex++ protocol moves to `docs/history/` (or equivalent), labelled as history.
- **FR-006**: `CHARTER.md` MUST state AEC's actual engineering rules, consistent with the constitution: stdlib only, thin argparse CLI, deterministic output, report-only, append-only records, and checks tested by violation and decoy. It may instead defer to the constitution explicitly. It MUST NOT keep rules for subsystems AEC doesn't have.
- **FR-007**: Doc-truth tests MUST fail if `README.md` or `AGENTS.md` mentions a repository path that doesn't exist or an `aec` subcommand the CLI doesn't have.
- **FR-008**: The decisions in `docs/speckit-log.md`, `specs/001-*/plan.md`/`research.md` and `specs/002-*/plan.md`/`tasks.md` MUST be reconstructed into records:
  - each has `origin: reconstructed`, `status: proposed` and a `source` record with path and sha256;
  - reversals are linked by `supersedes`;
  - a `docs/decisions-to-confirm.md` table is generated from the records.
- **FR-009**: `.aec/records.jsonl` stays append-only. Existing lines MUST NOT change.
- **FR-010**: The implementer MUST write `codex_++/intents/<date>__wp0-implementation.intent.md` recording every question it had, every assumption it made to proceed, every place the spec or repo was unclear or wrong, and the rework it did. This is calibration data for the handoff process (Kate, round 1), and it matters as much as the code.
- **FR-011**: All existing tests MUST still pass. Every new behaviour gets a violating fixture and a decoy (Constitution III).

### Key Entities

- **Imported purpose claim (extended)**: feature 002's claim plus `declared_io`, `declared_risks`, `declared_dependencies`, `declared_integration`, `declared_guarantees` and `declared_fields`.
- **Reconstructed decision**: a `decision` record with `status: proposed`, `origin: reconstructed`, `depends_on` its `source` record (path, sha256, section) and optionally `supersedes` an earlier reconstructed decision.

## Success Criteria *(mandatory)*

- **SC-001**: Importing AEC's own purpose files links the 3 whose named source exists (`aec.impact`, `aec.records`, `core.tools.ast_dependency_extractor`). The 2 whose source is gone (`core.driftdiff` → `src/core/driftdiff.py`, `core.parsing.semantic_chunk`) are reported as `missing-source`. That is itself a finding: AEC documents modules it no longer has. The template is skipped, and zero declared text is truncated.
- **SC-002**: On the Data-Guide purpose files, the number of imported claims with a non-empty `declared_io` equals the number of files with an Inputs/Outputs section (the reviewer counts these by hand).
- **SC-003**: The doc-truth tests pass. A fresh agent answers at least 9 of the 10 `cold-agent-questions.md` correctly from the repository alone (graded by the reviewer against the code).
- **SC-004**: At least 15 reconstructed decisions are present, 100% with source links and none `accepted`. `aec check` reports 0 errors.
- **SC-005**: The intent note exists and lists at least the questions and assumptions the implementer actually had. An empty list is suspicious: say so if there truly were none.

## Out of scope

Commit-addressed snapshots, topology analytics, `aec context`, reconciliation packets, drift triggers and handoff checks (WP1–WP4). Any change to the record vocabulary beyond the import fields above. Deciding the fate of `src/core/*` legacy code.

## Assumptions

- The implementer has this repository and its history. It does not have the chat threads. Anything it cannot determine from the repository is recorded as a question in the intent note, not guessed.
- The Data-Guide repository (`eraevous/Data-Guide`, public) can be cloned for SC-002. If it can't, record that and use AEC's own files and fixtures only.
