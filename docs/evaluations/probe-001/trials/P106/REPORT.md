<!-- recovered from the agent's final message; it could not write this file itself -->
I made the change, but I couldn't write `/tmp/claude-0/probe/trials/P106/REPORT.md`. The write tool refused to create a report file, so the report is below. `python3 -m pytest -q` passes (89 tests, about 2.5 minutes).

## What I changed
- **`src/data_profiler.py`:** `DataProfiler.profile_dataset()` no longer calls `profile_columns()`. It now computes only `metadata` and `column_types`, plus bivariate profiling if `include_bivariate=True`, which is unchanged. The `__main__` demo block now calls `profile_columns()` explicitly so it still produces a full report.
- **`src/profilers/univariate.py`:** This was the only caller in the repo that depended on the old behaviour. Its comment said `profile_dataset()` already calls `profile_columns()`, and it used `if "dataset" ... elif "columns"`. I changed the `elif` to a plain `if`. The default `analyses=["dataset","columns"]` still produces column stats. `analyses=["dataset"]` now runs only the fast dataset-level pass. The CLI (`src/cli.py`) reaches the profiler through this function, so it keeps working.

## Things the requester should know
- **Behaviour change for outside callers:** Anyone who calls `profile_dataset()` and expects `numeric_profiles`, `string_profiles`, `temporal_analyses` or `phone_profiles` in `results` must now also call `profile_columns()`. The AEC "no callers found" output was unreliable, since 874 of 1578 calls were unresolved. I found callers by grepping this repo. I can't see notebooks or scripts outside it.
- **`generate_report()`:** After only `profile_dataset()` it still works. It shows metadata, column types and row examples. It skips the column sections and the missing-value matrix, which `profile_columns()` produces.
- **Docs not updated:** `docs/` and `codex_++/purpose_files/` still describe the old behaviour, for example `data_profiler.purpose.md` line 64. I left them alone.
- **No new test:** No test covers `profile_dataset()` on its own, and I didn't add one.