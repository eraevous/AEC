"""`aec init`: scaffold AEC into an existing repository (feature 002, US1).

Creates only what is absent, never overwrites, and never touches Spec Kit's own files. The purpose
record it writes is a provisional stub: it cannot authorize or block anything until the owner replaces
it. Standard library only.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import edges as E

AEC_SOURCE = "git+https://github.com/eraevous/AEC.git"

README = """# .aec: purpose and justification records (AEC)

- `records.jsonl`: append-only reasoning records (purpose, requirements, claims, evidence, decisions,
  authorities). Never edit a line; append a new version. Vocabulary:
  https://github.com/eraevous/AEC/blob/main/docs/reasoning-vocabulary.md
- `edges.jsonl`: the structural snapshot of the code (`aec edges`). Regenerate it; never hand-edit it.
- `snippets/`: a Claude Code hook and a CI job to copy into place. Nothing here is active until you do.

Start by replacing the purpose stub `P0` with a new version stating what this project is for, in your
own words (`"version": 2`, `"epistemic": "provisional"` while you are still discovering it,
`"committed"` once changes to it should need your authorization).

All AEC results are structural: they show what changed and what relied on it, not whether the
remaining evidence is good enough. That stays a review question.
"""

HOOK = {
    "hooks": {
        "PostToolUse": [{
            "matcher": "Edit|Write|MultiEdit",
            "hooks": [{
                "type": "command",
                "command": "cd \"$CLAUDE_PROJECT_DIR\" && python3 -m aec edges . -o .aec/edges.jsonl 2>/dev/null; "
                           "python3 -m aec check .aec/records.jsonl --edges .aec/edges.jsonl >/dev/null || "
                           "(python3 -m aec check .aec/records.jsonl --edges .aec/edges.jsonl 1>&2; exit 2)",
                "timeout": 30,
            }],
        }]
    }
}

CI = f"""# Copy into .github/workflows/aec.yml. Pin @<ref> to a release or commit you have reviewed.
name: aec
on: [push, pull_request]
jobs:
  aec:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {{ python-version: "3.12" }}
      - run: pip install "aec @ {AEC_SOURCE}@main"
      - name: Structural snapshot (regenerated, never trusted from the branch)
        run: python3 -m aec edges . -o .aec/edges.jsonl
      - name: Records check (fails on errors, including dangling code references)
        run: python3 -m aec check .aec/records.jsonl --edges .aec/edges.jsonl
"""


def _records(owner: str) -> str:
    rows = [
        "// AEC records. Append-only: add a new version instead of editing a line.",
        {"id": "AU-owner", "version": 1, "type": "authority", "text": f"{owner}: design intent and acceptance",
         "governs": ["purpose", "design", "acceptance", "code"]},
        {"id": "P0", "version": 1, "type": "purpose", "subject": "purpose", "owner": "AU-owner",
         "epistemic": "provisional", "text": "TODO: the owner states what this project is for (stub from aec init)"},
    ]
    return "\n".join(r if isinstance(r, str) else json.dumps(r) for r in rows) + "\n"


def init(root: str | Path, owner: str) -> dict:
    root = Path(root)
    aec = root / ".aec"
    created, kept = [], []

    def put(rel: str, make):
        p = aec / rel
        key = f".aec/{rel}"
        if p.exists():
            kept.append(key)
            return
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(make(), encoding="utf-8")
        created.append(key)

    put("records.jsonl", lambda: _records(owner))
    put("edges.jsonl", lambda: E.dumps(E.snapshot(root)))
    put("README.md", lambda: README)
    put("snippets/claude-settings.json", lambda: json.dumps(HOOK, indent=2) + "\n")
    put("snippets/aec-ci.yml", lambda: CI)

    spec_kit = (root / ".specify").is_dir()
    steps = ["Replace the purpose stub P0 in .aec/records.jsonl with your own statement (append version 2).",
             "Copy .aec/snippets/claude-settings.json into .claude/settings.json (merge if one exists).",
             "Copy .aec/snippets/aec-ci.yml into .github/workflows/aec.yml.",
             "If the repo has Codex++ purpose files: python3 -m aec import-purpose ."]
    if spec_kit:
        steps.insert(1, "Spec Kit detected. Register the AEC hooks (report-only, removable): "
                        "specify extension add --dev <path-to-AEC-checkout>/extension")
    return {"created": created, "kept": kept, "spec_kit": spec_kit, "next_steps": "\n".join(steps)}
