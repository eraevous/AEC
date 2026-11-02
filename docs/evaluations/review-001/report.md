# review-001 report (GitHub Copilot, 2026-11-01)

Verbatim as Zach received it. Dispositions are in `../review-001.md`.

I’ll reconstruct the documented model and inspect the implementation/tests without modifying tracked files, then validate any suspected defects with isolated, non-destructive checks.

The architecture is deliberately report-only and distinguishes source/code structure from justification and authority. The biggest validation risk is whether the implementation preserves those distinctions across record checking, change propagation, and snapshots; I’m tracing those paths against their governing specs now.

The documented suite passes, but the canonical record check was blocked because `.aec/edges.jsonl` is intentionally absent/ignored in this checkout. I’ll regenerate the snapshot only under `/tmp`, then probe two integrity invariants that the docs describe as formal checks.

The additional probes confirmed two concrete integrity gaps: malformed record metadata is accepted, and a valid-but-colliding Python package/module layout silently loses call edges. A controlled mutation between the extractor’s two passes also produced an internally inconsistent snapshot; I’m treating its real-world likelihood separately from the reproducible behavior.

## A. System reconstruction

AEC addresses a gap between code behavior and the reasons people recorded for it: tests and static analysis can show what changed, but not which requirements, claims, or decisions relied on the prior state. Its governing rule is that structural findings prompt review; they do not establish semantic truth, purpose achievement, or authorization. The constitution requires standard-library Python, deterministic and inspectable outputs, append-only records, and tests with both violating fixtures and clean decoys.

The implementation keeps several representations distinct:

- **Reasoning records** in `.aec/records.jsonl` capture purposes, requirements, claims, evidence, decisions, authorities, and explicit relations between them. Records are versioned by `id@version`; `check` validates selected invariants, and `impact` classifies effects of record-change events.
- **Code topology** comes from Python AST extraction. `snapshot` and `diff` identify revisions and extraction methods; `code-impact` connects changes to records that explicitly reference changed code. `reach`, `fan`, and `unresolved` report structural queries with visibility limits.
- **Purpose-file imports** preserve declared contracts as provisional claims and report differences from observed callers. Source anchors and search check local artifact integrity and retrieve passages; they do not establish meaning or authority.
- **Spec Kit integration** is an optional, report-only extension. There is no automated drift loop, context briefing, semantic reconciliation, or handoff premise check yet.

The distinction between **built, partial, and proposed** is generally clear in `AGENTS.md` and `docs/architecture.md`. Important limits are also explicit: static Python analysis misses dynamic calls and other languages; records must be authored; authority is claimed rather than authenticated; evidence adequacy and applicability are narrow; and a passing check is not semantic validation.

One status ambiguity remains: the architecture document describes WP0 and WP1A as awaiting merge/review or release, while the agent guide describes their commands as built. These can both be true—implementation and release status differ—but the dated status table is not a current, authoritative project-state mechanism. Claims that decisions or architectures were approved also rely partly on private sources I could not inspect.

## B. Implementation assessment

**What works well:** The separation between code edges and justificatory relations is coherent and consistently documented. Commit snapshots identify their extraction method; reachability is projection-specific and carries visibility caveats; unresolved calls remain visible instead of being guessed. The source-anchor design distinguishes unavailable, missing, mismatched, and verified artifacts without pretending that a hash validates a claim. The code-impact rules also preserve important distinctions: deleting an implementation does not delete the obligation, and decisions are flagged for a human rather than invalidated by the tool.

**What is incomplete:** The system mostly tracks relationships that users explicitly record. It does not infer missing rationale, determine whether evidence is relevant, or automate reconsideration. Its authority checks confirm that a named authority record governs a subject, not that the person actually approved the decision. Those limits are intentional, but they mean AEC’s central value depends on careful record authoring and human review.

**Validation:** `PYTHONPATH=src python3 -m unittest discover -s tests -v` ran 161 tests successfully, with one optional Spec Kit install/remove test skipped because `specify` was unavailable. The documented check against `.aec/edges.jsonl` initially could not run because that ignored snapshot was absent. I generated edges to `/tmp` instead: 3,365 edges from 57 files, with 2 skipped; the repository records check reported 0 errors and 13 warnings, and the MtG example check reported 0 errors and 0 warnings. The warnings were anchor states—11 unavailable external/private sources and 2 digest mismatches—not proof that the underlying claims are wrong. The worktree remained unchanged. These checks establish structural behavior only, not semantic correctness or user benefit.

## C. Findings

| # | Severity | Confidence | Likely impact | Finding |
|---|---|---:|---|---|
| 1 | Medium | 10/10 | Medium | Record validation accepts malformed identity and prospective-freeze metadata. |
| 2 | Medium | 10/10 | Low–medium, layout-dependent | Same-named package and module files collide, silently losing call edges. |
| 3 | Medium | 10/10 for the pilot result | Strategic | The available outcome evaluation shows no incremental benefit on its tested tasks. |
| 4 | Low | 10/10 for reproduction; real-world frequency unknown | Low–medium | A changing working tree can produce a snapshot assembled from two different file states. |

**1. Malformed record metadata passes formal checks.** `Store.load` converts `version` with `int()` (`src/aec/records.py:64-74`), so a record with `version: 1.9` is silently loaded as version 1. Separately, `check` only tests whether `frozen_sha256` is truthy (`records.py:185-186`); a prospective claim with `"frozen_sha256": "not-a-sha256"` produces no error. I reproduced both cases with temporary record files; each returned no validation errors. The documented contract says versions are integers and prospective claims reference a frozen source (`docs/reasoning-vocabulary.md:27, 33, 121-123`). **Consequence:** malformed version identity can be normalized into a different record reference, and a fabricated freeze marker can pass a check intended to distinguish prospective evidence. **Remediation:** validate exact JSON types and allowed ranges before constructing records; validate hash format and the frozen-source reference required by the record contract. **Uncertainty:** a syntactically valid digest still does not authenticate consent or prove that its source is meaningful; the documentation correctly treats those as separate questions.

**2. A module-name collision drops topology without warning.** `_module_name` maps both `foo.py` and `foo/__init__.py` to `foo` (`src/aec/edges.py:46-49`); loading the second overwrites the first in `self.modules` (`edges.py:138-140`). Body scanning then visits only retained modules (`edges.py:439-441`), and the header reports only that one file for the module (`edges.py:559`). In a temporary fixture containing both files, the snapshot listed definitions from each but emitted calls only from `foo.py`; the call in `foo/__init__.py` was absent and no skipped/ambiguity warning identified it. **Expected:** represent this ambiguity or report it explicitly. **Actual:** a plausible topology with silent omissions, weakening reachability and caller lists. **Remediation:** detect duplicate module identities and mark/report the ambiguity rather than silently overwriting. **Uncertainty:** the layout is uncommon, and Python’s own import resolution may select one file in a given execution context; that does not make the other file’s omission safe to present as a complete snapshot.

**3. The current pilot does not demonstrate incremental value.** The pre-registered probe found all trials successful in all conditions, no task where the relevant briefing beat repository-only access, and no qualifying cost reduction (`docs/evaluations/probe-001-results.md:14-16`). All agents found the dependency; on T1 the relevant briefing itself said no resolved callers, while the actual call remained unresolved (`probe-001-results.md:71-84`). The README accurately reports this result (`README.md:103-108`). **Expected:** evidence that AEC’s structural information adds value beyond ordinary repo access. **Actual:** no signal on these tasks, with higher briefing token use on two of three. **Consequence:** the system’s added user value remains unproven, not disproven. **Remediation:** test against harder cases and an information-matched baseline before investing further in context delivery. **Uncertainty:** this was a small, single-model pilot with two trials per cell, tasks known to be easy to search, and no properly configured Spec Kit comparison.

**4. Mutable-tree extraction can mix versions of a file.** The extractor hashes and indexes source during its first pass (`src/aec/edges.py:128-140`) and reparses files for body scanning (`edges.py:439-441`). I used an isolated temporary fixture and changed a file after its first parse. The resulting snapshot defined `demo.old` but contained a call from `demo.new`, which was in neither that definition set nor the hashed first-pass content. **Expected:** a coherent snapshot or an explicit indication that input changed during extraction. **Actual:** a structurally inconsistent working-tree result. Commit-addressed extraction is less exposed because it materializes immutable revision contents; the concern is primarily concurrent edits during working-tree extraction. **Remediation:** detect content changes between passes and fail/retry, or ensure both passes consume identical content. **Uncertainty:** I established the behavior under a controlled mutation, not how often ordinary use encounters it.

## D. Architectural dissent

The clearest challenge is whether AEC’s graph and record machinery is worth its authoring and maintenance cost. The pilot offers no positive outcome signal, and the main reasoning graph only acts on explicit, maintained links. Ordinary search, tests, version control, and Spec Kit may be sufficient for many changes. **Against abandoning it:** the pilot does not cover cases where search is ineffective, weaker agents, large systems, or dynamic/cross-language dependencies; it also does not test the value of provenance and authority distinctions separately from graph briefings.

The extractor’s narrow constructor-local inference is another tradeoff worth revisiting. `docs/evaluations/resolver-001.md` reports 25 of 874 unresolved calls resolved correctly, with about a 20% extraction-time increase. The probe’s missed caller was among those resolved. This is a real improvement in the structural data, but its effect on agent decisions remains untested. **Against removing it:** the fix was narrowly scoped, hand-checked for precision, and addresses a common pattern; removing it could discard useful topology. Measure whether downstream users act on those edges before expanding the inference rules.

I would not replace append-only JSONL with a database or add a service based on this evidence. The current representation is inspectable and keeps meaning, structure, and authority separate. The more urgent architectural question is not infrastructure; it is whether users can maintain the records accurately enough, and whether AEC changes decisions enough to justify that work.

## E. Recommended next experiments

1. **Adversarial record-invariant fixtures.** Add invalid and clean-decoy records for fractional/boolean/zero versions, malformed hashes, and broken frozen-source references. Establish exactly which invariants `check` promises to enforce and verify both rejection and decoy behavior.
2. **Extractor ambiguity and mutation tests.** Freeze fixtures for `foo.py` plus `foo/__init__.py`, and for mutation between extraction passes. Decide whether AEC should fail closed, retry, or report incomplete topology; ensure the result cannot look complete when it is not.
3. **A stronger, matched-value probe.** Pre-register a small evaluation with genuinely difficult dependency discovery, relevant and irrelevant briefings, repository-only access, and the same purpose information supplied as ordinary prose. Measure preservation outcomes, false alarms, token/call cost, and whether agents relied on the information—not just whether they mentioned it.

## F. Self-assessment

**Established directly:** the documented architecture, feature specs, code paths, tests, current CLI outputs, the two record-validation gaps, the package/module collision, and the two-pass mutation behavior. The test suite and record checks establish repeatability and structural invariants only; they do not establish that AEC preserves purpose or improves development outcomes.

**Inferred:** that the collision and concurrent-edit behaviors could affect users’ topology results. Their practical frequency and downstream consequences were not measured. The pilot’s no-signal result is direct evidence about its tested tasks, not a general estimate of AEC’s effectiveness.

**Could not verify:** private coordination records, actual owner consent behind recorded approvals, external source artifacts unavailable in this checkout, real-world record-authoring cost, or usefulness to human teams. The repository itself reports that some cited sources are private or not measured.

**Instructions that shaped the review:** repository guidance established the intended authority boundaries, required reading the constitution and relevant specs, and cautioned against treating structural checks as semantic proof. The user’s constraints were followed: no tracked files were changed, and all experiments used temporary files outside the repository.