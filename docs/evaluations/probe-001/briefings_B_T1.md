## Structural context from AEC

Generated from a static analysis snapshot of this repository (`aec edges`). It lists what the code itself shows about the symbols below. It is structural only.

### `src.data_profiler.DataProfiler.profile_dataset`
- Defined at: src/data_profiler.py:541
- Resolved callers: none found
- Imported by (1; this symbol, its class or its module `src.data_profiler`):
  - src/profilers/univariate.py:3
- Calls (8): `?self.df.duplicated`, `?self.df.duplicated(...).sum`, `?self.df.isna`, `?self.df.isna(...).sum`, `?self.df.isna(...).sum(...).sum`, `?self.type_resolver.as_dict`, `src.data_profiler.DataProfiler.profile_bivariate`, `src.data_profiler.DataProfiler.profile_columns`

Across the repository, 874 of 1578 calls could not be resolved to a target (for example method calls on objects whose type the code does not state), so the caller lists above may be incomplete. No known caller is not proof of no caller.
