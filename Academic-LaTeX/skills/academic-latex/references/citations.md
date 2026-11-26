# Citations in the text — choosing the stack and using it correctly

Outputs shown were produced with TeX Live 2023 (biblatex 3.19 + biber 2.19,
natbib 8.31 + plainnat). For what a specific style guide requires (APA, IEEE,
Chicago, …) see `style-guides.md`; for the `.bib` side see `bibliography.md`.

## Contents
1. Choosing the citation stack
2. Command crosswalk (biblatex · natbib · plain LaTeX)
3. biblatex essentials
4. natbib / BibTeX essentials
5. Multiple citations, pages, pre/post notes, name prefixes
6. Footnote (notes) styles
7. Quotations
8. Hard rules

## 1. Choosing the stack

| Stack | Tool | Strengths | Use when |
|---|---|---|---|
| **biblatex** (+ a style package) | **biber** | Unicode `.bib`, rich data model (`@online`, `@software`, `@dataset`, `urldate`, `eprint`), styles configured in LaTeX, per-chapter bibliographies, multilingual entries | theses, dissertations, books, preprints and any venue without a mandated `.bst` |
| **natbib** (+ `.bst`) | **bibtex** | what most publisher classes and production pipelines expect; portable `.bbl` | journal/conference templates that ship a `.bst` (acmart, elsarticle, REVTeX, AAS, many others) |
| **cite** (+ `.bst`) | **bibtex** | sorts and compresses numeric citations `[1]–[3]` | IEEEtran and other numeric `.bst` templates |
| plain `\cite` + `.bst` | **bibtex** | minimal | LNCS (`splncs04`), AMS (`amsplain`) |
| `thebibliography` by hand | none | nothing to install | never for a long document: no checking, no style changes |
| class-specific (abntex2cite, apacite, chicago, …) | bibtex | a style the class implements | when the template uses it |

Rules of thumb: **follow the template**; never load biblatex and natbib together
(biblatex's `natbib=true` option provides `\citet`/`\citep` if you need them);
do not convert a publisher template to biblatex — editors and production
systems expect the `.bst` output. For arXiv see `submission.md` (upload the
`.bbl`).

## 2. Command crosswalk

| Intent | biblatex | natbib (author-year) | natbib (`numbers`) |
|---|---|---|---|
| parenthetical: (Knuth 1984) / [1] | `\parencite{k}` · `\autocite{k}` | `\citep{k}` | `\citep{k}` or `\cite{k}` |
| textual: Knuth (1984) / Knuth [1] | `\textcite{k}` | `\citet{k}` | `\citet{k}` (needs a `.bst` with author data) |
| with page | `\parencite[45]{k}` → (Knuth 1984, p. 45) | `\citep[p.~45]{k}` | `\citep[p.~45]{k}` → [2, p. 45] |
| with prefix and page | `\parencite[see][45--47]{k}` → (see Knuth 1984, pp. 45–47) | `\citep[see][p.~45]{k}` | same |
| author only / year only | `\citeauthor{k}` / `\citeyear{k}` | `\citeauthor{k}` / `\citeyear{k}` | — |
| full author list | `\textcite[…]{k}` with `maxcitenames` | `\citet*{k}` | — |
| capitalised at sentence start (van Dijk → Van Dijk) | `\Textcite{k}`, `\Parencite{k}` | `\Citet{k}` | — |
| footnote citation | `\footcite{k}` | — | — |
| several works | `\parencite{a,b}` | `\citep{a,b}` | `\citep{a,b}` → [1–3] with `sort&compress` |
| list without citing | `\nocite{k}` (`\nocite{*}` = all entries) | `\nocite{k}` | `\nocite{k}` |

Pitfalls verified in practice:
- **natbib author-year: plain `\cite` is textual** — `\cite{k}` prints
  "Knuth (1984)"; use `\citep` for "(Knuth, 1984)".
- **natbib's punctuation comes from the `.bst` unless you set it**: with
  `plainnat` and no option, `\citep` prints `[Knuth, 1984]`; load
  `\usepackage[round]{natbib}` (or `authoryear`) for `(Knuth, 1984)`.
- **`\citet` with a purely numeric `.bst`** (e.g. `elsarticle-num`) prints
  `Author?` and warns "Author undefined": the style writes no author data.
  Use the `-names` variant (`elsarticle-num-names`) or rephrase.
- **`\autocite`** lets the style choose: parentheses for author-year,
  brackets for numeric, superscripts for `nature`, footnotes for Chicago notes —
  the best default when the style may change.

## 3. biblatex essentials

```latex
\usepackage[english]{babel}             % languages before biblatex
\usepackage{csquotes}                   % biblatex uses it for quoted titles
\usepackage[backend=biber, style=authoryear]{biblatex}
\addbibresource{references.bib}         % WITH the .bib extension
...
\printbibliography                      % in a book/report: [heading=bibintoc] adds it to the TOC
```

Useful options (`\usepackage[<options>]{biblatex}` or `\ExecuteBibliographyOptions{}`):

| Option | Effect |
|---|---|
| `style=` / `citestyle=` + `bibstyle=` | style package (see `style-guides.md`); standard ones: `numeric`, `numeric-comp`, `alphabetic`, `authoryear`, `authoryear-comp`, `authortitle`, `verbose`, `verbose-ibid`, `reading` |
| `sorting=none` / `nyt` / `ynt` / `nty` | order of the list: citation order / name-year-title / year-… (numeric styles default to `nty`; use `none` for "order of citation") |
| `sortcites=true` | sort works inside one citation as in the list (otherwise they print in the order typed) |
| `maxcitenames=2`, `maxbibnames=10`, `minbibnames=7` | et al. thresholds in citations and in the list |
| `giveninits=true` | initials for given names |
| `uniquename=false`, `uniquelist=false` | stop "J. Smith 2020 / A. Smith 2020" disambiguation when the style guide does not want it |
| `useprefix=true` | keep name prefixes in citations: "van Dijk (2010)" (default drops them: "Dijk (2010)") |
| `doi=false`, `url=false`, `isbn=false`, `eprint=false` | hide fields |
| `dashed=false` | repeat author names instead of a dash in authoryear lists |
| `date=year` | print only years |
| `autocite=footnote` / `inline` / `superscript` | what `\autocite` does |
| `natbib=true` | define `\citet`, `\citep`, … for compatibility |
| `backref=true` | "Cited on page 12" after each entry |

Per-chapter or per-paper bibliographies (thesis by publication):
`\begin{refsection} … \printbibliography[heading=subbibintoc] \end{refsection}`;
or `refsegment=chapter` + `\printbibliography[segment=\therefsegment]`. Split
lists by type with keywords or categories: `\printbibliography[keyword=primary,
title={Primary sources}]`. Language of each entry: `langid = {german}` in the
`.bib` + `\usepackage[autolang=hyphen]{biblatex}`.

Customise through the style's options and hooks, not by editing `.bbx` files:
`\DeclareFieldFormat{title}{\mkbibquote{#1}}`,
`\AtEveryBibitem{\clearfield{note}}`, `\DeclareSourcemap{…}` to clean imported
data (drop `abstract`, `file`, `urldate` for DOIs).

## 4. natbib / BibTeX essentials

```latex
\usepackage[round, authoryear]{natbib}   % or [numbers, sort&compress] (or the class loads natbib)
...
\bibliographystyle{plainnat}             % the .bst; publisher templates fix it
\bibliography{references}                % file name, extension optional
```
- Options: `round` / `square`, `authoryear` / `numbers`, `sort`, `sort&compress`,
  `super` (superscript numbers), `comma` / `semicolon`, `longnamesfirst`.
- Change punctuation after loading with `\setcitestyle{authoryear,round,semicolon}`.
- Common `.bst`: `plainnat`, `abbrvnat`, `unsrtnat` (citation order), `apalike`
  (old APA look — **not** APA 7), `IEEEtran`, `ACM-Reference-Format`,
  `elsarticle-num`/`-num-names`/`-harv`, `splncs04`, `apsrev4-2`, `aipnum4-2`,
  `amsplain`/`amsalpha`, `agsm`/`dcu`/`kluwer` (Harvard family), `vancouver`,
  `naturemag`, `achemso`, `alphadin` (DIN). Check with `kpsewhich name.bst`.
- The `.bst` decides what is printed; fields it does not know are silently
  ignored (`urldate`, `date`, `@online` types under BibTeX — `bib-check.py`
  warns).

## 5. Multiple citations, pages, name prefixes

- Several works in one citation: `\parencite{a,b}` prints in the order typed
  unless `sortcites=true` (biblatex) or `sort` (natbib); many style guides want
  them in the list's order (APA: alphabetical; numeric: ascending).
- Page or locator: biblatex adds "p."/"pp." automatically to numeric
  postnotes (`\parencite[45]{k}`); for other locators write them: `[chap.~3]`,
  `[fig.~2]`, `[sec.~4.1]`. natbib prints the postnote verbatim: write `p.~45`.
- Same author, same year: the style adds 2020a/2020b itself — do not type the
  letters into the `.bib`.
- Name prefixes (van, von, de, da): biblatex drops them in citations by default
  ("Dijk (2010)"); `useprefix=true` keeps them ("van Dijk (2010)"), and
  `\Textcite` capitalises at sentence start ("Van Dijk (2010)"). Conventions
  differ by language and style guide (and by the person's own usage): check the
  guide, then set the option once for the whole document.
- Organisations: cite with the name the style prefers (full name or acronym);
  define it once in the `.bib` as `{{World Health Organization}}` and use
  `shortauthor = {WHO}` (biblatex) when the style allows abbreviations.
- Secondary citations ("Smith 1990, cited in Jones 2010"): cite what you read —
  `\parencite[cited in][]{jones2010}` with Smith named in the text; only Jones
  goes in the list (APA and most guides).

## 6. Footnote (notes) styles

Humanities and law often cite in footnotes (Chicago notes-bibliography,
OSCOLA, MHRA). In biblatex: `biblatex-chicago` (`\usepackage[notes]{biblatex-chicago}`),
`style=verbose` / `verbose-ibid` / `verbose-trad2`, `oscola`, `oxnotes`. Write
`\autocite{k}` (footnote) or `\footcite[45]{k}`; first citation full, later ones
short, "ibid." handled by the style. Never type footnote citations by hand.

## 7. Quotations

- Short quotations inline with `\enquote{…}` (csquotes picks the right quotation
  marks for the language) and the page in the citation.
- Long quotations (APA: 40+ words; Chicago: 100+ words / several lines; other
  guides differ) as a block: `\begin{displayquote}[\parencite[45]{k}] … \end{displayquote}`
  or `\blockquote[\parencite[45]{k}]{…}` (switches to a block automatically
  above a length threshold).
- Omissions `[…]`, interpolations `[sic]`, your emphasis noted ("emphasis
  added") as the style guide says. Never change quoted text silently.

## 8. Hard rules

- Every citation key exists in the `.bib`; every entry in the list was cited
  (biblatex/BibTeX print only cited entries unless `\nocite{*}`).
- Never invent a citation, a page number or a quote. Missing data → ask, or
  `% TODO: citation needed — <claim>`.
- Cite what you read: do not cite a paper from its abstract or from someone
  else's description as if you had read it.
- One citation system and one style for the whole document (thesis by
  publication: per-paper bibliographies are fine, one style).
- Use the commands; never type "(Smith, 2020)" or "[3]" by hand.
