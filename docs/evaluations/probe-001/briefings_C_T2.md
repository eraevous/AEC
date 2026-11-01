## Structural context from AEC

Generated from a static analysis snapshot of this repository (`aec edges`). It lists what the code itself shows about the symbols below. It is structural only.

### `src.connectors.credentials.CredentialsValidationError`
- Defined at: src/connectors/credentials.py:16
- Resolved callers (3):
  - `src.connectors.credentials._load_file` (src/connectors/credentials.py:23)
  - `src.connectors.credentials._validate` (src/connectors/credentials.py:32)
  - `src.connectors.credentials.load_credentials` (src/connectors/credentials.py:78)
- Imported by (1; this symbol, its class or its module `src.connectors.credentials`):
  - tests/test_credentials.py:5
- Referenced (not called) by (3):
  - `tests.test_credentials.test_wrong_type_raises` (tests/test_credentials.py:54)
  - `tests.test_credentials.test_missing_required_field_raises` (tests/test_credentials.py:65)
  - `tests.test_credentials.test_no_credentials_raises` (tests/test_credentials.py:73)

Across the repository, 874 of 1578 calls could not be resolved to a target (for example method calls on objects whose type the code does not state), so the caller lists above may be incomplete. No known caller is not proof of no caller.
