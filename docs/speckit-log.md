# Spec Kit + AEC log

A running record (Constitution V) of building AEC with a pinned GitHub Spec Kit, with what each
layer caught. It doubles as a learning record of how Spec Kit actually behaves.

## Feature 001: AST bedrock + AEC as an installable Spec Kit extension (2026-10-26)

Driver: the AEC Claude, under Zach's delegation. Spec Kit `specify-cli` v1.2.3, pinned (`uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@v1.2.3`).

### Setup lessons
- `uv tool install … spec-kit.git` with no tag installs a **dev build** (`1.2.4.dev0`). Pin a tag, as the white paper says.
- `specify init --here --force --non-interactive --integration claude` installs the commands as **Claude skills** (`.claude/skills/speckit-*`). The command names are `/speckit-specify` and so on, with hyphens; the docs use `speckit.specify`.
- Every core command checks `.specify/extensions.yml` for `before_*` and `after_*` hooks. Core extensions use `extension.yml` (schema 1.0) with `provides.commands` and `hooks`. **That is AEC's integration point.** No fork is needed.
- `specify init` defaults to `feature_numbering: sequential`. Spec directories are `specs/NNN-name`, independent of the git branch.

### Stage log
| stage | what Spec Kit produced or did | AEC alongside | minutes (approx.) |
|---|---|---|---|
| constitution | resolved the template; I filled 6 principles, governance and versioning | constitution **references** `.aec/records.jsonl` (`AEC-P0@1`, `AEC-R1..R4@1`, `AU-zach@1`); `aec check` = 0 errors | 10 |
| specify | spec + quality checklist; 1 validation fix (SC-002 had no size anchor) | spec header cites `AEC-P0@1`, `AEC-R1@1`, `AEC-R4@1` | 12 |
| clarify | designed as interactive (one question at a time to the user). Under delegation I answered 3 with defaults, marked overridable | n/a | 4 |
| plan | plan, research (R1–R6), data model, contracts, quickstart; constitution gate table | verified the extension schema against the installed package rather than from memory | 15 |
| tasks | 26 tasks, by user story, tests first | n/a | 6 |
| analyze | see below | see below | 6 |
| implement | 27 tasks, tests first. 1 fixture label corrected (unresolved targets name the callee expression); 1 vocabulary addition (`implemented_by`) | `aec check --edges` on AEC's own records: 0 errors. AEC-R5/R6 link requirements to code | 55 |
| converge | 6 findings → tasks T028–T033 (see below); then implemented | the stale-install finding came from *running* the package, not reading the code | 20 |

### analyze report (read-only pass, before implementation)
| ID | category | severity | location | finding | remediation |
|---|---|---|---|---|---|
| A1 | traceability | MEDIUM | tasks.md | No task cites an FR id. Coverage of FR-001..FR-010 can only be inferred (SC-001..005 are cited) | add explicit FR refs to tasks |
| A2 | coverage | HIGH | FR-001 / T004 | the `references` edge kind has no positive test (SC-001 and T004 cover 4 of 5 kinds) | extend T004 |
| A3 | constitution II | HIGH | FR-005 | "stdlib only" is a MUST with no task enforcing it | new test task T027 |
| A4 | edge cases | LOW | spec Edge Cases / T001 | duplicate function names across modules, `import *`, and function-local imports are listed but not in the fixtures | extend T001 |
| A5 | testability | LOW (accepted) | FR-008 | "hooks never modify Spec Kit artifacts" depends on agent behavior when a hook runs. It can't be fully unit-tested; T018 checks only core templates | command files state read-only explicitly; test the manifest and remove-cleanliness only |

Coverage: 11/11 FR and 6/6 SC have at least one task (A1 explicit after fix). Constitution: no violations; A3 was missing enforcement.

**Where AEC overlaps:** A1 is exactly what AEC's "references resolve" check is for. Spec Kit's analyze found it by *inference*, as its instructions direct. AEC would make it *mechanical* if tasks carried `FR-xxx` ids as references. That is a candidate AEC feature (traceability ids in tasks), logged here and not built.

### converge report (after implement)
| ID | gap | severity | source | finding |
|---|---|---|---|---|
| F1 | contradicts | MEDIUM | FR-009, Constitution II | `pip install` shipped the legacy top-level `core` package (pandas/typer code under a generic name). Fixed: packaging includes `aec*` only, plus an install test |
| F2 | missing | MEDIUM | FR-009 | no automated install test. Added `tests/test_install.py` (clean venv, `python -m aec edges`, asserts `core` is absent) |
| F3 | partial | MEDIUM | FR-010 | this log lacked the implement and converge sections. Fixed here |
| F4 | partial | LOW | data-model | snapshot header lacked `root`. Added |
| F5 | missing | LOW | spec Edge Cases (large repos) | first measurement on stdlib + site-packages (9,884 files, 1.08M edges): 176 s, **5.8 GB**. Refactored to parse each file twice and keep only an index: 186 s, **3.2 GB**, warnings suppressed. Data-Guide output byte-identical. Also fixed a latent naming mismatch for classes defined inside functions |
| F6 | unrequested | LOW | plan R5 | manifest `category`/`effect` fields not in the contract. They follow core extension convention; documented |

Re-check: all 33 tasks are satisfied by the code. Converged.

### Results against the spec
- SC-001: fixture, 5/5 edge kinds exact. SC-002: Data-Guide ~0.2 s (target < 2 s). SC-003: byte-identical runs.
- SC-004: code-impact fixtures. Changed symbol → requirement/claim `stale`, decision `needs_review`. Deleted → `unjustified`. Decoy unchanged.
- SC-005: Spec Kit init + AEC extension install into Data-Guide ≈ 1 s. A real install/remove into a fresh Spec Kit project is tested.
- 36 tests (one install test can be skipped with `AEC_SKIP_INSTALL_TEST=1`).

### What Spec Kit caught vs what AEC caught (this feature)
| caught by | finding |
|---|---|
| Spec Kit **analyze** (inference over spec/plan/tasks) | missing FR traceability in tasks (A1); an edge kind with no test (A2); a constitution MUST with no enforcing task (A3); edge cases missing from fixtures (A4) |
| Spec Kit **converge** (code vs artifacts) | the packaging contradiction, the missing install test, the incomplete log, the header field, the unmeasured edge case |
| **AEC** (`aec check --edges`) | in the Data-Guide trial, a dangling code reference. On this repo, nothing (records were written alongside the code) |
| neither | the large-tree memory problem only appeared because converge forced a *measurement* of a spec edge case |

**Honest read:** on a feature built by one agent in one sitting, Spec Kit's analyze and converge did most of the catching. AEC's distinctive value (change impact across *later* changes, and authority/revision distinctions) doesn't show up in a single feature's first build. It needs the Data-Guide overhaul, where records exist *before* the code changes. That is the comparison to run next.

### Lessons for using Spec Kit (for Zach)
1. **Pin the version.** The untagged install is a dev build.
2. **The commands are prompts, not programs.** `/speckit-*` skills instruct the agent. Quality depends on the agent following them, and analyze/converge are only as good as the reading. They were genuinely useful here.
3. **clarify expects a human.** Under delegation it turns into "agent answers its own questions". Mark those answers as such.
4. **Converge's rule "completion claims are not evidence"** is the most AEC-like part of Spec Kit: it ignores checkboxes and re-reads the code. Running things (an install, a big tree) found more than reading did.
5. **Extensions and hooks are the integration seam.** `extension.yml` + `.specify/extensions.yml`. No fork needed.
6. Candidate AEC features found along the way: mechanical FR→task traceability (A1); streaming edge output for very large repos.

**Total authoring time, feature 001:** ~3 hours of agent time across constitution → converge.


## Feature 002: AEC adoptable on a real repository (2026-10-27)

Driver: the AEC Claude. Scope from Kate's AEC round 3 (her ranking: A init, B import-purpose, E invariant, C outcome sufficiency, D narrow applicability; F blind cases after freeze; G Spec Kit replay = feature 003), under Zach's go-ahead ("move on to the next chunk", AEC "pretty well buttoned up" before Data-Guide).

Before the feature, two defects from Kate's PR #8 review were fixed on the PR #8 branch, tests first: a directly retracted dependency could mark a **decision** `unjustified`; `contradicts` was inert (new change kind `add` → `contested`).

### Stage log
| stage | Spec Kit | AEC alongside | minutes (approx.) |
|---|---|---|---|
| plan with Kate | n/a (ChatGPT AEC thread, round 3) | her acceptance gate became the spec's success criteria | 10 |
| specify | spec + checklist, 1 validation fix (FR-011 contradicted shipped behaviour: deleted implementing code is `unjustified`) | spec cites `AEC-R4@1`, `AEC-R2@1`, `AEC-P0@1` | 12 |
| clarify | skipped: no marker met the "no reasonable default" bar; Kate's round 3 had settled the open choices | n/a | 0 |
| plan / tasks | 7 design decisions, 16 tasks, tests first | n/a | 10 |
| analyze | 3 findings (below) | n/a | 4 |
| implement | 16 tasks; 3 fixes surfaced by the Data-Guide run | AEC-R7, AEC-R8 appended, linked to code; `check --edges` 0 errors | 70 |
| converge | 5 tasks (T017–T021) | n/a | 15 |

### analyze (self-run, before implementation)
| ID | severity | finding | remediation |
|---|---|---|---|
| A1 | HIGH | FR-011 said code changes yield review statuses only, but feature 001 makes a requirement whose implementing code is deleted `unjustified` | FR-011 now states the exception (explicit necessary link to deleted code) |
| A2 | MEDIUM | D5 left open whether evidence with no `evidence_kind` counts as conformance; counting it would warn on every legacy record | decided: unknown is not conformance; decoy test added |
| A3 | LOW | the CI snippet installs from `@main`, while the constitution pins versions | the snippet's first line says to pin a reviewed ref; no release tag exists yet |

### converge (after implementation): what the real repo caught
Running `init` + `import-purpose` on Data-Guide, not reading the spec, produced three of the five converge tasks:
- **Source-root imports** (T017). Data-Guide imports `src/data_profiler.py` as `data_profiler`. All three real callers of `data_profiler` were invisible, so SC-003 (hand-verified caller findings) could not have passed. A fixture-only build would have shipped this.
- **Wrong module for a file** (T018). The first module map took symbols from `defines` edges, so `data_profiler.py` mapped to its class `TypeResolver`. The header now carries a real module→file map.
- **Function-local imports** (T019) were attributed to the function, not the module, which hid the `data_profiler` ↔ `bivariate_profiler` import cycle.

### Spec Kit vs AEC, this feature
- Spec Kit's analyze-style pass caught a spec that contradicted shipped behaviour (A1). That is a cross-artifact consistency problem, squarely Spec Kit's job.
- AEC's distinctive contribution showed up on the *target* repo, not this one: on Data-Guide, `import-purpose` turned 26 old purpose files into 34 concrete declared-vs-actual findings (11 dead source files, 7 declared callers that don't exist, 4 real callers nobody declared). No Spec Kit artifact exists there yet to compare against; that is feature 003.
- Still unmeasured: whether the outcome-sufficiency check catches anything a careful reviewer would miss. It needs records written *before* code changes, which is exactly the Data-Guide overhaul.

### Lessons
- Run the tool on the real target during implement, not after. Three of the five converge tasks came from one Data-Guide run.
- "Report, never correct" made the import safe to run on a messy repo: nothing it found required a decision before the next step.
- Kate's narrowing of C ("tests can legitimately measure outcomes") changed the check from a rule about tests into a rule about evidence kinds. That is the difference between a check that passes when evidence is sufficient and a permanent warning generator.

### Kate's round-4 review (after the PR opened)
Kate read the code at `ee55e234`. **Provisionally accepted**, with one semantic correction. Feature 001 marked a *requirement* `unjustified` when its implementing code was deleted. Deleting the implementation invalidates the recorded claim that the code satisfies the requirement, not the requirement. Fixed structurally (T022): obligations get `needs_review` plus a finding; claims that `depends_on` deleted code remain `unjustified`. She also asked that the outcome check be described as a necessary-evidence-type check, not as proof of sufficiency. Neither the analyze pass nor converge caught this. It took a reviewer reasoning about what the statuses *mean*.

For feature 003 she proposed two replays against the same frozen diff:
- **A (realistic):** Spec Kit's native artifacts vs Spec Kit plus AEC records.
- **B (information-matched):** Spec Kit is given the same purpose information in prose. This is the only comparison that can isolate what AEC's representation and propagation add.

The Data-Guide purpose must be frozen before the fixture is introduced.

## Feature 003: self-reconciliation (WP0, 2026-10-29)

Implementer: Codex, from the frozen repository spec after PR #12 merged. The owner
corrected a wrong initial handoff; the separate pilot artifacts are excluded from
this feature. This is repository-only implementation, with that context limitation
recorded in the intent note rather than claimed as a pristine cold run.

- Tests first: singular source headers, source union, structured/raw field retention,
  long text, documentation paths/CLI names, and proposed append-only reconstruction.
  Old import expectations remain the compatibility decoy. Reconstruction tests
  reject acceptance, bad provenance and dangling reversals before writing anything.
- Disposable AEC import: 5 imports, 1 template skipped, 3 code links and 2 missing
  sources, full source text preserved. Data-Guide at
  `173c56108a27bf85b1c928a7a9a43b3a96a6f02b`: 26 imports, 1 template skipped;
  all 25 imported files with IO headings have structured rows. No target changes.
- Operating documents now state AEC's actual authority and engineering rules;
  historical instructions are labelled as history. Candidate decisions are linked
  to exact repository quotations and source hashes; reconstruction is not consent.
- Spec Kit analyze/converge were not run as agent workflows for this feature.
  The pinned v1.2.3 CLI was installed separately for the existing integration test.
  No new comparative efficacy claim is made. Record checks establish structure,
  not whether imported contracts or reconstructed judgments are adequate.
- Authoring cost: baseline began at 13:24 UTC. About 12 minutes of model elapsed
  work through implementation and initial unit checks; final verification/rework
  and cold-agent usability results are recorded in the dated WP0 intent note.
  Owner drafting/review time is not measured. This is calibration, not a controlled
  comparison. Useful findings: missing singular links, lost structured fields,
  ingestion truncation and inherited operating-rule drift; no assertion these
  would be missed by a careful ordinary review.

## Feature 004: source anchors and retrieval (WP-S, 2026-10-30)

Codex implements frozen spec 004 at 1afec55 after HO-20261030-001 and its network
clarification (git operations allowed; AEC source commands stay offline).
Plan/tasks preceded implementation. Tests-first coverage reproduces all P8/locator/
root fixtures plus clean decoys, bounded retrieval, direct unindexed-fact search,
current-digest associations, root confinement, no network/execution/writes, and
repeatable CLI output. Synthetic sources are generated in temporary directories;
no corpus is copied into the repository. Runtime is standard library only.

101 tests pass without skips, including packaging and pinned Spec Kit v1.2.3
install/remove. No Spec Kit agent analyze/converge workflow or comparative-outcome
evaluation was run; structural conformance does not establish owner benefit.
Code/record checks, final snapshot and measured cost are recorded in the dated
WP-S intent note. Propagation, existing record lines and frozen spec are unchanged.
Source-state observations remain separate from semantic/authority judgments.
