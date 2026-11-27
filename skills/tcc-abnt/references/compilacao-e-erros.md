# Compiling an abnTeX2 thesis anywhere, and triaging the log

## The chain — and why one pass is never enough

| Pass | What it does | If it is missing |
|---|---|---|
| `pdflatex` | discovers labels and citations; writes `.aux`, `.toc`, `.lof`, `.lot`, `.acn`/`.glo` | — |
| `bibtex main` (or `biber main` with biblatex) | reads `.aux`, writes **`main.bbl`** (the reference list) | REFERÊNCIAS empty, every citation prints `(????)` |
| `makeglossaries main` | writes `.acr`/`.gls` (siglas, glossário) — only for templates using `glossaries` | lista de siglas / glossário empty |
| `pdflatex` | fills numbers and citations | `??` and `(????)` remain |
| `pdflatex` | settles page numbers after the previous pass changed them | sumário/listas off by a page |

Diagnosis in two seconds: no `main.bbl` next to the sources (or in the build
dir) → BibTeX did not run; no `main.acr` → makeglossaries did not run. A PDF
that is "20 pages shorter than last time" almost always means a missing pass,
not lost text.

### Recipes

**latexmk (recommended everywhere):**
```
latexmk -pdf -interaction=nonstopmode -file-line-error main.tex
```
It runs pdflatex/bibtex/biber in the right order and as many times as needed.
It runs `makeglossaries` only if told to — ship `assets/latexmkrc` as
`.latexmkrc` in the project root (glossaries custom dependencies) for
templates with siglas via `glossaries`.

**Manual:**
```
pdflatex main.tex && bibtex main && makeglossaries main && pdflatex main.tex && pdflatex main.tex
```
(`biber main` instead of `bibtex main` for biblatex-abnt; skip makeglossaries
when the template does not use glossaries.)

**Full rebuild when things look stale:** delete `build/` (or `*.aux *.bbl
*.blg *.toc *.lof *.lot *.acn *.acr *.glo *.gls *.out`) and compile again. Or
`latexmk -gg -pdf main.tex`.

## Where the student compiles

### Overleaf (simplest, works from any computer)
Upload the project zip (exclude `build/` and `.tcc-workflow/`); Menu → Settings:
Compiler **pdfLaTeX**, Main document **main.tex**, TeX Live 2023 or newer.
Overleaf runs pdflatex → bibtex → pdflatex ×2 by itself. Glossaries: Overleaf
runs `makeglossaries` automatically when it detects `\makeglossaries`; if the
siglas list comes out empty, recompile once more or add a `latexmkrc` file at
the project root with the glossaries rule (Overleaf honours it).

### VS Code + LaTeX Workshop
The extension guesses the root file (by default from `\begin{document}`, and
from `\documentclass` in older/other configurations). With templates that put
`\documentclass` in an `\input`ed preamble (UniforTeX2: `lib/preambulo.tex`)
the guess can land on the preamble, which is then compiled alone from the
wrong directory — the symptom is `File 'lib/unifortex2.sty' not found` and
`Transcript written on preambulo.log`.
Fix: `% !TEX root = ../main.tex` as the first line of **every** `.tex` file
(`% !TEX root = ./main.tex` in `main.tex`), plus a workspace `settings.json`
that points the recipe at `%WORKSPACE_FOLDER%/main.tex` — see
`assets/vscode-settings.json`. Turn `autoBuild` off for big documents (dozens
of TikZ figures make per-keystroke builds unbearable).

### TeXstudio / MiKTeX (Windows)
Options → Configure → Build → Default Compiler: **`txs:///latexmk`** (not
PdfLaTeX, which runs a single pass); F5 to build and view. Let MiKTeX install
missing packages on the fly (MiKTeX Console → Settings). `assets/compilar.bat`
is a double-click build for peers who are not comfortable with editors: it
runs the chain (latexmk if present, otherwise the manual passes) and then
verifies `.bbl`, `.acr`, undefined references, error lines and the
caption/source balance.

### TeX Live on Linux/macOS
`tlmgr install abntex2 babel-portuges` if missing (Debian/Ubuntu:
`apt install texlive-publishers texlive-lang-portuguese texlive-bibtex-extra`).

### Sandboxes (Cowork, CI, minimal containers)
```
bash scripts/setup-sandbox-latex.sh          # once: abntex2, babel-portuges, lmodern, extras
bash scripts/compile-check.sh main.tex       # build + filtered summary; exit 1 if no PDF
```
`setup-sandbox-latex.sh` installs into `$TEXMFHOME` (default `~/texmf`) from
CTAN, never touching the system tree; it skips what `kpsewhich` already finds.
`compile-check.sh` exports `TEXMFHOME`, builds into `build/` with latexmk
(`-gg -f`), adds the glossaries rule when the sources use `\makeglossaries`,
and prints: pages, undefined citations/references, `!` errors (minus patterns
in `.tcc-workflow/benign-notices.txt`), overfull/float-too-large counts and a
placeholder scan. Read `build/compile.log` for the raw output.

## Error table

| Symptom | Cause | Fix |
|---|---|---|
| `Figura ??`, `Seção ??` | one pass missing, or wrong `\label`/`\ref` | recompile twice; check the label exists exactly once |
| `(????)` in citations | BibTeX/biber did not run, or the key is not in the `.bib` | run the chain; `grep -n "Citation" main.log`; fix the key |
| REFERÊNCIAS empty | no `.bbl` | run bibtex/biber; check `\bibliography{path}` points to the file (no `.bib` extension) |
| Lista de siglas / glossário empty | `makeglossaries` not run | run it; add `.latexmkrc`; on Overleaf recompile |
| `! Undefined control sequence` on a template macro | preamble not loaded; compiling a chapter instead of `main.tex`; package version removed the macro | `% !TEX root`; compile `main.tex`; see template quirks |
| `File 'lib/xxx.sty' not found` | wrong root/working directory (editor compiled an `\input`ed file) | `% !TEX root = ../main.tex` + editor recipe on `main.tex` |
| `! LaTeX Error: File 'abntex2.cls' not found` / `brazil.ldf` | abnTeX2 / babel-portuges not installed | `setup-sandbox-latex.sh`, `tlmgr`, or MiKTeX on-the-fly |
| `! Package babel Error: Unknown option 'brazil'` | same as above | same |
| `! Missing $ inserted` | `_`, `^`, `\alpha`, `%`-less special chars outside math | wrap in `$...$` or escape (`\_`, `\%`, `\&`, `\#`) |
| half a paragraph vanished | an unescaped `%` commented out the rest of the line | `\%` |
| `! There's no line here to end` | `\\` before `\section`/`\chapter` or on an empty line | delete the `\\` |
| `! Missing \begin{document}` right after the settings block, a stray `nao`/`sim` on the cover | a template setter (`\ifthenelse` with no else-branch — UniforTeX2's `\removerbordasdohyperlink`, `\cordohyperlink`, `\ehqualificacao`, `\orientadorfeminino`, `\coorientadorfeminino`) swallowed the next token | terminate each such setter with `{}` (`\cordohyperlink{nao}{}`); see the template profile |
| `apter]quadroloqQuadro` on page 1, `Environment quadro undefined` | `float` package loaded together with memoir's `\newfloat` | remove `\usepackage{float}` |
| `Float too large for page by N pt` | figure + caption + source taller than the text block | reduce width/height, shorten caption, `[htbp]` |
| Figures printed many pages after their call-out | float queue blocked by an oversized float | fix that float first; `\clearpage` at chapter end |
| `Overfull \hbox` in a table | columns wider than the text block | `p{}` columns, `\tabcolsep`, `\small`, or `sidewaystable` |
| Accents wrong / `Invalid UTF-8` | file not saved as UTF-8, or `inputenc` mismatch | save as UTF-8; `\usepackage[utf8]{inputenc}` (pdflatex) |
| `Repeated entry` in `.blg` | duplicate keys (case-insensitive!) across `.bib` files | rename/delete one |
| `Warning--I didn't find a database entry for "x"` | `\cite{x}` with no entry | add the entry or fix the key |
| Everything breaks after an edit | stale auxiliary files | full rebuild (`latexmk -gg` / delete `build/`) |

## Reading the log efficiently

```
grep -n "^!" main.log                         # real errors (then read 5 lines below each)
grep -n "Citation .* undefined" main.log      # bad keys
grep -n "Reference .* undefined" main.log     # bad labels
grep -c "Overfull \\\\hbox" main.log          # layout debt (count, trend)
grep -n "Float too large" main.log
grep -n "Output written" main.log             # pages
```
With `-file-line-error`, errors also appear as `./file.tex:123: ...` — the
fastest way to jump to the offending line.
