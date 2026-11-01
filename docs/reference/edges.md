# The edge snapshot (`aec edges`)

The structural map AEC builds from Python source: what defines, calls, imports, inherits from and refers to what. It is generated, never committed (see `.aec/.gitignore`).

```bash
PYTHONPATH=src python3 -m aec edges . -o .aec/edges.jsonl          # what defines/calls/imports/inherits/refers to what
PYTHONPATH=src python3 -m aec edges --diff old.jsonl .aec/edges.jsonl   # what changed structurally
PYTHONPATH=src python3 -m aec check .aec/records.jsonl --edges .aec/edges.jsonl   # dangling code: references
PYTHONPATH=src python3 -m aec code-impact .aec/records.jsonl old.jsonl .aec/edges.jsonl  # which conclusions a code change affects
```

- **Deterministic and stdlib-only**, fast enough to run after every edit: Data-Guide (32 files) takes about 0.2 s. It runs automatically through `.claude/settings.json` (PostToolUse) and in CI.
- Records point at code with `code:<dotted.symbol>` (for example `implemented_by`). A changed symbol makes the conclusions resting on it `stale`. A deleted one makes claims that `depends_on` it `unjustified`; requirements and purposes only lose their recorded satisfaction (`needs_review` plus a finding), and decisions are only flagged. Evidence `observed_on` changed code needs an applicability review and is never invalidated. A code dependency is not a justificatory dependency: see the invariant in `docs/reasoning-vocabulary.md`.
- Dynamic calls are kept as unresolved `?expr` targets and never guessed. On Data-Guide about half of all calls are unresolved (methods on local objects). They never trigger impact by themselves.
- It replaces the 2025 `src/core/tools/ast_dependency_extractor.py` (pandas and typer, calls only, methods lost their class). `--legacy-csv` writes the old format for comparison. See `docs/data-guide-trial.md`.
