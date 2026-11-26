#!/usr/bin/env bash
# compile-check.sh — build a LaTeX project with latexmk and print a short, actionable summary.
#
#   bash compile-check.sh [main.tex] [--outdir DIR] [--engine auto|pdflatex|lualatex|xelatex]
#                         [--quick] [--shell-escape] [--strict]
#
# Engine "auto" (default): --engine > "% !TEX program = ..." in the main file > $pdf_mode in the
# project's .latexmkrc > LuaLaTeX when fontspec/unicode-math/polyglossia are loaded > pdfLaTeX.
# latexmk runs biber/bibtex and makeindex itself; when the project has no .latexmkrc, rules for
# makeglossaries and nomencl are added if the sources need them. -shell-escape is added for
# minted/svg. Default is a full rebuild (latexmk -gg); --quick reuses auxiliary files.
#
# Prints: engine and bibliography tool · pages and page size · undefined citations/references ·
# duplicate labels · LaTeX errors (minus regexes in .academic-workflow/benign-notices.txt) ·
# bibliography-tool problems (.blg) · overfull/underfull/float-too-large counts · fonts not
# embedded or Type 3 (pdffonts) · unresolved "??" / "[?]" left in the PDF text · placeholders.
# Exit: 1 when no PDF was produced; with --strict also 3 when errors or undefined items remain.
# Raw output: <outdir>/compile.log. Needs bash (Linux, macOS, WSL or Git Bash on Windows).
set -uo pipefail

MAIN=""; OUTDIR="build"; ENGINE="auto"; FULL="-gg"; SHELLESC=0; STRICT=0
while [ $# -gt 0 ]; do
  case "$1" in
    --outdir) OUTDIR="$2"; shift 2 ;;
    --engine) ENGINE="$2"; shift 2 ;;
    --quick) FULL=""; shift ;;
    --shell-escape) SHELLESC=1; shift ;;
    --strict) STRICT=1; shift ;;
    -h|--help) sed -n '2,19p' "$0"; exit 0 ;;
    *) MAIN="$1"; shift ;;
  esac
done

if [ -z "$MAIN" ]; then
  if [ -f main.tex ] && grep -qsE '^[^%]*\\begin\{document\}' main.tex; then
    MAIN=main.tex
  else
    MAIN=$(grep -lsE '^[^%]*\\begin\{document\}' ./*.tex 2>/dev/null | head -1)
    [ -z "$MAIN" ] && MAIN=$(grep -rlsE '^[^%]*\\begin\{document\}' --include='*.tex' . 2>/dev/null | grep -v "/$OUTDIR/" | head -1)
  fi
fi
[ -z "$MAIN" ] && { echo "!! no main .tex file (with \\begin{document}) found; pass it explicitly" >&2; exit 2; }
command -v latexmk >/dev/null 2>&1 || { echo "!! latexmk not found — install TeX Live/MiKTeX or run setup-sandbox-latex.sh" >&2; exit 2; }
cd "$(dirname "$MAIN")" || exit 2
MAIN=$(basename "$MAIN"); BASE="${MAIN%.tex}"
[ -d "${TEXMFHOME:-$HOME/texmf}" ] && export TEXMFHOME="${TEXMFHOME:-$HOME/texmf}"
mkdir -p "$OUTDIR"
# \include{chapters/x} writes chapters/x.aux inside the output directory, and TeX cannot create
# folders ("I can't write on file `chapters/x.aux'"): mirror the source sub-folders first.
find . -name '*.tex' -not -path "./$OUTDIR/*" -not -path './.git/*' -exec dirname {} \; 2>/dev/null | sort -u \
  | while IFS= read -r d; do [ "$d" != "." ] && mkdir -p "$OUTDIR/$d"; done

RC=""; [ -f .latexmkrc ] && RC=.latexmkrc; [ -z "$RC" ] && [ -f latexmkrc ] && RC=latexmkrc
SRC_ALL=$(grep -rhs --include='*.tex' --include='*.sty' --include='*.cls' -v '^[[:space:]]*%' . 2>/dev/null)
ENGFLAG=""; ENGSRC="option"
if [ "$ENGINE" = "auto" ]; then
  magic=$(head -30 "$MAIN" | grep -ioE '%[[:space:]]*!TeX[[:space:]]+(TS-)?program[[:space:]]*=[[:space:]]*[a-z]+' | head -1 | sed -E 's/.*=[[:space:]]*//' | tr 'A-Z' 'a-z')
  if [ -n "$magic" ]; then ENGINE="$magic"; ENGSRC="magic comment"
  elif [ -n "$RC" ] && grep -qE '^\s*\$pdf_mode\s*=' "$RC"; then ENGINE="(from $RC)"; ENGSRC="$RC"
  elif echo "$SRC_ALL" | grep -qE '\\usepackage(\[[^]]*\])?\{(fontspec|unicode-math|polyglossia)\}'; then ENGINE="lualatex"; ENGSRC="fontspec/unicode-math/polyglossia"
  else ENGINE="pdflatex"; ENGSRC="default"; fi
fi
case "$ENGINE" in
  pdflatex|pdftex|pdflatexmk|latexmk) ENGFLAG="-pdf" ;;      # TeXShop's "pdflatexmk" etc. map to the engine
  lualatex|luatex|lualatexmk) ENGFLAG="-lualatex" ;;
  xelatex|xetex|xelatexmk) ENGFLAG="-xelatex" ;;
  "(from "*) ENGFLAG="" ;;
  *) echo "!! unknown engine '$ENGINE' (use pdflatex, lualatex or xelatex)" >&2; exit 2 ;;
esac

EXTRA=()
if [ -z "$RC" ]; then
  if echo "$SRC_ALL" | grep -qE '\\makeglossaries\b'; then
    EXTRA+=(-e 'add_cus_dep("acn","acr",0,"mkgls"); add_cus_dep("glo","gls",0,"mkgls"); sub mkgls { my ($b,$p)=fileparse($_[0]); my $c=Cwd::getcwd(); chdir $p if $p; my $r=system("makeglossaries",$b); chdir $c; return $r; }')
  fi
  if echo "$SRC_ALL" | grep -qE '\\makenomenclature\b'; then
    EXTRA+=(-e 'add_cus_dep("nlo","nls",0,"mknls"); sub mknls { return system("makeindex \"$_[0].nlo\" -s nomencl.ist -o \"$_[0].nls\""); }')
  fi
fi
if [ "$SHELLESC" = 1 ] || echo "$SRC_ALL" | grep -qE '\\usepackage(\[[^]]*\])?\{(minted|svg|gnuplottex)\}'; then
  EXTRA+=(-shell-escape); echo "   (adding -shell-escape: minted/svg/gnuplottex in use or --shell-escape given)"
fi

echo "== build: latexmk ${ENGFLAG:-(engine from $RC)} $FULL -outdir=$OUTDIR $MAIN    [engine: $ENGINE via $ENGSRC]"
latexmk $ENGFLAG $FULL -f -interaction=nonstopmode -file-line-error -synctex=1 -outdir="$OUTDIR" "${EXTRA[@]}" "$MAIN" > "$OUTDIR/compile.log" 2>&1
LOG="$OUTDIR/$BASE.log"; PDF="$OUTDIR/$BASE.pdf"; BLG="$OUTDIR/$BASE.blg"
problems=0

echo "== PDF"
if [ -f "$PDF" ]; then
  pages=$(grep -aoE "Output written on .*\(([0-9]+) pages?" "$LOG" 2>/dev/null | tail -1 | grep -oE "[0-9]+ pages?")
  size=""; command -v pdfinfo >/dev/null 2>&1 && size=$(pdfinfo "$PDF" 2>/dev/null | awk -F': *' '/^Page size/{print $2; exit}')
  [ -z "$pages" ] && command -v pdfinfo >/dev/null 2>&1 && pages="$(pdfinfo "$PDF" 2>/dev/null | awk '/^Pages/{print $2" pages"}')"
  echo "   $PDF — ${pages:-? pages} — ${size:-page size ?} ($(du -h "$PDF" | cut -f1))"
else
  echo "   NO PDF PRODUCED — read $OUTDIR/compile.log and $LOG"
fi
eng_used=$(head -1 "$LOG" 2>/dev/null | grep -oE 'pdfTeX|LuaHBTeX|LuaTeX|XeTeX' | head -1)
bib_used=$(grep -oE "Running '(biber|bibtex|bibtex8|bibtexu)[^']*'" "$OUTDIR/compile.log" 2>/dev/null | head -1 | sed -E "s/Running '([a-z0-9]+).*/\1/")
echo "   engine run: ${eng_used:-?} · bibliography tool run: ${bib_used:-none}"

echo "== undefined citations (wrong key, or the bibliography tool did not run)"
cites=$(grep -aoE "Citation [\`'][^']+' (on page|undefined)" "$LOG" 2>/dev/null | sed -E "s/Citation [\`']([^']+)'.*/\1/" | sort -u)
[ -n "$cites" ] && { echo "$cites" | sed 's/^/   /'; problems=1; } || echo "   (none)"

echo "== undefined references (\\label / \\ref mismatch, or a pass missing)"
refs=$(grep -aoE "Reference [\`'][^']+' on page" "$LOG" 2>/dev/null | sed -E "s/Reference [\`']([^']+)'.*/\1/" | sort -u)
[ -n "$refs" ] && { echo "$refs" | sed 's/^/   /'; problems=1; } || echo "   (none)"
dups=$(grep -aoE "Label [\`'][^']+' multiply defined" "$LOG" 2>/dev/null | sed -E "s/Label [\`']([^']+)'.*/\1/" | sort -u)
[ -n "$dups" ] && { echo "   duplicate labels: $(echo $dups)"; problems=1; }

echo "== LaTeX errors"
BENIGN=""; for b in .academic-workflow/benign-notices.txt .tcc-workflow/benign-notices.txt; do [ -f "$b" ] && BENIGN="$b" && break; done
errs=$(grep -aE "^!|^[^ :]+\.(tex|sty|cls|bbl|aux):[0-9]+: " "$LOG" 2>/dev/null | sort -u)
if [ -n "$errs" ] && [ -n "$BENIGN" ]; then
  while IFS= read -r pat; do
    [ -z "$pat" ] && continue; case "$pat" in \#*) continue ;; esac
    errs=$(echo "$errs" | grep -vE -- "$pat")
  done < "$BENIGN"
fi
if [ -n "$errs" ]; then echo "$errs" | head -25 | sed 's/^/   /'; problems=1; else echo "   (none)"; fi
[ -n "$BENIGN" ] && echo "   (benign patterns filtered: $BENIGN)"

echo "== bibliography tool (.blg)"
if [ -f "$BLG" ]; then
  bl=$(grep -aE "ERROR|WARN|^Warning--|error message|I couldn't open|Repeated entry|I was expecting" "$BLG" | grep -v 'INFO - ' | sed -E 's/^\[[0-9]+\] [^ ]+ //' | sort -u | head -15)
  [ -n "$bl" ] && echo "$bl" | sed 's/^/   /' || echo "   (clean)"
  grep -qaE "ERROR|error message|I couldn't open" "$BLG" && problems=1
else
  echo "   (no .blg: no bibliography run)"
fi

echo "== layout"
echo "   overfull boxes: $(grep -ac 'Overfull \\' "$LOG" 2>/dev/null)   underfull: $(grep -ac 'Underfull \\' "$LOG" 2>/dev/null)   float too large: $(grep -ac 'Float too large' "$LOG" 2>/dev/null)   missing glyphs: $(grep -ac 'Missing character: There is no' "$LOG" 2>/dev/null)"
grep -aE "Overfull \\\\hbox \(([0-9]{2,}|[5-9])\.[0-9]+pt" "$LOG" 2>/dev/null | head -5 | sed 's/^/   worst: /'

if [ -f "$PDF" ] && command -v pdffonts >/dev/null 2>&1; then
  echo "== fonts (pdffonts: venues and PDF/A require every font embedded, many reject Type 3)"
  pdffonts "$PDF" 2>/dev/null | awk '
    NR==2 { n=split($0, seg, " "); pos=1; for (i=1;i<=n;i++){ start[i]=pos; len[i]=length(seg[i]); pos+=len[i]+1 } next }
    NR>2  { name=substr($0,start[1],len[1]); type=substr($0,start[2],len[2]); emb=substr($0,start[4],len[4]);
            gsub(/ +$/,"",name); gsub(/ +$/,"",type); gsub(/ /,"",emb); total++;
            if (emb=="no") { ne++; printf "   NOT EMBEDDED: %s (%s)\n", name, type }
            if (type ~ /Type 3/) { t3++; printf "   Type 3: %s\n", name } }
    END { printf "   %d fonts, %d not embedded, %d Type 3\n", total, ne+0, t3+0 }'
fi

if [ -f "$PDF" ] && command -v pdftotext >/dev/null 2>&1; then
  echo "== unresolved markers in the PDF text"
  unres=$(pdftotext -q "$PDF" - 2>/dev/null | grep -nE '\?\?|\[\?\]|\(\?\)' | head -5)
  [ -n "$unres" ] && { echo "$unres" | cut -c1-120 | sed 's/^/   /'; problems=1; } || echo "   (none: no ??, [?] or (?))"
fi

echo "== placeholders in the sources (TODO/FIXME/XXX/TBD, \\todo, lipsum, example-image)"
ph=$(grep -rnsE --include='*.tex' --exclude-dir="$OUTDIR" --exclude-dir='.academic-workflow' --exclude-dir='.git' \
       '\bTODO\b|\bFIXME\b|\bXXX\b|\bTBD\b|\\todo\b|\\lipsum|\\blindtext|[Ll]orem ipsum|example-image' . 2>/dev/null | cut -c1-140)
if [ -n "$ph" ]; then echo "$ph" | head -20 | sed 's/^/   /'; n=$(echo "$ph" | wc -l); [ "$n" -gt 20 ] && echo "   … $((n-20)) more (audit-tex.py lists all)"; else echo "   (none)"; fi

echo "== done — full log: $OUTDIR/compile.log · LaTeX log: $LOG"
[ -f "$PDF" ] || exit 1
[ "$STRICT" = 1 ] && [ "$problems" = 1 ] && exit 3
exit 0
