# Telosmith in 90 seconds

One toy project, end to end: `init`, a purpose, a requirement linked to a function, a claim and its
evidence, a `check` that catches a typo, an edit to a helper two calls away, the `code-impact` pointer,
and the Claude Code hook reporting with exit 2. Every command below was run against release 0.5.0 on
2026-11-04; the output is pasted as printed, trimmed only where marked. The whole script runs in about
two seconds.

You need Python 3.10+, git and bash (the `sed -i.bak` form works with GNU and BSD sed).

## 0. Install

```bash
pip install "git+https://github.com/eraevous/Telosmith.git@v0.5.0"   # until the tag exists, use @main
aec --version; telosmith --version
```

```text
aec 0.5.0
telosmith 0.5.0
```

## 1. A toy project and `init`

`apply_discount` calls `clamp`, which calls `round_cents`.

```bash
mkdir -p shop/shop && cd shop && git init -q
touch shop/__init__.py
cat > shop/pricing.py <<'EOF'
def round_cents(x):
    return round(x, 2)


def clamp(x):
    return max(0.0, round_cents(x))


def apply_discount(price, pct):
    return clamp(price * (1 - pct / 100))
EOF
aec init . --owner "Ada"
head -1 .aec/records.jsonl
```

```text
created .aec/records.jsonl
created .aec/edges.jsonl
created .aec/README.md
created .aec/.gitignore
created .aec/snippets/claude-settings.json
created .aec/snippets/aec-ci.yml

Next steps:
  - Replace the purpose stub P0 in .aec/records.jsonl with your own statement (append version 2).
  - Copy .aec/snippets/claude-settings.json into .claude/settings.json (merge if one exists).
  - Copy .aec/snippets/aec-ci.yml into .github/workflows/aec.yml.
  - The hook runs the aec installed in your environment: it needs `code-impact --exit-code` (a release >= v0.5.0, or pip install "git+https://github.com/eraevous/Telosmith.git@v0.5.0").
  - If the repo has Codex++ purpose files: python3 -m aec import-purpose .
// Telosmith records. Append-only: add a new version instead of editing a line.
```

## 2. Purpose, requirement, claim, evidence (with two deliberate mistakes)

The requirement's function name is misspelt (`apply_discnt`) and the evidence has no `text`.

```bash
cat >> .aec/records.jsonl <<'EOF'
{"id": "P0", "version": 2, "type": "purpose", "subject": "purpose", "owner": "AU-owner", "epistemic": "provisional", "text": "A tiny shop whose checkout never charges a negative amount."}
{"id": "R-1", "version": 1, "type": "requirement", "subject": "code", "epistemic": "committed", "text": "Discounts never make a price negative.", "relations": [{"rel": "implemented_by", "to": "code:shop.pricing.apply_discnt"}, {"rel": "serves", "to": "P0@2"}]}
{"id": "C-1", "version": 1, "type": "claim", "tier": "candidate", "text": "Checkout totals are never negative.", "relations": [{"rel": "depends_on", "to": "R-1@1"}]}
{"id": "E-1", "version": 1, "type": "evidence", "relations": [{"rel": "supports", "to": "C-1@1"}]}
EOF
aec check .aec/records.jsonl --edges .aec/edges.jsonl; echo "exit $?"
```

```text
[ERROR] code-reference: R-1@1: implemented_by -> code:shop.pricing.apply_discnt: no such symbol in the edge snapshot (renamed or deleted?); did you mean code:shop.pricing.apply_discount?
[WARNING] evidence-text: E-1@1: evidence has no text: reports will show it as an empty line; say what was observed
aec check: 1 error(s), 1 warning(s) (structural)
exit 1
```

These lines have not been committed yet, so fix them in place. Once records are committed, change one by
appending the same `id` with the next `version`.

```bash
sed -i.bak -e 's/apply_discnt/apply_discount/' \
  -e 's/"type": "evidence", "relations"/"type": "evidence", "text": "apply_discount(10, 150) returned 0.0 by hand.", "relations"/' \
  .aec/records.jsonl && rm .aec/records.jsonl.bak
aec check .aec/records.jsonl --edges .aec/edges.jsonl; echo "exit $?"
git add -A && git commit -qm "toy shop with records"
```

```text
aec check: 0 error(s), 0 warning(s) (structural)
exit 0
```

## 3. Edit a helper two hops away

`round_cents` is two calls away from the linked `apply_discount`. Pointers reach one call by default;
`--reach-depth 2` widens them.

```bash
cp .aec/edges.jsonl .aec/before.jsonl
sed -i.bak 's/return round(x, 2)/return int(x * 100) \/ 100/' shop/pricing.py && rm shop/pricing.py.bak
aec edges . -o .aec/edges.jsonl
aec code-impact .aec/records.jsonl .aec/before.jsonl .aec/edges.jsonl
aec code-impact .aec/records.jsonl .aec/before.jsonl .aec/edges.jsonl --reach-depth 2
```

```text
aec edges: 5 edges from 2 files (0 skipped) -> .aec/edges.jsonl
# derived 0 change event(s) from the structural diff
# aec impact

0 affected, 3 conclusions with no status change
# derived 0 change event(s) from the structural diff
# aec impact

[finding] structural: code:shop.pricing.apply_discount reaches changed code:shop.pricing.round_cents via code:shop.pricing.clamp (calls/calls, depth 2); no status change; candidate for attention: R-1@1

0 affected, 3 conclusions with no status change (1 pointer(s) above: candidates for attention)
```

A pointer is a candidate for attention. It changes no record's status.

## 4. The Claude Code hook

Claude Code runs the hook command from `.aec/snippets/claude-settings.json` after each Edit or Write,
once you copy it into `.claude/settings.json`. Here it is run by hand, the same way, three times.
It compares the working tree with `HEAD` at the default depth of one call, so the two-hop edit above
stays quiet.

```bash
HOOK=$(python3 -c "import json; print(json.load(open('.aec/snippets/claude-settings.json'))['hooks']['PostToolUse'][0]['hooks'][0]['command'])")
CLAUDE_PROJECT_DIR=$PWD bash -c "$HOOK"; echo "exit $?"      # after the two-hop edit
sed -i.bak 's/max(0.0, /max(0, /' shop/pricing.py && rm shop/pricing.py.bak
CLAUDE_PROJECT_DIR=$PWD bash -c "$HOOK"; echo "exit $?"      # after editing clamp, one hop away
sed -i.bak 's/pct \/ 100)/pct \/ 100.0)/' shop/pricing.py && rm shop/pricing.py.bak
CLAUDE_PROJECT_DIR=$PWD bash -c "$HOOK"; echo "exit $?"      # after editing apply_discount itself
```

```text
exit 0
# derived 0 change event(s) from the structural diff
# aec impact

[finding] structural: code:shop.pricing.apply_discount reaches changed code:shop.pricing.clamp (calls, depth 1); no status change; candidate for attention: R-1@1

0 affected, 3 conclusions with no status change (1 pointer(s) above: candidates for attention)
(Telosmith: stale/needs_review lines are status changes; structural pointer lines are candidates for attention and change no status.)
exit 2
# derived 1 change event(s) from the structural diff
# aec impact

- change: revise code:shop.pricing.apply_discount (by code, authorized_by None)

[stale] R-1@1: Discounts never make a price negative.
    via code:shop.pricing.apply_discount -> R-1@1
[needs_review] C-1@1: Checkout totals are never negative.
    via code:shop.pricing.apply_discount -> R-1@1 -> C-1@1

2 affected, 1 conclusions with no status change
(Telosmith: stale/needs_review lines are status changes; structural pointer lines are candidates for attention and change no status.)
exit 2
```

Exit 2 is how a Claude Code hook hands its stderr back to the agent. The report says which
conclusions to look at again; it does not say whether they are now false. Blank lines in the output
are trimmed to one.

What next: [the getting-started guide](guide/getting-started.md) covers comparing against a branch, the
CI job, and repositories with Codex++ purpose files.
