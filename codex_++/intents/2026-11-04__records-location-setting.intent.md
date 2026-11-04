# Records location as a setting; relay-kit pin — intent, 2026-11-04

@ai-intent: Let people other than Zach point Telosmith at their own relay-kit records, and pin the relay-kit release Telosmith documents. Handoff HO-RK-20261103-5J0W (claude:relay-kit to claude:aec), authorized by Zach 2026-11-03 08:50 CT: "Plan and build it. I also approve Telosmith pinning a tagged relay-kit release" (relay-kit DEC-044, DEC-045). PR only; Zach merges.

## What changed

- `SourceContext.roots` reads an optional `records_root` (alias of the records root; default `records`) and `$RELAYKIT_RECORDS`, which overrides that one root's path. Precedence: env, then `.aec/sources.json`, then unset (`unavailable`).
- An unusable env value (URL, UNC, control characters) drops the records root, so its anchors report `unavailable`. It never falls back to the configured path: the user asked for a different place, and reading the old one silently would mislead.
- This repository's `.aec/sources.json` adds `"records_root": "relay-kit-private"`; the path is unchanged, so Zach sees no difference.
- `docs/integrations/relay-kit.md` is the one place a relay-kit version is named; a test checks every reference agrees.
- `docs/architecture.md` now speaks of "the owner's relay-kit records (made with `relay-kit init`)", with relay-kit-private as Zach's instance.

## Choices and assumptions

- **Env name.** `RELAYKIT_RECORDS` is the variable relay-kit's own handoff and status tools already read, so one setting serves both. A relative value resolves from the working directory, as relay-kit does; config paths stay repo-relative as before.
- **No implicit sibling.** The handoff asked that Zach's layout stay the default. It stays the default *as configured in this repo*; Telosmith does not probe `../relay-kit-private` when nothing names it (SECURITY.md: only configured roots are read). A decoy test pins this.
- **Default alias `records`**, not `relay-kit-private`, so a new user's anchors don't carry Zach's repository name. Existing anchors keep `relay-kit-private` via `records_root`; record lines were not edited.
- **Pin is a commit, not a tag.** The v0.1.0 tag could not be created from the dispatching session (the proxy denies tag writes). Pinned `a7fa03a362ca1c0cd6dc911bec4d9f0b54f9bf7e` (relay-kit main after #13, 134/134 tests); moving to `@v0.1.0` is a one-line change.
- **No pin in init output or CI.** Telosmith does not depend on relay-kit in its package, `aec init` snippets or CI today, so there was nothing to pin there. Adding relay-kit to init output would be a new feature (outside the handoff's "Doesn't cover") and would touch `init.py`, which a sibling branch is changing. `init.py` is untouched.

## Questions for Zach

- Should `aec init` offer the pinned relay-kit install line when a repo uses relay-kit records? That is a feature decision, not part of this handoff.
- Should `docs/failure-modes.md` and `docs/release-readiness.md`, which cite relay-kit-private paths as historical sources, be reworded too? Left as they are: they cite where something was recorded, which is true of Zach's instance.
