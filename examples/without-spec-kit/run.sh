#!/usr/bin/env bash
# Reproduces docs/integrations/without-spec-kit.md in a temporary git repo with no Spec Kit.
# Needs Python 3.10+, git, and Telosmith >= 0.5.0 importable as `python3 -m aec`
# (pip install, or PYTHONPATH=<checkout>/src). Offline. Takes a few seconds.
set -u
here=$(cd "$(dirname "$0")" && pwd)
work=$(mktemp -d); trap 'rm -rf "$work"' EXIT
git init -q -b main "$work/origin.git" --bare
cp -R "$here/project" "$work/shop" && cd "$work/shop"
git init -q -b main && git config user.email demo@example.invalid && git config user.name Demo
python3 -m aec init . --owner "Ada" >/dev/null           # keeps the shipped records; adds edges, snippets
mkdir -p .claude && cp .aec/snippets/claude-settings.json .claude/settings.json
cp "$here/pre-commit" "$here/pre-push" .git/hooks/ && chmod +x .git/hooks/pre-*
git add -A && git commit -qm base && git remote add origin "$work/origin.git" && git push -q origin main 2>/dev/null
git remote set-head origin main

echo "== check"; python3 -m aec check .aec/records.jsonl --edges .aec/edges.jsonl
HOOK=$(python3 -c "import json; print(json.load(open('.claude/settings.json'))['hooks']['PostToolUse'][0]['hooks'][0]['command'])")
hook() { CLAUDE_PROJECT_DIR=$PWD bash -c "$HOOK"; echo "exit $?"; }
echo "== hook, clean tree"; hook
echo "== hook, clamp edited (pointer)"; sed -i.bak 's/max(0.0, /max(0, /' shop/pricing.py; rm shop/pricing.py.bak; hook
git checkout -q shop/pricing.py
echo "== hook, LIMIT edited (two hops: silent at default depth)"; sed -i.bak 's/LIMIT = 1000.0/LIMIT = 100.0/' shop/pricing.py; rm shop/pricing.py.bak; hook
git checkout -q shop/pricing.py
echo "== hook, RATE edited (module link)"; sed -i.bak 's/RATE = 0.08/RATE = 0.07/' shop/tax.py; rm shop/tax.py.bak; hook
git checkout -q shop/tax.py

git checkout -q -b feature
sed -i.bak 's/pct \/ 100)/pct \/ 100.0)/' shop/pricing.py; rm shop/pricing.py.bak; git add -A
echo "== pre-commit, blocking mode"; TELOSMITH_BLOCK=1 git commit -qm "float pct"; echo "commit exit $?"
echo "== pre-commit, report-only"; git commit -qm "float pct"; echo "commit exit $?"
echo "== pre-push"; git push -q origin feature; echo "push exit $?"

echo "== CI impact step (job summary written to a file)"
export GITHUB_STEP_SUMMARY="$work/summary.md" AEC_BASE=$(git rev-parse origin/main)
python3 -m aec edges . -o .aec/edges.jsonl >/dev/null
python3 - <<'PY' > "$work/ci_step.sh"
y = open('.aec/snippets/aec-ci.yml').read().split('run: |\n', 1)[1]
print('\n'.join(l[10:] for l in y.splitlines()))
PY
bash "$work/ci_step.sh" >/dev/null; echo "step exit $?"; cat "$GITHUB_STEP_SUMMARY"

echo "== append-only guard"
echo '{"id": "C-1", "version": 2, "type": "claim", "tier": "candidate", "text": "Checkout totals are never negative, including after float pct.", "relations": [{"rel": "depends_on", "to": "R-1@1"}]}' >> .aec/records.jsonl
sh "$here/append-only.sh" origin/main; echo "exit $? (appended)"
sed -i.bak 's/Checkout totals are never negative\./Checkout totals are always positive./' .aec/records.jsonl; rm .aec/records.jsonl.bak
sh "$here/append-only.sh" origin/main; echo "exit $? (edited in place)"
