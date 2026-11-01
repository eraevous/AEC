# Release readiness: "a release we can be proud of"

Zach's brief (2026-11-01): bring AEC up to "where the inclusion could build momentum,
including … a true and realized value add, and hygiene enough for a release that we can be
proud of." He chose "proud of" on purpose, to draw on the different ways people judge
whether something is ready. This file turns that phrase into checks. It is the bar for the
first public release (v0.4.0), not for AEC as a finished product.

People mean at least seven different things when they say they are proud of a release. A
release can pass one and fail another, so each gets its own checks.

| Reading | The question a person asks | What would embarrass us |
|---|---|---|
| **Proud to show** | Can a stranger tell what it is in a minute and run it in five? | A README that opens with internal record ids; a first command that fails |
| **Proud to stand behind** | Is every claim true, and are the limits said out loud? | A capability table that is ahead of the code; any claim that AEC "improves" outcomes with nothing measured |
| **Proud of the craft** | Is it well made where nobody is looking? | Tests that pass on one Python version only; an install with no `aec` command; dead code shipped beside live code |
| **Proud to invite** | Could someone else contribute without asking Zach first? | A three-line CONTRIBUTING; no small, scoped first tasks; unclear rules about what an outsider may change |
| **Proud of the result** | Does it do something measurably useful, for someone besides us? | Only self-referential evidence (AEC checking AEC); a demo that was tuned until it passed |
| **Proud over time** | Will this version still make sense in six months? | No tag, no changelog, no statement of what is stable and what is experimental |
| **Proud of how it was made** | Would we be comfortable if people saw the process? | Approvals no one can trace; an AI-written project that hides that it is AI-written |

Two of these pull against each other. "Proud to show" wants a confident front page; "proud
to stand behind" (and Constitution IV) wants every claim hedged to what is measured. The
resolution is to be confident about what AEC *does* (deterministic, inspectable, specific)
and exact about what it has *shown*. A null or mixed result reported plainly passes
"proud of the result" better than a strong result nobody can reproduce.

## The checklist

Status as of 2026-11-01. ✅ done · 🔧 in this release branch · ⏳ needs work · 👤 owner decision.

### Proud to show
- 🔧 README opens with the problem and the one question AEC answers, then a quickstart.
- 🔧 Quickstart works on a repository that is not AEC: `pip install`, `aec init`, `aec edges`, `aec check`.
- 🔧 Governance detail (authority records, constitution) moves below the fold, linked, not deleted.
- ✅ Example with real data (`examples/mtg-pilot/`).

### Proud to stand behind
- ✅ Doc-truth tests: every path and command named in README and AGENTS exists (`tests/test_docs_truth.py`).
- ✅ Built / partial / planned table, and "no known caller is not proof of no caller".
- 🔧 A "What AEC is not" section near the top: not a semantic verifier, not a replacement for tests or Spec Kit.
- ⏳ Every value claim in the README links to a recorded measurement, or is phrased as a hypothesis.

### Proud of the craft
- ✅ 107 tests, standard library only, deterministic output, CI dogfoods AEC on itself.
- 🔧 `aec` console command after install (`[project.scripts]`), and a `[build-system]` table.
- 🔧 CI runs on Python 3.10, 3.11, 3.12 and 3.13 (the README claims 3.10+).
- 🔧 Every subcommand has one line of `--help` text.
- 👤 Legacy `src/core/` (2025 extractor): archive under `docs/history/`, or keep it labelled. It is not shipped either way.

### Proud to invite
- 🔧 CONTRIBUTING.md with setup, the test command, the fixture-plus-decoy rule, and what contributors may and may not change.
- 🔧 Issue templates (bug, proposal).
- 🔧 CODE_OF_CONDUCT.md and SECURITY.md.
- 👤 Three to five `good first issue` items opened on GitHub (drafts in this branch's PR description).

### Proud of the result
- ⏳ One measured outcome on a task AEC did not design for itself: the WP2-probe pilot, pre-registered in `docs/evaluations/probe-001.md` before any run.
- ⏳ The result, whatever it is, reported in README in one sentence with a link.

### Proud over time
- 🔧 CHANGELOG.md, starting from v0.1.
- 🔧 Stability note: which commands and record fields are stable for v0.4, which are experimental.
- 👤 Tag `v0.4.0` and a GitHub release (owner action).
- 👤 PyPI publication (optional; owner decision on name and account).

### Proud of how it was made
- ✅ Approvals quoted with sources (handoffs, PR descriptions, `relay-kit-private` decision log).
- ✅ Spec Kit workflow and its measured costs (`docs/speckit-log.md`).
- 🔧 One paragraph in README saying plainly that AEC is built by Zach with AI agents (Claude, Codex, ChatGPT), and that its own records are the audit trail of that.

## What is deliberately not required for v0.4.0

WP1A (commit snapshots), WP2A (context delivery) and the safeguards package. Clearing
`docs/decisions-to-confirm.md`. A name change to EACH. None of these block an honest first
release; listing them as planned is enough.
