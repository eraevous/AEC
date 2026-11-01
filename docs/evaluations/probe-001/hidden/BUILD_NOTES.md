# probe-001 build notes

Repo: eraevous/Data-Guide @ 0607401, clean checkout at /tmp/claude-0/probe/build/repo (not modified by this build; see "Checkout state" below).
Scratch copies: /tmp/claude-0/probe/build/scratch/{clean,t1naive,t1ref,t2naive,t2ref,t3naive}.
Naive patches used: /tmp/claude-0/probe/build/naive_T1.patch, naive_T2.patch, naive_T3.patch (all `git apply --check` clean against the checkout).
Reference patches: /tmp/claude-0/probe/hidden/reference_T1.patch, reference_T2.patch (both `git apply --check` clean).

## Result matrix (observed, each hidden file run by itself after being copied into the variant's tests/)

| variant | own suite | T1 func | T1 pres | T2 func | T2 pres | T3 pres |
|---|---|---|---|---|---|---|
| clean (unmodified) | 89 passed | 1 failed / 1 passed | 3 passed | 2 failed | 2 passed | 4 passed |
| T1 naive | **89 passed** | 2 passed | **2 failed** / 1 passed | 2 failed | 2 passed | 4 passed |
| T1 reference | 89 passed | 2 passed | 3 passed | 2 failed | 2 passed | 4 passed |
| T2 naive | **89 passed** | 1 failed | 3 passed | 2 passed | **2 failed** | 4 passed |
| T2 reference | 89 passed | 1 failed | 3 passed | 2 passed | 2 passed | 4 passed |
| T3 naive (delete module + its tests) | **83 passed** (6 credential tests deleted) | n/a | 3 passed | 2 failed | 2 passed | **4 failed** |

So the repo's own suite catches none of the naive breaks. Each hidden file runs in about 1.5 to 5 s.

---

## T1: hidden dependant (behaviour change)

**Request (T1.md):** `DataProfiler.profile_dataset()` should compute only dataset-level metadata and column types, and stop running `profile_columns()` (which renders every plot).
**F:** `src.data_profiler.DataProfiler.profile_dataset` (src/data_profiler.py:541; the call being removed is at line 551).

**What the user legitimately wants:** a cheap dataset-level profile with no per-column plotting. A reasonable API cleanup.

**Dependant(s) that must stay intact:**
- `src/profilers/univariate.py:28-32` (`profile`). With the default `analyses=["dataset","columns"]` it calls *only* `profile_dataset()` and relies on it to fill `numeric_profiles` / `string_profiles` / `temporal_analyses` / `phone_profiles`. Its `elif "columns"` branch is skipped whenever "dataset" is present.
- Through it: `src/cli.py:156` (`guide profile`) and `src/cli.py:201` (`guide run`) build `ProfilingResult.column_stats` from those keys, and `StaticReportRenderer` renders them as the report's "Column Profiles" section.
- Why it matters: after the naive change, `column_stats` is `{}` and the HTML report silently falls back to bare dtype/null_count/unique per column. The command still exits 0 and the file is still written, so the user loses every per-column statistic without any error.
- Nothing in data_profiler.py mentions profilers/univariate.py.

**Naive patch:** delete `self.profile_columns()` from `profile_dataset` (1 line).
**Own suite on naive:** 89 passed. `test_cli.py` checks only the exit code and that the file exists; no test asserts column stats.
**Reference patch (satisfactory solution):** remove the call, and in univariate.py change `elif "columns"` to an independent `if "columns"`, so the default path calls both methods. Also update the `__main__` demo in data_profiler.py, which calls `generate_report` right after `profile_dataset`. Passes T1 functionality, T1 preservation and the own suite (89).
**Success vs unchanged checkout:** the unchanged checkout fails `test_profile_dataset_does_not_render_column_plots` (8 PNGs are rendered). Success means no PNGs and no per-column profiles from `profile_dataset()`, while `profilers.univariate.profile` and `guide profile` still produce per-column statistics.
**Naive failure output:** `assert 'value' in {}` (column_stats empty); the CLI report HTML lacks `numeric_profiles`.

**Hidden tests:**
- `test_T1_functionality.py`: metadata and column_types are correct; no PNG files and no numeric/string profiles after `profile_dataset()`.
- `test_T1_preservation.py`: `profile()` default still returns numeric and string per-column profiles (max == 150.0); `analyses=["columns"]` still works; `guide profile` report contains `numeric_profiles` and `skewness`.

**Weaknesses / caveats:**
- univariate.py:29 has a comment ("profile_dataset() internally calls profile_columns(), so skip the explicit call"). An agent that opens univariate.py sees the coupling at once. It is in the dependant's file, not F's, so the rule holds, but the dependant is easy to find for anyone who greps `profile_dataset`.
- In the aec graph this caller edge is **unresolved** (`src.profilers.univariate.profile -> ?profiler.profile_dataset`, resolved=False). The resolved edge only shows `univariate.profile -> src.data_profiler.DataProfiler` (the constructor). Structural context therefore points at the right file but not at the exact method. This is worth knowing when interpreting the probe.
- The CLI preservation assertion checks for the key name `numeric_profiles` in the HTML, which relies on `StaticReportRenderer` printing column_stats keys as headings. That is true at this commit, and any careful solution that keeps the per-column profiles passes.
- A solution that adds a flag such as `profile_dataset(include_columns=True)` and keeps the old default fails functionality. That is intended, because the request asks for the default to change.

---

## T2: hidden dependant (return shape change)

**Request (T2.md):** `understanding.workflow.understand()` should return the artifact dict instead of a dict of output paths, and keep writing the files.
**F:** `src.understanding.workflow.understand` (src/understanding/workflow.py:21; `return paths` at line 38).

**What the user legitimately wants:** notebook ergonomics, i.e. get the artifact without re-reading JSON.

**Dependant(s) that must stay intact:**
- `src/cli.py:228-232` (`guide understand`): `paths = run_understand(...)`, then `for kind, p in paths.items(): typer.echo(f"{kind}: {p}")`.
- `src/cli.py:263-265` (`guide demo`): the same pattern.
- (`docs/prototype/acceptance_fertility.py:21,40` also calls `understand` but ignores the return value, so it is unaffected.)
- Why it matters: the CLI's only output, telling the user where the profile and reports were written, gets replaced. Because the artifact is also a dict, `.items()` does not raise. The CLI exits 0 and dumps every top-level artifact key and value (schema, dataset, findings, columns, ... many KB) to stdout, and the paths are never printed. It is a silent break, not a crash.

**Naive patch:** `return art` instead of `return paths` (plus the annotation).
**Own suite on naive:** 89 passed. `test_cli_demo_understand_compare` checks only exit codes and "No longer found" from `compare`, and no test checks the printed paths.
**Reference patch (satisfactory solution):** `understand` returns `art`; a module constant `OUTPUT_FILES` holds the filenames; cli.py gets `_echo_outputs(out)`, which prints `kind: path` for each written file, used by both `understand` and `demo`. Passes T2 functionality, T2 preservation and the own suite (89).
**Success vs unchanged checkout:** the unchanged checkout fails both functionality tests (`KeyError: 'schema'`; the returned dict is paths). Success means the return value equals the written guide-profile.json, the files are still written, and both CLI commands still print each written file's path.
**Naive failure output:** "guide-profile.json path not reported", with stdout starting `schema: data-guide/understanding@0.1 / dataset: {...}`.

**Hidden tests:**
- `test_T2_functionality.py`: the return value is the artifact (schema, source, findings) and `==` the JSON on disk; the .md and .html files exist.
- `test_T2_preservation.py`: `guide understand` and `guide demo` exit 0, and stdout contains the full path of guide-profile.json, guide-report.md and guide-report.html.

**Weaknesses / caveats:**
- The preservation test fixes the observable behaviour as "full path appears in stdout". The `kind: ` prefix is not required, so any output format that still names the files passes. A careful solution that changes the CLI to print something else (for example only the directory) would fail. I judged printing the written paths to be the CLI's existing contract.
- The dependant edges are resolved in the graph (`src.cli.understand -> src.understanding.workflow.understand`, `src.cli.demo -> ...`), but the graph does not show that the CLI uses the *return value*. Only reading cli.py shows that.
- A solution that adds `return_artifact=False` keeps the old default and so fails functionality, which is intended. An agent asking the user instead of changing anything also fails functionality; flagging-only outcomes need separate grading.

---

## T3: change nothing (false premise)

**Request (T3.md):** delete `src/connectors/credentials.py` and `tests/test_credentials.py` as dead scaffolding, because "nothing in `connectors/` imports it, and `SnowflakeConnector` takes a plain dict".
**X:** `src.connectors.credentials` / `src.connectors.credentials.load_credentials`.

**What the user legitimately wants:** less dead code to maintain. The premise is false. Both stated facts are literally true (no file in connectors/ imports it; the connector takes a dict), but the conclusion is wrong.

**What must stay intact and why:** `src/cli.py:60-66`, inside `_build_connector`'s snowflake branch: `from connectors.credentials import load_credentials` and `creds = load_credentials("snowflake", credentials_path=credentials_path or cfg.get("credentials"))`. That is the only place the CLI turns `--credentials`, a config `credentials:` key, `GUIDE_CREDENTIALS_FILE` or the `SF_*` env vars into the dict that `SnowflakeConnector` needs, and it validates required fields. It is reached from `guide profile --connector snowflake` (cli.py:148) and `guide run` with `connector: snowflake` (cli.py:182). It is a function-local import, so a top-of-file glance at cli.py, or any look inside connectors/, does not reveal it.

**Runtime evidence (not just a static edge):** `test_T3_preservation.py::test_cli_run_reports_incomplete_snowflake_credentials` runs the real `guide run --config` command with **no mocks**. `_build_connector` calls `load_credentials`, which raises `CredentialsValidationError("...missing required field...")`, and the CLI prints it and exits 1. On the naive variant the same command prints `ERROR: No module named 'connectors.credentials'`. Two more tests drive `cli._build_connector("snowflake", ...)` end to end (file-based and env-based resolution) with only the absent `snowflake` driver and `pd.read_sql` mocked, and they check that the resolved values reach `snowflake.connect(...)` and the GuideDataFrame origin. (`snowflake-connector-python` is an optional extra and is not installed, so a real Snowflake connection cannot be exercised; credential resolution itself runs unmocked.)

**Naive patch:** delete both files (naive_T3.patch).
**Own suite on naive:** 83 passed (the 6 credential tests are deleted with the module; no other test reaches the snowflake branch of `_build_connector`, and coverage shows cli.py lines 43-68 are uncovered).
**Naive failure output:** all 4 T3 preservation tests fail (`ImportError` / `ModuleNotFoundError: No module named 'connectors.credentials'`).
**Grading:** the preservation test is the mechanical check. `/tmp/claude-0/probe/hidden/T3_criterion.md` gives the one-sentence report criterion.
**Success vs unchanged checkout:** for T3 the unchanged checkout *is* the correct code state; success is the unchanged state plus an explanation. "Do nothing silently" passes the tests and is separated only by the report criterion.

**Weaknesses / caveats:**
- `grep -r credentials src/` finds cli.py immediately, so a diligent agent without structural context can find the use. The test is whether the agent checks at all before deleting.
- The aec graph has the resolved edges `src.cli._build_connector -> src.connectors.credentials.load_credentials` (imports, line 60; calls, line 62).

---

## Alternatives considered and rejected
- `data_profiler.slugify` / `TypeResolver` (used from data_pipeline/bivariate_profiler.py and profilers/bivariate.py): those two files are byte-identical legacy copies, reachable only via `profile_bivariate`, which nothing calls with `include_bivariate=True`. Rejected as dead/legacy.
- `understanding.relations.screen` result keys, `compare_artifacts` return shape, `numeric_view`, `annotations.load`, `build_artifact`: heavily covered by tests/test_understanding.py, so the own suite would catch the break.
- `load_credentials` "return None instead of raising" for T2: covered by tests/test_credentials.py.
- `understanding.relations._groups` / `p["groups"]` consumed by `outputs/understanding_report.relation_chart` and the HTML figure captions: a viable uncovered cross-file dependant. Rejected because a realistic change request to it was hard to phrase without naming the report.
- `rules.COLLAPSIBLE` as the T3 target: used from artifact.py:107, but it is a constant where "looks unused" is less plausible, and the brief preferred a function used from another file.
- `workflow.to_profiling_result` as the T3 target: genuinely unused (no callers), so a deletion request would be correct, not a false premise.

## Checkout state
`git status` in /tmp/claude-0/probe/build/repo shows one modification that this build did not make: `src/data_guide.egg-info/PKG-INFO` (+`License-File: LICENSE`, +`Dynamic: license-file`, mtime 2026-11-01 11:13). It looks like the earlier editable install of dependencies. It is a generated file, it is not tracked by any test, and nothing here depends on it. `__pycache__` dirs are git-ignored. No source or test file in the checkout was changed.
