# Report

## What I changed
Nothing. I did not delete `src/connectors/credentials.py` or `tests/test_credentials.py`.

## Why
The premise of the request is wrong: the module is not dead code. Nothing inside `connectors/` imports it, but `src/cli.py` does, in `_build_connector`, snowflake branch (around line 60):

    from connectors.credentials import load_credentials
    creds = load_credentials("snowflake", credentials_path=credentials_path or cfg.get("credentials"))
    return SnowflakeConnector(credentials=creds, ...)

`SnowflakeConnector` does take a plain dict, but the CLI builds that dict with `load_credentials` (file path, config, env var lookup and validation). Deleting the module would make `--connector snowflake` fail with ImportError at runtime. The imports are lazy (inside the function), so the tests would not catch it. The `--credentials` CLI option also depends on it. The module and its tests are listed in the April redesign plan (`docs/superpowers/plans/2026-04-20-eda-tool-redesign.md`) as intended deliverables.

Test status: `tests/test_credentials.py` and `tests/test_cli.py` pass (14 passed). The full suite is slow (more than 2 minutes) but finished with exit code 0.

## For the requester
- If you do want to retire it, first decide how the CLI should get Snowflake credentials (for example inline in the config dict only), then remove the `--credentials` option and the import in `src/cli.py` and update the docs. Then delete the module and tests.
- `src/data_guide.egg-info/SOURCES.txt` also lists both files (a generated artifact, would need regenerating).
- Happy to do that follow-up if you confirm the CLI should drop file-based credential loading.
