# Implementation Plan: source anchors and retrieval (WP-S)

**Branch**: speckit/004-source-anchors · **Spec**: [spec.md](spec.md) · **Date**: 2026-10-30
**Base**: 1afec55 · **Serves**: AEC-P0@1, AEC-R2@1, failure mode P8.

## Technical context and constitution check

Python 3.10+, standard library only; unittest. Record.data already retains optional
anchors and rationale. Do not change the vocabulary, propagation, prior record
lines or reconstructed decision statuses. Source access is read-only and local;
no provider, execution, network access, indexing service or source copying.
Principles I/IV: integrity/locator observations do not establish meaning or consent.
II/VI: deterministic paths/order, raw-byte hashes, explicit root confinement.
III: violation and clean decoy tests precede implementation. V: record cost and
actual checks; no evaluation or comparative-benefit claim.

## Design and explicit interpretations

- Add src/aec/sources.py for shape validation, root configuration, inspection,
  passage rendering and direct fallback search. records.check accepts an optional
  source context and adds errors for malformed anchors/rationale and warnings for
  non-verified filesystem states. Verified anchors yield no Finding; the CLI also
  prints their state, so every anchor is accounted for without flagging the decoy.
- Shape: anchors must be a list of objects; path is a nonempty relative file path,
  confined to its root; root is optional/string, digest is 64 hex, for is text or
  rationale, locator is positive/inclusive L<n> or L<a>-<b>, or nonempty single-line
  q:text. rationale, when present, is a string. Escape paths are malformed; symlink
  escapes/unreadable sources are unavailable, never read. File absence in an
  available directory is missing; absent/unconfigured root is unavailable.
- Precedence: validate shape, resolve root, read file, compare raw-byte SHA256,
  resolve locator. A digest mismatch takes precedence over locator_invalid. Still
  resolve a current-file locator so show can display current text with a warning.
  An invalid locator has no passage to show; do not substitute unrelated content.
- .aec/sources.json maps aliases to local paths (absolute or repo-relative). The
  implicit repository root is used by anchors without root; search --root . selects
  it explicitly. Default search covers named configured roots, not the entire
  repository implicitly. --root R selects a configured alias, never an arbitrary
  extra path. Unknown selected alias/configuration errors are CLI usage errors.
- CLI: retain check RECORDS [--edges], add --repo ROOT; default repo is inferred
  from RECORDS under .aec/, otherwise cwd. source show/search also accept --repo
  ROOT and --records PATH (default ROOT/.aec/records.jsonl). This supplies the
  repository/record inputs omitted from the short command sketches in the spec.
- UTF-8 with replacement is used only for text views; hashes always use raw bytes.
  Line numbering follows splitlines, including CRLF handling; quotes match within
  one line and select the first occurrence. Missing/unavailable sources show no
  passages. Rendered source is sent to stdout, never saved by AEC.
- show context is nonnegative and max-lines positive, capped per anchor passage
  including context, with explicit omitted-line count. search max is nonnegative
  (default 20); literal matching is default, regex explicit. Search counts matching
  lines, sorts by displayed path then line (root alias breaks ties), and counts all
  omitted matching lines. It reports the current file digest and all anchoring
  record versions, even when those anchors pin older bytes.
- Search does not follow directory symlinks (avoids cycles); in-root file symlinks
  are readable. Resolve containment before reading each regular file; never read
  external symlinks, devices or pipes. Absent/unreadable roots/files get explicit
  visibility notes. Configuration cannot name URL/UNC remote providers.
- Cache inspections within one command to avoid checking and displaying different
  reads of an anchor. No persistent source cache or copying into the repository.
- Synthetic fixture metadata goes in tests/fixtures/anchors/. Synthetic source
  files are created in temporary directories by tests, not copied from a corpus.

## Project structure and validation

src/aec/sources.py; records.py/check integration; thin CLI dispatch; test_sources.py
and fixture metadata. README documents hashing, root/CLI semantics, state ordering,
limits and optional rationale. AGENTS lists the built source command. Output
schema/templates are tested for structural labels and forbidden attestation words;
source contents are exempt (a quote is data, not an AEC assertion).

Run every frozen fixture; test all record types, legacy decoys, escape confinement,
exact context/line bounds, search without records, stale-file associations, malformed
configuration/regex/limits, no execution/network, read-only behavior and repeated
byte-identical CLI output. Then full existing suite, canonical/example checks,
regenerate edges from product sources, and record final cost/issues in the intent.
