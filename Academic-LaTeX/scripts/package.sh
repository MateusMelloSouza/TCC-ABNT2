#!/usr/bin/env bash
# package.sh — build dist/academic-latex.zip (the skill folder as the ZIP root, as claude.ai
# expects; the evals/ folder is left out) and run the sanity checks.
#   bash scripts/package.sh            # build + check
#   bash scripts/package.sh --check    # only verify that dist/academic-latex.zip matches the sources
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NAME=academic-latex
SKILL_DIR="$ROOT/skills/$NAME"
OUT="$ROOT/dist/$NAME.zip"

python3 "$ROOT/scripts/check.py"

list_files() { ( cd "$ROOT/skills" && find "$NAME" -type f ! -name '*.pyc' ! -path '*/__pycache__/*' ! -path "$NAME/evals/*" | LC_ALL=C sort ); }

if [ "${1:-}" = "--check" ]; then
  [ -f "$OUT" ] || { echo "!! $OUT missing — run scripts/package.sh"; exit 1; }
  tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
  unzip -q "$OUT" -d "$tmp"
  if diff -r --exclude='__pycache__' --exclude='evals' "$SKILL_DIR" "$tmp/$NAME" >/dev/null; then
    echo "dist/$NAME.zip is up to date"
  else
    echo "!! dist/$NAME.zip is stale — run scripts/package.sh and commit it"
    diff -r --exclude='__pycache__' --exclude='evals' "$SKILL_DIR" "$tmp/$NAME" | head -20; exit 1
  fi
  exit 0
fi

mkdir -p "$ROOT/dist"
rm -f "$OUT"
( cd "$ROOT/skills" && list_files | zip -X -q "$OUT" -@ )
echo "built $OUT ($(du -h "$OUT" | cut -f1))"
unzip -l "$OUT" | tail -1
