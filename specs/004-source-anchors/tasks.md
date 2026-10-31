# Tasks: source anchors and retrieval (WP-S)

Spec 004 is frozen. Implement in order; tests first, each check/classifier with a
violating fixture and a clean decoy. Keep the dated intent note throughout.

## Setup
- [X] T001 Write plan/tasks and WP-S intent; record authorization clarification, base and interpretations.
- [X] T002 Confirm baseline suite and canonical record/edge checks.

## US1/US4: anchor shape, integrity and rationale
- [X] T003 Add synthetic fixture metadata for every frozen case; generate sources only in temporary directories.
- [X] T004 Write failing shape/state tests: all five states, malformed fields, every record type, rationale separation, confinement and legacy decoys.
- [X] T005 Implement offline source context/inspection and integrate errors/warnings into records.check without propagation changes.
- [X] T006 Add check CLI root resolution/state reporting; verify deterministic output and error exit behavior.

## US2: record-directed passage retrieval
- [X] T007 Write failing show tests: inclusive ranges, first single-line exact quote, context, warnings, missing/unavailable suppression, truncation and invalid arguments.
- [X] T008 Implement show and thin CLI dispatch with bounded, labelled read-only output.

## US3: fallback search
- [X] T009 Write failing search tests: unindexed fact, literal/regex, stable ordering/limits/omitted count, current hashes and record associations, selected roots, escaped symlinks and no network/execution.
- [X] T010 Implement direct configured-root search and CLI dispatch; no index or provider.

## Verification and documentation
- [X] T011 Add output-template/doc-truth checks for SC-4; document raw-byte hashes, root/default/limit behavior, optional rationale and source access limits.
- [X] T012 Run frozen-case suite and full regressions, verify deterministic/read-only behavior and unchanged prior records/propagation; regenerate .aec/edges.jsonl and check canonical/example records.
- [X] T013 Finish intent with wall time, tokens if available, spec issues and dissent; commit/push to existing branch, no new PR or merge. Return result for claude:aec to file.
