#!/usr/bin/env bash
# package.sh — build dist/tcc-abnt.zip (the skill folder as the ZIP root, as claude.ai expects)
# and run the sanity checks. Run after any change under skills/tcc-abnt/.
#   bash scripts/package.sh            # build + check
#   bash scripts/package.sh --check    # only verify that dist/tcc-abnt.zip matches the sources
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_DIR="$ROOT/skills/tcc-abnt"
OUT="$ROOT/dist/tcc-abnt.zip"

python3 "$ROOT/scripts/check.py"

if [ "${1:-}" = "--check" ]; then
  [ -f "$OUT" ] || { echo "!! $OUT missing — run scripts/package.sh"; exit 1; }
  tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
  unzip -q "$OUT" -d "$tmp"
  if diff -r --exclude='__pycache__' "$SKILL_DIR" "$tmp/tcc-abnt" >/dev/null; then
    echo "dist/tcc-abnt.zip is up to date"
  else
    echo "!! dist/tcc-abnt.zip is stale — run scripts/package.sh and commit it"; diff -r --exclude='__pycache__' "$SKILL_DIR" "$tmp/tcc-abnt" | head -20; exit 1
  fi
  exit 0
fi

mkdir -p "$ROOT/dist"
rm -f "$OUT"
( cd "$ROOT/skills" && find tcc-abnt -type f ! -name '*.pyc' ! -path '*/__pycache__/*' | LC_ALL=C sort | zip -X -q "$OUT" -@ )
echo "built $OUT ($(du -h "$OUT" | cut -f1))"
unzip -l "$OUT" | tail -1
