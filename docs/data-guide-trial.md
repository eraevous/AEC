# Data-Guide trial (US4, tasks T021–T022), 2026-10-26

Target: `eraevous/Data-Guide` @ main (32 Python files, ~3,200 lines). Ahead of the Spec Kit + AEC overhaul.

## Edge graph
- `python -m aec edges <repo>`: **1,434 edges from 32 files, 0 skipped, ~0.2 s** (3 runs: 0.18 / 0.25 / 0.18 s). SC-002 target is < 2 s.
- Kinds: calls 919, defines 224, imports 206, references 78, inherits 7.
- **53% of call edges are unresolved** (`?x.y`), mostly methods on local objects (DataFrames, plot axes). Static analysis can't type these without inference. Impact only travels through resolved symbols, so these never trigger change impact. They are still recorded and diffed.

## Comparison with the existing `ast_deps.csv` (2025 extractor)
Run from the same root (`src/`), both normalized (`\` → `.`, class stripped from methods to match the old convention):

```
old ast_deps.csv: 1299 edges | new (root=src/): 739 call edges
  780  source function not in current code (CSV is older than the code)
         e.g. ['data_pipeline.api_client.__init__ -> requests.Session', 'data_pipeline.api_client.load_cookies -> os.path.exists']
  279  old defect: method on self/local recorded as a module function (new: resolves self.x or marks ?x)
         e.g. ['data_pipeline.api_client.load_cookies -> data_pipeline.api_client.self.session.cookies.update', 'data_pipeline.api_client.login -> data_pipeline.api_client.self.save_cookies']
  130  old defect: builtin recorded as a module-local call (new: builtins dropped)
         e.g. ['data_pipeline.api_client.load_cookies -> data_pipeline.api_client.open', 'data_pipeline.api_client.load_cookies -> data_pipeline.api_client.print']
   77  same source, callee resolved differently (new resolves through imports, or marks unresolved)
         e.g. ['data_pipeline.bivariate_profiler.__init__ -> os.makedirs', 'data_pipeline.bivariate_profiler.__init__ -> os.path.exists']
   33  match
         e.g. ['data_pipeline.bivariate_profiler.anova_test -> scipy.stats.f_oneway', 'data_pipeline.bivariate_profiler.box_plot -> seaborn.boxplot']
```

What this shows:
- **The old CSV is stale.** 780 of its 1,299 edges come from functions that no longer exist in the code (for example `data_pipeline/api_client.py` is gone, and `bivariate_profiler` no longer calls `os.makedirs`). A dependency file that isn't regenerated on every change drifts away from the code, which is the case for running the bedrock constantly.
- **The old extractor recorded 409 spurious edges:** 130 builtins counted as module functions (`api_client.print`), and 279 methods on `self` or locals counted as module functions (`api_client.self.session.post`). The new extractor drops builtins, resolves `self.x` through the class and its known bases, and marks the rest unresolved.
- Only 33 edges match exactly, and 77 more resolve differently from the same source. The pair of files isn't a fair accuracy benchmark, because the code changed in between. The hand-labelled fixture (`tests/fixtures/edges_pkg_v1`) is the accuracy test: 5/5 edge kinds exact.

## Install (SC-005)
In a copy of Data-Guide: `specify init --here --integration claude` then `specify extension add --dev <AEC>/extension` took **about 1 s**. The skills `/speckit-aec-purpose-link`, `/speckit-aec-check` and `/speckit-aec-impact` appear, and three optional hooks are registered.

## Records smoke test
A provisional `DG-P0` purpose and two requirements were linked to code with `implemented_by`. One link was deliberately misspelled (`…BivariateProfilr`). `aec check --edges` reported it as a dangling code reference and passed the correct one.

## For the overhaul
- Start by running `aec edges` and committing `.aec/edges.jsonl`. Delete `ast_deps.csv`, `ast_dependency_cli.py` and `combine_scripts.py`, or keep them only as history.
- Write the Data-Guide purpose as **provisional** until the overhaul's `/speckit-specify` settles it. Changes to it then show as `exploratory`, not drift.
