# resolver-001: calls on locals built from a known class (C-11)

**Question.** probe-001 found that its most consequential caller went unresolved because of a common
pattern, `x = C(...); x.m()`. How many unresolved calls does a narrow, deterministic fix for that
pattern resolve, how many of those are correct, what does it deliberately leave unresolved, and
what does it cost?

**Answer, in one line.** On Data-Guide it resolves 25 of the 874 unresolved calls (2.9%). The
probe-001 caller is one of them. All 25 were correct when checked by hand. Eight more calls on
constructor-assigned locals stay unresolved by design, because those locals can hold more than one
value. Extraction takes about 15% longer.

**What this does not show.** Whether resolving these calls changes what an agent does. probe-001's
agents found every dependant without AEC's caller list, so this is a better measuring tool, not a
better outcome. That stays untested until probe-002 (C-12).

## The rule (extractor tool_version 0.4.1)

A function-local name resolves `x.m` against class `C` and C's known bases, exactly as `self.m`
already did, when all of these hold:

- it is assigned exactly once in the function, by a plain top-level statement `x = C(...)` or
  `x: T = C(...)`, not inside `if`, `for`, `while`, `try` or `with`;
- `C` resolves to a class defined in the analysed tree, and neither C nor a known base defines `__new__`;
- the name is not a parameter, a loop, `with` or `except` target, a walrus target, deleted,
  declared `global` or `nonlocal`, imported locally, or defined as a nested function or class;
- the use is in the same function. Closures, module-level code and class bodies are not covered.

An attribute C doesn't define (an instance attribute such as `x.data.fit()`, or a method from an
unknown base) stays unresolved, with why `local_value`. Everything else is unchanged.

## Method

- Target: `eraevous/Data-Guide` at `0607401`, the commit probe-001 froze: 46 Python files and
  2,427 edges. The current head, `51d647a`, gives identical counts.
- Before: AEC main at `364e7fe` (WP1A merged), extractor 0.4.0. After: the C-11 branch, extractor 0.4.1.
- Snapshots are diffed by edge identity (kind, source, destination).
- **Precision:** each of the 25 changed edges was hand-checked against the source: the assignment,
  the class it names (including which of two same-named `BivariateProfiler` classes the local import
  picks), and that the method is defined on that class or its base.
- **Recall:** an independent AST scan found every function-local name assigned from a call to any
  class defined in the repository and later used as `name.method(...)`. Each was classified by why
  the rule does or doesn't apply. The scan matches class names loosely (by last segment), so it
  over-counts candidates, which is the safe direction for recall.
- **Cost:** median of 7 in-process `snapshot()` runs on the same machine.

## Results

| | Before (0.4.0) | After (0.4.1) |
|---|---|---|
| Edges | 2,427 | 2,427 |
| Call edges | 1,578 | 1,578 |
| Unresolved call edges | 874 | 849 |
| of which `local_value` | 519 | 494 |
| Median extraction time | 0.34 s | 0.40 s |

The edge count doesn't change because each of the 25 edges changes its destination: `?x.m` becomes
the method's symbol.

**Precision: 25 of 25 correct.** They break down as:

- `univariate.profile → DataProfiler.profile_dataset` and `profile_columns`. This is the probe-001
  caller (`src/profilers/univariate.py:26-30`).
- Six calls from `DataProfiler.profile_columns` to its plotting and temporal helpers.
- `DataProfiler.profile_bivariate → data_pipeline.bivariate_profiler.BivariateProfiler.profile`.
  This is the class the function-local import names, not the same-named class in `src/profilers/`.
- `cli.profile → StaticReportRenderer.render`, and two calls in the legacy `ast_dependency_cli.analyze`.
- Thirteen calls from tests to connector `connect`/`load` and to the report renderer.

**Recall against the rule: every eligible call resolved.** Eight calls on constructor-assigned
locals stay unresolved by design:

- **Five assigned inside a branch or `try`.** Examples: `cli.run`'s `renderer`, and the SQL and
  Snowflake connector tests. The local may be unbound or hold something else on another path.
- **Three on a reassigned local.** `profile_columns`'s `profiler` is a `StringProfiler` or a
  `NumericProfiler` depending on the column, so it is genuinely ambiguous.

Module-level code (`if __name__ == "__main__":` blocks) is out of scope.

**What's left.** The 494 remaining `local_value` calls are methods on values the extractor can't
type without inference: DataFrames, plot axes, values returned by functions and parameters. The
fix was never meant to touch them. Their cost is unchanged: impact never travels through them.

## Tests

`tests/test_edges.py::TestLocalConstructorCalls` has four violation cases: a direct method, an
inherited method, an annotated assignment and a bound-method reference. Its decoys cover a
reassigned local, a conditional assignment, a parameter, a class with `__new__`, a factory function,
a missing method, an instance attribute, a loop target, an `except` target, a closure, a `global`,
and a class body. The hand-labelled fixture `edges_pkg_v1` had exactly this pattern
(`w = Worker(); w.run()`), labelled unresolved under the old rule. It is relabelled
`pkg.base.Base.run`, the method Worker inherits.

## Reproduce

```bash
git -C Data-Guide worktree add ../dg-0607401 0607401
PYTHONPATH=src python3 -m aec edges ../dg-0607401 -o after.jsonl   # on this branch; before.jsonl from main@364e7fe
```

Snapshots made with extractor 0.4.0 and 0.4.1 report a `tool_version` method difference when
compared (WP1A). Regenerate both sides with the same version.
