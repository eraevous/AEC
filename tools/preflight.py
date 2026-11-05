"""Run locally what CI gates on, before a pull request is opened or marked ready.

    python3 tools/preflight.py              # against origin/main
    python3 tools/preflight.py --base origin/some-branch

Mirrors .github/workflows/ci.yml for one Python version: the unit tests, record touch (a src/ change appends a
record or says why not), the records check against a fresh edge snapshot, the MtG example check, and the adoption
path on the fixture repo. Also runs ruff when it is installed (CI does not). Report-only CI steps (code-impact, the
structural diff artifact) are not run: they never fail a build. Stops at nothing: every step runs, then a summary,
and the exit code is 1 if any step failed. Standard library only; writes only to a temporary directory.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(name: str, cmd: list[str], env: dict | None = None) -> bool:
    print(f"== {name}: {' '.join(cmd)}", flush=True)
    r = subprocess.run(cmd, cwd=ROOT, env={**os.environ, **(env or {})}, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    if r.returncode != 0:
        print("\n".join(out.splitlines()[-25:]))  # the tail is where a failure is reported
    print(f"   {'ok' if r.returncode == 0 else f'FAILED (exit {r.returncode})'}", flush=True)
    return r.returncode == 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", default="origin/main", help="what the PR merges into (default origin/main)")
    a = ap.parse_args()
    py, src = sys.executable, {"PYTHONPATH": "src"}
    tmp = Path(tempfile.mkdtemp(prefix="aec-preflight-"))
    remote = a.base.split("/", 1)[0] if "/" in a.base else None
    if remote:
        subprocess.run(["git", "fetch", "-q", remote], cwd=ROOT, check=False)
    results = {}
    results["unit tests"] = run("unit tests", [py, "-m", "unittest", "discover", "-s", "tests"], src)
    results["record touch"] = run("record touch", [py, "tools/record_touch.py", "--base", a.base])
    results["edge snapshot"] = run("edge snapshot", [py, "-m", "aec", "edges", ".", "-o", str(tmp / "edges.jsonl")], src)
    results["records check"] = run("records check", [py, "-m", "aec", "check", ".aec/records.jsonl",
                                                     "--edges", str(tmp / "edges.jsonl")], src)
    results["mtg example check"] = run("mtg example check", [py, "-m", "aec", "check",
                                                             "examples/mtg-pilot/records.jsonl"], src)
    repo = tmp / "repo"
    shutil.copytree(ROOT / "tests" / "fixtures" / "purpose_repo", repo)
    results["adoption path"] = (
        run("adoption: init", [py, "-m", "aec", "init", str(repo), "--owner", "ci"], src)
        and run("adoption: import-purpose", [py, "-m", "aec", "import-purpose", str(repo)], src)
        and run("adoption: check", [py, "-m", "aec", "check", str(repo / ".aec/records.jsonl"),
                                    "--edges", str(repo / ".aec/edges.jsonl")], src))
    if shutil.which("ruff"):
        results["ruff"] = run("ruff", ["ruff", "check", "."])
    else:
        print("== ruff: not installed, not run (CI does not run it either)")
    shutil.rmtree(tmp, ignore_errors=True)
    failed = [k for k, ok in results.items() if not ok]
    print(f"\npreflight: {len(results) - len(failed)} of {len(results)} passed"
          + (f"; FAILED: {', '.join(failed)}" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
