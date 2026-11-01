## Structural context from AEC

Generated from a static analysis snapshot of this repository (`aec edges`). It lists what the code itself shows about the symbols below. It is structural only.

### `src.connectors.credentials`
- Defined at: not found in the snapshot
- Resolved callers: none found

### `src.connectors.credentials.load_credentials`
- Defined at: src/connectors/credentials.py:45
- Resolved callers (7):
  - `src.cli._build_connector` (src/cli.py:62)
  - `tests.test_credentials.test_load_from_file` (tests/test_credentials.py:19)
  - `tests.test_credentials.test_load_from_env_vars` (tests/test_credentials.py:31)
  - `tests.test_credentials.test_load_from_guide_credentials_file_env` (tests/test_credentials.py:47)
  - `tests.test_credentials.test_wrong_type_raises` (tests/test_credentials.py:55)
  - `tests.test_credentials.test_missing_required_field_raises` (tests/test_credentials.py:66)
  - `tests.test_credentials.test_no_credentials_raises` (tests/test_credentials.py:74)
- Imported by (2; this symbol, its class or its module `src.connectors.credentials`):
  - src/cli.py:60
  - tests/test_credentials.py:5
- Calls (5): `?env_vals.items`, `os.environ.get`, `src.connectors.credentials.CredentialsValidationError`, `src.connectors.credentials._load_file`, `src.connectors.credentials._validate`

Across the repository, 874 of 1578 calls could not be resolved to a target (for example method calls on objects whose type the code does not state), so the caller lists above may be incomplete. No known caller is not proof of no caller.
