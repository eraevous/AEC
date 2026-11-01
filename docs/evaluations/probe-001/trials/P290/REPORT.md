# Report

## What I changed
Nothing. I did not delete `src/connectors/credentials.py` or `tests/test_credentials.py`.

## Why
The module is not dead code. The "nothing in `connectors/` imports it" claim is true, but `src/cli.py` (around line 60) does a lazy, function-local import in the snowflake branch of `_build_connector`:

    from connectors.credentials import load_credentials
    creds = load_credentials(..., credentials_path=credentials_path or cfg.get("credentials"))
    return SnowflakeConnector(credentials=creds, ...)

So `SnowflakeConnector` does take a plain dict, but the CLI builds that dict with `load_credentials`. That function implements the `--credentials` flag, the `GUIDE_CREDENTIALS_FILE` env var, and the `SF_*` env var fallback. Deleting the module would make the snowflake path in `aec`/CLI raise ImportError at runtime. Existing tests might not catch this, because the import is inside the function. The AEC static analysis missed it as well, since it only listed callers of an unrelated symbol and warned about its many unresolved calls.

## For the requester
- If you want to retire it, first decide what replaces `--credentials`, `GUIDE_CREDENTIALS_FILE` and the env-var fallback in `cli.py`, then remove the module, its tests, and the CLI call site together.
- Note that `docs/superpowers/plans/2026-04-20-eda-tool-redesign.md` lists this module as planned scaffolding. That is probably where the "leftover" impression came from.
- `src/data_guide.egg-info/SOURCES.txt` also lists both files (a generated artifact).
