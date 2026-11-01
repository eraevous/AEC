<!-- recovered from the agent's final message; it could not write this file itself -->
I changed `profile_dataset()` as requested, but I couldn't write `REPORT.md`. The write was refused, so the report is below. The full test suite passes (89 tests).

## What I changed
- **`src/data_profiler.py`:** `DataProfiler.profile_dataset()` no longer calls `profile_columns()`. It now sets only `results["metadata"]` (row count, column count, missing values, duplicates) and `results["column_types"]`. It still runs bivariate profiling if `include_bivariate=True`. I added a docstring saying so, and the `__main__` demo now calls `profile_columns()` itself before `generate_report`.
- **`src/profilers/univariate.py`:** This was the one place in the repo that relied on the old behaviour; a comment there said `profile_dataset()` internally calls `profile_columns()`. It used `if "dataset" … elif "columns"`. I made those two independent `if`s. The default `analyses=["dataset","columns"]` still produces column stats, and `analyses=["dataset"]` now means dataset-level only.

## Verification
- **Tests:** The full suite passes, in about 1 to 2.5 minutes.
- **Manual check:** `profile_dataset()` now returns only `metadata` and `column_types`. After calling `profile_columns()`, the temporal, string, numeric, phone and plots keys appear.
- **Coverage gap:** No existing test calls `profile_dataset` or `univariate.profile` directly, so the passing suite says little about this change. I added no tests.

## Things the requester should know
- **Behaviour change for other callers:** Anything that calls `profile_dataset()` and expects column profiles or plots will now get none. It has to call `profile_columns()` as well.
- **Why I trust the caller search:** The AEC data lists no callers and says 874 of 1578 calls were unresolved. I grepped the Python source instead and found only the two call sites above.
- **Reports are now sparser:** `generate_report()` after `profile_dataset()` alone still works, but the report has only metadata, column types and row examples. It has no missing-value matrix and no per-column sections. The error message "Call profile_dataset() before generating a report." is now slightly misleading.
- **Docs not updated:** `codex_++/purpose_files/data_profiler.purpose.md` (line 64) and `docs/superpowers/plans/2026-04-20-eda-tool-redesign.md` still describe the old behaviour. `ast_deps.csv` is a generated snapshot, so it is stale.
- **Other copies not touched:** `ast_deps.csv` references `profiler.py`, `profiler_update.py` and `data_pipeline/profiler.py`, which have their own `profile_dataset`. Only `src/data_profiler.py` defines it in the current source, so I left everything else alone.