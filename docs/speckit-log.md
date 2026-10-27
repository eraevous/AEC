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
