# Lifecycle gaps intent — 2026-11-04

@ai-intent: Fix four defects a docs builder reported while testing the no-Spec-Kit paths (superseded references, depth-2 silence, moved symbol, init tag pin). Requested through the coordinator (actor `aec#lifecycle`); not owner-authorized, so `AEC-R-lifecycle@1` is provisional. Branch `fix/lifecycle-gaps`; Zach merges.

## Decisions taken inside the request

- **Superseded references: a warning plus a pointer, never a status.** Only latest versions take an impact status (`_dependents`), so an old reference stays invisible by design. Giving C-1@1 a status from a change to R-1@2 would change what `depends_on R-1@1` means. Instead `check` warns (as `evidence-text` in #53, only the latest referrer is judged, so re-pointing clears it) and `code-impact` emits a `structural:` pointer. `supersedes` and same-id references are history and are skipped. The pointer is in `code_impact`, not in `impact`: the report asked about `code-impact`, and changing `aec impact`'s output for explicit events is a separate decision.
- **Depth note above the summary, not below it.** #51's tests (and readers) rely on the summary being the last line. The note counts *symbols* one layer past the walk, not changed symbols: counting changed ones would compute depth+1 and then withhold the result. It is a `notes` entry, not a finding, so `--exit-code` and the hook stay quiet on it. Shown only when some definition changed.
- **Moved symbol: same-name matches follow the sibling typo matches.** The prefix rule is unchanged and still wins alone; typo matches keep their place; same-name matches in other modules fill up to three suggestions in all, with a count of the rest.
- **Source checkout pins HEAD.** Detected with `git ls-files --error-unmatch` on the package's `__init__.py` (so a venv that sits untracked inside a user's repo is not mistaken for a checkout), then `rev-parse HEAD`. Always the commit, never a local tag, matching "git installs pin the commit". The note says to push the commit and warns about uncommitted changes. `install_ref` (the #51 rule) is untouched; `init.CI` is now resolved on first use so importing `aec.init` does not run git.

## Review round (fresh-context review of 7562d5a, relayed by the coordinator)

- S1 (coordinator reading; Zach may reverse): evidence and decision referrers are exempt from `superseded-reference` and the pointer. Alternative for Zach: an explicit `version_pinned: true` per relation instead of a type rule.
- S2: the note now counts *changed* definitions at exactly depth+1 from linked symbols whose records are not already classified, and is silent otherwise. The first cut fired on edits nothing links to. Function name `unexamined_beyond` kept so `AEC-R-lifecycle@1`'s `code:` links still resolve.
- S3: `EV-lifecycle-tests@2` corrects @1's count of violating cases (three init cases errored only because `resolve_install_ref` did not exist).
- Nits: same-name suggestions rank module-level definitions before methods; a source checkout counts only when its `pyproject.toml` names `telosmith`.
- The MtG pilot keeps one warning, `CL-boundary-rule@1 -> P-01@1` (a claim on a superseded purpose): the rule as reviewed keeps it, contrary to the review's "pilot to 0" expectation.

## Not changed

- Telosmith's own records: `EV-DN2X-tests@1` and `EV-DN2X-qual@1` support `CL-DN2X-coverage@1` while `@2` exists, and the new rule flags them. Re-pointing evidence at a claim it was not gathered for would assert support nobody checked, so they stay as they are for Zach to decide. After the S1 exemption they no longer warn.
- `reached_changes` lists every record linking a symbol, superseded versions included. Pre-existing; left as is.
