# Style guides — what each one wants and how to get it in LaTeX

**Decision rule: the venue's or institution's instructions win.** "APA" or
"Harvard" in a graduate-school guide often means a local variant; a journal's
"IEEE style" is whatever its `.bst` prints. Use the style package as shipped,
then adjust only what the instructions explicitly require, through options —
never by editing `.bbx`/`.bst` files in place.

Availability and the loading lines below were compiled with TeX Live 2023
(package versions in brackets). Newer editions of a guide may need a newer
package: check `texdoc <package>` or the CTAN page for the edition it
implements.

## Contents
1. Quick map
2. Author-date guides: APA, Chicago author-date, Harvard, MLA
3. Numeric guides: IEEE, Vancouver/ICMJE, Nature, Science, ACS, AIP/APS, ACM, LNCS, AMS, Elsevier
4. Notes guides: Chicago notes-bibliography, OSCOLA, Oxford
5. National standards: ISO 690, ABNT (Brazil), GB/T 7714 (China), GOST (Russia), DIN (Germany)
6. Changing style safely

## 1. Quick map

| Guide | biblatex (biber) | BibTeX `.bst` | Notes |
|---|---|---|---|
| APA 7th | `style=apa` [biblatex-apa 9.17] | `apacite` package implements APA **6** | APA 6: `style=apa6` |
| Chicago 17th, author-date | `\usepackage[authordate]{biblatex-chicago}` [3.18] | `chicago.bst` (old) | load the package, not `style=chicago-authordate` (fails) |
| Chicago 17th, notes | `\usepackage[notes]{biblatex-chicago}` | — | citations in footnotes via `\autocite` |
| Harvard (generic) | `style=authoryear` (+ options), `style=ext-authoryear-comp`, `style=bath` (Bath Harvard) | `agsm`, `dcu`, `kluwer` (harvard family), `plainnat` + natbib | no single standard: follow the institution's sheet |
| MLA (current Handbook) | `style=mla` [biblatex-mla 2.1a] | — | `mla7` for the 7th edition |
| IEEE | `style=ieee` [biblatex-ieee 1.3f] | `IEEEtran` (+ `cite` package) | IEEE templates use the `.bst` |
| Vancouver / ICMJE | `style=vancouver` [0.1], `style=nejm` | `vancouver` | biomedicine; journal abbreviations (NLM) |
| Nature | `style=nature` [1.3d] | `naturemag` | superscript citations |
| Science | `style=science` | — | |
| ACS (chemistry) | `style=chem-acs` (also `chem-rsc`, `chem-angew`, `chem-biochem`) | `achemso` | |
| AIP / APS (physics) | `style=phys` | `aipnum4-2`, `apsrev4-2` (REVTeX picks it) | |
| ACM | `style=acmnumeric` / `acmauthoryear` **inside acmart** with `natbib=false` | `ACM-Reference-Format` | the ACM biblatex styles need acmart's commands |
| Springer LNCS | `style=lncs` [0.7] | `splncs04` | LNCS templates use the `.bst` |
| AMS (mathematics) | `style=alphabetic` / `numeric` | `amsplain`, `amsalpha` | |
| Elsevier | — | `elsarticle-num`, `elsarticle-num-names`, `elsarticle-harv` | `\citet` needs `-num-names` or `-harv` |
| ISO 690 | `style=iso-authoryear` / `iso-numeric` [biblatex-iso690 0.4.1] | — | |
| ABNT NBR 6023/10520 (Brazil) | `style=abnt` (biblatex-abnt) | `abntex2cite` (`[alf]`/`[num]`) | see §5 |
| GB/T 7714-2015 (China) | `style=gb7714-2015` | — | |
| GOST (Russia) | `style=gost-numeric` / `gost-authoryear` | — | |
| DIN 1505 (Germany) | `style=iso-*` (DIN ISO 690) or the standard styles | `alphadin`, `plaindin` | |
| OSCOLA (UK law) | `style=oscola` | — | notes |
| Oxford (humanities) | `style=oxnotes` / `oxyear` / `oxnum` | — | |
| SBL (biblical studies) | `style=sbl` | — | notes |
| Unified Style Sheet for Linguistics | `style=unified` (needs `hyperref` loaded) | — | |
| Philosophy | `style=philosophy-modern` / `-classic` / `-verbose` | — | |

Not usable as-is in TeX Live 2023: `style=historian` fails with biblatex 3.19
(`Option 'url' already defined`).

## 2. Author-date guides

### APA 7th edition (psychology, education, social sciences, nursing)
```latex
\usepackage[american]{babel}      % or english/british; biblatex-apa ships the language strings
\usepackage{csquotes}
\usepackage[backend=biber, style=apa]{biblatex}
\addbibresource{references.bib}
```
- In text: `(Author, 2020)`, `Author (2020)`, page `(Author, 2020, p. 45)`.
  Three or more authors → first author + "et al." from the first citation;
  two authors always both. Several works: alphabetical, separated by
  semicolons (biblatex-apa sorts them). Write `\parencite`, `\textcite`,
  `\parencite[45]{k}`.
- Reference list: alphabetical, hanging indent, up to 20 authors (the style
  handles truncation), DOIs as `https://doi.org/…` (store the bare DOI), article
  titles in sentence case (biblatex-apa converts — so brace proper nouns and
  acronyms in the `.bib`), journal and volume in italics.
- Figures and tables (APA's own rules): number in bold and title in italics
  **above** the figure or table, notes below.
- `apacite` (BibTeX) implements the 6th edition; natbib + `apalike` is only an
  approximation — neither is APA 7.

### Chicago Manual of Style — author-date
`\usepackage[authordate, backend=biber]{biblatex-chicago}` (load biblatex-chicago
**instead of** biblatex; `style=chicago-authordate` alone fails). TeX Live 2023's
biblatex-chicago 3.18 follows the **17th** edition; for the 18th (2024) check
whether your installed version supports it (`texdoc biblatex-chicago`).
In text `(Knuth 1984, 97)`: no comma between author and year.

### Harvard
"Harvard" is a family, not a standard: each university publishes its own sheet
(punctuation, "et al." threshold, `Available at:` and `[Accessed …]` for web
sources). Start from `style=authoryear` (or `ext-authoryear-comp` for finer
control; `bath` for Bath's variant) and set: `maxcitenames=2` or 3,
`giveninits=true`, `uniquename=false`, `dashed=false`, `date=year`; adjust
punctuation with `\DeclareDelimFormat{nameyeardelim}{\addcomma\space}` for
"(Smith, 2020)". With BibTeX: natbib + `agsm`/`dcu`.

### MLA (literature, languages, humanities)
`\usepackage[backend=biber, style=mla]{biblatex}` — in text `(Knuth 97)`:
author and page, no year; "Works Cited" list. The package tracks the current
Handbook (8th/9th editions; `style=mla7` for the old one).

## 3. Numeric guides

### IEEE (electrical engineering, computing)
- IEEE templates: `\bibliographystyle{IEEEtran}` + `\usepackage{cite}` (sorted,
  compressed `[1]–[3]`); journal abbreviations via `\bibliography{IEEEabrv,refs}`
  with `journal = IEEE_J_TPAMI`-style macros (from IEEEabrv.bib).
- Without the class: `style=ieee` (biblatex-ieee).
- Numbered in order of first citation; `[1]`, `[1], [3]`, `[1]–[3]`; the number
  can stand as a noun ("as shown in [2]"). Never "in reference [2] by [2]".

### Vancouver / ICMJE (medicine, biomedical sciences)
`style=vancouver` or `style=nejm`; BibTeX `vancouver.bst`. Numbers in order of
citation; journal titles abbreviated as in the NLM Catalog; usually the first
six authors then "et al." — check the journal's instructions, which vary.

### Nature, Science and other journals
Nature `style=nature` (superscript numbers via `\autocite`); Science
`style=science`; Cell, PLOS, Wiley, Taylor & Francis, MDPI, Frontiers and
others distribute their own templates and `.bst` files — use those. For a
journal without a LaTeX template, any numeric or author-year style that
matches their examples is acceptable at submission; production restyles it.

### Chemistry and physics
ACS: `style=chem-acs` or `\bibliographystyle{achemso}`; RSC `chem-rsc`; Angewandte
`chem-angew`. AIP/APS: REVTeX selects `apsrev4-2`/`aipnum4-2` from the class
options; `style=phys` with biblatex.

### ACM, LNCS, AMS, Elsevier
See `templates/publisher-classes.md`: ACM `ACM-Reference-Format` (numeric;
`\citestyle{acmauthoryear}` for author-year) or acmart's biblatex styles with
`natbib=false`; LNCS `splncs04`; AMS `amsplain`/`amsalpha`; Elsevier
`elsarticle-num` (no author data for `\citet`), `elsarticle-num-names`,
`elsarticle-harv` (with the `authoryear` class option).

## 4. Notes guides (humanities, law)

- **Chicago notes-bibliography**: `\usepackage[notes, backend=biber]{biblatex-chicago}`;
  cite with `\autocite{k}` / `\autocite[45]{k}` — first note full, later notes
  short, bibliography at the end.
- **OSCOLA** (UK law): `style=oscola` (supports legal sources via its own entry
  types — read its manual).
- **Oxford** styles: `style=oxnotes` (notes), `oxyear`, `oxnum`, `oxalph`.
- Generic: `style=verbose`, `verbose-ibid`, `verbose-trad2`.
Never type footnote citations by hand: "ibid.", short forms and cross-references
change whenever text moves.

## 5. National standards

### ISO 690
`style=iso-authoryear` or `iso-numeric` (biblatex-iso690) — common in Czech,
Slovak, Scandinavian and some German-speaking institutions.

### ABNT — Brazil (NBR 6023:2018, NBR 10520:2023, NBR 14724:2024)
The dedicated **`tcc-abnt` skill** (same repository) covers abnTeX2, the norms
and institutional templates in depth. Essentials, verified in TeX Live 2023:
- abnTeX2 + `abntex2cite` (BibTeX): `\usepackage[alf]{abntex2cite}`; prints the
  NBR 10520:**2002** form `(SILVA, 2020)`. For the 2023 form `(Silva, 2020)`, add
  to the `.bib` an options entry and activate it — the reference list keeps
  `SILVA, J.` as NBR 6023 requires:
  ```bibtex
  @ABNT-options{nbr10520-2023, abnt-cite-style = "(Author, YEAR)", key = "aaaa"}
  ```
  ```latex
  \usepackage[alf,nbr10520-2023]{abntex2cite}
  \def\UrlLeft{}\def\UrlRight{}     % NBR 6023:2018: "Disponível em: URL" without < >
  ```
- `biblatex-abnt` (`style=abnt`) also prints `(KNUTH, 1984)`; the 2023 form with
  the list unchanged: `\renewcommand*{\mkbibnamefamily}[1]{#1}` after loading
  biblatex. With any Portuguese babel option it warns `File
  'brazilian-abnt-abnt.lbx' not found!` — harmless, the output is correct.
- Institutions differ on which editions they enforce: ask the library.

### GB/T 7714-2015 (China), GOST (Russia), DIN (Germany)
`style=gb7714-2015` (and `gb7714-2015ay` author-year); `style=gost-numeric` /
`gost-authoryear` (Russian theses also need `babel` Russian and Cyrillic fonts);
German: DIN 1505 `.bst` files (`alphadin`, `plaindin`) or DIN ISO 690 via
`biblatex-iso690`; many German universities simply prescribe `authoryear` or
`alphabetic`.

## 6. Changing style safely

1. Confirm the target (guide, edition, any local variant) and keep a copy.
2. Same stack (biblatex → biblatex): change `style=` (or the loading line for
   biblatex-chicago), recompile with biber, read the PDF.
3. Across stacks (natbib ↔ biblatex): change the preamble, convert citation
   commands (`\citet`→`\textcite`, `\citep`→`\parencite`), switch the build
   chain (bibtex ↔ biber), and re-check the `.bib` (biblatex fields are
   ignored by BibTeX and vice versa — `bib-check.py --backend bibtex|biber`).
4. Author-year ↔ numeric changes prose: "Smith (2020) showed" works in both
   only with `\textcite`; "[3] showed" does not survive a switch to author-year.
   Re-read every citation sentence.
5. Recompile from scratch and read the reference list against the guide's
   examples: names, capitalisation, italics, DOIs, punctuation.
