#!/usr/bin/env bash
# latex-matrix.sh — generate every skeleton variant with new-project.py and compile it.
# Fails (exit 1) when any variant has no PDF, a LaTeX error, an undefined citation or
# reference, or a biber/BibTeX error. Needs a TeX Live with biber and latexmk.
#   bash tests/latex-matrix.sh            # full matrix
#   bash tests/latex-matrix.sh --quick    # one variant per document type and engine
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NP="$ROOT/skills/academic-latex/scripts/new-project.py"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/latex-matrix.XXXXXX")"
echo "== work dir: $WORK"
fail=0

run() {  # run <name> <new-project args...>
  local name="$1"; shift
  if ! python3 "$NP" "$WORK/$name" "$@" >"$WORK/$name.gen.log" 2>&1; then
    echo "FAIL $name (generator)"; fail=1; return
  fi
  local main=main; [ -f "$WORK/$name/response.tex" ] && main=response
  ( cd "$WORK/$name" && timeout 300 latexmk -interaction=nonstopmode -file-line-error >"$WORK/$name.build.log" 2>&1 )
  local log="$WORK/$name/$main.log" pdf="$WORK/$name/$main.pdf" blg="$WORK/$name/$main.blg"
  local errs und biberr pages
  errs=$(grep -c '^!\|^\./.*:[0-9]*: ' "$log" 2>/dev/null); errs=${errs:-0}
  und=$(grep -cE "Citation .* undefined|Reference .* undefined|There were undefined" "$log" 2>/dev/null); und=${und:-0}
  biberr=$(grep -cE '^ERROR|ERROR -|I couldn.t open|error message' "$blg" 2>/dev/null); biberr=${biberr:-0}
  pages=$(grep -oE 'Output written on .* \(([0-9]+) pages?' "$log" 2>/dev/null | grep -oE '[0-9]+ pages?')
  if [ -f "$pdf" ] && [ "$errs" = 0 ] && [ "$und" = 0 ] && [ "$biberr" = 0 ]; then
    printf 'ok   %-32s %s\n' "$name" "${pages:-?}"
  else
    printf 'FAIL %-32s pdf=%s errors=%s undefined=%s bib-errors=%s (see %s)\n' "$name" \
      "$([ -f "$pdf" ] && echo yes || echo no)" "$errs" "$und" "$biberr" "$WORK/$name"
    fail=1
  fi
}

if [ "${1:-}" = "--quick" ]; then
  run thesis --type thesis
  run article --type article
  run letter --type letter
  run thesis-lualatex --type thesis --engine lualatex
else
  for s in $(python3 "$NP" --list-styles | awk 'NR%2==1{print $1}'); do
    run "article-$s" --type article --style "$s"
    run "thesis-$s" --type thesis --style "$s"
  done
  for e in lualatex xelatex; do
    run "thesis-$e" --type thesis --engine "$e"
    run "article-$e" --type article --engine "$e"
    run "letter-$e" --type letter --engine "$e"
  done
  run letter --type letter
  run thesis-british-letter-double-twoside --type thesis --language british --paper letter --spacing double --twoside
  run thesis-ngerman --type thesis --language ngerman
  run thesis-abnt-brazilian --type thesis --style abnt --language brazilian
  run article-apa-american --type article --style apa --language american
fi
[ "$fail" = 0 ] && echo "== latex matrix: all variants compiled cleanly" || echo "== latex matrix: FAILURES (outputs kept in $WORK)"
exit "$fail"
