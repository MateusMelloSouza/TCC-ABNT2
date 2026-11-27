# Citações no texto (NBR 10520:2023) with abntex2cite / biblatex-abnt

Two systems exist — **autor-data** (author-date) and **numérico** (numeric).
Pick one and use it throughout. Author-date is the common default for Brazilian
TCCs; abnTeX2 enables it with `\usepackage[alf]{abntex2cite}` (numeric: `[num]`).

Edition note: examples below use the **2023** form `(Silva, 2020)`. abnTeX2
prints the 2002 form `(SILVA, 2020)` unless switched — see
`normas-e-versoes.md` — and many institutions still accept either. Whatever the
choice, it must be uniform across the whole document.

## Direct vs indirect

- **Citação direta (textual):** the author's exact words. Needs the page
  (`p. 30`) when the source has pagination; for e-books without pages the
  norm's examples use a locator (`local. 132`) — confirm the form with the library.
- **Citação indireta (paráfrase):** the idea in your own words. Page optional.
- Prefer paraphrase; reserve direct quotes for definitions and precise wording.

## Short direct quote (up to 3 lines)

Inline, inside double quotation marks, with the source:

> Segundo Silva (2020, p. 30), "a normalização garante a integridade dos dados".

> "A normalização garante a integridade dos dados" (Silva, 2020, p. 30).

Note the period placement: after the parenthetical citation when the citation
closes the sentence.

## Long direct quote (more than 3 lines)

A separate block: indented from the left margin (4 cm is the conventional
value), **smaller font (10)**, **single spacing**, **no quotation marks**, with
the page number.

```latex
\begin{citacao}
A normalização é o processo de organização das colunas e tabelas de um banco de
dados relacional para minimizar a redundância de dados. Envolve dividir tabelas
grandes em tabelas menores e definir relacionamentos entre elas
\cite[p.~42]{silva2020}.
\end{citacao}
```

abnTeX2's `citacao` environment applies the indent, size and spacing. Quotes in
another language: `\begin{citacao}[english] ... \end{citacao}`.

## Author capitalization

| Position | 2023 form | 2002 form (abnTeX2 default) |
|---|---|---|
| Inside parentheses | `(Silva, 2020)`, `(Pereira; Alves; Oliveira, 2022)` | `(SILVA, 2020)` |
| Part of the sentence | `Silva (2020) afirma que…` | same |
| Entity/acronym | `(IBGE, 2011)`, `(Brasil, 2021)`, `(Universidade Federal do Pará, 2023)` | `(IBGE, 2011)`, `(BRASIL, 2021)` |

## Multiple authors and works

- 2 or 3 authors: separated by `;` inside parentheses — `(Silva; Souza; Lima,
  2021)`; in the sentence, `Silva, Souza e Lima (2021)`.
- 4 or more: all authors, **or** first + *et al.* (`(Silva et al., 2021)`),
  consistently across the document. abntex2cite abbreviates from 4 authors by
  default (`abnt-etal-cite=3` = "more than 3"); `abnt-etal-cite=0` lists all.
- Same author, same year: `(Silva, 2020a)`, `(Silva, 2020b)` — BibTeX adds the
  letters automatically when the author-year pair repeats.
- Several works together: `;`-separated, **alphabetical order** —
  `(Alves, 2019; Silva, 2020)`. `\cite{a,b}` prints in the order you write the
  keys, so order the keys alphabetically by author yourself.
- Same surname, different authors: add initials — `(Silva, C., 2020)`,
  `(Silva, O., 2020)`.
- Authorless works: first word of the title in caps + `…` — `(ANTEPROJETO…,
  1987, p. 55)`.

## apud (citação de citação)

Only when the original is genuinely inaccessible:

> (Moraes, 1998 *apud* Silva, 2020, p. 12) — Moraes, cited by Silva.

abntex2cite: `\apud{moraes1998}{silva2020}`; only the consulted work (Silva)
goes in the references. Latin terms (*apud*, *et al.*, *idem*, *ibidem*) are set
in italics under the 2023 edition (abntex2cite: `abnt-etal-text=it`).

## Supressões, interpolações, ênfase

- Omission inside a quote: `[...]`
- Your interpolation/comment: `[texto]`
- Emphasis you added: end the citation with `grifo nosso` —
  `(Silva, 2020, p. 5, grifo nosso)`; emphasis in the original: `grifo do autor`.
- A transcription error in the original: `[sic]`.
- Translation you made: `tradução nossa` inside the parentheses.
- Never add bold/italics inside a literal quote without `grifo nosso`.

## abntex2cite commands (author-date)

| Command | Output |
|---|---|
| `\cite{chave}` | `(Sobrenome, ano)` |
| `\cite[p.~30]{chave}` | `(Sobrenome, ano, p. 30)` |
| `\citeonline{chave}` | `Sobrenome (ano)` — author is part of the sentence |
| `\citeonline[p.~30]{chave}` | `Sobrenome (ano, p. 30)` |
| `\citeauthor{chave}` / `\citeauthoronline{chave}` | author only (caps / mixed) |
| `\citeyear{chave}` | year only |
| `\apud{orig}{citante}` / `\apudonline{orig}{citante}` | citation of citation |
| `\nocite{chave}` | list in references without citing (rarely legitimate) |
| `\citeoption{...}` | activate `.bst` options such as the 2023 citation case — global to the BibTeX run (see `normas-e-versoes.md`) |

```latex
\citeonline{silva2020} afirma que a normalização reduz a redundância.
A redundância é minimizada pela normalização \cite[p.~42]{silva2020}.
Estudos anteriores convergem nesse ponto \cite{alves2019,silva2020}.
```

UniforTeX2 adds `\citeautoronline{key}` (like `\citeonline`, but without the page argument).

## biblatex-abnt commands (author-date)

`\cite{key}` → `(SOBRENOME, ano)`; `\textcite{key}` → `Sobrenome (ano)`;
`\cite[30]{key}` → with page; `\citeauthor`, `\citeyear`; multiple works
`\cites{a}{b}` or `\cite{a,b}`. Compile with **biber**. Use
`\usepackage[style=abnt,backend=biber,...]{biblatex}` plus `\addbibresource{}`.

## Footnotes

Explanatory notes are allowed (size 10, single spacing, numbered continuously).
With the author-date system, do not put bibliographic references in footnotes;
in the numeric system, notas de referência are the mechanism.

## Hard rules

- Every direct quote needs a page (or locator) when the source has one.
- Every citation has a reference entry and every entry is cited at least once.
- Never invent a citation. Missing data → ask, or insert `% TODO: referência`.
- The Conclusão normally brings no new citations or data (an orientador
  convention, not a norm); do not cite the abstract of a paper you did not read
  as if it were the paper.
- `\cite` with several keys: alphabetical order of authors.
