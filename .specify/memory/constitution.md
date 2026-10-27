<!--
Sync Impact Report
- Version change: template → 1.0.0 (initial ratification)
- Principles added: I. Purpose Lives in AEC Records; II. Standard Library, Deterministic, Inspectable;
  III. Checks Are Tested by the Violations They Exist to Catch; IV. Structural ≠ Purpose (claim honesty);
  V. Earn It Against the Baseline; VI. Bedrock Facts Come From the Code
- Sections added: Additional Constraints; Development Workflow; Governance
- Templates requiring updates: none (plan/spec/tasks templates read this file at runtime) ✅
- Deferred TODOs: none
-->
# AEC Constitution

## Core Principles

### I. Purpose Lives in AEC Records (no competing authority)
Purpose, authority by subject, evidence status and criteria versions live in `.aec/records.jsonl`,
in AEC's own record format. This constitution **references** them and does not restate them:
`AEC-P0@1` (purpose), `AEC-R1@1`…`AEC-R4@1` (requirements), `AU-zach@1` (design and acceptance
authority), `AU-speckit@1` (workflow authority). Spec Kit owns the workflow: specs, plans, tasks,
analyze, converge. AEC findings go back into that workflow as review items. AEC MUST NOT rewrite
specs or overrule the owner. A feature spec MUST cite the AEC purpose or requirement it serves by
`id@version`.
Rationale: two documents that both claim authority over purpose is the failure AEC exists to prevent.

### II. Standard Library, Deterministic, Inspectable
Runtime code MUST use only the Python standard library (3.10+). Every command MUST produce the same
output for the same input; ordering MUST be stable so outputs diff cleanly. Records are append-only
JSON lines with `id@version` references. No graph database or service is introduced unless plain
records are shown to be insufficient, and that has to be recorded as a decision.
Rationale: AEC has to run anywhere the code it governs runs, including CI and other people's repos.

### III. Checks Are Tested by the Violations They Exist to Catch (NON-NEGOTIABLE)
Every check or classifier ships with at least one fixture that **violates** it and fails, and at
least one clean decoy that MUST NOT be flagged. Tests come before implementation for each check.
A check without a failing fixture is described as "planned", never as "enforced".
Rationale: over-flagging is a failure too, and an untested enforcement claim is a false claim.

### IV. Structural ≠ Purpose (claim honesty)
Outputs and docs MUST label deterministic results as structural. No document, README or report may
claim that AEC preserves purpose, reduces failures, or beats Spec Kit unless that is backed by a
recorded comparison (`AEC-R2@1`). Decisions are never declared invalid by a tool. They are flagged
for the governing authority.
Rationale: plausible intermediate results presented as justified conclusions are the problem class itself.

### V. Earn It Against the Baseline
A feature's value is judged against a well-configured, pinned Spec Kit workflow given equivalent
information, with authoring and maintenance cost counted (`AEC-R3@1`). Where ordinary Spec Kit
artifacts perform as well, the outcome is to simplify AEC. Each feature records its authoring cost
and what Spec Kit's own `analyze` and `converge` caught, in `docs/speckit-log.md`.
Rationale: AEC is an extension, so it must show an increment.

### VI. Bedrock Facts Come From the Code
Structural facts about a codebase (what defines, calls, imports and refers to what) MUST come from
deterministic static analysis of the code itself, never from model summaries. They are cheap enough
to regenerate on every change. Records and contracts *reference* these facts; they do not copy them.
Rationale: the AST edge graph is the one layer that cannot drift from the code, so everything else anchors to it.

## Additional Constraints

- Spec Kit is pinned (v1.2.3). Integration happens through Spec Kit's extension and hook mechanism
  (`.specify/extensions.yml`), never by editing Spec Kit's core templates or scripts.
- AEC must be installable into another repository (first target: Data-Guide), not copied by hand (`AEC-R4@1`).
- The 2025 Codex++ conventions (`.purpose.md`, `.intent.md`, `AGENTS.md`) remain supported. New
  machinery must not break them.

## Development Workflow

- Spec Kit sequence per feature: `/speckit-specify` → `/speckit-clarify` → `/speckit-plan` →
  `/speckit-tasks` → `/speckit-analyze` → `/speckit-implement` → `/speckit-converge`.
- Alongside each stage, AEC records are appended (purpose links, assumptions, decisions), and
  `python -m aec check` MUST pass before implementation and after convergence.
- Every PR runs the unit tests, `aec check` on `.aec/records.jsonl` and on the examples, and the AEC drift
  checks once they exist. A PR that adds a subsystem includes a dissent review: what it might violate,
  the evidence for and against, what follows if the concern is right, and what to test.

## Governance

This constitution supersedes ad-hoc practice for this repository. Amendments require a recorded
decision event approved by `AU-zach@1`, with a semantic version bump: MAJOR when a principle is removed
or redefined, MINOR when one is added or materially expanded, PATCH for wording. Purpose changes are
made in `.aec/records.jsonl` as new record versions with a `supersedes` relation. Earlier versions are
never edited. Every PR review verifies compliance with Principles I–VI. Unjustified complexity is a
review finding.

**Version**: 1.0.0 | **Ratified**: 2026-10-26 | **Last Amended**: 2026-10-26
