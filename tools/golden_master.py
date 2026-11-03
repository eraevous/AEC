#!/usr/bin/env python3
"""Golden master: run every command on fixed inputs and compare outputs byte for byte.

A refactor that claims "no behaviour change" must leave every output identical. Save a baseline from
the code before the change, then compare the code after it:

    PYTHONPATH=src python3 tools/golden_master.py --save /tmp/gold-before [--extra PATH ...]
    # ...refactor...
    PYTHONPATH=src python3 tools/golden_master.py --compare /tmp/gold-before [--extra PATH ...]

Inputs are the repository's own fixtures and examples. `--extra PATH` adds a Python tree (such as a
checkout of another project) to the extraction cases, which is how real-world code is covered without
shipping it. Outputs record stdout, stderr and the exit code; local paths are replaced so baselines
taken from different checkouts compare. Standard library only.
"""
from __future__ import annotations

import argparse
import filecmp
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def cases(work: Path, extras: list[Path]) -> list[tuple[str, list[str]]]:
    fx, ex = "tests/fixtures", "examples"
    v1, v2 = work / "v1.jsonl", work / "v2.jsonl"
    out = [
        ("edges-fixture-v1", ["edges", f"{fx}/edges_pkg_v1"]),
        ("edges-fixture-v1-file", ["edges", f"{fx}/edges_pkg_v1", "-o", str(v1)]),
        ("edges-fixture-v2-file", ["edges", f"{fx}/edges_pkg_v2", "-o", str(v2)]),
        ("edges-diff", ["edges", "--diff", str(v1), str(v2)]),
        ("edges-diff-json", ["edges", "--diff", str(v1), str(v2), "--json"]),
        ("edges-legacy-csv", ["edges", f"{fx}/edges_pkg_v1", "--legacy-csv", str(work / "legacy.csv")]),
        ("check-mtg", ["check", f"{ex}/mtg-pilot/records.jsonl"]),
        ("check-itsdangerous", ["check", f"{ex}/itsdangerous-demo/records.jsonl"]),
        ("check-code-impact-fixture", ["check", f"{fx}/code_impact/records.jsonl", "--edges", str(v1)]),
        ("code-impact-fixture", ["code-impact", f"{fx}/code_impact/records.jsonl", str(v1), str(v2)]),
        ("code-impact-fixture-json", ["code-impact", f"{fx}/code_impact/records.jsonl", str(v1), str(v2), "--json"]),
        ("import-purpose-fixture", ["import-purpose", f"{fx}/purpose_repo", "--dry-run"]),
    ]
    for scenario in sorted((ROOT / ex / "mtg-pilot").glob("scenario*.jsonl")):
        changes = f"{ex}/mtg-pilot/{scenario.name}"
        out.append((f"impact-{scenario.stem}", ["impact", f"{ex}/mtg-pilot/records.jsonl", changes]))
        out.append((f"impact-json-{scenario.stem}", ["impact", f"{ex}/mtg-pilot/records.jsonl", changes, "--json"]))
    for i, extra in enumerate(extras):
        snap = work / f"extra{i}.jsonl"
        out += [
            (f"extra{i}-edges", ["edges", str(extra)]),
            (f"extra{i}-edges-file", ["edges", str(extra), "-o", str(snap)]),
            (f"extra{i}-unresolved", ["unresolved", "--repo", str(extra), "--json"]),
            (f"extra{i}-fan", ["fan", "--repo", str(extra), "--json"]),
            (f"extra{i}-snapshot", ["snapshot", str(extra)]),
            (f"extra{i}-import-purpose", ["import-purpose", str(extra), "--dry-run"]),
        ]
        records = extra / ".aec" / "records.jsonl"
        if records.exists():
            out += [
                (f"extra{i}-check", ["check", str(records), "--edges", str(snap)]),
                (f"extra{i}-code-impact-self", ["code-impact", str(records), str(snap), str(snap)]),
            ]
    return out


def run(dest: Path, extras: list[Path]) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="golden-"))
    env = dict(os.environ, PYTHONPATH=str(ROOT / "src"))
    replacements = [(str(work), "WORK"), (str(ROOT), "ROOT")] + [(str(e), f"EXTRA{i}") for i, e in enumerate(extras)]
    for name, args in cases(work, extras):
        r = subprocess.run([sys.executable, "-m", "aec", *args], cwd=ROOT, env=env, capture_output=True, text=True)
        text = f"{r.stdout}\n--- stderr ---\n{r.stderr}\n--- exit {r.returncode} ---\n"
        for old, new in replacements:
            text = text.replace(old, new)
        (dest / f"{name}.txt").write_text(text, encoding="utf-8")
    for name in ("v1.jsonl", "v2.jsonl", "legacy.csv"):
        if (work / name).exists():
            (dest / name).write_bytes((work / name).read_bytes())


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--save", type=Path, help="write a baseline to this directory")
    mode.add_argument("--compare", type=Path, help="compare current outputs with this baseline")
    ap.add_argument("--extra", type=Path, action="append", default=[], help="another Python tree to extract")
    a = ap.parse_args(argv)
    extras = [e.resolve() for e in a.extra]
    if a.save:
        run(a.save, extras)
        print(f"golden master: {len(list(a.save.iterdir()))} outputs saved to {a.save}")
        return 0
    current = Path(tempfile.mkdtemp(prefix="golden-now-"))
    run(current, extras)
    cmp = filecmp.dircmp(a.compare, current)
    differ = sorted(cmp.diff_files + cmp.left_only + cmp.right_only)
    if differ:
        print("golden master: outputs differ: " + ", ".join(differ))
        print(f"  baseline {a.compare}\n  current  {current}")
        return 1
    print(f"golden master: {len(cmp.same_files)} outputs identical")
    return 0


if __name__ == "__main__":
    sys.exit(main())
