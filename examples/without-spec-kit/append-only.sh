#!/bin/sh
# Fails when .aec/records.jsonl at HEAD does not start with the bytes it had at the base revision
# (a line was edited, reordered or deleted instead of appended). Usage: append-only.sh <base-rev>
f=.aec/records.jsonl
base=$(git merge-base "$1" HEAD) || exit 0
git cat-file -e "$base:$f" 2>/dev/null || exit 0          # no records at the base: nothing to protect
old=$(mktemp); trap 'rm -f "$old"' EXIT
git show "$base:$f" > "$old"
n=$(wc -c < "$old")
if head -c "$n" "$f" | cmp -s - "$old"; then echo "append-only: ok ($f grew from $n bytes)"; exit 0; fi
echo "append-only: $f no longer starts with its content at $(echo "$base" | cut -c1-8); append a new version instead of editing a line" >&2
exit 1
