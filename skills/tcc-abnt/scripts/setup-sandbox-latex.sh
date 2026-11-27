#!/usr/bin/env bash
# setup-sandbox-latex.sh — make a bare TeX Live able to compile abnTeX2 projects.
#
# Many sandboxes (Cowork, CI runners, minimal Docker images) ship TeX Live without
# abnTeX2 or Portuguese babel. This script installs what is missing into the user
# tree ($TEXMFHOME, default ~/texmf) straight from CTAN, without touching the system
# TeX tree and without root. Safe to re-run: anything kpsewhich already finds is skipped.
#
#   bash setup-sandbox-latex.sh                 # abntex2 + babel-portuges (+ defaults below)
#   bash setup-sandbox-latex.sh algorithm2e xurl   # also fetch extra CTAN packages by name
#   bash setup-sandbox-latex.sh --force         # reinstall even if already found
#
# Your own machine (TeX Live full / MiKTeX / Overleaf) normally does not need this:
# there, `tlmgr install abntex2 babel-portuges` or MiKTeX on-the-fly installation is enough.
# On Debian/Ubuntu the same packages come from apt:
#   sudo apt-get install texlive-publishers texlive-lang-portuguese texlive-bibtex-extra
set -euo pipefail

TEXMFHOME="${TEXMFHOME:-$HOME/texmf}"
export TEXMFHOME
MIRRORS=("${CTAN_MIRROR:-https://mirrors.ctan.org}" "https://mirror.ctan.org" "https://ctan.math.utah.edu/ctan/tex-archive")
FORCE=0
EXTRA=()
for a in "$@"; do
  case "$a" in
    --force) FORCE=1 ;;
    -h|--help) sed -n '2,18p' "$0"; exit 0 ;;
    *) EXTRA+=("$a") ;;
  esac
done
# Packages commonly required by institutional abnTeX2 templates but absent from
# small TeX Live installs. Each is skipped when kpsewhich already finds it.
DEFAULT_EXTRA=(algorithm2e algorithms tracklang)   # tracklang: needed by glossaries, missing in trimmed images

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

need() { command -v "$1" >/dev/null 2>&1; }
have_tex_file() { [ "$FORCE" -eq 0 ] && kpsewhich "$1" >/dev/null 2>&1; }

fetch() {  # fetch <ctan-relative-path> <out-file>
  local rel="$1" out="$2" m
  for m in "${MIRRORS[@]}"; do
    if curl -fsSL --retry 2 --connect-timeout 20 -o "$out" "$m/$rel" && unzip -tq "$out" >/dev/null 2>&1; then
      return 0
    fi
  done
  echo "!! could not download $rel from any CTAN mirror" >&2
  return 1
}

for t in pdflatex bibtex latexmk kpsewhich unzip curl; do
  if ! need "$t"; then
    echo "!! '$t' not found. Install a TeX Live base first (Debian/Ubuntu: texlive-latex-extra latexmk)." >&2
    exit 1
  fi
done
mkdir -p "$TEXMFHOME"

# 1. abnTeX2 — class, abntex2cite, .bst styles, canonical models (TDS archive: just unzip)
if have_tex_file abntex2.cls; then
  echo "== abntex2: already available ($(kpsewhich abntex2.cls))"
else
  echo "== abntex2: downloading TDS archive"
  fetch install/macros/latex/contrib/abntex2.tds.zip "$WORK/abntex2.tds.zip"
  unzip -oq "$WORK/abntex2.tds.zip" -d "$TEXMFHOME"
fi

# 2. babel-portuges — provides brazil.ldf (option `brazil`/`brazilian` of babel).
#    CTAN ships it as source; run the .ins with plain TeX to generate the .ldf files.
if have_tex_file brazil.ldf; then
  echo "== babel-portuges: already available ($(kpsewhich brazil.ldf))"
else
  echo "== babel-portuges: downloading and generating .ldf files"
  fetch macros/latex/contrib/babel-contrib/portuges.zip "$WORK/portuges.zip"
  mkdir -p "$WORK/portuges" && unzip -oq "$WORK/portuges.zip" -d "$WORK/portuges"
  ( cd "$WORK/portuges/portuges" && tex -interaction=batchmode portuges.ins >/dev/null 2>&1 || pdflatex -interaction=batchmode portuges.ins >/dev/null 2>&1 || true )
  dest="$TEXMFHOME/tex/generic/babel-portuges"; mkdir -p "$dest"
  find "$WORK/portuges" -name '*.ldf' -exec cp {} "$dest/" \;
  [ -f "$dest/brazil.ldf" ] || { echo "!! brazil.ldf was not generated" >&2; exit 1; }
fi

# 3. Latin Modern fonts — the canonical abnTeX2 model loads `lmodern`, and trimmed
#    TeX Live images often lack it. The CTAN bundle is already TDS-shaped: merge and
#    enable its font map for pdfTeX.
if have_tex_file lmodern.sty; then
  echo "== lmodern: already available ($(kpsewhich lmodern.sty))"
else
  echo "== lmodern: downloading Latin Modern bundle (~19 MB)"
  if fetch fonts/lm.zip "$WORK/lm.zip"; then
    mkdir -p "$WORK/lm" && unzip -oq "$WORK/lm.zip" -d "$WORK/lm"
    cp -r "$WORK/lm/lm/." "$TEXMFHOME/"
    mktexlsr "$TEXMFHOME" >/dev/null 2>&1 || true
    updmap-user --quiet --enable Map=lm.map >/dev/null 2>&1 || updmap --quiet --enable Map=lm.map >/dev/null 2>&1 || \
      echo "   (could not run updmap; if pdfTeX complains about lm fonts, run: updmap-user --enable Map=lm.map)"
  else
    echo "   (skipped — templates that use \\usepackage{lmodern} will fail; Times-based templates such as UniforTeX2 are unaffected)"
  fi
fi

# 4. Extra CTAN packages by name (best effort: unzip, run .ins if any, copy style files)
for pkg in "${DEFAULT_EXTRA[@]}" "${EXTRA[@]}"; do
  if have_tex_file "$pkg.sty" || { [ "$pkg" = algorithms ] && have_tex_file algorithmic.sty; }; then
    echo "== $pkg: already available"; continue
  fi
  echo "== $pkg: downloading from CTAN"
  if ! fetch "macros/latex/contrib/$pkg.zip" "$WORK/$pkg.zip" 2>/dev/null && ! fetch "macros/generic/$pkg.zip" "$WORK/$pkg.zip" 2>/dev/null; then
    echo "   (skipped — not found under macros/latex/contrib or macros/generic; install it by hand if your template needs it)"; continue
  fi
  mkdir -p "$WORK/$pkg" && unzip -oq "$WORK/$pkg.zip" -d "$WORK/$pkg"
  while IFS= read -r ins; do
    ( cd "$(dirname "$ins")" && pdflatex -interaction=batchmode "$(basename "$ins")" >/dev/null 2>&1 || true )
  done < <(find "$WORK/$pkg" -name '*.ins' -not -path '*/samples/*')
  dest="$TEXMFHOME/tex/latex/$pkg"; mkdir -p "$dest"
  find "$WORK/$pkg" -not -path '*/samples/*' \( -name '*.sty' -o -name '*.cls' -o -name '*.def' -o -name '*.clo' -o -name '*.cfg' -o -name '*.ldf' \) -exec cp {} "$dest/" \;
  gdest="$TEXMFHOME/tex/generic/$pkg"; mkdir -p "$gdest"   # generic .tex helpers produced by the .ins (e.g. tracklang.tex)
  find "$WORK/$pkg" -maxdepth 2 -name '*.tex' -not -path '*/samples/*' -not -path '*/doc/*' -not -name 'sample*' -newer "$WORK/$pkg.zip" -exec cp {} "$gdest/" \;
  bst=$(find "$WORK/$pkg" -name '*.bst' | head -1)
  if [ -n "$bst" ]; then mkdir -p "$TEXMFHOME/bibtex/bst/$pkg"; find "$WORK/$pkg" -name '*.bst' -exec cp {} "$TEXMFHOME/bibtex/bst/$pkg/" \; ; fi
done

mktexlsr "$TEXMFHOME" >/dev/null 2>&1 || texhash "$TEXMFHOME" >/dev/null 2>&1 || true

echo
echo "== check"
for f in abntex2.cls abntex2cite.sty abntex2-alf.bst brazil.ldf lmodern.sty; do
  printf '   %-18s %s\n' "$f" "$(kpsewhich "$f" || echo MISSING)"
done
echo
echo "Toolchain ready. Compile with:"
echo "  TEXMFHOME=$TEXMFHOME latexmk -pdf -interaction=nonstopmode -outdir=build main.tex"
echo "or run scripts/compile-check.sh (it exports TEXMFHOME for you)."
