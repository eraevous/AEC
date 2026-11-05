"""`aec init`: scaffold Telosmith (formerly AEC) into an existing repository (feature 002, US1).

Creates only what is absent, never overwrites, and never touches Spec Kit's own files. The purpose
record it writes is a provisional stub: it cannot authorize or block anything until the owner replaces
it. Standard library only.
"""
from __future__ import annotations

import json
import re
import subprocess
import textwrap
from pathlib import Path

from . import __version__
from . import edges as E

AEC_SOURCE = "git+https://github.com/eraevous/Telosmith.git"
# The first release whose `aec` has `snapshot`, `code-impact --exit-code` and module/reach logic, which the
# generated hook and CI job below call. v0.4.1 (the latest tag when this was written) has none of them.
FIRST_DELIVERY_RELEASE = (0, 5, 0)

README = """# .aec: purpose and justification records (Telosmith, formerly AEC)

- `records.jsonl`: append-only reasoning records (purpose, requirements, claims, evidence, decisions,
  authorities). Never edit a line; append a new version. Vocabulary:
  https://github.com/eraevous/Telosmith/blob/main/docs/reasoning-vocabulary.md
- `edges.jsonl`: the structural snapshot of the code (`aec edges`). Generated, so it is git-ignored
  (`.aec/.gitignore`): regenerate it rather than committing or hand-editing it.
- `snippets/`: a Claude Code hook and a CI job to copy into place. Nothing here is active until you do.

Start by replacing the purpose stub `P0` with a new version stating what this project is for, in your
own words (`"version": 2`, `"epistemic": "provisional"` while you are still discovering it,
`"committed"` once changes to it should need your authorization).

All Telosmith results are structural: they show what changed and what relied on it, not whether the
remaining evidence is good enough. That stays a review question.
"""

# After each edit: refresh the snapshot, fail on record errors, then compare against HEAD and tell the agent
# (stderr, exit 2) when linked code changed or reaches a change. Quiet when nothing linked moved. HEAD's snapshot
# goes to its own git-ignored file so a baseline the user keeps in `.aec/before.jsonl` is never overwritten.
# An installed `aec` too old for this (no `--exit-code`) is reported to the user (exit 1, non-blocking).
HOOK_COMMAND = (
    "cd \"$CLAUDE_PROJECT_DIR\" || exit 0; "
    "python3 -m aec code-impact --help 2>/dev/null | grep -q -- --exit-code || "
    "{ echo 'Telosmith hook: the installed aec has no code-impact --exit-code; install a release >= v0.5.0 "
    "or the commit your CI job pins' >&2; exit 1; }; "
    "python3 -m aec edges . -o .aec/edges.jsonl 2>/dev/null; "
    "python3 -m aec check .aec/records.jsonl --edges .aec/edges.jsonl >/dev/null || "
    "{ python3 -m aec check .aec/records.jsonl --edges .aec/edges.jsonl 1>&2; exit 2; }; "
    "python3 -m aec snapshot . --rev HEAD -o .aec/hook-before.jsonl 2>/dev/null || exit 0; "
    "out=$(python3 -m aec code-impact .aec/records.jsonl .aec/hook-before.jsonl .aec/edges.jsonl --exit-code 2>&1) || "
    "{ printf '%s\\n' \"$out\" "
    "'(Telosmith: stale/needs_review lines are status changes; structural pointer lines are candidates for "
    "attention and change no status.)' >&2; exit 2; }"
)

HOOK = {
    "hooks": {
        "PostToolUse": [{
            "matcher": "Edit|Write|MultiEdit",
            "hooks": [{"type": "command", "command": HOOK_COMMAND, "timeout": 30}],
        }]
    }
}

# Report-only: compares the merge-base with this checkout and writes the report to the job summary, where a
# reviewer sees it on the run page. Never fails the job (a code change is not an error).
CI_IMPACT = """base=$(git merge-base "$AEC_BASE" HEAD 2>/dev/null) || base=""
if [ -z "$base" ]; then
  echo "code-impact skipped: no base revision for this event" | tee -a "$GITHUB_STEP_SUMMARY"; exit 0
fi
python3 -m aec snapshot . --rev "$base" -o .aec/before.jsonl || {
  echo "code-impact skipped: could not snapshot $base" | tee -a "$GITHUB_STEP_SUMMARY"; exit 0; }
report=$(python3 -m aec code-impact .aec/records.jsonl .aec/before.jsonl .aec/edges.jsonl 2>&1) || true
printf '%s\\n' "$report"
{ echo "## Telosmith code-impact (structural, report-only) vs $base"; echo '```'
  printf '%s\\n' "$report"; echo '```'; } >> "$GITHUB_STEP_SUMMARY"
exit 0
"""

def _release(version: str) -> tuple[int, ...] | None:
    m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", version)
    return tuple(int(p) for p in m.groups()) if m else None


def _installed_commit() -> str | None:
    """The commit this package was pip-installed from (PEP 610 `direct_url.json`), when that install is the
    code running now; None for a source checkout, an editable install or a wheel from an index."""
    try:
        from importlib import metadata
        dist = metadata.distribution("telosmith")
        if Path(str(dist.locate_file("aec"))).resolve() != Path(__file__).resolve().parent:
            return None
        sha = json.loads(dist.read_text("direct_url.json") or "{}").get("vcs_info", {}).get("commit_id", "")
        return sha if re.fullmatch(r"[0-9a-f]{40}", sha) else None
    except Exception:  # noqa: BLE001 - any metadata problem means "unknown"
        return None


def install_ref(version: str = __version__, commit: str | None = None) -> str:
    """What the generated CI job installs: the commit this aec was installed from when known; else this
    version's tag when it is a release that has the delivery commands; else `main` (with a warning)."""
    if commit:
        return commit
    rel = _release(version)
    if rel is not None and rel >= FIRST_DELIVERY_RELEASE:
        return f"v{version}"
    return "main"


def _checkout_commit(pkg_dir: Path) -> tuple[str, bool] | None:
    """(HEAD, dirty) when pkg_dir is tracked in a git checkout (run with PYTHONPATH=src, or an editable
    install of Telosmith, whose pyproject names it); None otherwise, including a package that only sits
    untracked inside some repo (a venv) or a copy vendored into another project."""
    def git(*args):
        return subprocess.run(["git", "-C", str(pkg_dir), *args], capture_output=True, text=True, timeout=10)
    try:
        if git("ls-files", "--error-unmatch", "__init__.py").returncode:
            return None
        top = git("rev-parse", "--show-toplevel").stdout.strip()
        pyproject = Path(top) / "pyproject.toml" if top else None
        if not (pyproject and pyproject.is_file()
                and re.search(r'^name\s*=\s*"telosmith"', pyproject.read_text(encoding="utf-8"), re.M)):
            return None  # src/aec vendored into some other project: its HEAD is not a Telosmith commit
        head = git("rev-parse", "HEAD")
        sha = head.stdout.strip()
        if head.returncode or not re.fullmatch(r"[0-9a-f]{40}", sha):
            return None
        return sha, git("diff", "--quiet", "HEAD", "--", ".").returncode != 0
    except (OSError, subprocess.SubprocessError):
        return None


def resolve_install_ref(version: str = __version__, commit: str | None = None,
                        pkg_dir: Path | None = None) -> tuple[str, str | None]:
    """The ref the generated CI job installs, and a note to print. A git install's recorded commit comes
    first. A source checkout has no recorded commit, but its HEAD is known, while this version's tag may not
    exist yet (offline, it cannot be checked): pin HEAD. Otherwise `install_ref`'s rule (#51) applies."""
    if not commit:
        found = _checkout_commit(Path(__file__).resolve().parent if pkg_dir is None else pkg_dir)
        if found:
            sha, dirty = found
            note = (f"aec runs from a source checkout, so the CI snippet pins its HEAD commit {sha[:12]} "
                    f"rather than the tag v{version}, which may not exist yet. Push that commit, or replace the "
                    "pin with a release tag you have checked.")
            if dirty:
                note += " The checkout has uncommitted changes in aec/; CI will not run them."
            return sha, note
    return install_ref(version, commit), None


def __getattr__(name):  # CI is resolved on first use, not at import (resolving it may run git)
    if name == "CI":
        return ci_snippet(resolve_install_ref(__version__, _installed_commit())[0])
    raise AttributeError(name)


def ci_snippet(ref: str) -> str:
    first = "v" + ".".join(map(str, FIRST_DELIVERY_RELEASE))
    if ref == "main":
        head = (f"# WARNING: UNPINNED. This aec ({__version__}) was not installed from a known commit, and no release\n"
                f"# >= {first} (the first with `aec snapshot` and `code-impact --exit-code`, which the last step\n"
                f"# needs) was known when it was generated. `@main` runs whatever main holds at job time. Replace\n"
                f"# `main` with a commit SHA you have reviewed, or a release tag >= {first}.")
    elif ref.startswith("v"):
        head = (f"# Pinned to the Telosmith release that generated it ({ref}); change the ref only to a release or\n"
                f"# commit you have reviewed.")
    else:
        head = (f"# Pinned to the Telosmith commit that generated it ({ref[:12]}); change the ref only to a release\n"
                f"# >= {first} or a commit you have reviewed.")
    return f"""# Copy into .github/workflows/aec.yml.
{head}
name: aec
on: [push, pull_request]
jobs:
  aec:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: {{ fetch-depth: 0 }}
      - uses: actions/setup-python@v5
        with: {{ python-version: "3.12" }}
      - run: pip install "{AEC_SOURCE}@{ref}"
      - name: Structural snapshot (regenerated, never trusted from the branch)
        run: python3 -m aec edges . -o .aec/edges.jsonl
      - name: Records check (fails on errors, including dangling code references)
        run: python3 -m aec check .aec/records.jsonl --edges .aec/edges.jsonl
      - name: Code impact against the base (report-only; see the job summary)
        env:
          AEC_BASE: ${{{{ github.event.pull_request.base.sha || github.event.before }}}}
        run: |
{textwrap.indent(CI_IMPACT, " " * 10)}"""


GITIGNORE = """# Generated by `aec edges`; regenerate it instead of committing it (committed copies conflict on
# every pair of pull requests that touch code). Keep a baseline with: cp .aec/edges.jsonl .aec/before.jsonl
# hook-before.jsonl is the Claude Code hook's snapshot of HEAD, rewritten on every edit.
edges.jsonl
before.jsonl
hook-before.jsonl
"""


STUB_PURPOSE = "TODO: the owner states what this project is for (stub from aec init)"


def _records(owner: str, purpose: str | None = None, anchor: dict | None = None) -> str:
    p0 = {"id": "P0", "version": 1, "type": "purpose", "subject": "purpose", "owner": "AU-owner",
          "epistemic": "provisional", "text": purpose or STUB_PURPOSE}
    if anchor:
        p0["anchors"] = [anchor]
    rows = [
        "// Telosmith records. Append-only: add a new version instead of editing a line.",
        {"id": "AU-owner", "version": 1, "type": "authority", "text": f"{owner}: design intent and acceptance",
         "governs": ["purpose", "design", "acceptance", "code"]},
        p0,
    ]
    return "\n".join(r if isinstance(r, str) else json.dumps(r) for r in rows) + "\n"


def init(root: str | Path, owner: str, *, purpose: str | None = None, purpose_anchor: str | None = None,
         hooks: bool | None = None) -> dict:
    """Scaffold .aec/ without overwriting anything.

    purpose: the text of P0@1 instead of the stub (still provisional: the owner commits it by appending P0@2).
    purpose_anchor: `PATH#LOCATOR` in ROOT that the purpose cites; hashed and checked now (DEC-095).
    hooks: write the Claude Code hook and CI snippets. None (default) writes them only when ROOT has Python
    code, since code-impact has nothing to report in a repository without it."""
    root = Path(root)
    aec = root / ".aec"
    created, kept = [], []
    if purpose_anchor and not purpose:
        raise ValueError("--purpose-anchor needs --purpose: an anchor cites the text of a stated purpose")
    anchor = None
    if purpose_anchor:
        from .append import make_anchor
        from .sources import SourceContext
        anchor = make_anchor(SourceContext(root), purpose_anchor, "text")  # raises before anything is written
    snapshot = E.snapshot(root)
    if hooks is None:
        hooks = snapshot["header"]["files"] > 0

    def put(rel: str, make):
        p = aec / rel
        key = f".aec/{rel}"
        if p.exists():
            kept.append(key)
            return
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(make(), encoding="utf-8")
        created.append(key)

    put("records.jsonl", lambda: _records(owner, purpose, anchor))
    put("edges.jsonl", lambda: E.dumps(snapshot))
    put("README.md", lambda: README)
    # v0.4.1: the snapshot is generated; committing it makes every pair of code-touching PRs conflict.
    put(".gitignore", lambda: GITIGNORE)
    ref, note = None, None
    if hooks:
        put("snippets/claude-settings.json", lambda: json.dumps(HOOK, indent=2) + "\n")
        ref, note = resolve_install_ref(__version__, _installed_commit())
        put("snippets/aec-ci.yml", lambda: ci_snippet(ref))

    spec_kit = (root / ".specify").is_dir()
    steps = []
    if purpose:
        steps.append("P0@1 states your purpose (provisional). When it is settled, append P0@2 with "
                     '"epistemic": "committed".')
    else:
        steps.append("Replace the purpose stub P0 in .aec/records.jsonl with your own statement (append version 2).")
    if hooks:
        steps += ["Copy .aec/snippets/claude-settings.json into .claude/settings.json (merge if one exists).",
                  "Copy .aec/snippets/aec-ci.yml into .github/workflows/aec.yml"
                  + (" (it pins @main: replace it with a reviewed commit SHA or a release >= v0.5.0)."
                     if ref == "main" else "."),
                  "The hook runs the aec installed in your environment: it needs `code-impact --exit-code` "
                  f"(a release >= v0.5.0, or pip install \"{AEC_SOURCE}@{ref}\")."]
    else:
        steps.append("No hook or CI snippet written: " + ("this repository has no Python code, so code-impact has "
                     "nothing to report. Re-run `aec init --hooks` after adding code." if snapshot["header"]["files"] == 0
                     else "--no-hooks was given."))
    steps.append("Add records with computed anchors: aec append .aec/records.jsonl '<record JSON>' "
                 "--anchor PATH#LOCATOR")
    steps.append("If the repo has Codex++ purpose files: python3 -m aec import-purpose .")
    if spec_kit:
        steps.insert(1, "Spec Kit detected. Register the Telosmith hooks (report-only, removable): "
                        "specify extension add --dev <path-to-Telosmith-checkout>/extension")
    if note and ".aec/snippets/aec-ci.yml" in created:
        steps.insert(0, "Note: " + note)
    return {"created": created, "kept": kept, "spec_kit": spec_kit, "next_steps": "\n".join(steps)}
