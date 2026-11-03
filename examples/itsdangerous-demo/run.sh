#!/usr/bin/env bash
# Reproduces the README's worked example end to end. Needs git, Python 3.10+ and network access
# (to clone itsdangerous and install its test dependencies). Everything happens in a temporary
# directory; nothing outside it is changed.
#
#   examples/itsdangerous-demo/run.sh [AEC_REF]
#
# AEC_REF defaults to this checkout; pass a tag such as v0.4.0 to test a release instead.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
AEC_ROOT="$(cd "$HERE/../.." && pwd)"
ITSD_COMMIT=672971d
WORK="$(mktemp -d)"
echo "# working in $WORK"
python3 -m venv "$WORK/venv"
PY="$WORK/venv/bin/python"; AEC="$WORK/venv/bin/aec"
if [ "${1:-}" ]; then
  "$PY" -m pip install -q "git+https://github.com/eraevous/Telosmith.git@$1"
else
  "$PY" -m pip install -q "$AEC_ROOT"
fi
"$PY" -m pip install -q pytest freezegun
"$AEC" --version

git clone -q https://github.com/pallets/itsdangerous "$WORK/itsdangerous"
cd "$WORK/itsdangerous"
git -c advice.detachedHead=false checkout -q "$ITSD_COMMIT"

echo; echo "## 1. init, record a requirement and a claim, check they resolve"
"$AEC" init . --owner "Demo" > /dev/null
grep -v '^//' "$HERE/records.jsonl" >> .aec/records.jsonl
"$AEC" check .aec/records.jsonl --edges .aec/edges.jsonl
cp .aec/edges.jsonl "$WORK/old.jsonl"

echo; echo "## 2. the library's tests before the edit"
PYTHONPATH=src "$PY" -m pytest -q 2>&1 | tail -1

echo; echo "## 3. an agent 'simplifies' the comparison"
sed -i.bak 's/return hmac.compare_digest(sig, self.get_signature(key, value))/return sig == self.get_signature(key, value)/' src/itsdangerous/signer.py
rm -f src/itsdangerous/signer.py.bak
git diff --stat

echo; echo "## 4. the library's tests after the edit"
PYTHONPATH=src "$PY" -m pytest -q 2>&1 | tail -1

echo; echo "## 5. what AEC reports"
"$AEC" edges . -o .aec/edges.jsonl
"$AEC" edges --diff "$WORK/old.jsonl" .aec/edges.jsonl
"$AEC" code-impact .aec/records.jsonl "$WORK/old.jsonl" .aec/edges.jsonl
