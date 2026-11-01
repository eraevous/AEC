# walkthrough-002: fresh reader on the reorganized README (PR #29)

A fresh Claude Sonnet agent with no project history read the README on branch `docs/reorg`, answered six comprehension questions before running anything, then followed the quickstart. Its report is reproduced unedited below. The fixes it led to are in the same PR: why to use AEC and what it costs; the record types and relations, plus `init`'s next steps, inline in the quickstart; a runnable command for the worked example; one pinned install line in both the README and the guide; `aec` instead of `PYTHONPATH=…` in the edges reference; and a real Spec Kit integration page. **Not tested: the published install command.** The release tag `v0.4.1` didn't exist yet, so the agent installed from the PR branch (`@docs/reorg`). Re-run the install line once v0.4.1 is published.

---

# AEC newcomer report (branch docs/reorg)

## 1. Two-minute test: answers written before any install (verbatim)

**What problem does this solve?**
When a coding agent (or person) changes code, tests only tell me behaviour broke. They don't tell me that a written-down requirement, a claim, or a decision relied on the old behaviour. AEC stores those reasons as records linked to code, and after an edit lists which ones to re-check ("stale", "needs_review").

**What must I supply for it to work?**
Python 3.10+, the pip install, and an `aec init` in my repo. The README also implies I must hand-write the records: requirements, claims, and their relations to code names, as JSON lines in .aec/records.jsonl. I must also take a "before" snapshot and make an "after" snapshot around my change. Nothing is inferred for me, except optionally `aec import-purpose` if I already have Codex++ purpose files.

**What does it actually detect?**
Structural change: that code (Python only, static analysis of defines/calls/imports) or a record that a requirement/claim/decision is linked to changed, and who is downstream of it. It labels them stale/needs_review/unjustified/weakened etc. It does not say whether the change is wrong.

**What is beyond its knowledge?**
Truth/correctness; non-Python code; dynamic dispatch calls (unresolved, so "no known caller" is not "no caller"); anything nobody wrote a record for; whether it improves outcomes (README says not shown to). Also no comparison to Spec Kit.

**What happens to my repository?**
It never edits my code or specs. `aec init .` creates a .aec/ directory (records, git-ignored edge snapshot, CI/hook snippets). Beyond that I'm unsure if init touches .gitignore, hooks, or CI files itself ("snippets" is ambiguous).

**Where can I see a reproducible example?**
examples/itsdangerous-demo/run.sh in the repo (linked in "Worked example"); clones itsdangerous at a pinned commit, runs its tests, and shows AEC's report.

## 2. Quickstart (fresh venv /tmp/claude-0/reader2/venv, Python 3.13.18, project /tmp/claude-0/reader2/proj)

| # | Command | Result | As README said? |
|---|---|---|---|
| 0 | `pip install "git+https://github.com/eraevous/AEC.git@docs/reorg"` (README's `@v0.4.1` tag is unpublished, per instructions) | installed aec 0.4.1 | yes |
| 0b | `aec --version` | `aec 0.4.1` | yes |
| 1 | `aec init . --owner "Test Dev"` | created .aec/{records.jsonl, edges.jsonl, README.md, .gitignore, snippets/claude-settings.json, snippets/aec-ci.yml}; printed next steps | yes. Touched only .aec/; no edits to my code, .gitignore, or hooks |
| 2 | `grep '"defines"' .aec/edges.jsonl \| grep apply_discount` | one line, `"dst": "src.mypkg.pricing.apply_discount"` | yes, matches `code:src.mypkg.pricing.apply_discount` |
| 3 | append the two JSON records to .aec/records.jsonl | accepted | yes |
| 4 | `aec check .aec/records.jsonl --edges .aec/edges.jsonl` | `0 error(s), 0 warning(s) (structural)` | yes |
| 4b | (extra) typo'd target `apply_discnt` | `[ERROR] ... did you mean code:...apply_discount?`, rc=1 | yes, near-miss suggestion works |
| 5 | `cp .aec/edges.jsonl .aec/before.jsonl`, edit apply_discount (removed the `max(0.0, ...)` clamp) | fine | yes |
| 6 | `aec edges . -o .aec/edges.jsonl` | `1 edges from 2 files (0 skipped)` | yes |
| 7 | `aec code-impact .aec/records.jsonl .aec/before.jsonl .aec/edges.jsonl` | `[stale] R-1@1`, `[needs_review] C-1@1`, "2 affected" | yes, exactly as promised |

The quickstart works first time, end to end, in about 8 commands. The tool does what the README claims.

Things I observed that the README did not tell me:
- `init` printed next steps (replace purpose stub P0, copy snippets into .claude/settings.json and .github/workflows/aec.yml). None are in the README Quickstart. I skipped them and nothing broke.
- init leaves a stub purpose record P0 ("TODO: the owner states...") in records.jsonl. The README never mentions it.
- The impact output header says `authorized_by None`. It is not explained anywhere in the README.
- My edit was a behaviour-breaking one, but AEC flagged it from a body hash change only. It can't tell a refactor from a regression; the README does say this, in prose.

## 3. Points of confusion (README quote, under 15 words)

1. Install pins an unpublished tag: "pip install "aec @ git+...@v0.4.1"". `git ls-remote --tags` shows only v0.4.0. The documented install command fails today. The getting-started guide uses `@main` with a comment about `@v0.4.0`, so the two docs disagree on the install line.
2. "never edits your code or your specs" vs "creates .aec/ ... CI/hook snippets". Snippets are only written into .aec/, but a skim reads as if CI/hooks get installed.
3. "Both references resolve? (suggests near misses)" is a bare comment. I had to run it to learn that it exits non-zero on failure.
4. "find the name AEC uses for your function". The grep tells you the name but the record needs a `code:` prefix. This is only learned from the example JSON. A newcomer with a different layout has to infer the rule.
5. "a deterministic static-analysis snapshot of what defines, calls and imports". Vague on what "snapshot" means until the Quickstart.
6. "Append ... to `.aec/records.jsonl`, one JSON object per line". Nothing says what `type`, `epistemic`, `tier`, `rel` values are legal, and "committed", "candidate" and "implemented_by" are unexplained. The vocabulary doc is linked only later, in the getting-started guide.
7. "`stale` ... `needs_review`" table: seven dispositions defined, but only two appear in the Quickstart. `rebaseline`, `exploratory` and `contested` need concepts (authority, versions) the Quickstart never introduces.
8. "Decisions are never declared unjustified by the tool". Decisions and authority have no example in the README, so this reads as noise.
9. "Records are written by people (or agents)". The biggest cost, hand-writing the requirements, is buried at the end of the limitations list. The Quickstart makes it feel like a few lines.
10. "who has authority over them". Authority records exist (init created AU-owner) but the README never shows how authority matters to a first-time user.
11. "AEC is designed and owned by Zach Rhodes ... built with AI agents". Fine, but the README never says who the intended user is. Is it for agent users, for Spec Kit users, for anyone with Python?
12. "Not shown to improve outcomes" in the Evidence section directly undercuts the pitch in the opening. It is honest, but a newcomer is left asking why they should use it. The README never answers that.
13. "Python 3.10 or newer; no other dependencies" is stated twice. Elsewhere the tool says it only analyzes Python, so a non-Python project gets nothing. That is mentioned only mid-list under "Not complete about your code".
14. "The seven commands ... documented here". Only five are shown in the README (init, check, edges, code-impact, and indirectly import-purpose). `impact` and `source` are never explained there.
15. "Compare edge snapshots made by the same AEC version". Stated in the Stability section without saying how to know the version of a snapshot.
16. The README's "How AEC is built" says it is built with Claude, Codex and ChatGPT. The governance doc calls ChatGPT "Kate". That is explained in governance.md only, and README readers will not see it.

## 4. Links

All 16 raw-file targets linked from the README returned HTTP 200, as did the docs/evaluations/ directory page, docs/data-guide-trial.md, and the worked example script.

Landing quality:
- Getting started (docs/guide/getting-started.md, 72 lines): useful. It repeats the Quickstart nearly word for word, which is good for orientation but means no new information for someone who followed the README. Adds git worktree baseline and Codex++ purpose import. Weaknesses: install uses `@main` vs README `@v0.4.1`; the Codex++ section assumes you know what ".purpose.md" files and "Codex++" are, and the Data-Guide trial bullet is internal-project noise for a newcomer. Its link to `../../docs/reasoning-vocabulary.md` resolves.
- Docs map: the README table's targets are of very uneven quality.
  - docs/reasoning-vocabulary.md (127 lines): useful reference, but a newcomer is never told to read it before writing records.
  - docs/reference/edges.md (15 lines): short and useful, but every command uses `PYTHONPATH=src python3 -m aec`, which is a developer-checkout form that doesn't match the installed `aec` command.
  - docs/reference/source-anchors.md (98 lines): advanced; assumes the vocabulary.
  - docs/integrations/spec-kit.md (3 lines): essentially a stub. It names `specify extension add --dev <AEC>/extension` with an unexplained `<AEC>` path placeholder.
  - docs/architecture.md (175 lines): not newcomer material. Opens with approval status, references to "Kate (ChatGPT)", a private relay repository and DEC-016 to DEC-022 decisions. The README sells it as "where AEC is going", but it is mostly internal governance.
  - docs/history/about.md and docs/governance.md: internal and philosophical, and they cite a private repo that readers cannot check. governance.md says so openly.
  - docs/evaluations/ is a directory link, so it lands on a file list rather than a page.
- Worked example: examples/itsdangerous-demo/run.sh exists and is well commented (needs git, Python 3.10+, network; clones itsdangerous at pinned commit 672971d). I did not run it (outside the requested scope and the tool budget). Its header says `AEC_REF defaults to this checkout`, so a newcomer reading it via raw.githubusercontent.com has to clone first. The README gives no command to run it.
- Nothing was broken (no 404s).

## 5. Verdict: could a newcomer do this alone?

Mostly yes for the mechanical part, no for the part that matters.

- The Quickstart is accurate and ran with zero deviation. Error messages are good (near-miss suggestion). A newcomer who copies commands will get a `stale` report in under five minutes.
- The README gets the "what does it detect" and "what can't it know" questions across well. Its honesty about limits (Python only, static, not shown to improve outcomes) is a strength.
- But the newcomer is not told:
  - the real cost, which is hand-authoring requirement and claim records, and which ones to write;
  - the install command currently fails, because tag v0.4.1 is unpublished (only v0.4.0 exists);
  - the init next-steps (purpose stub, hook/CI snippet install) that were not in the Quickstart;
  - how to run the worked example.
- The Quickstart demonstrates the mechanism on a requirement the user wrote knowing the answer, so it shows a tidy stale flag but not why a newcomer would bother in a real repo. The README is upfront about that for the itsdangerous demo but not for the Quickstart.
- The docs map sends a newcomer toward architecture and governance material full of private-repo and AI-agent coordination references that they cannot use.

Fixes in priority order: publish v0.4.1 or change the README to v0.4.0/@main; add a sentence saying the user authors the records and roughly how many to write; add the run command for the demo; mark architecture/governance/history as "for contributors"; replace `PYTHONPATH=src python3 -m aec` in docs/reference/edges.md with `aec`; flesh out or remove the 3-line spec-kit page.
