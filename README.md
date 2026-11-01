# AEC

**AEC keeps the recorded reasons for code attached to the code, and tells you which requirements, claims and decisions need reassessing when something they depend on changes.**

It reports structure, not truth: "this conclusion's recorded support changed", never "this
conclusion is false". It is a standard-library Python command-line tool, works with or without
[Spec Kit](https://github.com/github/spec-kit), and never edits your code or your specs.

## Why it exists

AI coding agents are good at making a change and bad at knowing what else depended on the old
behaviour: a requirement someone wrote down, a claim a decision rested on, a caller nobody
mentioned. Tests catch broken behaviour; they don't catch a broken *reason*.

For example, an agent "simplifies" `hmac.compare_digest(sig, expected)` to `sig == expected` in
[pallets/itsdangerous](https://github.com/pallets/itsdangerous). All 297 of the library's tests
still pass. If a constant-time requirement had been recorded against that function, AEC reports it,
and the claim resting on it, as `stale`: look again. ([Reproduce it](#worked-example).)

AEC records those reasons as plain, append-only JSON lines (purposes, requirements, claims, evidence,
decisions, and who has authority over them). It links them to the code through a deterministic
static-analysis snapshot of what defines, calls and imports what.

## Install

```bash
pip install "aec @ git+https://github.com/eraevous/AEC.git@v0.4.1"
aec --version
```

Python 3.10 or newer; no other dependencies.

## Quickstart

```bash
cd your-project
aec init . --owner "Your Name"      # creates .aec/: records, an edge snapshot (git-ignored), CI/hook snippets
grep '"defines"' .aec/edges.jsonl | grep apply_discount    # find the name AEC uses for your function
```

Append a requirement and a claim that rests on it to `.aec/records.jsonl`, one JSON object per line:

```json
{"id": "R-1", "version": 1, "type": "requirement", "subject": "code", "epistemic": "committed", "text": "Discounts never make a price negative.", "relations": [{"rel": "implemented_by", "to": "code:src.mypkg.pricing.apply_discount"}]}
{"id": "C-1", "version": 1, "type": "claim", "tier": "candidate", "text": "Checkout totals are never negative.", "relations": [{"rel": "depends_on", "to": "R-1@1"}]}
```

```bash
aec check .aec/records.jsonl --edges .aec/edges.jsonl   # both references resolve? (suggests near misses)
cp .aec/edges.jsonl .aec/before.jsonl                   # keep the "before" snapshot
# ...edit apply_discount...
aec edges . -o .aec/edges.jsonl                          # the "after" snapshot
aec code-impact .aec/records.jsonl .aec/before.jsonl .aec/edges.jsonl
```

`code-impact` marks `R-1@1` as `stale` and `C-1@1` as `needs_review`. Records are append-only:
to change one, append the same `id` with `"version": 2`. The
[getting-started guide](docs/guide/getting-started.md) covers comparing against a branch, CI and the
Claude Code hook, and repositories with existing Codex++ purpose files.

## What the results mean

Each conclusion that relied on something that changed gets a review disposition, not a truth value:

| Disposition | Meaning |
|---|---|
| `stale` | the code or record it rests on changed without an authorized revision: look again |
| `needs_review` | it sits downstream of something stale, broken or contested, or it is a decision whose basis changed |
| `unjustified` | a claim's explicit support broke (for example, code it depends on was deleted) |
| `weakened` | it lost one support but keeps others |
| `rebaseline` | an authorized revision: re-examine it, but it is not drift |
| `exploratory` | what changed was provisional, which is expected while a purpose is still being worked out |
| `contested` | new evidence contradicts it |

Decisions are never declared unjustified by the tool; they belong to a human authority and are
flagged for review. The full vocabulary is in [docs/reasoning-vocabulary.md](docs/reasoning-vocabulary.md).

## Worked example

[`examples/itsdangerous-demo/run.sh`](examples/itsdangerous-demo/run.sh) reproduces the
itsdangerous example above end to end in a temporary directory: it clones the library at a pinned
commit, records a constant-time requirement and a claim, makes the edit, runs the library's tests
(297 pass before and after) and shows AEC's report. Be exact about what it shows: someone who knew
what to look for wrote the requirement down, so it demonstrates the mechanism, not discovery.

## Evidence and limitations

- **Not shown to improve outcomes.** In the first measured test,
  [probe-001](docs/evaluations/probe-001-results.md), Claude Sonnet 5.5 agents found every hidden
  dependant on their own on three dependency-sensitive tasks (18 of 18 trials succeeded in every
  condition). AEC's structural briefing changed no outcome and raised token use on two of the three
  tasks. It was a small, exploratory pilot. It also exposed a gap in AEC's caller resolution.
- **Not a comparison with Spec Kit.** Nothing has yet been run against a properly configured Spec
  Kit baseline with the same information.
- **Not complete about your code.** The snapshot is static analysis of Python only. Calls through
  dynamic dispatch stay unresolved and are never guessed: no known caller is not proof of no caller.
- **Not a replacement for tests or review.** It keeps a layer they don't: why things are the way they
  are, and who may change that.
- **Records are written by people (or agents).** `aec import-purpose` can seed them from existing
  Codex++ purpose files; the rest is authored, and authoring cost is logged in `docs/speckit-log.md`.

## Stability

AEC is alpha (v0.4). The seven commands and the record fields documented here are what this version
supports; a minor version before 1.0 may change output formats or record fields, and every change is
listed in [CHANGELOG.md](CHANGELOG.md). Compare edge snapshots made by the same AEC version: `edges
--diff` does not yet refuse snapshots from different extractor versions.

## Documentation

| If you want to… | Read |
|---|---|
| set AEC up in a real repository | [Getting started](docs/guide/getting-started.md) |
| understand the edge snapshot | [docs/reference/edges.md](docs/reference/edges.md) |
| anchor records to source passages | [docs/reference/source-anchors.md](docs/reference/source-anchors.md) |
| use AEC inside Spec Kit | [docs/integrations/spec-kit.md](docs/integrations/spec-kit.md) |
| see where AEC is going | [docs/architecture.md](docs/architecture.md) and [docs/history/about.md](docs/history/about.md) |
| check the evidence | [docs/evaluations/](docs/evaluations/) |
| see how the project governs itself | [docs/governance.md](docs/governance.md) |

## How AEC is built

AEC is designed and owned by Zach Rhodes and built with AI agents (Claude, Codex and ChatGPT) working
from written handoffs, using Spec Kit. It tracks its own development with its own records, so the
project is its own longest-running test case; [docs/governance.md](docs/governance.md) explains which
of that evidence is public and which is kept private.

Contributions are welcome: see [CONTRIBUTING.md](CONTRIBUTING.md). To report a security issue, see
[SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE). Contributions are made under the [Contributor License Agreement](CLA.md), which keeps
them open under the same licence while letting the maintainer also offer commercial versions.
