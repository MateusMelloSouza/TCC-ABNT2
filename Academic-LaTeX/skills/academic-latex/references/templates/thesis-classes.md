# Thesis classes — when there is no official template, and when there is

First choice: the graduate school's or department's own class/template. When
none exists, the formatting guide (margins, spacing, numbering, title page)
must be implemented on a general class. The setups below compile with TeX Live
2023 (`tests/thesis-classes/*.tex` and the skeleton in `assets/skeletons/thesis/`).

## Contents
1. The bundled skeleton (book + geometry + setspace + biblatex)
2. memoir
3. KOMA-Script (scrbook, scrreprt)
4. classicthesis and other designed styles
5. University classes on CTAN
6. Implementing a formatting guide — checklist

## 1. The bundled skeleton

`python3 scripts/new-project.py thesis --type thesis --style apa` (styles:
`--list-styles`; `--engine lualatex`, `--paper letter`, `--spacing double`,
`--twoside`, `--language ngerman,english`). It produces:

```
main.tex                     preamble + assembly (no \input'ed preamble: editors find the root)
frontmatter/                 titlepage, declaration, abstract, acknowledgements, abbreviations
chapters/                    introduction, background, methodology, results, discussion, conclusion
appendices/appendix-a.tex
figures/                     \graphicspath target
references.bib               real example entries — replace them
.latexmkrc  .gitignore
```
Design choices, all verified by compiling every style and engine combination:
`book` class with `oneside,openany` (switch to `twoside,openright` for print);
`geometry` margins with a wide binding margin; `setspace` (`\onehalfspacing`;
footnotes and floats stay single); `\pagestyle{plain}` (a fancyhdr block for
top-right numbers is in the comments); `\frontmatter`/`\mainmatter` for roman and
arabic numbering; abbreviations with `glossaries` + `\makenoidxglossaries`
(no external tool) printed with the `alttree` style (aligned, and not a table — `long` styles would advance the table counter); biblatex + biber with the
chosen style; `hyperref` with the title page excluded from page anchors (it
avoids the `destination with the same identifier (name{page.i})` warning);
`cleveref` last. Every place the author must fill carries a `% TODO:` comment,
which `audit-tex.py` lists until it is resolved.

## 2. memoir

One class with layout, chapter styles, spacing, captions and lists built in —
fewer packages, fewer conflicts:
```latex
\documentclass[12pt, a4paper, oneside]{memoir}
\setlrmarginsandblock{35mm}{25mm}{*}   % left (inner), right
\setulmarginsandblock{25mm}{25mm}{*}   % top, bottom
\checkandfixthelayout
\OnehalfSpacing                         % memoir's own spacing commands (\DoubleSpacing)
\usepackage{graphicx}                   % needed by chapter styles such as madsen (\resizebox)
\chapterstyle{madsen}                   % or default, bianchi, veelo, ...
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{microtype}
\usepackage[hidelinks]{hyperref}
\begin{document}
\frontmatter \tableofcontents*           % starred: the TOC does not list itself
\mainmatter \chapter{Introduction}
\backmatter
\end{document}
```
Do not add `geometry`, `setspace`, `titlesec` or `tocloft` to memoir: it has
equivalents (`\setlrmarginsandblock`, `\OnehalfSpacing`, `\chapterstyle`,
`\cftsetindents`). memoir rounds the text height to whole lines, so margins can
measure a millimetre off — expected. Manual: `texdoc memoir`.

## 3. KOMA-Script

European-style typography with options instead of packages:
```latex
\documentclass[12pt, a4paper, oneside, BCOR=8mm, DIV=12, parskip=half,
               bibliography=totoc, listof=totoc]{scrbook}   % or scrreprt
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{scrlayer-scrpage}          % headers and footers (not fancyhdr)
\usepackage[hidelinks]{hyperref}
\begin{document}
\frontmatter \tableofcontents
\addchap{Abstract}                     % unnumbered chapter listed in the TOC
\mainmatter \chapter{Introduction}
\end{document}
```
`DIV` and `BCOR` compute the type area (classic proportions); when a guide
gives exact margins, use `\usepackage[…]{geometry}` *instead of* DIV (and
accept KOMA's warning) or `\areaset`. Fonts via `\setkomafont{disposition}{…}`;
not `titlesec`. Manual: `texdoc scrguide` (also in German: `scrguide-de`).

## 4. classicthesis and other designed styles

- **classicthesis** (André Miede): a polished look on top of KOMA —
  `\documentclass[…, headinclude, footinclude, BCOR=5mm]{scrreprt}` +
  `\usepackage[pdfspacing]{classicthesis}` (compiles cleanly; KOMA warns that
  classicthesis uses `titlesec` and `tocloft` — expected). Its full template
  (`ClassicThesis.tex` with chapters and front matter) is on CTAN and Overleaf.
  Check that the look is allowed by the guide (many prescribe margins and fonts
  classicthesis does not use).
- `cleanthesis` (package), `tufte-book` (wide margins for side notes), and
  `kaobook` (on CTAN) — design-oriented; same caveat.

## 5. University classes on CTAN

Present in TeX Live 2023: `thuthesis` (Tsinghua), `ut-thesis` (Toronto),
`yathesis` (French doctoral theses), `toptesi` (Italian, Politecnico di Torino),
`msu-thesis` (Michigan State), `uothesis` (Oregon), `ucthesis` (University of
California, old), `mitthesis` (MIT), `umthesis` (UMass Amherst), `abntex2`
(Brazilian ABNT norms — see the `tcc-abnt` skill). Many more exist on
Overleaf and university sites. Before using one, check that it is current and
accepted by your graduate school (classes are often maintained by students
and lag behind rule changes); read its manual (`texdoc <class>`).

## 6. Implementing a formatting guide — checklist

Turn every rule of the guide into a line of preamble, then verify it in the PDF:

| Rule | Implementation | Verify |
|---|---|---|
| Paper size | `a4paper` / `letterpaper` class option | `pdfinfo` Page size |
| Margins (binding) | geometry / memoir / KOMA (above) | `\usepackage{showframe}`, ruler on a printout; microtype's protrusion hangs punctuation 1–2 pt into the margin (optical alignment) — if a format checker measures margins strictly, load `\usepackage[protrusion=false]{microtype}` |
| Font and size | class option `12pt`; font package | `pdffonts` |
| Line spacing | setspace (`\doublespacing`), memoir `\DoubleSpacing` | count lines per page |
| Single-spaced elements (quotes, captions, bibliography) | `singlespace` env, `\AtBeginBibliography{\singlespacing}` | visual |
| Page numbering (roman front matter, arabic from Ch. 1, position) | `\frontmatter`/`\mainmatter`, `\pagestyle`, fancyhdr / scrlayer-scrpage | each section's first page |
| Title page wording and layout | `titlepage` env copying the official sample | side by side with the sample |
| Order of front matter | order of `\input` lines in `main.tex` | TOC and PDF bookmarks |
| Chapter title format | memoir `\chapterstyle`, KOMA `\setkomafont`, titlesec (standard classes) | visual |
| Caption style and position | `caption` package; position per guide | visual |
| Lists (figures, tables, abbreviations) and their TOC entries | `\listoffigures`, `\listoftables`, glossaries; `tocbibind` or class options | TOC |
| Bibliography style | biblatex style or `.bst` per guide | compare with the guide's examples |
| Appendix naming ("Appendix A") and TOC entries | `\appendix`, `appendix` package | TOC |
| PDF/A, embedded fonts, metadata | `\DocumentMetadata`, hyperref `\hypersetup` | veraPDF, `pdffonts`, `pdfinfo` |
