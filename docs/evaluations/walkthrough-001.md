# walkthrough-001: clean install, first use, from the README alone

**What this is.** On 2026-11-01 a fresh Claude Sonnet agent, given none of the project's history,
followed the README on branch `release/v0.4-readiness` (at `8bd6143`) as a newcomer would. It
recorded its first-screen understanding before reading further, and logged every failure. It is an
agent, not a human stranger, so it reads faster and more literally than a person would. Its report is
reproduced unedited below.

**What changed because of it** (commit following `8bd6143`):
- F1 (no install line): added an "Install" section.
- F2 (record shape undocumented): added "Your first `stale` report", with the `relations` shape inline.
- F3 (the `src.` prefix): the quickstart explains where names come from. `check` now suggests close
  matches, including a missing source-root prefix, for an unknown `code:` reference.
- F4 (tool_version 0.3.0 vs 0.4.0): the Stability section explains that the extractor version is
  separate from the package version. It is not bumped, because extraction did not change.
- F6 (reference material before the workflow): "Adopting" and "bedrock" now come first under Reference.
- Writing the new quickstart exposed one more error. The draft said both records would be `stale`, but
  a claim resting on a stale requirement is reported as `needs_review`. Running the exact snippet
  caught it before it shipped.

---

# AEC newcomer walkthrough (branch release/v0.4-readiness)

## 1. First-screen understanding (verbatim, written before reading past line 40)

AEC is a Python command-line tool that stores the reasons behind code (requirements, claims, decisions) as append-only JSON lines and links them to code through static analysis. When code changes, it tells you which recorded requirements or claims may no longer hold. It is aimed at developers who use AI coding agents and want to catch changes that break an unstated dependency, and possibly at teams that use Spec Kit.

Accuracy check afterwards: right on the mechanism and audience. The first screen did not make clear that records are hand-written, which the README only admits at lines ~290+.

## 2. Commands run, in order

1. `curl -sS .../README.md -o README.md` - worked (312 lines).
2. `python3 -m venv venv` - worked (Python 3.13).
3. `pip install "git+https://github.com/eraevous/AEC.git@release/v0.4-readiness"` - worked, aec 0.4.0. SUBSTITUTION: the README has no install line at all (see F1), so I used the branch line you gave me.
4. `aec --help` - worked; lists 7 subcommands matching the README.
5. Wrote a 3-file package (`src/tiny/{__init__,pricing,cart}.py`) in /tmp/claude-0/walkthrough/proj and ran `git init`.
6. `aec init . --owner "Newcomer"` - worked as expected. Created .aec/ with records, edges, README, snippets. Printed sensible next steps.
7. `aec check .aec/records.jsonl --edges .aec/edges.jsonl` - 0 errors, as expected.
8. `cp .aec/edges.jsonl old.jsonl`, then appended a requirement and claim using top-level `implemented_by` / `depends_on` fields (my guess from README prose) - `aec check` gave 2 warnings "relation-shape ... write them as relations" with rc=0. It did not do what I wanted (the links were not live), but the warning was clear and told me the fix. See F2.
9. Fetched the repo clone (README links examples/.../records.jsonl, so this is a README-directed lookup) and copied the record shape: `"relations":[{"rel":"implemented_by","to":"code:..."}]`. Replaced my bad lines (I deleted them by hand, which breaks "append-only"; it was my scratch file).
10. `aec check` again - 0 errors, 0 warnings. Good.
11. Added a deliberately wrong reference `code:tiny.pricing.apply_discount` - `aec check` gave `[ERROR] code-reference ... no such symbol in the edge snapshot (renamed or deleted?)`, rc=1. Expected, and it is the useful behaviour. See F3 for the hint it lacks.
12. Edited `apply_discount` (dropped the `pct < 0` guard), `aec edges . -o .aec/edges.jsonl`, `aec edges --diff old.jsonl .aec/edges.jsonl` - printed `defs_changed: src.tiny.pricing.apply_discount`. Worked.
13. `aec code-impact .aec/records.jsonl old.jsonl .aec/edges.jsonl` - `[stale] R-range@1` and `[stale] C-range@1`, "2 affected". This is the payoff and it worked first time once the record shape was right.
14. Edited only the caller `cart.total` and ran code-impact against the previous snapshot - "0 affected, 2 conclusions unaffected". Correct: nothing recorded rests on `total`.
15. `git clone --branch release/v0.4-readiness` and `bash examples/itsdangerous-demo/run.sh release/v0.4-readiness` - worked, about 10 s. 297 tests pass before and after the edit, and AEC reports 2 stale. Output matches the README, apart from F6.

Total: about 12 tool calls.

## 3. Confusion and failures

F1. No install instructions. Expected `pip install ...`. Found none: grep for "pip|install" only hits the Spec Kit extension and the demo script. Nothing in the README says how to get the `aec` command. The task brief says the README's install line points at the default branch; on this branch I could not find one. Every README command is `PYTHONPATH=src python3 -m aec ...`, which only works inside a clone. Only the "Adopting AEC" section uses `python3 -m aec` with no PYTHONPATH, and it still assumes it is installed. Quote: "The script installs AEC from this checkout, or from a tag" (the only install hint). Biggest blocker.

F2. The record format is not documented in the README. I wanted to record a requirement pointing at a function. The README says only "Records point at code with `code:<dotted.symbol>` (for example `implemented_by`)". That reads as a field named implemented_by, and I guessed that. The real shape is `relations: [{rel, to}]`. The only complete requirement/claim record is in examples/itsdangerous-demo/records.jsonl, which is linked as an example rather than as the format spec. `subject`, `epistemic` and `tier` are used there with no explanation. The `.aec/README.md` that init writes also does not show a record. Quote: "Records point at code with `code:<dotted.symbol>`". Credit: the tool's own warning rescued me.

F3. Symbol names carry a `src.` prefix. I tried `tiny.pricing.apply_discount` (how Python imports it). The valid name is `src.tiny.pricing.apply_discount`. The README says "dotted.symbol" and nothing about module naming for src layouts. The error message "no such symbol" does not suggest the close match, though it could. The edges file is the only place to look up names, and the README does not say to look there.

F4. Version mismatch in the snapshot. `aec --version` says 0.4.0 but edges.jsonl header says `"tool_version": "0.3.0"`. Not harmful here. It matters because the README warns "compare snapshots from the same AEC version", and a user would see the number and wonder. Also the README reference table says `src/aec/` is "v0.3" while the title says v0.4.

F5. Two overlapping command styles and a long, inward-looking README. The first ~50 lines are good. After that come the MtG pilot, Spec Kit, WP-S source anchors and governance of the repo itself, all before a newcomer gets the command sequence for their own repo. "Adopting AEC in an existing repo" is the section I actually needed, and it is buried at about line 170. It does not show the step that matters: record something, snapshot, change, `code-impact`. That workflow is split across three sections ("bedrock", "adopting", demo). Also "The seven commands ... documented here" - `impact` and `import-purpose` need records formats that are not explained.

F6. Minor: the README's sample output omits the `via ...` lines and the `defs_changed:` line that real output prints, and the final line "2 affected, 0 conclusions unaffected" is shown without the blank-line header. Cosmetic, but a newcomer diffing output notices. Also the `edges --diff old.jsonl` step requires you to copy the snapshot yourself before editing (`cp .aec/edges.jsonl old.jsonl`). The README mentions `old.jsonl` but never says where it comes from; I had to read run.sh to see it is a manual copy. Easy to miss: if you run `aec edges` before copying, the diff is empty and you get no warning.

F7. Honest caveat on "stale": `code-impact` flags a function whose body changed in any way (my +0 edit to apply_discount body would also flag). There is no sense of whether the change matters. The README says this ("`stale` means look again"), so it is not a docs failure, but expect noise.

## 4. Surprises

Good:
- The tool warns on mis-shaped relations instead of silently ignoring them, and `check` fails (rc=1) on dangling code references.
- Zero dependencies, installs in seconds, `init` never overwrites and prints next steps.
- The demo script worked first time, in 10 s, on pinned commits. Uses a branch/tag argument well.
- README is candid about limits ("Not a verifier", "Not shown to improve outcomes yet"). Credible.
- Caller-only edits correctly cause no impact.

Bad:
- No install line (F1).
- A README that is mostly the maintainer's project log: it names the owner, private repos, white paper and WP numbers before explaining how to use it.
- "Seven commands" are not all introduced with usage; `impact` appears only by example on MtG data.

## 5. Verdict

Could a newcomer get from zero to a useful `stale` report on their own code in about 5 minutes? **No, not from the README alone; yes with fixes.** The tool itself did this in about 6 commands once I knew the record shape. The time sink is finding how to install (F1) and the record format (F2), which required leaving the README for examples/ and run.sh. I would also have been stuck on F3 had the `src.` prefix not been derivable from the error plus the edges file.

Fixes, in order of value:
1. Add an install section (`pip install "git+https://github.com/eraevous/AEC.git@<ref>"`, then `aec --version`) near the top.
2. Add a 15-line "Your first stale report" quickstart: init, copy edges to old.jsonl, append the two example records (show the `relations` shape inline), check, edit, `edges -o`, `code-impact`.
3. Document the minimum record fields (`id, version, type, subject, epistemic/tier, text, relations`) and say symbol names come from `edges.jsonl` and include the source root prefix (`src.`).
4. Make the "dangling code reference" error suggest the closest known symbol.
5. Fix tool_version 0.3.0 in snapshots and the "v0.3" label in the table.
6. Move the MtG pilot, WP-S source anchors and governance sections below a reference divider, or into docs/.
