# Formatting with LaTeX — what to set, what to leave to the class, how to fix it

The class and the template already decide page layout, fonts, spacing and
heading styles. **Do not hand-set them in chapter files**, and never change them
in a publisher template. This file is the reference for what *you* control —
floats, tables, cross-references, math, units, code, abbreviations, languages,
PDF properties — and for building a layout when there is no template.

## Contents
1. Page layout, fonts and spacing (only when you own the layout)
2. Sections, numbering, table of contents
3. Figures
4. Float placement — the queue problem
5. Tables
6. Captions
7. Cross-references
8. Mathematics and theorems
9. Numbers and units
10. Code listings and algorithms
11. Lists
12. Abbreviations, glossaries, nomenclature, index
13. Quotations, emphasis, dashes, spaces
14. Languages
15. Hyperlinks, PDF metadata, PDF/A, accessibility
16. Drafting aids

## 1. Page layout, fonts and spacing

Only for documents without a template (or when a graduate-school guide gives
numbers to implement).

- **Margins**: `\usepackage[top=25mm, bottom=25mm, left=35mm, right=25mm]{geometry}`;
  a binding offset: `bindingoffset=10mm` (two-sided: inner margin). memoir uses
  `\setlrmarginsandblock`/`\setulmarginsandblock` + `\checkandfixthelayout`;
  KOMA-Script uses `\KOMAoptions{DIV=12, BCOR=8mm}` — do not add geometry to
  those classes unless you know why. Debug with `\usepackage{showframe}`.
- **Paper**: `a4paper` (most of the world) or `letterpaper` (US/Canada) as a
  class option; mismatches are common in submissions — `pdfinfo main.pdf` shows
  "Page size".
- **Fonts** — pdfLaTeX: `\usepackage[T1]{fontenc}` plus one of `lmodern`
  (default look), `newtxtext,newtxmath` (Times-like), `tgtermes` (TeX Gyre
  Termes), `libertinus`, `newpxtext,newpxmath` (Palatino-like); avoid the
  obsolete `times` and `mathptmx` for new work. LuaLaTeX/XeLaTeX:
  `\usepackage{fontspec}` + `\setmainfont{TeX Gyre Termes}` (or any installed
  OpenType font) and `unicode-math` + `\setmathfont{TeX Gyre Termes Math}`.
  Always `\usepackage{microtype}` (better justification, fewer overfull lines).
- **Font size**: class option `10pt`/`11pt`/`12pt` (KOMA and memoir allow
  more). Never change sizes with `\fontsize` in the body.
- **Line spacing**: `\usepackage{setspace}` + `\onehalfspacing` or
  `\doublespacing` — setspace keeps footnotes and floats (figures, tables,
  their captions) single-spaced; not `\linespread` + manual fixes. When a guide
  also wants block quotes or the reference list single-spaced: wrap quotes in
  `\begin{singlespace}`, and add `\AtBeginBibliography{\singlespacing}`
  (biblatex) to the preamble; `\captionsetup{font=singlespacing}` forces it for
  captions explicitly.
- **Paragraphs**: indentation (default) or `\usepackage{parskip}` for
  vertical space — not `\setlength{\parskip}` by hand.
- **Page numbers and headers**: `\pagestyle{plain}` (centred number), fancyhdr
  for custom headers (`\fancyhead[R]{\thepage}`, and redefine the `plain` style
  for chapter pages); KOMA: `scrlayer-scrpage`.
- **Two-sided printing**: `twoside,openright` (chapters start on right pages,
  blank pages appear — expected); electronic-only deposits usually prefer
  `oneside`.

## 2. Sections, numbering, table of contents

- Hierarchy: `\part` > `\chapter` (book/report/memoir/KOMA) > `\section` >
  `\subsection` > `\subsubsection` > `\paragraph`. Articles have no chapters.
- Depth: `\setcounter{secnumdepth}{3}` (numbered levels), `\setcounter{tocdepth}{2}`
  (levels in the TOC). Avoid a single subsection under a section, and levels
  deeper than three in papers.
- Unnumbered but listed: `\chapter*{Preface}\addcontentsline{toc}{chapter}{Preface}`
  (in `\frontmatter` of book/memoir/KOMA, plain `\chapter` is already
  unnumbered and listed); KOMA: `\addchap`, `\addsec`.
- Restyle headings with the class's own interface (KOMA `\setkomafont`, memoir
  `\chapterstyle`) or `titlesec` for standard classes — not with manual
  `\vspace` and `\Large` around each heading.
- `\label{sec:…}` right after the heading; refer with `\cref{sec:…}`.
- Appendices: `\appendix` then `\chapter{…}` (book/report) or `\section{…}`
  (article) → "Appendix A". Front/main/back matter in book-like classes:
  `\frontmatter` (roman numbers, unnumbered chapters), `\mainmatter`,
  `\backmatter`; in `report`, use `\pagenumbering{roman}` / `arabic`.

## 3. Figures

```latex
\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.8\linewidth]{architecture}   % no extension needed; \graphicspath{{figures/}}
  \caption{System architecture. The caption says what the reader should see.}
  \label{fig:architecture}
\end{figure}
```
- **Formats**: vector PDF for plots, diagrams and anything with text; PNG for
  screenshots and raster images; JPEG only for photographs; EPS needs
  conversion with pdfLaTeX (automatic via `epstopdf` in TeX Live) — prefer PDF.
  SVG: export to PDF (Inkscape), or the `svg` package (needs `-shell-escape`).
- **Sizes**: `width=\linewidth` (current column) rather than `\textwidth`
  inside minipages and two-column layouts; `height=0.8\textheight,keepaspectratio`
  for tall images. Produce plots at their final size so that text in the figure
  matches the caption size (matplotlib: `figsize=(3.3, 2.2)` inches for a single
  column, `savefig("fig.pdf", bbox_inches="tight")`, and
  `matplotlib.rcParams["pdf.fonttype"] = 42` to avoid Type 3 fonts that IEEE and
  ACM checks reject). pgfplots/TikZ draw in the document's own fonts
  (`\pgfplotsset{compat=1.18}`).
- **Subfigures**: `subcaption` only (not the obsolete `subfigure`, avoid `subfig`):
  ```latex
  \begin{figure}[htbp]
    \centering
    \begin{subfigure}{0.48\linewidth}
      \includegraphics[width=\linewidth]{a}\caption{Before.}\label{fig:before}
    \end{subfigure}\hfill
    \begin{subfigure}{0.48\linewidth}
      \includegraphics[width=\linewidth]{b}\caption{After.}\label{fig:after}
    \end{subfigure}
    \caption{Effect of the filter.}\label{fig:filter}
  \end{figure}
  ```
- **Two-column layouts**: `figure*` / `table*` span both columns and float only
  to the top of a page (`[t]`) or a float page.
- **Accessibility**: `\includegraphics[alt={A bar chart …}]{…}` is accepted by
  current graphicx (TeX Live 2023 tested); use colour-blind-safe palettes
  (Okabe–Ito, viridis) and never encode meaning by colour alone.
- **Rights**: figures reproduced from other works need permission or a licence
  that allows it, plus the credit line the publisher or style guide requires
  ("Reprinted from …", "Adapted from …"); some institutions require a
  "Source:" line under every figure (ABNT does).

## 4. Float placement — the queue problem

LaTeX places floats of each type in order (FIFO). One float that fits nowhere
— a tall figure plus a long caption, or a `[h!]` that cannot be honoured —
blocks every later float, and a whole chapter's figures can drift 10–25 pages
away from the text that cites them.

- Default to `[htbp]`; reserve `[H]` (float package) for small floats in
  exceptional places.
- Fix the oversized float first (log: `Float too large for page by …`), then
  recompile; later floats usually fall into place.
- Flush the queue at chapter ends (`\clearpage`) or per section with
  `\usepackage[section]{placeins}` (`\FloatBarrier`).
- For documents with many floats, relax the parameters once in the preamble:
  `\renewcommand{\topfraction}{0.85}` `\renewcommand{\textfraction}{0.1}`
  `\renewcommand{\floatpagefraction}{0.75}`.
- Never "push" floats with `\newpage`, `\vspace` or by moving source lines on
  every edit; decide the logical place (right after the paragraph that first
  refers to it) and let LaTeX place it.

## 5. Tables

```latex
\begin{table}[htbp]
  \centering
  \caption{Accuracy and latency of the compared methods (mean over five runs).}
  \label{tab:results}
  \begin{tabular}{l S[table-format=2.1] S[table-format=3.0]}
    \toprule
    {Method} & {Accuracy (\%)} & {Latency (\unit{\milli\second})} \\
    \midrule
    Baseline & 71.2 & 120 \\
    Proposed & 78.9 & 135 \\
    \bottomrule
  \end{tabular}
\end{table}
```
- **booktabs**: `\toprule`, `\midrule`, `\cmidrule(lr){2-3}`, `\bottomrule`;
  no vertical rules, no double rules. Group with spacing (`\addlinespace`), not
  boxes.
- **Numbers**: siunitx `S` columns align on the decimal marker
  (`table-format=2.1`; uncertainties `78.9(3)` with `uncertainty-mode=separate`
  for "78.9 ± 0.3"); headers inside braces. Same number of decimals per column.
- **Width**: `p{4cm}` or `tabularx`'s `X` columns
  (`\begin{tabularx}{\linewidth}{lX}`) for text; `\small` plus
  `\setlength{\tabcolsep}{4pt}`; `sidewaystable` (rotating) or `landscape`
  (pdflscape) for very wide tables. Avoid `\resizebox{\linewidth}{!}{…}`: it
  scales the font to an arbitrary size, often illegibly small, and differs from
  table to table.
- **Long tables** across pages: `longtable` or `xltabular`, with the header
  repeated (`\endhead`) and a "continued" note.
- **Notes** under a table: `threeparttable` (`tablenotes` with `\item[a]`), not
  footnotes inside the tabular.
- Merge cells sparingly (`multirow`, `\multicolumn`); colour rows only if the
  template allows (`xcolor` with `table` option).
- Text-heavy comparisons (definitions, feature lists) are still tables in most
  guides; some national standards distinguish tables (numeric) from boxes or
  charts (textual) — ABNT's "quadros", for example.

## 6. Captions

- Position: **tables above, figures below** in most styles (IEEE, ACM, Springer,
  Elsevier, Chicago); **APA puts both number and title above** (number in bold,
  title in italics on its own line) with notes below. Follow the template.
- `\usepackage[font=small, labelfont=bf]{caption}` for the look;
  `\captionsetup[table]{position=above}` fixes spacing for top captions;
  `\caption[Short entry for the list]{Long caption with details.}` keeps the
  list of figures readable.
- A caption is a sentence or a noun phrase that lets the figure stand alone:
  what is shown, conditions, the meaning of symbols, the source if not yours.
- `\captionof{figure}{…}` (caption package) for a caption outside a float (in
  a minipage, a tcolorbox).

## 7. Cross-references

- `\label` **after** `\caption` (or inside it). Before the caption it captures
  the section counter: the reference prints the section number.
- Prefixes by type: `fig:`, `tab:`, `sec:`, `ch:`, `eq:`, `app:`, `alg:`,
  `lst:`, `thm:`. Labels are case-sensitive and must be unique
  (`Label 'x' multiply defined`).
- Plain LaTeX: `Figure~\ref{fig:x}` (non-breaking `~`), `Eq.~\eqref{eq:y}`,
  `p.~\pageref{…}`. **cleveref**: `\cref{fig:x}` → "Fig. 1" / "Figure 1",
  `\Cref` at sentence start, `\cref{fig:a,fig:b}` → "Figures 1 and 2",
  `\crefrange{fig:a}{fig:d}`; options `capitalise`, `noabbrev`; language follows
  babel. Load order: **hyperref, then cleveref, last** — the reverse is a hard
  error (`cleveref must be loaded after hyperref!`).
- `\autoref` (hyperref) and `\vref` (varioref) are alternatives; use one system
  consistently.
- Never type numbers ("see Figure 3", "Section 2.1", "Equation (5)"):
  `audit-tex.py` lists hard-coded references.
- Every figure, table and numbered equation that matters is referenced in the
  text, ideally before it appears (`audit-tex.py` lists floats never referenced
  and floats placed before their first reference).

## 8. Mathematics and theorems

- `\usepackage{amsmath, amssymb}` (and `mathtools`). Inline `$…$` or `\(…\)`;
  displayed `\[…\]` or `equation`; several lines `align` (`&` before the
  relation), `gather`, `multline`, `split` inside `equation`; `cases` for
  piecewise definitions. **Never `$$…$$`** (plain TeX, wrong spacing) **or
  `eqnarray`** (inconsistent spacing).
- Number only equations you refer to (`\nonumber`/`\notag`, or starred
  environments). Number by chapter: `\numberwithin{equation}{chapter}`.
- Displayed equations are part of the sentence: end them with a comma or period
  as grammar requires, and continue with "where …" without indentation.
- Words and operators: `\text{if }`, `\mathrm{d}x` (if your field uses upright
  d), `\DeclareMathOperator{\argmax}{arg\,max}`; vectors and matrices
  consistently (`\mathbf`, `\bm` from bm, or `\boldsymbol`).
- Delimiters `\left( … \right)` only when needed; `\bigl( … \bigr)` give
  control. Use `\dots`, `\cdots` (amsmath picks the right one with `\dots`).
- Theorems: `amsthm` + `\newtheorem{theorem}{Theorem}[chapter]`,
  `\newtheorem{lemma}[theorem]{Lemma}`, `\theoremstyle{definition}`; `proof`
  environment. (llncs and some classes predefine these — see
  `templates/publisher-classes.md`.)
- Physics/chemistry: `physics` (derivatives, bra-kets), `mhchem` or
  `chemformula` (`\ce{H2SO4}`), `siunitx` for quantities.

## 9. Numbers and units

siunitx v3 (TeX Live 2023 ships 3.3):
```latex
\num{12345.678}                 % 12 345.678 (grouping per locale)
\qty{3.5}{\milli\second}        % 3.5 ms  (v2 syntax \SI{3.5}{\milli\second} still works)
\unit{\kilo\gram\per\cubic\metre}
\qtyrange{10}{20}{\celsius}  \ang{30}  \num{1.2e-3}
\sisetup{locale = DE}           % decimal comma for German; or output-decimal-marker = {,}
```
- A space between number and unit (siunitx does it); `\%` follows the
  number per the style (siunitx `\qty{5}{\percent}`).
- Same precision within a table column; report uncertainty and sample size
  where meaningful; decimal marker of the document's language.

## 10. Code listings and algorithms

- **listings** (no external tools — safe for journals and arXiv):
  ```latex
  \usepackage{listings}
  \lstset{basicstyle=\ttfamily\small, breaklines=true, columns=fullflexible, frame=lines}
  \begin{lstlisting}[language=Python, caption={Training loop.}, label={lst:train}]
  for epoch in range(10):
      train(model)
  \end{lstlisting}
  \lstinputlisting[language=C, firstline=10, lastline=40]{code/main.c}
  ```
- **minted** (Pygments highlighting) needs `-shell-escape` and Python Pygments —
  fine for a thesis built locally or on Overleaf, risky for submissions.
- **Algorithms**: either `algorithm` + `algpseudocode` (algorithmicx) or
  `algorithm2e` — never both (conflicting definitions):
  ```latex
  \usepackage{algorithm}
  \usepackage{algpseudocode}
  \begin{algorithm}[htbp]
    \caption{Binary search.}\label{alg:bs}
    \begin{algorithmic}[1]
      \Require sorted array $A$, value $x$
      \State $lo \gets 0$, $hi \gets |A|-1$
      \While{$lo \le hi$}
        \State $m \gets \lfloor (lo+hi)/2 \rfloor$
        \If{$A[m] = x$} \State \Return $m$ \EndIf
      \EndWhile
    \end{algorithmic}
  \end{algorithm}
  ```

## 11. Lists

`itemize`, `enumerate`, `description`; customise with `enumitem`
(`\begin{enumerate}[label=(\alph*), nosep]`, `\setlist{nosep}`). Keep list items
parallel in grammar; a list is not a substitute for argument in prose sections.

## 12. Abbreviations, glossaries, nomenclature, index

| Package | Build tool | Notes |
|---|---|---|
| `glossaries` with `\makenoidxglossaries` | none | simplest; sorting done by TeX (fine for dozens of entries); used by the thesis skeleton |
| `glossaries` with `\makeglossaries` | **makeglossaries** (latexmk rule in `assets/latexmkrc`) | large lists, language-aware sorting |
| `glossaries-extra` with `record` | **bib2gls** (Java) | entries in `.bib`-like files; most powerful |
| `acro` | none | `\DeclareAcronym{gpu}{short=GPU, long=graphics processing unit}`, `\ac{gpu}`, `\printacronyms` |
| `acronym` | none | simple; `\acro{GPU}{graphics processing unit}` in an `acronym` environment |
| `nomencl` | makeindex with `nomencl.ist` (latexmk rule) | lists of symbols |
| `imakeidx` / `makeidx` | makeindex (latexmk runs it) | `\index{term}`, `\printindex` |

- Define each abbreviation once and always write `\gls{key}` / `\ac{key}`: the
  first use prints "graphics processing unit (GPU)", later uses "GPU", plurals
  with `\glspl`/`\acp`, sentence start with `\Gls`/`\Ac`. Typing "GPU" by hand
  skips the first-use expansion and the list entry (`audit-tex.py` reports
  abbreviations typed literally and definitions never used).
- Only used entries appear in the list (unless `\glsaddall` — avoid it).
- Expand abbreviations again in the abstract if the guide requires it (the
  abstract must stand alone): `\glsreset{key}` or simply write it out.
- `\newacronym` in `glossaries` loaded **after** hyperref gives clickable entries.
- Glossary styles `long*` and `super*` are (long)tables: they advance the **table counter**, so with
  continuous numbering the first real table becomes "Table 2" (verified). Use `alttree` with
  `\glsfindwidesttoplevelname[\acronymtype]` before printing (aligned, not a table), `index` or `listdotted`.

## 13. Quotations, emphasis, dashes, spaces

- Quotation marks: `\enquote{…}` (csquotes, language-aware) or ``` ``…'' ``` in
  English; never straight `"…"` (pdfLaTeX prints two closing marks; babel
  shorthands make `"` active in German and other languages).
- Emphasis: `\emph{}` (nests correctly); `\textbf{}` for headings-like emphasis
  only; foreign terms in italics as the style guide says.
- Hyphen `-` (compound words), en dash `--` (ranges 10--20, connections
  Michelson--Morley), em dash `---` (punctuation, or a spaced en dash in British
  style), minus sign only in math `$-1$`.
- Non-breaking spaces: `Figure~\ref{}`, `p.~45`, `Dr.~Smith`, `10~kg` (or
  siunitx). After an abbreviation's period mid-sentence: `e.g.\ ` or `e.g.,`;
  a capital-letter abbreviation ending a sentence: `NASA\@.` — or simply
  `\frenchspacing` for single spacing after periods.
- Ellipsis `\dots`; degrees and other symbols via siunitx or `textcomp`
  commands, not typed lookalikes.

## 14. Languages

- babel: `\usepackage[ngerman, english]{babel}` — the **last** language is the
  main one (hyphenation, "Figure"/"Abbildung", dates); switch for passages with
  `\foreignlanguage{ngerman}{…}` or `\begin{otherlanguage}{ngerman}`; an
  abstract in a second language inside `otherlanguage`.
- polyglossia (Xe/LuaLaTeX only): `\setmainlanguage{english}`,
  `\setotherlanguage{german}`. Do not load both.
- Rename fixed strings per language: `\addto\captionsenglish{\renewcommand{\figurename}{Fig.}}`
  (babel re-applies captions at `\begin{document}`, so a plain `\renewcommand`
  in the preamble is overwritten).
- Hyphenation exceptions: `\hyphenation{data-base}`; URLs with `xurl`.
- US vs UK spelling is a choice of the venue or institution: pick one, set
  `american`/`british` in babel, stay consistent.
- Decimal marker, quotation marks, date formats, thousand separators follow the
  document language (`siunitx` `locale`, `csquotes`, `datetime2`).

## 15. Hyperlinks, PDF metadata, PDF/A, accessibility

- `\usepackage{hyperref}` late in the preamble (most packages before it;
  cleveref and glossaries after it). Print versions: `hidelinks`; on-screen
  versions: `colorlinks=true, allcolors=blue!50!black` or the template's choice.
- Metadata: `\hypersetup{pdftitle={…}, pdfauthor={…}, pdfkeywords={…}}` — and
  **empty for anonymous review** (`pdfauthor={}`).
- Math or commands in headings used for PDF bookmarks:
  `\section{\texorpdfstring{$\alpha$-stable laws}{alpha-stable laws}}`.
- **PDF/A** (many graduate schools and repositories require it): with TeX Live
  2023 or newer, `\DocumentMetadata{pdfstandard=a-2b, lang=en-US}` as the first
  line (before `\documentclass`) writes the PDF/A metadata (tested: XMP
  declares part 2, conformance B); the older route is the `pdfx` package
  (`\usepackage[a-2b]{pdfx}` + a `\jobname.xmpdata` file). Either way, validate
  the result with veraPDF or the repository's checker — declaring is not
  complying (embedded fonts, no transparency in PDF/A-1, colour profiles).
- All fonts must be embedded (`pdffonts main.pdf`, column `emb` = yes;
  `compile-check.sh` reports it).
- Tagged/accessible PDF is an active LaTeX development
  (`\DocumentMetadata{testphase=…}` in recent TeX Live); provide alt text,
  real headings, real lists and tables meanwhile.

## 16. Drafting aids

- `\usepackage{lineno}` + `\linenumbers` — line numbers for reviewers and
  response letters.
- `todonotes` (`\todo{check this}`; `\usepackage[disable]{todonotes}` hides them)
  — or `% TODO:` comments, which `audit-tex.py` tracks.
- `draft` class option (images as boxes, faster builds); `\includeonly{chapters/results}`
  with `\include` to compile one chapter with correct numbering; `subfiles` to
  compile a chapter on its own.
- `latexdiff old.tex new.tex > diff.tex` (`--flatten` for multi-file projects)
  produces a marked-up PDF of the changes for reviewers and supervisors.
- `\usepackage{showframe}` shows the text block and margins.
