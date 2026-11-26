#!/usr/bin/env bash
# setup-sandbox-latex.sh — make an empty or minimal environment able to compile LaTeX projects.
#
#   bash setup-sandbox-latex.sh                 # toolchain + the packages most theses and papers use
#   bash setup-sandbox-latex.sh --minimal       # LaTeX, latexmk, biber and the common packages only
#   bash setup-sandbox-latex.sh --fonts         # also the big font collection (newtx, libertinus, ...)
#   bash setup-sandbox-latex.sh --lang german,french   # also babel language support
#   bash setup-sandbox-latex.sh PKG ...         # also these CTAN packages (e.g. acmart algorithm2e)
#   bash setup-sandbox-latex.sh --from-log build/main.log   # install what a failed build was missing
#   bash setup-sandbox-latex.sh --check         # report what is available; install nothing
#
# Strategies, in order: (1) Debian/Ubuntu apt (as root or with password-less sudo): TeX Live
# collections and single files mapped to their Debian package (apt-file when installed);
# (2) tlmgr, when a vanilla TeX Live (not Debian's) is present; (3) CTAN archives unpacked into
# $TEXMFHOME (default ~/texmf), no root needed. Sandboxes often block some of these hosts: the
# script reports which strategy failed and what to do instead (e.g. upload the missing .sty).
# Your own computer normally needs none of this: TeX Live (tlmgr), MacTeX, MiKTeX (installs
# missing packages on the fly) and Overleaf already have almost everything.
set -uo pipefail

TEXMFHOME="${TEXMFHOME:-$HOME/texmf}"; export TEXMFHOME
MIRRORS=("${CTAN_MIRROR:-https://mirrors.ctan.org}" "https://mirror.ctan.org" "https://ctan.math.utah.edu/ctan/tex-archive")
MODE=default; FONTS=0; LANGS=""; FROMLOG=""; CHECK=0; PKGS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --minimal) MODE=minimal; shift ;;
    --fonts) FONTS=1; shift ;;
    --lang) LANGS="$2"; shift 2 ;;
    --from-log) FROMLOG="$2"; shift 2 ;;
    --check) CHECK=1; shift ;;
    -h|--help) sed -n '2,20p' "$0"; exit 0 ;;
    *) PKGS+=("$1"); shift ;;
  esac
done

have() { command -v "$1" >/dev/null 2>&1; }
SUDO=""; if [ "$(id -u)" != 0 ]; then have sudo && sudo -n true 2>/dev/null && SUDO="sudo -n"; fi
APT=0; if have apt-get && { [ "$(id -u)" = 0 ] || [ -n "$SUDO" ]; }; then APT=1; fi
TLMGR=0; if have tlmgr && ! { have dpkg && dpkg -S "$(readlink -f "$(command -v tlmgr)")" >/dev/null 2>&1; }; then TLMGR=1; fi

report() {
  echo "== available tools"
  for t in pdflatex lualatex xelatex latexmk bibtex biber makeglossaries makeindex texcount pdffonts pdftotext; do
    printf '   %-15s %s\n' "$t" "$(command -v $t || echo MISSING)"
  done
  if have kpsewhich; then
    echo "== key packages (kpsewhich)"
    for f in biblatex.sty apa.bbx ieee.bbx natbib.sty glossaries.sty siunitx.sty tikz.sty fontspec.sty \
             IEEEtran.cls acmart.cls elsarticle.cls llncs.cls revtex4-2.cls memoir.cls scrbook.cls mwe.sty; do
      printf '   %-15s %s\n' "$f" "$(kpsewhich "$f" || echo MISSING)"
    done
  fi
  echo "== install routes: apt=$([ $APT = 1 ] && echo yes || echo no) tlmgr=$([ $TLMGR = 1 ] && echo yes || echo no) TEXMFHOME=$TEXMFHOME"
}
[ "$CHECK" = 1 ] && { report; exit 0; }

# ---------------------------------------------------------------- Debian package map (verified with dpkg -S)
deb_for() {  # deb_for <file>  -> Debian package name, or empty
  case "$1" in
    latexmk) echo latexmk ;; biber) echo biber ;; chktex) echo chktex ;;
    texcount|latexpand|latexdiff|latexindent|arara) echo texlive-extra-utils ;;
    makeglossaries|makeglossaries-lite) echo texlive-latex-extra ;; bib2gls) echo texlive-bibtex-extra ;;
    *.bbx|*.cbx|*.lbx|biblatex*.sty|biblatex.cfg) echo texlive-bibtex-extra ;;
    IEEEtran.*|acmart.cls|ACM-Reference-Format.bst|elsarticle*|llncs.cls|splncs04.bst|revtex4-*|apsrev4-*|aipnum4-*|\
    aastex*|mnras.cls|jmlr.cls|abntex2*|classicthesis.sty|arsclassica.sty|cleanthesis.sty|thuthesis.cls|ut-thesis.cls|\
    yathesis.cls|toptesi.cls|msu-thesis.cls|uothesis.cls|ucthesis.cls|mitthesis.cls|umthesis.cls|achemso.*) echo texlive-publishers ;;
    algorithm2e.sty|algorithmicx.sty|algpseudocode.sty|algorithm.sty|algorithmic.sty|siunitx.sty|mhchem.sty|physics.sty|\
    chemformula.sty|braket.sty|SIunits.sty|clrscode*.sty) echo texlive-science ;;
    tikz.sty|pgf*.sty|pgfplots.sty|chemfig.sty|tufte-*.cls|forest.sty|circuitikz.sty|tikz-*.sty|pgfgantt.sty) echo texlive-pictures ;;
    fontspec.sty|unicode-math.sty|polyglossia.sty|microtype.sty|memoir.cls|scr*.cls|scr*.sty|beamer.cls|listings.sty|\
    booktabs.sty|setspace.sty|subcaption.sty|caption.sty|mathtools.sty|pdfpages.sty|lineno.sty|xcolor.sty) echo texlive-latex-recommended ;;
    newtx*.sty|libertinus*.sty|libertine.sty|zi4.sty|inconsolata.sty|stix2.sty|fourier.sty|kpfonts.sty|fontawesome*.sty|sourcesanspro.sty|\
    inconsolata.sty|roboto.sty|lato.sty|noto*.sty|FiraSans.sty|ebgaramond.sty|baskervillef.sty|newpx*.sty) echo texlive-fonts-extra ;;
    tgtermes.sty|tgpagella.sty|tgheros.sty|tgschola.sty|tgbonum.sty|tgadventor.sty|tgcursor.sty|tgchorus.sty) echo tex-gyre ;;
    texgyre*.otf) echo fonts-texgyre ;;
    *.ldf) echo "" ;;
    *.sty|*.cls|*.bst) echo texlive-latex-extra ;;
    *) echo "" ;;
  esac
}
lang_deb() {  # babel option or language name -> texlive-lang-* package
  case "$1" in
    english|american|british|UKenglish|USenglish|canadian|australian) echo "" ;;
    german|ngerman|austrian|naustrian|swissgerman) echo texlive-lang-german ;;
    portuguese|portuges|brazil|brazilian) echo texlive-lang-portuguese ;;
    french|francais|acadian) echo texlive-lang-french ;;
    spanish|catalan|galician|basque) echo texlive-lang-spanish ;;
    italian) echo texlive-lang-italian ;;
    polish) echo texlive-lang-polish ;;
    russian|ukrainian|bulgarian|serbianc) echo texlive-lang-cyrillic ;;
    greek) echo texlive-lang-greek ;;
    chinese|japanese|korean|cjk) echo texlive-lang-cjk ;;
    arabic|farsi|persian|hebrew) echo texlive-lang-arabic ;;
    czech|slovak) echo texlive-lang-czechslovak ;;
    *) echo texlive-lang-european ;;   # dutch, swedish, danish, finnish, norsk, turkish, ...
  esac
}

APT_UPDATED=0
apt_install() {  # apt_install pkg...
  [ "$APT" = 1 ] || return 1
  if [ "$APT_UPDATED" = 0 ]; then $SUDO apt-get update -qq >/dev/null 2>&1 || true; APT_UPDATED=1; fi
  echo "== apt-get install $*"
  DEBIAN_FRONTEND=noninteractive $SUDO apt-get install -y -qq --no-install-recommends "$@" >/tmp/setup-latex-apt.log 2>&1 \
    && return 0
  echo "   apt failed (see /tmp/setup-latex-apt.log)"; return 1
}

fetch() {  # fetch <ctan-relative-path> <out-file>
  local rel="$1" out="$2" m
  have curl || return 1
  for m in "${MIRRORS[@]}"; do
    if curl -fsSL --retry 2 --connect-timeout 20 -o "$out" "$m/$rel" && unzip -tq "$out" >/dev/null 2>&1; then return 0; fi
  done
  return 1
}

ctan_install() {  # ctan_install <ctan-package-name>: TDS archive first, then the source zip (+ .ins)
  local pkg="$1" work; work="$(mktemp -d)"
  mkdir -p "$TEXMFHOME"
  if fetch "install/macros/latex/contrib/$pkg.tds.zip" "$work/$pkg.tds.zip"; then
    unzip -oq "$work/$pkg.tds.zip" -d "$TEXMFHOME" && echo "   $pkg: installed from CTAN (TDS) into $TEXMFHOME"
  elif fetch "macros/latex/contrib/$pkg.zip" "$work/$pkg.zip" || fetch "macros/generic/$pkg.zip" "$work/$pkg.zip"; then
    mkdir -p "$work/src" && unzip -oq "$work/$pkg.zip" -d "$work/src"
    while IFS= read -r ins; do ( cd "$(dirname "$ins")" && pdflatex -interaction=batchmode "$(basename "$ins")" >/dev/null 2>&1 || true ); done \
      < <(find "$work/src" -name '*.ins' -not -path '*/samples/*')
    local dest="$TEXMFHOME/tex/latex/$pkg"; mkdir -p "$dest"
    find "$work/src" -not -path '*/samples/*' \( -name '*.sty' -o -name '*.cls' -o -name '*.def' -o -name '*.cfg' \
      -o -name '*.clo' -o -name '*.ldf' -o -name '*.bbx' -o -name '*.cbx' -o -name '*.lbx' -o -name '*.dbx' \) -exec cp {} "$dest/" \;
    if find "$work/src" -name '*.bst' | grep -q .; then
      mkdir -p "$TEXMFHOME/bibtex/bst/$pkg"; find "$work/src" -name '*.bst' -exec cp {} "$TEXMFHOME/bibtex/bst/$pkg/" \;
    fi
    echo "   $pkg: installed from CTAN (source) into $TEXMFHOME"
  else
    rm -rf "$work"; return 1
  fi
  rm -rf "$work"; have mktexlsr && mktexlsr "$TEXMFHOME" >/dev/null 2>&1; return 0
}

install_file() {  # install_file <file name, e.g. acmart.cls, apa.bbx, biber>
  local f="$1" base="${1%.*}" deb
  if have kpsewhich && kpsewhich "$f" >/dev/null 2>&1; then echo "   $f: already available"; return 0; fi
  if have "$f"; then echo "   $f: already available"; return 0; fi
  if [ "$APT" = 1 ]; then
    deb="$(deb_for "$f")"
    if have apt-file; then
      local hit; hit=$(apt-file search -x "/$f\$" 2>/dev/null | head -1 | cut -d: -f1); [ -n "$hit" ] && deb="$hit"
    fi
    if [ -n "$deb" ] && apt_install "$deb" && { kpsewhich "$f" >/dev/null 2>&1 || have "$f"; }; then echo "   $f: installed via $deb"; return 0; fi
    if ! have apt-file; then   # the static map missed: let apt-file map the file to its package (~1 min, once)
      echo "   $f: not in the built-in map — installing apt-file to look it up"
      apt_install apt-file && $SUDO apt-file update >/dev/null 2>&1
    fi
    if have apt-file; then
      deb=$(apt-file search -x "/$f\$" 2>/dev/null | head -1 | cut -d: -f1)
      if [ -n "$deb" ] && apt_install "$deb" && { kpsewhich "$f" >/dev/null 2>&1 || have "$f"; }; then echo "   $f: installed via $deb"; return 0; fi
    fi
  fi
  if [ "$TLMGR" = 1 ]; then
    local tp; tp=$(tlmgr search --global --file "/$f" 2>/dev/null | awk -F: '/^[a-z0-9-]+:$/{print $1; exit}')
    [ -n "$tp" ] && tlmgr install "$tp" >/dev/null 2>&1 && { echo "   $f: installed via tlmgr ($tp)"; return 0; }
  fi
  case "$f" in *.bbx|*.cbx) base="biblatex-$base" ;; esac
  ctan_install "$base" && return 0
  echo "   !! $f: could not be installed (apt=$APT tlmgr=$TLMGR, CTAN unreachable or no package named '$base')."
  echo "      Ask for CTAN/apt access, find the package at https://ctan.org/search?phrase=$f, or upload the file next to main.tex."
  return 1
}

# ---------------------------------------------------------------- 1. toolchain
MIN_DEBS=(texlive-latex-base texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended texlive-bibtex-extra
          texlive-plain-generic biber latexmk)
FULL_DEBS=(texlive-science texlive-pictures texlive-publishers texlive-luatex texlive-xetex texlive-extra-utils tex-gyre
           fonts-texgyre chktex poppler-utils)
TARGETED=0; { [ -n "$FROMLOG" ] || [ ${#PKGS[@]} -gt 0 ] || [ -n "$LANGS" ]; } && TARGETED=1
if ! have pdflatex || ! have latexmk || ! have biber || [ "$TARGETED" = 0 ]; then
  if [ "$APT" = 1 ]; then
    debs=("${MIN_DEBS[@]}"); [ "$MODE" = default ] && debs+=("${FULL_DEBS[@]}"); [ "$FONTS" = 1 ] && debs+=(texlive-fonts-extra)
    apt_install "${debs[@]}" || echo "!! apt could not install the toolchain"
  elif ! have pdflatex; then
    echo "!! no LaTeX found and no apt/sudo: install TeX Live (https://tug.org/texlive/), MacTeX or MiKTeX, or use Overleaf." >&2
    exit 1
  fi
fi
if [ -n "$LANGS" ]; then
  for l in ${LANGS//,/ }; do d="$(lang_deb "$l")"; [ -n "$d" ] && { apt_install "$d" || ctan_install "babel-$l" || true; }; done
fi

# ---------------------------------------------------------------- 2. what a failed build was missing
if [ -n "$FROMLOG" ]; then
  [ -f "$FROMLOG" ] || { echo "!! log not found: $FROMLOG" >&2; exit 2; }
  blg="${FROMLOG%.log}.blg"
  missing=$( { grep -aoE "File [\`']?[^' ]+\.(sty|cls|bst|bbx|cbx|lbx|def|cfg|clo)'? not found" "$FROMLOG";
               grep -aoE "Style [\`']?[A-Za-z0-9-]+'? not found" "$FROMLOG" | sed -E "s/Style [\`']?([^' ]+)'? not found/\1.bbx/";
               [ -f "$blg" ] && grep -aoE "I couldn't open style file [^ ]+" "$blg" | awk '{print $NF}';
               grep -aoE "You do not have the [A-Za-z0-9]+" "$FROMLOG" | awk '{print $NF".sty"}' | sed 's/^inconsolata\.sty$/zi4.sty/';
               grep -aoE "(biber|makeglossaries|bib2gls|texcount): (command )?not found" "$FROMLOG" "$(dirname "$FROMLOG")/compile.log" 2>/dev/null | sed -E 's/.*:([a-z0-9]+): .*/\1/; s/: .*//';
             } 2>/dev/null | sed -E "s/^File [\`']?//; s/'? not found//" | sort -u )
  langs=$(grep -aoE "Unknown option [\`']?[A-Za-z]+'? for package [\`']?babel|Package babel Error: Unknown option [\`']?[A-Za-z]+" "$FROMLOG" \
          | grep -oE "option [\`']?[A-Za-z]+" | awk '{print $2}' | tr -d "\`'" | sort -u)
  [ -z "$missing$langs" ] && echo "== $FROMLOG: no missing files reported"
  for f in $missing; do echo "== missing: $f"; install_file "$f"; done
  for l in $langs; do echo "== missing babel language: $l"; d="$(lang_deb "$l")"; [ -n "$d" ] && apt_install "$d"; done
  grep -aq "must invoke LaTeX with the -shell-escape flag" "$FROMLOG" && echo "== note: minted/svg need -shell-escape (compile-check.sh adds it); minted also needs Pygments (apt: python3-pygments)"
  grep -aq "Font .* cannot be found\|The font .* cannot be found" "$FROMLOG" && echo "== note: fontspec cannot find a font: install it (Debian: fonts-*), or load it by file name with [Extension=.otf, ...]"
fi

# ---------------------------------------------------------------- 3. packages by name
for p in "${PKGS[@]}"; do
  echo "== package: $p"
  if have kpsewhich && { kpsewhich "$p.sty" >/dev/null 2>&1 || kpsewhich "$p.cls" >/dev/null 2>&1; }; then echo "   $p: already available"; continue; fi
  deb="$(deb_for "$p.sty")"; [ -n "$(deb_for "$p.cls")" ] && [ "$(deb_for "$p.cls")" != texlive-latex-extra ] && deb="$(deb_for "$p.cls")"
  { [ "$APT" = 1 ] && [ -n "$deb" ] && apt_install "$deb" && { kpsewhich "$p.sty" >/dev/null 2>&1 || kpsewhich "$p.cls" >/dev/null 2>&1; } && echo "   $p: installed via $deb"; } \
    || { [ "$TLMGR" = 1 ] && tlmgr install "$p" >/dev/null 2>&1 && echo "   $p: installed via tlmgr"; } \
    || ctan_install "$p" \
    || echo "   !! $p: not installed (no route worked) — upload its .sty/.cls next to main.tex or allow CTAN"
done

have mktexlsr && [ -d "$TEXMFHOME" ] && mktexlsr "$TEXMFHOME" >/dev/null 2>&1
echo; report
echo; echo "Ready. Build with: bash $(dirname "$0")/compile-check.sh main.tex"
