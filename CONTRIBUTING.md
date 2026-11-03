# Contributing to Telosmith

Thanks for considering a contribution. Telosmith is small, standard-library Python, and most
changes can be made and tested in a few minutes.

## Set up

```bash
git clone https://github.com/eraevous/Telosmith
cd Telosmith
python3 -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
aec --help
```

Telosmith has no runtime dependencies beyond Python 3.10+. The optional pre-commit hooks
(`.pre-commit-config.yaml`) run ruff: lint, import order and formatting, configured in `pyproject.toml`.

## Run the checks

These are the same commands CI runs (`.github/workflows/ci.yml`):

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m aec edges . -o .aec/edges.jsonl
PYTHONPATH=src python3 -m aec check .aec/records.jsonl --edges .aec/edges.jsonl
PYTHONPATH=src python3 -m aec check examples/mtg-pilot/records.jsonl
```

One test installs Telosmith into a fresh virtual environment, which needs network access to
fetch setuptools; set `AEC_SKIP_INSTALL_TEST=1` to skip it offline. The Spec Kit
extension test skips unless the pinned Spec Kit CLI (v1.2.3) is installed.

## The rules that matter most

These come from the project's [constitution](.specify/memory/constitution.md) and
[charter](CHARTER.md). A pull request that breaks one will be asked to change.

1. **Standard library only, deterministic output.** The same input gives byte-identical
   output, with stable ordering so results diff cleanly.
2. **Every check ships with a violation and a decoy.** A new check or classifier needs at
   least one fixture it must flag and at least one clean fixture it must *not* flag, both
   written before the implementation. Fixtures live under `tests/fixtures/`.
3. **Structural is not semantic.** Output and docs say what the records and code show,
   never that a conclusion is true, a purpose is met or Telosmith improves outcomes, unless a
   recorded measurement backs it (`docs/evaluations/`).
4. **Docs tell the truth.** Every path and `aec` command named in `README.md`, `AGENTS.md`
   and this file must exist; `tests/test_docs_truth.py` checks this.
5. **Keep the CLI thin.** Logic goes in the modules under `src/aec/`; `src/aec/__main__.py` only parses arguments.

## What you may change, and what you may not

You may change code, tests, docs and fixtures through a pull request, as usual.

You may not, even in a pull request:
- edit existing lines of `.aec/records.jsonl` or any other record file (records are append-only: add a new version);
- hand-edit `.aec/edges.jsonl` (regenerate it with `aec edges`);
- mark a proposed decision as accepted, or change Telosmith's purpose or authority records.
  You can *propose* any of these (open an issue); only the maintainer, or someone he names for that
  subject, can accept them.

Larger features follow the Spec Kit workflow used for features 001 to 005 (`specs/`):
open an issue first so the scope can be agreed before you write a spec.

## Where to start

Issues labelled `good first issue` are scoped to one file or one fixture. If nothing is
labelled, the "planned" rows in [docs/history/about.md](docs/history/about.md) and the fixture column of
`docs/failure-modes.md` are the open work.

## Contributions written with AI agents

Welcome, and common here: Telosmith itself is built with Claude, Codex and ChatGPT. Say so in
the pull request, check the generated code as if you wrote it, and make sure the tests
you add would fail without your change.

## Licence and the CLA box

The project is under the [MIT licence](LICENSE). Contributions are made under the
[Contributor License Agreement](CLA.md): they are licensed like the project, you keep your copyright,
and the maintainer may also offer them in commercial versions. Tick the CLA box in the pull request
template to agree. Only the person (or organisation) granting those rights can agree: an agent must
never tick the box on a contributor's behalf. The maintainer's own pull requests, including ones his
agents open for him, don't need it.
