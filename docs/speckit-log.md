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
