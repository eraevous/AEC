# Spec Kit integration

AEC ships a Spec Kit extension (Spec Kit ≥ 1.2.0, tested on v1.2.3) in [`extension/`](../../extension/). Its hooks are optional and report-only: they never edit specs, plans, tasks, the constitution or records.

| Spec Kit step | AEC command it runs | What it reports |
|---|---|---|
| after `specify` | `/speckit-aec-purpose-link` | whether the spec cites the AEC purpose or requirement it serves (`id@version`), and whether that resolves |
| after `tasks` | `/speckit-aec-check` | `aec check` on `.aec/records.jsonl` against a fresh edge snapshot |
| after `implement` | `/speckit-aec-impact` | the structural code diff and the records it affects |

Install, in a repository that already has `.aec/` (run `aec init .` first; it detects Spec Kit and prints this command):

```bash
specify extension add --dev /path/to/AEC/extension      # from a checkout of AEC
specify extension remove aec                            # to remove it
```

Everything the hooks report is structural; a clean result does not show the purpose was preserved. Only install and removal are tested automatically; the hooks' agent-executed behaviour can't be unit-tested. AEC itself is built with Spec Kit: see `specs/` and the build log `docs/speckit-log.md`.
