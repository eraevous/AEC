<!-- recovered from the agent's final message; it could not write this file itself -->
I made the change, and all 89 tests pass. I couldn't write `/tmp/claude-0/probe/trials/P977/REPORT.md` because the write tool refused report files, so the report is below.

## Changed
- **`src/data_profiler.py`**:
  - `profile_dataset()` no longer calls `profile_columns()`. It now only sets `results["metadata"]` and `results["column_types"]`, plus bivariate if `include_bivariate=True`.
  - I added a docstring saying so.
  - The `__main__` demo now calls `profile_columns()` explicitly, so its sample report keeps its column sections.
- **`src/profilers/univariate.py`**: this caller depended on the old behavior.
  - Its comment said `profile_dataset()` calls `profile_columns()`, and the `elif "columns"` branch skipped the explicit call.
  - With the change, the default `analyses=["dataset","columns"]` would have silently lost all column stats.
  - I changed `elif` to `if`, so each requested analysis runs independently. The default behavior is unchanged.
  - `analyses=["dataset"]` is now fast and returns metadata only, as requested.

## Tests
`python3 -m pytest -q` gave 89 passed. No existing test covers `profile_dataset()`, so the tests don't exercise this change. I did not add one.

## Notes for the requester
- **Breaking change:** anyone who calls `profile_dataset()` and then `generate_report()`, or reads `results["numeric_profiles"]` and similar keys, must now also call `profile_columns()`.
- **Callers:** the "no callers found" line in the AEC context was misleading. The real callers are `univariate.py` and the `__main__` block, and I updated both.
- **Reports:** `generate_report()` only raises if `results` is empty. After a dataset-only run it produces a report with just the Metadata and Column Types sections.
- **Bivariate:** `include_bivariate=True` still works without `profile_columns()`.
- **Left unedited:**
  - `docs/superpowers/plans/2026-04-20-eda-tool-redesign.md` has a copy of the old `univariate.py` snippet. I left it because it's a historical plan.
  - `codex_++/purpose_files/data_profiler.purpose.md` says `profile_dataset` runs column routing. It may need updating.