#!/usr/bin/env bash
# run-tests.sh — everything CI runs, in order. Needs Python 3.8+; the LaTeX parts need TeX Live
# with latexmk and biber (they are skipped with a notice otherwise).
#   bash tests/run-tests.sh            # checks + unit tests + full LaTeX matrix + template documents
#   bash tests/run-tests.sh --quick    # one skeleton variant per type
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0
echo "== check.py";            python3 scripts/check.py || fail=1
echo "== unit tests";          python3 -m unittest discover -s tests || fail=1
if command -v latexmk >/dev/null 2>&1 && command -v biber >/dev/null 2>&1; then
  echo "== skeleton matrix";   bash tests/latex-matrix.sh "${1:-}" || fail=1
  echo "== template documents (tests/publisher, tests/thesis-classes)"
  for f in tests/publisher/*.tex tests/thesis-classes/*.tex; do
    work="$(mktemp -d "${TMPDIR:-/tmp}/tpl.XXXXXX")"; cp "$f" "$work/"; cp tests/publisher/refs.bib "$work/"
    b="$(basename "${f%.tex}")"
    ( cd "$work" && timeout 300 latexmk -pdf -interaction=nonstopmode -file-line-error "$b.tex" >/dev/null 2>&1 )
    errs=$(grep -c '^!\|^\./.*:[0-9]*: ' "$work/$b.log" 2>/dev/null); und=$(grep -cE 'Citation .* undefined|Reference .* undefined' "$work/$b.log" 2>/dev/null)
    if [ -f "$work/$b.pdf" ] && [ "${errs:-1}" = 0 ] && [ "${und:-1}" = 0 ]; then echo "ok   $f"; else echo "FAIL $f (errors=$errs undefined=$und, see $work)"; fail=1; fi
  done
else
  echo "== LaTeX tests skipped (latexmk/biber not installed)"
fi
[ "$fail" = 0 ] && echo "== ALL TESTS PASSED" || echo "== SOME TESTS FAILED"
exit "$fail"
