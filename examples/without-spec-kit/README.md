# Telosmith without Spec Kit: the scratch project

The project, records and hook scripts used in
[docs/integrations/without-spec-kit.md](../../docs/integrations/without-spec-kit.md) and
[docs/use-cases.md](../../docs/use-cases.md).

- `project/`: the `shop` package (`shop/pricing.py`, `shop/tax.py`), `docs/pricing.md`, and `.aec/records.jsonl`,
  as written by `aec init . --owner "Ada"` plus the appended lines. `R-1`'s anchor holds the sha256 of
  `docs/pricing.md` as shipped; edit that file and `check` reports `anchor-mismatch`.
- `pre-commit`, `pre-push`, `append-only.sh`: the git hooks and guard from the integration doc.
- `run.sh`: runs every path on the page in a temporary git repo (no `.specify/`), offline, in a few seconds.

```bash
PYTHONPATH=src examples/without-spec-kit/run.sh      # from a Telosmith checkout; or with aec pip-installed
```
