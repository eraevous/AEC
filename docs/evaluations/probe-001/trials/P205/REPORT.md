<!-- recovered from the agent's final message; it could not write this file itself -->
I made the change and the tests pass, but I couldn't write `REPORT.md`. The write tool refused it because this agent has to return reports as text. The report is below.

## What changed
- **`src/data_profiler.py`:**
  - `DataProfiler.profile_dataset()` no longer calls `profile_columns()`.
  - It now computes only the metadata (row count, column count, missing values, duplicates) and the column types, plus bivariate profiling if `include_bivariate=True`.
  - The `__main__` demo now calls `profile_columns()` explicitly, so its sample report keeps the column sections.
- **`src/profilers/univariate.py`:**
  - `profile()` relied on the old behaviour. It used an `if/elif`, so it skipped `profile_columns()` whenever "dataset" was requested.
  - Without a fix, the default `["dataset", "columns"]` would have lost its column stats.
  - I changed `elif` to `if`, so each requested analysis runs on its own. The default behaviour is unchanged, and `["dataset"]` alone is now fast.

## Tests
`python3 -m pytest -q` gave 89 passed. A full run takes roughly 90 to 140 seconds, mostly the CLI end-to-end tests.

## Things the requester should know
- **Behaviour change for external callers:** anyone who relied on `profile_dataset()` to fill `numeric_profiles`, `string_profiles`, `temporal_analyses`, `phone_profiles` or `plots` must now also call `profile_columns()`. I found no other callers in the repo.
- **Report after `profile_dataset()` alone:** `generate_report()` still works, but it now has only the Metadata and Column Types sections. The missing-value matrix is gone too, because it is drawn in `profile_columns()`.
- **Docs left stale:** line 64 of `codex_++/purpose_files/data_profiler.purpose.md` now describes the old behaviour. `docs/superpowers/plans/2026-04-20-eda-tool-redesign.md` also still shows the old pattern. I didn't edit either.
- **No new test:** nothing tests the split directly, and I didn't add one.

Files are under `/tmp/claude-0/probe/trials/P205/repo/src`: `data_profiler.py` and `profilers/univariate.py`.