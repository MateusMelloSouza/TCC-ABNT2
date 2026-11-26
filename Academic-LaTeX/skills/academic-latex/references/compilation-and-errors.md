# Compiling a LaTeX document anywhere, and triaging the log

Error messages quoted below were reproduced with TeX Live 2023 (pdfTeX 1.40.25,
biblatex 3.19, biber 2.19, latexmk 4.83).

## Contents
1. The build chain — and why one run is never enough
2. Engines: pdfLaTeX, LuaLaTeX, XeLaTeX
3. latexmk recipes and `.latexmkrc`
4. Where people compile (Overleaf, VS Code, TeXstudio, TeXShop, Windows, CLI, sandboxes)
5. Error table
6. Reading the log efficiently

## 1. The build chain

| Pass | What it does | If it is missing |
|---|---|---|
| LaTeX (pdflatex/lualatex/xelatex) | typesets; records labels, citations and list entries in `.aux`, `.bcf`, `.toc`, `.lof`, `.lot`, `.glo`/`.acn`, `.idx` | — |
| **biber** (biblatex) or **bibtex** (natbib/cite/`.bst`) | reads the citation list, writes the bibliography to `main.bbl` | every citation prints `[?]`, `(?)` or the key in bold; no reference list |
| makeglossaries / bib2gls / makeindex | builds glossaries, lists of abbreviations, nomenclature, index | lists empty or missing |
| LaTeX again (×1–2) | fills in numbers, citations, page references | `??`, `[?]`, a table of contents one page off |

Which bibliography tool? **biblatex → biber** (unless `backend=bibtex`);
**`\bibliographystyle` + `\bibliography` → bibtex**. Running the wrong one is a
classic: a biblatex document run through bibtex gives `I found no \citation
commands`, `I found no \bibdata command` in the `.blg` and the log asks
`Please (re)run Biber on the file`; a natbib document run through biber gives
`ERROR - Cannot find 'main.bcf'!` and every citation prints `[?]`. TeXstudio
users: Options → Configure → Build → **Default Bibliography Tool** must match.

Two-second diagnosis: no `main.bbl` next to the sources (or in the output
directory) → the bibliography tool did not run. A PDF that is suddenly 20 pages
shorter almost always means a missing pass, not lost text.

## 2. Engines

| Engine | Use when | Notes |
|---|---|---|
| **pdfLaTeX** | most journal/conference classes and university templates; arXiv's default | 8-bit fonts: `\usepackage[T1]{fontenc}` + a font package (`lmodern`, `newtxtext,newtxmath`, `tgtermes`); UTF-8 input is the default since 2018, but characters without a definition stop the run (`Unicode character ≤ (U+2264)`) |
| **LuaLaTeX** | new documents needing system/OpenType fonts, many scripts, `unicode-math` | `\usepackage{fontspec}` (Latin Modern by default) + `\setmainfont{…}` (finds fonts in the TeX tree and the OS); slower than pdfLaTeX |
| **XeLaTeX** | legacy Unicode projects, some CJK/RTL setups (`xeCJK`, `bidi`) | finds fonts **by name only through the operating system** (fontconfig): if `The font "X" cannot be found`, install the font or load it by file name: `\setmainfont{texgyretermes}[Extension=.otf, UprightFont=*-regular, BoldFont=*-bold, ItalicFont=*-italic, BoldItalicFont=*-bolditalic]` |

Never switch a publisher's template to another engine. Tell editors which
engine to use with a magic comment on the first line —
`% !TEX program = lualatex` (TeXstudio, TeXShop, VS Code LaTeX Workshop, Overleaf
honour it in various ways) — and with `$pdf_mode` in `.latexmkrc` (latexmk and
Overleaf).

## 3. latexmk (recommended everywhere)

```
latexmk -pdf main.tex            # pdfLaTeX      (-lualatex / -xelatex for the Unicode engines)
latexmk                          # uses .latexmkrc: $pdf_mode, @default_files, custom rules
latexmk -pvc main.tex            # rebuild on every save (continuous preview)
latexmk -c                       # remove auxiliary files (keep the PDF); -C also removes the PDF
latexmk -gg -pdf main.tex        # force a full rebuild when things look stale
```
It runs biber/bibtex and makeindex automatically and as many LaTeX passes as
needed. It does **not** know makeglossaries or nomencl: the rules are in
`assets/latexmkrc` (copy it to the project root as `.latexmkrc`; Overleaf
reads it too). `$pdf_mode = 1` pdfLaTeX, `4` LuaLaTeX, `5` XeLaTeX.

Output directories (`-outdir=build`, LaTeX Workshop's `outDir`, TeXstudio's
build folder): `\include{chapters/intro}` writes `chapters/intro.aux` *inside*
the output directory, and TeX cannot create folders — `I can't write on file
'chapters/intro.aux'`. Create the sub-folders in the output directory
(`compile-check.sh` does) or use `\input` instead of `\include`.

`-shell-escape` is needed by `minted` (`You must invoke LaTeX with the
-shell-escape flag`; it also needs Python's Pygments), `svg`, `gnuplottex` and
TikZ externalization. Overleaf enables it; arXiv and most journal systems do
not — prefer `listings` and pre-generated PDFs for submissions.

Other build tools you may meet: **arara** (directives in the file header),
**Tectonic** (self-contained engine that downloads packages on demand — handy in
CI), plain Makefiles. Respect what the project already uses.

## 4. Where people compile

### Overleaf
Menu → Settings: **Compiler** (pdfLaTeX / LuaLaTeX / XeLaTeX), **Main document**,
**TeX Live version** (keep what the template was made for). Overleaf runs
latexmk, so biber/bibtex, makeindex and (for `\makeglossaries`) makeglossaries
run automatically; a project `latexmkrc` is honoured. "Recompile from scratch"
(the menu next to Recompile) clears stale auxiliary files. Logs and output files
→ the "Raw logs" view shows the full log. File names are **case-sensitive** on
Overleaf (and on Linux and arXiv): `Figure.PNG` ≠ `figure.png`. Free-plan
compile timeouts on long theses: `\includeonly`, the `draft` class option, or
externalized TikZ.

### VS Code + LaTeX Workshop
The extension guesses the root file; in multi-file projects it can pick a
chapter or a preamble file and compile it alone (`File 'x.sty' not found`,
`Undefined control sequence` for project macros). Put `% !TEX root =
../main.tex` as the first line of every chapter file and use a recipe that
always builds `main.tex` (`assets/vscode-settings.json`). Turn `autoBuild` off
for large documents.

### TeXstudio (and Texmaker)
Options → Configure → Build: Default Compiler **`txs:///latexmk`** (a single
PdfLaTeX run is not a build), Default Bibliography Tool **Biber** for biblatex
documents (BibTeX for `.bst` styles). `% !TeX program = lualatex` and `% !BIB
program = biber` magic comments override them per document.

### TeXShop / MacTeX (macOS)
Engine via the toolbar or `% !TEX TS-program = lualatex`; Typeset → BibTeX runs
the tool set in Preferences (set it to biber for biblatex) — or choose the
`latexmk` engine (`pdflatexmk`, `lualatexmk`) to run everything.

### Windows (MiKTeX or TeX Live)
MiKTeX installs missing packages on the fly (MiKTeX Console → Settings →
"Always install missing packages") and needs Perl (e.g. Strawberry Perl) for
latexmk. `assets/build.bat` is a double-click build for collaborators who do not
use an editor: latexmk when it works, otherwise the manual passes (it detects
biber vs bibtex and makeglossaries), then a short verification. PDF viewers that
lock the file (Adobe Reader) cause `I can't write on file 'main.pdf'` — use
SumatraPDF or close the viewer.

### TeX Live / MacTeX command line
`tlmgr install <pkg>` installs a missing package (`tlmgr search --global --file
/x.sty` finds which). Debian/Ubuntu package TeX Live as `texlive-*`
collections; their `tlmgr` cannot install system packages — use apt (or
`setup-sandbox-latex.sh`, which maps files to packages).

### Sandboxes and CI (Claude's own environment, Cowork, GitHub Actions, Docker)
```
bash scripts/setup-sandbox-latex.sh                      # once: TeX Live + biber + latexmk + common packages
bash scripts/compile-check.sh main.tex                   # build + actionable summary; exit 1 if no PDF
bash scripts/setup-sandbox-latex.sh --from-log build/main.log   # install whatever the build said was missing
```
`setup-sandbox-latex.sh` tries apt (root or password-less sudo; `apt-file` maps
any missing file to its Debian package), then tlmgr, then CTAN archives
unpacked into `$TEXMFHOME`; it reports which route the network blocked. On
Debian/Ubuntu, `acmart` also needs `texlive-fonts-extra` (Libertine, newtxmath,
Inconsolata), and LuaLaTeX/XeLaTeX font names need the OpenType files
(`fonts-texgyre`, `fonts-lmodern`). `compile-check.sh` builds into `build/`
with latexmk (full rebuild unless `--quick`), picks the engine (`--engine` >
magic comment > `.latexmkrc` > fontspec → LuaLaTeX > pdfLaTeX), adds glossaries
and nomencl rules when the project has no `.latexmkrc`, adds `-shell-escape` for
minted/svg, and prints: pages and paper size, undefined citations/references,
duplicate labels, real errors (minus `.academic-workflow/benign-notices.txt`),
`.blg` problems, overfull/underfull counts, unembedded or Type 3 fonts, leftover
`??`/`[?]` in the PDF text and placeholders. `--strict` exits 3 when problems
remain (useful in CI).

## 5. Error table

| Symptom | Cause | Fix |
|---|---|---|
| `[?]`, `(?)`, citation keys in bold, no reference list | bibliography tool not run, wrong tool, or wrong key | run the chain (latexmk); biblatex → biber, `.bst` → bibtex; `grep "Citation" main.log` for the keys |
| `ERROR - Cannot find 'refs'!` (biber) | `\addbibresource{refs}` without the extension | `\addbibresource{refs.bib}` (biblatex needs the full name; BibTeX's `\bibliography{refs}` does not) |
| `ERROR - Cannot find 'main.bcf'!` | biber run on a document that does not use biblatex | run bibtex instead |
| `I found no \citation commands` / `\bibdata` / `\bibstyle` | bibtex run on a biblatex document (or on the wrong `.aux`) | run biber; with output directories, run the tool where the `.aux` is (latexmk does) |
| `Please (re)run Biber on the file` / `Label(s) may have changed. Rerun` | more passes needed | latexmk, or run the missing pass |
| `I didn't find a database entry for 'x'` (.blg) | `\cite{x}` with no such key — check case: biber keys are case-sensitive | fix the key or add the entry |
| `Repeated entry` (bibtex) | two keys equal ignoring case | rename or delete one (`bib-check.py` lists them) |
| `Found biblatex control file version X, expected version Y` | biblatex and biber versions do not match (mixed installations, old MiKTeX, distro packages) | update both together (tlmgr/MiKTeX), or use the biber that ships with the same TeX distribution |
| `Figure ??`, `Section ??` | missing pass, or `\ref` to a label that does not exist | recompile; check the label exists exactly once |
| reference shows the **section** number for a figure | `\label` placed before `\caption` | put `\label` after (or inside) `\caption` |
| `Label 'x' multiply defined` | same `\label` twice (copy-paste) | rename one |
| `! Package cleveref Error: cleveref must be loaded after hyperref!` | package order | hyperref, then cleveref as the last package |
| `! LaTeX Error: Option clash for package x` | `x` already loaded (often by the class or another package) with other options | set options after loading (`\hypersetup{…}`, `\captionsetup{…}`) or `\PassOptionsToPackage{opts}{x}` before `\documentclass` |
| `! LaTeX Error: Command \x already defined` | two packages define the same command (e.g. llncs + amsthm: `Command \proof already defined`) | for llncs: `\let\proof\relax \let\endproof\relax` before `\usepackage{amsthm}`; otherwise drop one package |
| `! LaTeX Error: File 'x.sty' not found` | package not installed, or wrong working directory for a local `.sty` | install it (`tlmgr`, MiKTeX, apt, `setup-sandbox-latex.sh --from-log`); compile from the main file's folder |
| `! Undefined control sequence` | typo; package not loaded; command from a newer package version; compiling a chapter alone | read the command named in the next log line; `% !TEX root`; update the package |
| `! LaTeX Error: Unicode character ≤ (U+2264) not set up for use with LaTeX` | pdfLaTeX meets a character no loaded font encoding defines | use the LaTeX command (`$\leq$`, `\textmu` or siunitx `\micro`), `\DeclareUnicodeCharacter`, or LuaLaTeX |
| `Package inputenc Error: Invalid UTF-8 byte sequence` | file saved in another encoding (Latin-1, Windows-1252) | re-save as UTF-8 (editor, or `iconv -f latin1 -t utf8`) |
| `! Missing $ inserted` | `_` or `^` in text, math command outside math | `\_`, `\textasciicircum`, `$…$`; for file names and URLs use `\url{}`/`\path{}` |
| half a line vanished | an unescaped `%` commented out the rest (also in `.bib` titles) | `\%` |
| `! Misplaced alignment tab character &` | `&` in running text or in a `.bib` field | `\&` |
| `Paragraph ended before \x was complete` / `Runaway argument` | missing `}`, or a blank line inside an argument | close the brace; no blank lines inside `\caption{}`, `\footnote{}`, macro arguments |
| `! There's no line here to end` | `\\` at the start of a paragraph or just before `\section` | delete the `\\`; use a blank line for paragraphs |
| `! LaTeX Error: Too many unprocessed floats` / figures far from their text | the float queue is blocked by one float that fits nowhere | fix that float (size, `[htbp]`), `\clearpage` at chapter end, `placeins` `\FloatBarrier` |
| `Float too large for page by Npt` | float plus caption taller than the text block | smaller graphic (`height=0.8\textheight,keepaspectratio`), shorter caption |
| `! LaTeX Error: Not in outer par mode` / `Float(s) lost` | a figure/table inside a minipage, a box, a footnote or another float | move it out; use `\captionof` (caption package) for non-floating captions |
| `Overfull \hbox (Npt too wide)` | unbreakable content: long words, URLs, wide tables, inline math | `xurl`, `\-` hyphenation hints, `p{}`/`tabularx` columns, rephrase; `microtype` reduces them; only values above a few pt are visible |
| `Underfull \hbox (badness 10000)` | `\\` used to end paragraphs, ragged layouts | remove manual breaks; usually harmless |
| `destination with the same identifier (name{page.i})` | hyperref sees two pages numbered "i" (title page + reset counter) | `\hypersetup{pageanchor=false}` around the title page (as the thesis skeleton does) |
| `Token not allowed in a PDF string` | math or commands in a section title used for PDF bookmarks | `\texorpdfstring{$\alpha$-test}{alpha-test}` |
| `! Package fontspec Error: The font "X" cannot be found` | the engine cannot see the font (XeLaTeX searches the OS only) | install the font; or load it by file name with `Extension=.otf` |
| `Missing character: There is no X in font Y` | the chosen font lacks that glyph (log only — the PDF silently omits it) | choose a font that has it, or `\setmainfont` fallback / a font for that script |
| `! Package minted Error: You must invoke LaTeX with the -shell-escape flag` | minted needs to call Pygments | `-shell-escape` (and `pip install pygments`), or switch to `listings` |
| `! Package babel Error: Unknown option 'x'` | language not installed or misspelled (`ngerman`, `brazilian`, `british`) | install the language support (TeX Live `collection-lang*`, Debian `texlive-lang-*`) |
| `I can't write on file 'chapters/x.aux'` | output directory without the sub-folder (see §3) | create `build/chapters/`, or use `\input` |
| `I can't write on file 'main.pdf'` | the PDF is open in a viewer that locks it (Windows) | close it or use a non-locking viewer |
| `TeX capacity exceeded, sorry [main memory size]` | runaway recursion in a macro, or huge TikZ/pgfplots figures | fix the macro; externalize figures or use LuaLaTeX (dynamic memory) |
| `! Dimension too large` | TikZ/pgfplots arithmetic on large values | `\usetikzlibrary{fpu}`, `restrict y to domain`, rescale data |
| `*** (job aborted, no legal \end found)` / `Emergency stop` | missing `\end{document}`, or an earlier fatal error | read the first error, not the last |
| everything breaks after an edit that "cannot" have caused it | stale auxiliary files | full rebuild (`latexmk -gg`, delete `build/`, Overleaf "Recompile from scratch") |

## 6. Reading the log efficiently

```
grep -n "^!" main.log                               # real errors; read the next lines for context
grep -nE "^\./.*:[0-9]+: " main.log                 # the same, with -file-line-error (file:line: message)
grep -n "Citation .* undefined" main.log            # bad keys
grep -n "Reference .* undefined" main.log           # bad labels
grep -n "multiply defined" main.log                 # duplicate labels
grep -c "Overfull \\\\hbox" main.log                # layout debt (count, watch the trend)
grep -n "Float too large" main.log
grep -n "Output written" main.log                   # pages
grep -nE "ERROR|WARN" main.blg                      # biber; "Warning--" for bibtex
texfot pdflatex main.tex                            # TeX Live: run LaTeX and show only interesting lines
chktex -q main.tex                                  # lint: spacing, quotes, dashes, common mistakes
```
Always fix the **first** error first: later ones are often consequences.
