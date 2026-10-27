# AEC Spec Kit extension

Adds AEC's checks to the Spec Kit flow (Spec Kit ≥ 1.2.0). All hooks are **optional** and **report-only**: they never edit specs, plans, tasks, the constitution or records.

| hook | command | what it reports |
|---|---|---|
| `after_specify` | `/speckit-aec-purpose-link` | whether the spec cites the AEC purpose or requirement it serves (`id@version`), and whether those resolve |
| `after_tasks` | `/speckit-aec-check` | `aec check` on `.aec/records.jsonl` against a fresh code edge snapshot |
| `after_implement` | `/speckit-aec-impact` | the structural code diff, plus the records, claims and decisions it affects |

## Install

```bash
pip install git+https://github.com/eraevous/AEC        # the aec commands (stdlib only)
specify extension add --dev /path/to/AEC/extension      # from a checkout
# or: specify extension add aec --from <release zip URL>
```

## Remove

```bash
specify extension remove aec
```

## Labels

Everything AEC reports is **structural**. A clean result does not show that the purpose was preserved. That still takes judgment.
