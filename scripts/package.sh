#!/usr/bin/env bash
# package.sh — build dist/tcc-abnt.zip (the skill folder as the ZIP root, as claude.ai expects)
# and run the sanity checks. The ZIP is not committed: CI builds it on every push and the
# release job attaches it to the GitHub release.
#   bash scripts/package.sh            # check + build
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/dist/tcc-abnt.zip"

python3 "$ROOT/scripts/check.py"

mkdir -p "$ROOT/dist"
rm -f "$OUT"
( cd "$ROOT/skills" && find tcc-abnt -type f ! -name '*.pyc' ! -path '*/__pycache__/*' | LC_ALL=C sort | zip -X -q "$OUT" -@ )
echo "built $OUT ($(du -h "$OUT" | cut -f1))"
unzip -l "$OUT" | tail -1
