# Implementation Plan: AEC reconciled with itself (WP0)

**Spec**: [spec.md](spec.md) · **Implementer**: Codex (cold) · **Date**: 2026-10-28

## Technical context
Python 3.10+, standard library only (Constitution II). The code involved:
- `src/aec/purpose_import.py`: parse, `_resolve`, `import_purpose`;
- `src/aec/records.py`: Store, check;
- `src/aec/__main__.py`: CLI.

Tests use `unittest`; run them with `PYTHONPATH=src python3 -m unittest discover -s tests`. Spec Kit 1.2.3 is pinned, but the implementer does not need Spec Kit to do this work.

## Constitution check
I (records govern purpose), II (stdlib, deterministic), III (violation plus decoy per check), IV (claim honesty) and VI (structural facts from code) all apply. The reconstructed decisions must not look accepted (I, IV).

## Design decisions (fixed; raise concerns in the intent note rather than changing them silently)
- **P1 Field parsing.** Extend `HEADER` so it also matches lines starting with `#` (the `ast_dependency_extractor` file uses `# @ai-source-file`). Source files = union of `ai-source-file` and `ai-source-files`, each parsed with `_list`. If both are present, also record a `duplicate-source-field` finding.
- **P2 Sections.** Split the body on Markdown headings (any level). Normalise each title by removing emoji, numbering and punctuation, then lower-casing. Map titles to keys with a small table: intent/responsib → responsibilities; input/output → io; risk → risks; dependenc → dependencies; integration/pipeline → integration; test guarantee → guarantees. Parse Markdown tables in the io section into rows of `{direction, name, type, description}`, keeping unrecognised columns. Keep every other section's raw text in `declared_sections`.
- **P3 No ingestion cap.** Remove `MAX_TEXT` from ingestion. `render()` may shorten for display and must say so.
- **P4 Reconstructed decisions.** Add a small, separate, reviewable script `tools/reconstruct_decisions.py` (not a CLI command). It reads a hand-written input file, `.aec/reconstructed/2026-10-history.jsonl`, in which each line names a decision, its text, the source path and section, and what it supersedes. The script appends `source` and `decision` records with `origin: reconstructed`, `status: proposed` and the source's sha256, then writes `docs/decisions-to-confirm.md`. Writing the input file is the judgment work: the implementer reads the logs and specs and states each decision in one sentence, with no embellishment.
- **P5 Docs.** The new `AGENTS.md` is under about 120 lines. The old protocol moves to `docs/history/codex-plus-plus-AGENTS.md` with a one-line note at the top explaining what it was. `CHARTER.md` becomes AEC's engineering rules or an explicit pointer to the constitution's principles. `VISION.md` references point to what exists.
- **P6 Doc-truth test.** `tests/test_docs_truth.py` extracts backticked repository paths and `python -m aec <sub>` / `aec <sub>` mentions from `README.md` and `AGENTS.md`. It asserts that each path exists and each subcommand is registered in the CLI parser. A small decoy fixture checks that the test does fail on a bad path.

## Project structure
```
src/aec/purpose_import.py             P1-P3
tools/reconstruct_decisions.py        P4
.aec/reconstructed/2026-10-history.jsonl   P4 input (hand-written, reviewed)
docs/decisions-to-confirm.md          P4 output (generated)
AGENTS.md, CHARTER.md, README.md      P5
docs/history/codex-plus-plus-AGENTS.md     P5
tests/test_import_purpose.py (+ fixtures), tests/test_docs_truth.py
codex_++/intents/<date>__wp0-implementation.intent.md   FR-010
```
