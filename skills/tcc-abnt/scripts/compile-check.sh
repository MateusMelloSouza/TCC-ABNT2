#!/usr/bin/env bash
# compile-check.sh — build an abnTeX2 project and print a short, actionable summary.
#
#   bash compile-check.sh [main.tex] [--outdir DIR] [--engine pdflatex|xelatex|lualatex] [--quick] [--lenient]
#
# Defaults: main file auto-detected (the .tex containing \begin{document}), outdir "build",
# engine pdflatex, full rebuild (latexmk -gg). --quick skips the full rebuild.
# Run scripts/setup-sandbox-latex.sh first in sandboxes that lack abnTeX2.
#
# Prints: pages · undefined citations · undefined references · LaTeX errors (minus the
# patterns listed one per line in .tcc-workflow/benign-notices.txt) · overfull/float-too-large
# counts · placeholder scan. Raw log: <outdir>/compile.log
# The previous output PDF is removed before building, so a stale PDF never counts as success.
#
# Exit codes:
#   0  PDF produced, no LaTeX errors, no undefined citations, no undefined references
#   1  no PDF produced
#   2  usage error / no main .tex found
#   3  PDF produced but the log shows LaTeX errors, undefined citations or undefined references
#      (--lenient restores the old behaviour: exit 0 whenever a PDF exists)
set -uo pipefail

MAIN=""; OUTDIR="build"; ENGINE="pdflatex"; FULL="-gg"; LENIENT=0
while [ $# -gt 0 ]; do
  case "$1" in
    --outdir|--engine)
      [ $# -ge 2 ] || { echo "compile-check.sh: $1 needs a value" >&2; exit 2; }
      if [ "$1" = --outdir ]; then OUTDIR="$2"; else ENGINE="$2"; fi
      shift 2 ;;
    --quick) FULL=""; shift ;;
    --lenient) LENIENT=1; shift ;;
    -h|--help) sed -n '2,20p' "$0"; exit 0 ;;
    *) MAIN="$1"; shift ;;
  esac
done

# Work from the project root (the directory of the main file).
if [ -z "$MAIN" ]; then
  if [ -f main.tex ] && grep -qsE '^[^%]*\\begin\{document\}' main.tex; then
    MAIN=main.tex
  else
    MAIN=$(grep -lsE '^[^%]*\\begin\{document\}' ./*.tex 2>/dev/null | head -1)
    [ -z "$MAIN" ] && MAIN=$(grep -rlsE '^[^%]*\\begin\{document\}' --include='*.tex' . 2>/dev/null | grep -v "$OUTDIR/" | head -1)
  fi
fi
[ -z "$MAIN" ] && { echo "!! no main .tex file (with \\begin{document}) found; pass it explicitly" >&2; exit 2; }
cd "$(dirname "$MAIN")" || exit 2
MAIN=$(basename "$MAIN"); BASE="${MAIN%.tex}"

[ -d "${TEXMFHOME:-$HOME/texmf}" ] && export TEXMFHOME="${TEXMFHOME:-$HOME/texmf}"
mkdir -p "$OUTDIR"

case "$ENGINE" in
  xelatex) ENG="-xelatex" ;;
  lualatex) ENG="-lualatex" ;;
  *) ENG="-pdf" ;;
esac

# Glossaries: honour the project's .latexmkrc; otherwise inject the rule when the sources use it.
GLOSS_ARGS=()
if [ ! -f .latexmkrc ] && [ ! -f latexmkrc ] && grep -rqs --include='*.tex' '\\makeglossaries' . ; then
  GLOSS_ARGS=(-e 'add_cus_dep("acn","acr",0,"makeglossaries"); add_cus_dep("glo","gls",0,"makeglossaries"); sub makeglossaries { my ($base,$path)=fileparse($_[0]); my $cwd=Cwd::getcwd(); chdir $path if $path; my $r=system("makeglossaries",$base); chdir $cwd; return $r; }')
fi

rm -f "$OUTDIR/$BASE.pdf"
# TeX wraps log lines at 79 columns by default, which cuts error messages in the middle
# ("Package babel E") and defeats the benign-notice patterns. TeX Live reads these from
# the environment; other distributions ignore them.
export max_print_line=10000 error_line=254 half_error_line=238
echo "== build: latexmk $ENG $FULL -outdir=$OUTDIR $MAIN"
latexmk $ENG $FULL -f -interaction=nonstopmode -file-line-error -outdir="$OUTDIR" ${GLOSS_ARGS[@]+"${GLOSS_ARGS[@]}"} "$MAIN" > "$OUTDIR/compile.log" 2>&1
LOG="$OUTDIR/$BASE.log"; PDF="$OUTDIR/$BASE.pdf"

echo "== PDF"
if [ -f "$PDF" ]; then
  pages=$(grep -oE "Output written on .*\(([0-9]+) pages?" "$LOG" 2>/dev/null | tail -1 | grep -oE "[0-9]+ pages?")
  [ -z "$pages" ] && command -v pdfinfo >/dev/null 2>&1 && pages="$(pdfinfo "$PDF" 2>/dev/null | awk '/^Pages/{print $2" pages"}')"
  echo "   $PDF — ${pages:-? pages} ($(du -h "$PDF" | cut -f1))"
else
  echo "   NO PDF PRODUCED — read $OUTDIR/compile.log"
fi

echo "== undefined citations (fix the key or run the bibliography pass)"
cites=$(grep -oE "Citation \`[^']+' on page" "$LOG" 2>/dev/null | sed -E "s/Citation \`([^']+)'.*/\1/" | sort -u)
[ -n "$cites" ] && echo "$cites" | sed 's/^/   /' || echo "   (none)"

echo "== undefined references (bad \\label / \\ref)"
refs=$(grep -oE "Reference \`[^']+' on page" "$LOG" 2>/dev/null | sed -E "s/Reference \`([^']+)'.*/\1/" | sort -u)
[ -n "$refs" ] && echo "$refs" | sed 's/^/   /' || echo "   (none)"

echo "== LaTeX errors"
BENIGN=".tcc-workflow/benign-notices.txt"
errs=$(grep -E "^!|^([A-Za-z]:)?[^ :]+:[0-9]+: " "$LOG" 2>/dev/null | sort -u)
if [ -n "$errs" ] && [ -f "$BENIGN" ]; then
  while IFS= read -r pat; do
    [ -z "$pat" ] && continue; case "$pat" in \#*) continue ;; esac
    errs=$(echo "$errs" | grep -vE -- "$pat")
  done < "$BENIGN"
fi
if [ -n "$errs" ]; then echo "$errs" | sed 's/^/   /'; else echo "   (none)"; fi
[ -f "$BENIGN" ] && echo "   (benign patterns filtered from $BENIGN)"

echo "== layout"
echo "   overfull boxes: $(grep -c 'Overfull \\' "$LOG" 2>/dev/null)   float too large: $(grep -c 'Float too large' "$LOG" 2>/dev/null)   undefined-references warning: $(grep -c 'There were undefined references' "$LOG" 2>/dev/null)"

echo "== placeholders in sources (lipsum / lorem ipsum / TODO / FIXME)"
ph=$( { grep -rniE --include='*.tex' --exclude-dir="$OUTDIR" --exclude-dir='.tcc-workflow' 'lipsum|lorem ipsum' . 2>/dev/null;
        grep -rnE  --include='*.tex' --exclude-dir="$OUTDIR" --exclude-dir='.tcc-workflow' '\bTODO\b|\bFIXME\b|\bXXX\b' . 2>/dev/null; } \
      | grep -vE '^\./[^:]+:[0-9]+:\s*%' | sort -t: -k1,1 -k2,2n -u | cut -c1-140)
[ -n "$ph" ] && echo "$ph" | sed 's/^/   /' || echo "   (none)"

echo "== done — full log: $OUTDIR/compile.log · LaTeX log: $LOG"
[ -f "$PDF" ] || exit 1
if [ "$LENIENT" -eq 0 ] && { [ -n "$errs" ] || [ -n "$cites" ] || [ -n "$refs" ]; }; then
  echo "== FAILED — LaTeX errors, undefined citations or undefined references above (use --lenient to ignore)" >&2
  exit 3
fi
exit 0
