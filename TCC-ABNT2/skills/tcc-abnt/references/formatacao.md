# Formatação visual (NBR 14724, 6024) — what to verify and how to fix it

The abnTeX2 class (and the institutional template on top of it) already sets
margins, fonts, spacing and pagination. **Do not hand-set them** in chapter
files. This file is the spec to verify against, plus the fixes for the
recurring problems that the class cannot prevent (floats, tables, lists).

## Página, fonte, espaçamento, paginação

- Paper A4; margins **left and top 3 cm, right and bottom 2 cm** (mirrored on
  the verso for two-sided printing: `twoside,openright`).
- Body: 12 pt, black; Times (`mathptmx`/`times`) or Arial (`helvet`) family
  per institution; abnTeX2's default (Latin Modern) is accepted by many.
- **Smaller, uniform size (10):** long quotes, footnotes, page numbers, ficha
  catalográfica, and the identification and source of illustrations and
  tables. References and the natureza do trabalho stay at 12 pt.
- Line spacing **1.5** in the body; **single** in long quotes, footnotes,
  references, captions/sources, ficha catalográfica, natureza do trabalho.
  References are separated by one blank line.
- abnTeX2 prints captions at 12 pt by default (the reduced caption font is
  commented out in the class); `\fonte{}`/`\nota{}` are reduced, memoir's
  `\legend{}` is not. If the institution enforces the reduced size for
  legends, add `\captionnamefont{\ABNTEXfontereduzida}` and
  `\captiontitlefont{\ABNTEXfontereduzida}` to the preamble.
- Page number: top right corner (2 cm from the top edge), size 10, from the
  first textual page; pre-textual pages counted but not numbered. The class's
  `\pretextual`/`\textual`/`\postextual` regions do this.
- To see the margins while debugging: `\usepackage[showframe,pass]{geometry}`
  temporarily.

## Seções (NBR 6024)

- Progressive numbering `1`, `1.1`, `1.1.1`, `1.1.1.1`, `1.1.1.1.1` — five
  levels maximum; do not create a sub-level with a single child.
- Number and title separated by one space, **no period** after the number
  (`2.3 Metodologia`, not `2.3. Metodologia`), aligned left; a title that wraps
  aligns its second line under the first letter of the title.
- Primary sections start on a new page (`\chapter`); their typographic
  hierarchy (caps, bold, italics) must be consistent and mirrored in the
  sumário — class options `chapter=TITLE`, `section=TITLE`, etc.
- Unnumbered elements (errata, agradecimentos, resumo, listas, sumário,
  referências, glossário, apêndices, anexos, índice) are centered.
- Always `\label{sec:...}` right after the sectioning command; reference with
  `Seção~\ref{sec:...}`.

## Ilustrações (figuras, gráficos, quadros, fluxogramas…)

- Identification **above**: type + number + travessão + título —
  `Figura 3 – Arquitetura do sistema`. Numbering is sequential per type in the
  whole document.
- **Source below**, size 10, mandatory even for your own material:
  `Fonte: elaborada pelo autor (2026).` / `Fonte: Silva (2020, p. 3).` /
  `Fonte: adaptada de Silva (2020).` / `Fonte: dados da pesquisa (2026).`
  Optional notes after the source (`Nota: …`). The source is a citation: the
  author must be in the references (NBR 14724:2024).
- **Call out before it appears** (`A Figura~\ref{fig:x} mostra…`) and place it
  as close as possible to the call-out. Every float must be referenced at
  least once.
- Legend, source and notes align with the figure's own margins and never exceed
  its width. One consistent alignment (centered is usual) for the whole work.

```latex
\begin{figure}[htb]
  \centering
  \caption{Arquitetura do sistema}
  \includegraphics[width=0.8\textwidth]{figuras/arquitetura.png}
  \fonte{elaborada pelo autor (2026).}   % prints "Fonte: …" in the reduced font
  \label{fig:arquitetura}
\end{figure}
```
(In abnTeX2 the caption goes **before** the graphic; `\fonte{}` adds the
"Fonte:" label and the reduced size — `\legend{Fonte: …}` would print at 12 pt.
Templates often replace this with their own macro — UniforTeX2:
`\UNIFORfig{\Caption{…}}{\includegraphics…}{\Fonte{…}}`.)

### Float placement — the queue problem

LaTeX places floats in FIFO order. One float that does not fit anywhere (a
tall figure plus a long caption, or a `[h!]` that cannot be honoured) blocks
every float after it, and a whole chapter's figures land 10–25 pages after the
text that cites them — a real NBR 14724 violation found in audits.

- Prefer `[htb]` or `[htbp]`; reserve `[h!]`/`[H]` for small floats.
- Keep tall figures under ~0.9 of the text height including caption and source
  (`width=0.9\textwidth` or `height=0.8\textheight,keepaspectratio`); shorten
  captions and move detail to a `\nota{}`/`Nota:`.
- Grep the log for `Float too large for page` and `Overfull \vbox`; fix those
  first, then recompile — later floats usually fall into place.
- A float frame (templates that wrap the graphic in a box) adds a few points:
  `width=\textwidth` may overflow by ~5 pt; use `0.98\textwidth`.
- `\clearpage` at the end of a chapter flushes the queue (acceptable), never
  `\newpage` inside text to "push" a figure.

## Tabelas vs quadros

- **Tabela**: numeric/statistical data; follows IBGE's *Normas de apresentação
  tabular* — **open lateral borders** (`\toprule`/`\midrule`/`\bottomrule` from
  `booktabs`, no vertical rules), title above, source below.
- **Quadro**: textual, qualitative or comparative information (definitions,
  feature comparisons, configuration listings) — **closed borders** on all
  sides. Numbered and listed separately (Lista de quadros). A "table" whose
  cells are prose is a quadro; misclassifying it is the ABNT point most likely
  to be raised by a Brazilian banca.
- Both: identification above, source below (size 10), called out in the text,
  as close as possible to the call-out, and not wider than the text block —
  use `p{width}` columns or `\tabcolsep`/font reduction (never below the
  source line's 10 pt for readability), or rotate with `rotating`'s
  `sidewaystable` as a last resort.
- A table that must break across pages uses `longtable`/`xltabular`, repeating
  the header and adding "(continua)" / "(conclusão)" marks per IBGE.

```latex
\begin{table}[htb]
  \centering
  \caption{Comparação de SGBDs}
  \begin{tabular}{lcc}
    \toprule
    SGBD & Modelo & Licença \\ \midrule
    Exemplo A & relacional & Apache 2.0 \\
    Exemplo B & documento  & SSPL \\ \bottomrule
  \end{tabular}
  \fonte{elaborada pelo autor (2026).}
  \label{tab:sgbds}
\end{table}
```

A quadro is a separate float type. The canonical model defines it with
memoir's `\newfloat[chapter]{quadro}{loq}{\quadroname}` plus
`\newlistof{listofquadros}{loq}{\listofquadrosname}` and prints
`\listofquadros*`; institutional templates usually ship their own. Never load
the `float` package on top of it — its `\newfloat` has a different signature
and breaks the definition.

## Equações

Numbered at the right margin, referenced as `Equação~\ref{eq:dft}` (or
`\eqref` if the institution wants parentheses), and cited in the text at least
once. Decimal **comma** in Portuguese text and formulas: `$0{,}5$` (the braces
suppress the space after the comma).

```latex
\begin{equation}
  X_k = \sum_{n=0}^{N-1} x_n\, e^{-j 2\pi k n / N}
  \label{eq:dft}
\end{equation}
```

## Listas pré-textuais (siglas, símbolos)

- **Siglas:** only the ones **used in the text**, alphabetical, with the full
  expression; first occurrence in the text spells it out — `Trabalho de
  Conclusão de Curso (TCC)`. With `glossaries`, `\glsaddall` prints **every**
  defined acronym, used or not: either curate the definitions file or drop
  `\glsaddall` and reference acronyms with `\gls{}`/`\acrshort{}`.
- **Símbolos:** in **order of first appearance** in the text, with meaning;
  disambiguate a symbol that means two things (`$N$ (amostras)`, `$N$ (nós)`).
  Symbols that never appear in the text do not belong in the list.
- Empty lists (no algorithm, no código-fonte) are removed, not printed empty.

## Alíneas

```latex
\begin{alineas}
  \item primeira alínea;
  \item segunda alínea:
  \begin{subalineas}
    \item primeira subalínea;
    \item segunda subalínea.
  \end{subalineas}
\end{alineas}
```
Alíneas are lettered `a)`, `b)`, end with `;` (last with `.`), start lowercase.

## Typographic conventions in pt-BR academic text

- Foreign terms in italics (`\textit{framework}`), acronyms not italicized.
- Decimal comma (`0,907`), thousands separator by point or thin space (`1.217`),
  `%` after a non-breaking thin space or directly (`67\,\%` / `67\%`),
  consistently.
- Non-breaking space before references: `Figura~\ref{}`, `Tabela~\ref{}`,
  `Seção~\ref{}`, `p.~30`.
- Travessão `--` in captions is produced by the class; in text use `---` (or
  `--` per institution) consistently.
- Do not use `\\` to break paragraphs; a blank line starts a new paragraph.
  A stray `\\` before `\section` produces `There's no line here to end`.
