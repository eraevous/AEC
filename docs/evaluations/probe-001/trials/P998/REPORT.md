# Report: credentials.py removal (P998)

## What I changed
Nothing. I did not delete `src/connectors/credentials.py` or `tests/test_credentials.py`.

## Why
The premise ("nothing in `connectors/` imports it") is true but misleading. The importer is outside `connectors/`:
- `src/cli.py:60` runs `from connectors.credentials import load_credentials` inside the `snowflake` branch of `_build_connector`. The import is lazy, inside the function, so a grep for top-level imports misses it.
- `src/cli.py:62-66` calls `load_credentials("snowflake", credentials_path=credentials_path or cfg.get("credentials"))` and passes the result to `SnowflakeConnector`.
- `_build_connector` is called from `src/cli.py:148` and `src/cli.py:182`. The `--credentials` CLI option at `src/cli.py:124` exists to feed this loader.

`SnowflakeConnector` does take a plain dict. That dict is built by `load_credentials`, which handles the `--credentials` file, the `GUIDE_CREDENTIALS_FILE` env var, the `SF_*` env vars, and validation. Deleting the module would make `--connector snowflake` fail with ImportError at runtime. The tests would not catch it, because `tests/test_cli.py` doesn't exercise that branch. Deleting `tests/test_credentials.py` would also remove the only coverage of this loader.

The AEC snapshot listed `src/cli.py:60` and `:62` as callers/importers of `load_credentials`. Its "not found" entry for the module symbol itself is just a module-vs-symbol resolution gap.

## For the requester
- If the goal is to remove the credentials loader, `cli.py` needs a replacement first. Options are to build the dict inline from env vars, or to require the credentials file to be passed straight to `SnowflakeConnector`. That would drop the `GUIDE_CREDENTIALS_FILE` and `SF_*` behaviour that `docs/superpowers/specs/2026-04-20-eda-tool-design.md` (lines ~95-96) specifies. That is a design decision for you, not a cleanup.
- If you only want less scaffolding, I can do that separately. One option is to leave the module as is and add a CLI test for the snowflake branch.
- `src/data_guide.egg-info/SOURCES.txt` also lists both files. It is generated, so I didn't touch it.
