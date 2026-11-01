#!/usr/bin/env python3
"""probe-001 mechanical grading. For each trial: save the diff, run the repo's own suite and the hidden
tests on a scratch copy of the trial's final repo, and write results.jsonl. Never modifies the trial repo."""
import json, shutil, subprocess, sys
from pathlib import Path

ROOT = Path("/tmp/claude-0/probe")
SEALED = Path("/root/.cache/p001-sealed")
HIDDEN = SEALED / "hidden"
sched = {x["trial"]: x for x in json.loads((SEALED / "schedule.private.json").read_text())}
out = []


def pytest(repo, args):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *args], cwd=repo,
                       capture_output=True, text=True, timeout=600)
    tail = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-200:]
    return r.returncode == 0, tail


for tid in sorted(sched):
    x = sched[tid]
    t = ROOT / "trials" / tid
    repo = t / "repo"
    diff = subprocess.run(["git", "diff", "HEAD", "--stat"], cwd=repo, capture_output=True, text=True).stdout
    patch = subprocess.run(["git", "diff", "HEAD"], cwd=repo, capture_output=True, text=True).stdout
    untracked = subprocess.run(["git", "status", "--porcelain"], cwd=repo, capture_output=True, text=True).stdout
    (t / "final.patch").write_text(patch)
    scratch = ROOT / "grading" / tid
    if scratch.exists():
        shutil.rmtree(scratch)
    shutil.copytree(repo, scratch, symlinks=True)
    for f in HIDDEN.glob(f"test_{x['task']}_*.py"):
        shutil.copy(f, scratch / "tests" / ("hidden_" + f.name))
    own_ok, own = pytest(scratch, ["tests", "--ignore-glob=tests/hidden_*"])
    res = {"trial": tid, "own_suite_pass": own_ok, "own_suite": own,
           "report_exists": (t / "REPORT.md").exists(), "diffstat": diff.strip().splitlines()[-1] if diff.strip() else "no changes",
           "status": untracked.strip().splitlines()}
    for kind in ("functionality", "preservation"):
        f = scratch / "tests" / f"hidden_test_{x['task']}_{kind}.py"
        if f.exists():
            ok, tail = pytest(scratch, [str(f.relative_to(scratch))])
            res[kind + "_pass"], res[kind] = ok, tail
    out.append(res)
    print(json.dumps(res))
(ROOT / "grading" / "mechanical.jsonl").write_text("\n".join(json.dumps(r) for r in out) + "\n")
