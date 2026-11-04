#!/usr/bin/env python3
"""Record-touch check: a change to src/ must append to .aec/records.jsonl or say why not.

Usage: python3 tools/record_touch.py --base REF [--head REF]

Passes when the diff base...head does not touch src/, or touches .aec/records.jsonl too,
or a commit in base..head carries the trailer ``AEC-Record: none - <reason>`` with a reason.
This is a structural prompt to keep records current, not a check that the records are right.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys

RECORDS = ".aec/records.jsonl"
TRAILER = re.compile(r"^AEC-Record:\s*none\s*[-:–—]\s*(\S.*)$", re.M | re.I)


def evaluate(changed: list[str], messages: list[str]) -> tuple[bool, str]:
    code = sorted(p for p in changed if p.startswith("src/"))
    if not code:
        return True, "record-touch: no src/ changes"
    if RECORDS in changed:
        return True, f"record-touch: {len(code)} src/ file(s) changed; {RECORDS} appended"
    for m in messages:
        hit = TRAILER.search(m)
        if hit:
            return True, f"record-touch: {len(code)} src/ file(s) changed; no record, reason given: {hit.group(1).strip()}"
    return False, (f"record-touch: {len(code)} src/ file(s) changed ({', '.join(code[:5])}"
                   f"{', ...' if len(code) > 5 else ''}) but {RECORDS} was not appended.\n"
                   "Append a record (requirement, claim or evidence) for the change, or add a commit trailer\n"
                   "'AEC-Record: none - <reason>' saying why the change needs none.")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--head", default="HEAD")
    a = ap.parse_args(argv)
    changed = [name for name in git("diff", "--name-only", f"{a.base}...{a.head}").splitlines() if name]
    messages = git("log", "--format=%B%x00", f"{a.base}..{a.head}").split("\x00")
    ok, msg = evaluate(changed, messages)
    print(msg, file=sys.stdout if ok else sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
