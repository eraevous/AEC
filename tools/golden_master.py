#!/usr/bin/env python3
"""Golden master: run each command on fixed inputs and compare outputs byte for byte.

A refactor that claims "no behaviour change" must leave every output identical. Save a baseline from
the code before the change, then compare the code after it:

    PYTHONPATH=src python3 tools/golden_master.py --save /tmp/gold-before [--extra PATH ...]
    # ...refactor...
    PYTHONPATH=src python3 tools/golden_master.py --compare /tmp/gold-before [--extra PATH ...]

Covered: edges (extract, diff, legacy CSV), check, impact, code-impact, import-purpose (dry run and
write mode), init, snapshot, diff (stored snapshots), reach, fan, unresolved, and usage-error paths;
`source` and the self-checks run on `--extra` trees. Files that `init` and `import-purpose` write are
captured too. Tracebacks are not compared: their line numbers move legitimately when code is refactored.

Inputs are the repository's own fixtures and examples. `--extra PATH` adds a Python tree (such as a
checkout of another project) to the extraction cases, which is how real-world code is covered without
shipping it. To include Telosmith's own code, pass a *pinned* checkout (`git worktree add DIR <sha>`),
never the working tree: analysing the code you are refactoring changes its own output legitimately.
This is a tool for comparing two revisions, not a second test suite: behaviour is specified in tests/. Outputs record stdout, stderr and the exit code; local paths are replaced so baselines
taken from different checkouts compare. Standard library only.
"""
from __future__ import annotations

import argparse
import filecmp
import os
import shutil
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
        ("import-purpose-write", ["import-purpose", str(work / "purpose_copy")]),
        ("init", ["init", str(work / "init_repo"), "--owner", "Golden"]),
        ("snapshot-fixture", ["snapshot", f"{fx}/edges_pkg_v1"]),
        ("diff-stored", ["diff", "--base-snapshot", str(v1), "--head-snapshot", str(v2)]),
        ("diff-stored-json", ["diff", "--base-snapshot", str(v1), "--head-snapshot", str(v2), "--json"]),
        ("reach-fixture", ["reach", "pkg.core.load", "--repo", f"{fx}/edges_pkg_v1"]),
        ("reach-fixture-callees-json", ["reach", "pkg.core.main", "--direction", "callees", "--depth", "2",
                                        "--repo", f"{fx}/edges_pkg_v1", "--json"]),
        ("fan-fixture", ["fan", "--repo", f"{fx}/edges_pkg_v1"]),
        ("unresolved-fixture", ["unresolved", "--repo", f"{fx}/edges_pkg_v1"]),
        ("error-diff-half-stored", ["diff", "--base-snapshot", str(v1)]),
        ("error-diff-method-override", ["diff", "--allow-method-mismatch", "--repo", f"{fx}/edges_pkg_v1"]),
        ("error-edges-not-a-directory", ["edges", f"{ex}/mtg-pilot/records.jsonl"]),
        ("error-import-purpose-no-dir", ["import-purpose", f"{fx}/edges_pkg_v1"]),
        ("error-unknown-command", ["nosuch"]),
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
            (f"extra{i}-source-search", ["source", "search", "append-only", "--root", ".", "--repo", str(extra)]),
        ]
        records = extra / ".aec" / "records.jsonl"
        if records.exists():
            out += [
                (f"extra{i}-check", ["check", str(records), "--edges", str(snap)]),
                (f"extra{i}-code-impact-self", ["code-impact", str(records), str(snap), str(snap)]),
            ]
            anchored = next((line.split('"id": "')[1].split('"')[0] + "@1" for line in records.read_text().splitlines()
                             if '"anchors"' in line and '"version": 1' in line), None)
            if anchored:
                out.append((f"extra{i}-source-show", ["source", "show", anchored, "--repo", str(extra)]))
    return out


def _written(directory: Path) -> str:
    """The files a command wrote, for cases that write (init, import-purpose)."""
    parts = []
    for f in sorted(p for p in directory.rglob("*") if p.is_file() and ".git" not in p.parts):
        parts.append(f"=== {f.relative_to(directory).as_posix()}\n{f.read_text(encoding='utf-8', errors='replace')}")
    return "\n".join(parts)


def run(dest: Path, extras: list[Path]) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="golden-"))
    shutil.copytree(ROOT / "tests" / "fixtures" / "purpose_repo", work / "purpose_copy")
    (work / "init_repo").mkdir()
    env = dict(os.environ, PYTHONPATH=str(ROOT / "src"))
    paths = [(str(work), "WORK"), (str(ROOT), "ROOT")] + [(str(e), f"EXTRA{i}") for i, e in enumerate(extras)]
    paths.sort(key=lambda pair: len(pair[0]), reverse=True)  # longest first, so nested paths map cleanly
    # The fixtures live inside this repository, so their snapshots record its HEAD commit, which every
    # commit changes: normalise it there. Extra trees keep their own (pinned) commits.
    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], check=False, capture_output=True, text=True).stdout.strip()

    def normalise(text: str, own_fixture: bool) -> str:
        for old, new in paths:
            text = text.replace(old, new)
        return text.replace(head, "REPO_HEAD") if head and own_fixture else text

    try:
        for name, args in cases(work, extras):
            r = subprocess.run([sys.executable, "-m", "aec", *args], check=False, cwd=ROOT, env=env,
                               capture_output=True, text=True)
            text = f"{r.stdout}\n--- stderr ---\n{r.stderr}\n--- exit {r.returncode} ---\n"
            if name == "init":
                text += "\n--- written ---\n" + _written(work / "init_repo")
            elif name == "import-purpose-write":
                text += "\n--- written ---\n" + _written(work / "purpose_copy" / ".aec")
            (dest / f"{name}.txt").write_text(normalise(text, not name.startswith("extra")), encoding="utf-8")
        for name in ("v1.jsonl", "v2.jsonl", "legacy.csv"):
            if (work / name).exists():
                (dest / name).write_text(normalise((work / name).read_text(encoding="utf-8"), True), encoding="utf-8")
    finally:
        shutil.rmtree(work, ignore_errors=True)


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
    current = Path(tempfile.mkdtemp(prefix="golden-now-"))  # kept on a difference, for inspection
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
