# Norm editions, what changed, and what abnTeX2 actually produces

ABNT revised three core norms after abnTeX2's last release (v1.9.7, 2018-11-24).
Institutions adopted the new editions at different speeds, and many library
manuals and templates still print the old forms. This file tells you what is
current, what abnTeX2 emits by default, and the **tested** way to reconcile them.

Decision rule: **the institution's manual (biblioteca/PPG/orientador) wins**.
If the user does not know which edition their institution follows, tell them in
one paragraph what changed, recommend asking the library, and default to what
the template already produces (consistency inside the document matters more
than the edition). Record the decision in `.tcc-workflow/STATUS.md`.

## Edition table

| Norm | Subject | Current edition | Previous | Notes |
|---|---|---|---|---|
| NBR 14724 | Trabalhos acadêmicos — apresentação | **2024** (published 16 Dec 2024) | 2011 | 4th edition |
| NBR 10520 | Citações em documentos | **2023** (19 Jul 2023) | 2002 | biggest practical change |
| NBR 6023 | Referências — elaboração | **2018** + Errata 2 (2020) | 2002 | |
| NBR 6028 | Resumo, resenha e recensão | **2021** | 2003 | |
| NBR 6024 | Numeração progressiva das seções | 2012 | 2003 | |
| NBR 6027 | Sumário | 2012 | 2003 | |
| NBR 6022 | Artigo em publicação periódica | 2018 | 2003 | |
| NBR 15287 | Projeto de pesquisa | 2011 | 2005 | |
| NBR 6034 | Índice | 2004 | | |
| NBR 12225 | Lombada | 2004 | | |

abnTeX2 v1.9.7 declares support for NBR 14724:2011, NBR 10520:2002, NBR 6023
(2002 output with some 2018 forms), NBR 6028:2003, NBR 6024:2012, NBR 6027:2012.
`biblatex-abnt` (CTAN lists v4.0; its README still documents 3.4, 2018) targets
NBR 10520:2002 for citations — check its manual for the NBR 6023 edition it
follows.

## NBR 10520:2023 — citations

What changed (versus 2002):

- **Author names inside parentheses take only an initial capital:**
  `(Silva, 2020)`, `(Pereira; Alves; Oliveira, 2022)`, `(Silva et al., 2023)`.
  In the running text nothing changed: `Silva (2020)`.
- **Entity/corporate authors** may be cited by acronym or full name:
  `(IBGE, 2011)`, `(Universidade Federal do Pará, 2023)`; acronyms stay in caps.
  Government/jurisdiction: `(Brasil, 2021)`.
- ***et al.*** for works with **four or more** authors is optional (cite all or
  cite the first + *et al.*), but be consistent throughout the document.
- **Latin expressions in italics**: *et al.*, *apud*, *idem*, *ibidem*.
- Page number in direct quotes is required when the source has pagination; for
  e-books without pages use the locator: `(Montes; Casoy, 2009, local. 132)`.
- **Long direct quotes (> 3 lines):** still a separate block, smaller font,
  single spacing, no quotation marks; the indent is now a "recuo padronizado"
  (4 cm remains the conventional value and what abnTeX2's `citacao` environment
  gives).
- Several documents cited together are separated by `;` in alphabetical order
  (unchanged, but frequently violated: `\cite{a,b}` prints in the order given).

### Making abntex2cite print `(Silva, 2020)` — tested, no `.bst` editing

`abntex2-alf.bst` already implements both styles; the switch is an option read
from a special `@ABNT-options` entry. The entry shipped with abnTeX2 for this
option is unusable (its key collides case-insensitively with another entry,
BibTeX reports `Repeated entry`), so define your own:

1. Add to the project's `.bib` (any `.bib` passed to `\bibliography`):
   ```bibtex
   @ABNT-options{nbr10520-2023,
     abnt-cite-style = "(Author, YEAR)",
     key = "aaaa"}
   ```
2. Activate it — either as a package option:
   ```latex
   \usepackage[alf,nbr10520-2023]{abntex2cite}
   ```
   or, when you must not touch the template's preamble (UniforTeX2:
   `lib/preambulo.tex`), in `main.tex` right after the preamble is loaded:
   ```latex
   \AtBeginDocument{\citeoption{nbr10520-2023}}
   ```
   (`\citeoption` in the preamble itself is silently ignored because the `.aux`
   is not open yet — hence `\AtBeginDocument`.)
3. Recompile the full chain (pdflatex → bibtex → pdflatex ×2).

Verified output on the canonical model: `(Araujo, 2015a; Araujo, 2015c)`,
`(Wilson; Madsen, 2010)`, `(ABNT, 2002)`; `\citeonline` → `Araujo (2015a)`; the
reference list keeps `ARAUJO, L. C.` (NBR 6023 still wants caps there).
Entity authors: write `{{\relax Brasil}}`, `{{\relax Instituto Brasileiro de
Geografia e Estat{\'i}stica}}` — `{\relax ...}` keeps the citation case of the
document **and** the CAPS the reference list needs (plain `{{Brasil}}` prints
`Brasil.` in the list; `organization = {Brasil}` prints `(BRASIL, 2018)` in the
text whatever the style). Acronyms (`{{IBGE}}`) are caps anyway. Accents in
these fields must be TeX escapes, or the uppercasing produces `ASSOCIAçãO`.

`biblatex-abnt` users: the style still uppercases family names in citations;
a documented community workaround is `\renewcommand*{\mkbibnamefamily}[1]{#1}`
after loading biblatex — test it in the project before relying on it.

## NBR 6023:2018 — references

What changed (versus 2002), as it affects a `.bib`-driven workflow:

- `Disponível em: URL.` and `Acesso em: 5 jun. 2026.` **without angle brackets**.
- `[S. l.]` (sine loco) and `[s. n.]` (sine nomine) with spaces; avoid them when
  the place/publisher can be found (for anais/proceedings use the publisher's
  headquarters: `Piscataway: IEEE`, `New York: ACM`).
- Place names as they appear in the document (do not translate `New York`).
- DOI may be given as `DOI: 10.xxxx/...` (in abnTeX2, `doi = {...}`).
- Four or more authors: list all, or the first + *et al.* (consistently).

### Making abntex2cite drop the `<URL>` brackets — tested

The brackets come from `abntex2cite.sty` (`\def\UrlLeft{<}` `\def\UrlRight{>}`),
not from the `.bst`. After loading the package (or after the template's
preamble) add:

```latex
\def\UrlLeft{}\def\UrlRight{}
```

Verified output: `Disponível em: http://www.abntex.net.br/.` The same
definitions govern every `\url{}` in the body and footnotes, which lose their
brackets too (desirable, but say so). Keep `abnt-url-package=url` (the default)
so URLs still break across lines; add `\usepackage{xurl}` for very long URLs.
`[S.l.]` without the space is hard-coded in the `.bst`; give the real `address`
or write `address = {[S. l.]}` yourself.

## NBR 6028:2021 — resumo

- 150–500 words for TCC, dissertação, tese and relatórios; 100–250 for
  artigos; 50–100 for brief indications. One paragraph, concise sentences, no
  bullet points, third person recommended (active voice no longer mandatory).
- Keywords: `Palavras-chave: termo um; termo dois; termo três.` — separated by
  **semicolons**, lowercase initials (except proper nouns), period at the end.
  Under the 2003 edition they were separated by periods, which is what many
  templates (UniforTeX2 included) still show in their examples. Follow the
  institution; be consistent between Palavras-chave and Keywords.
- The abstract is a faithful translation of the resumo, followed by `Keywords:`.

## NBR 14724:2024 — structure and presentation

Margins, fonts, spacing and pagination are the same as in 2011. Changes that
matter for a LaTeX thesis:

- Sources of figures, tables and quadros follow NBR 10520:2023 — author outside
  parentheses: `Fonte: Silva (2020, p. 3).`; own material: `Fonte: elaborada
  pelo autor (2026).` (or `elaborado pelo próprio autor`). All parts of an
  illustration (type, number, title, source, legend, notes) align with the
  illustration's own margins and do not exceed its width.
- The body is organised in **seções** with progressive numbering (NBR 6024);
  the norm no longer speaks of "capítulos". In abnTeX2 the primary section is
  still produced by `\chapter`; when cross-referencing, prefer "na Seção 2" over
  "no Capítulo 2" if the institution follows the 2024 wording.
- References cited only inside an **anexo** stay with the anexo (footnotes or a
  list after it), not in the main reference list.
- Ficha catalográfica: "conforme código de catalogação vigente" (AACR2 no
  longer named); in electronic files it follows the folha de rosto. Whether it
  is counted in the pagination is interpreted differently by libraries — ask.
- Epígrafe: the pre-textual one need not follow NBR 10520; an epígrafe opening a
  primary section must be cited properly and appear in the references.
- Tables still follow IBGE's *Normas de apresentação tabular* (open sides).

## Telling the user (template)

> Seu template segue a NBR 10520:2002 (autores em CAIXA ALTA nas citações entre
> parênteses). A edição vigente é a NBR 10520:2023, que usa apenas a inicial
> maiúscula — `(Silva, 2020)`. Muitas bibliotecas já exigem a forma nova; outras
> aceitam a antiga desde que o trabalho seja consistente. Confirme com a sua
> biblioteca/orientador. Se quiser a forma nova, a mudança é de duas linhas e
> não altera a lista de referências.
