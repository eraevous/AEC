# Report

## Changes
- `src/data_profiler.py`: `profile_dataset()` no longer calls `profile_columns()`. It now sets only `results["metadata"]` and `results["column_types"]` (plus bivariate if requested). The `__main__` demo now calls `profile_columns()` explicitly so its report still has column sections.
- `src/profilers/univariate.py`: this is the only internal caller (used by the CLI `profile` command, which defaults to `analyses=["dataset","columns"]`). It relied on `profile_dataset()` running columns, with a comment saying so. I changed `if/elif` to two independent `if`s, so "dataset" and "columns" each run what they name. CLI behaviour is unchanged. Previously `analyses=["columns"]` alone worked and still does.
- `codex_++/purpose_files/data_profiler.purpose.md`: updated the `profile_dataset` description (CHARTER requires purpose files to stay in sync).

## Tests
`python3 -m pytest -q`: 89 passed (about 85s).

## Notes for the requester
- This is a behaviour change for any external caller that used `profile_dataset()` and then read `numeric_profiles`, `string_profiles`, `plots`, etc. from `results`. They must now call `profile_columns()`. I found no other callers in the repo (notebooks and other scripts aren't present as .py files).
- `generate_report()` after only `profile_dataset()` works (it tolerates missing sections) but omits the column sections and the missing-value matrix.
- No test covers `profile_dataset()` skipping columns; I didn't add one.
