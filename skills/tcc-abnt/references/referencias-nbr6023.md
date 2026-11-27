# Referências (NBR 6023:2018) and `.bib` hygiene

You write `.bib` entries; the style (`abntex2-alf.bst` / `abntex2-num.bst`, or
`biblatex-abnt`) formats them. You still must know the target format to enter
data correctly, and you must know the handful of BibTeX behaviours that silently
produce wrong output.

## List presentation

- Title **REFERÊNCIAS**, centered, unnumbered (the class does it).
- **Left-aligned** (not justified), **single spacing within an entry**, **one
  blank line between entries**, in the body font size (12 pt — only quotes,
  footnotes, captions/sources, page numbers and the ficha are reduced).
  abntex2cite: option `bibleftalign` (default) or `bibjustif`. The canonical
  model already prints the blank line; some templates lose it (UniforTeX2 does)
  and get it back with `\AfterTheBibliography{\setlength{\itemsep}{\onelineskip}}`
  — check the rendered list before adding it, or the gap doubles.
- Author-date system → alphabetical by author surname; numeric → citation order.
- Author surname in CAPS; given names spelled out or abbreviated, consistently
  (`abnt-full-initials=no|yes`).
- Only works actually cited. Bibliography "consulted but not cited" is a
  separate optional list, not part of Referências.

## Patterns by source type (2018)

**Livro:**
```
SOBRENOME, Nome. Título: subtítulo. Edição. Local: Editora, ano.
```
`MACHADO, Felipe Nery Rodrigues. Banco de dados: projeto e implementação. 3. ed. São Paulo: Érica, 2014.`

**Capítulo de livro:**
```
SOBRENOME, Nome. Título do capítulo. In: SOBRENOME, Nome (org.). Título do livro. Local: Editora, ano. p. x-y.
```

**Artigo de periódico:**
```
SOBRENOME, Nome. Título do artigo. Título do Periódico, Local, v. X, n. Y, p. x-y, mês ano. DOI: ...
```

**Trabalho acadêmico (TCC, dissertação, tese):**
```
SOBRENOME, Nome. Título. Ano. Nº f. Tipo (Grau) – Instituição, Local, ano.
```
`SILVA, Ana. Detecção de anomalias em séries temporais. 2025. 84 f. Trabalho de Conclusão de Curso (Bacharelado em Ciência da Computação) – Universidade Exemplo, Cidade, 2025.`

**Trabalho em anais de evento:**
```
SOBRENOME, Nome. Título do trabalho. In: NOME DO EVENTO, n., ano, Local. Anais [...]. Local: Editora, ano. p. x-y.
```
For IEEE/ACM proceedings the "Local: Editora" is the publisher's headquarters
(`Piscataway: IEEE`, `New York: ACM`), which also resolves virtual events —
avoid `[S. l.: s. n.]` when the publisher is known.

**Documento online / site:**
```
AUTOR (ou ENTIDADE). Título. Local, ano. Disponível em: URL. Acesso em: 5 jun. 2026.
```
No angle brackets around the URL (2018). Months abbreviated to three letters +
period — `jan.`, `fev.`, `mar.`, `abr.`, `maio`, `jun.`, `jul.`, `ago.`, `set.`,
`out.`, `nov.`, `dez.` (`maio` is never abbreviated).

**Legislação:**
```
BRASIL. Lei nº 13.709, de 14 de agosto de 2018. Lei Geral de Proteção de Dados Pessoais (LGPD). Diário Oficial da União: seção 1, Brasília, DF, ano 155, n. 157, p. 59, 15 ago. 2018.
```
Jurisdiction (or the responsible body) is the author, in caps; the DOU date is
the publication date, not the signing date.

**Norma técnica:**
```
ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS. ABNT NBR 14724: informação e documentação: trabalhos acadêmicos: apresentação. Rio de Janeiro: ABNT, 2024.
```

**Software / dataset / repositório:** treat as documento online with the
version and access date; cite the version you used.

## Writing the `.bib` (BibTeX + abntex2cite)

```bibtex
@book{machado2014,
  author    = {Machado, Felipe Nery Rodrigues},
  title     = {Banco de dados: projeto e implementa{\c{c}}{\~a}o},
  edition   = {3},
  address   = {S{\~a}o Paulo},
  publisher = {{\'E}rica},
  year      = {2014}
}

@article{silva2020,
  author  = {Silva, Jo{\~a}o and Souza, Maria},
  title   = {Normaliza{\c{c}}{\~a}o em bancos relacionais},
  journal = {Revista Brasileira de Computa{\c{c}}{\~a}o},
  volume  = {12},
  number  = {2},
  pages   = {30--45},
  month   = {jun.},
  year    = {2020},
  doi     = {10.1000/exemplo}
}

% Evento: the .bst has native fields for the event. This renders
% "In: EUROPEAN CONFERENCE ON COMPUTER VISION, 15., 2018, Munich. Proceedings [...]. Cham: Springer, 2018. p. 472-489."
@inproceedings{beery2018terra,
  author              = {Beery, Sara and {\relax Van Horn}, Grant and Perona, Pietro},
  title               = {Recognition in {Terra Incognita}},
  organization        = {European Conference on Computer Vision},
  conference-number   = {15},
  conference-year     = {2018},
  conference-location = {Munich},
  booktitle           = {Proceedings [...]},   % or "Anais [...]"
  address             = {Cham},
  publisher           = {Springer},
  year                = {2018},
  pages               = {472--489}
}

% Norma técnica / entity author: {\relax ...} keeps the whole name as one surname,
% prints it in CAPS in the list and in the citation case the document uses.
@misc{abnt14724,
  author    = {{\relax Associa{\c{c}}{\~a}o Brasileira de Normas T{\'e}cnicas}},
  title     = {{ABNT NBR 14724}: informa{\c{c}}{\~a}o e documenta{\c{c}}{\~a}o: trabalhos acad{\^e}micos: apresenta{\c{c}}{\~a}o},
  address   = {Rio de Janeiro},
  publisher = {ABNT},
  year      = {2024}
}

@misc{ibge2022censo,
  author        = {{IBGE}},
  title         = {Censo Demogr{\'a}fico 2022: resultados},
  year          = {2023},
  url           = {https://www.ibge.gov.br/},
  urlaccessdate = {5 jun. 2026}
}

% Legislação: the documented abnTeX2 form is @article + organization + journal/section.
% Renders "BRASIL. Lei nº 13.709, de 14 de agosto de 2018. Lei Geral de Proteção de Dados
% Pessoais (LGPD). Diário Oficial da União: seção 1, Brasília, DF, v. 155, n. 157, p. 59, 15 ago. 2018."
@article{brasil2018lgpd,
  organization = {Brasil},
  title        = {Lei n{\textordmasculine} 13.709, de 14 de agosto de 2018. {Lei Geral de Prote{\c{c}}{\~a}o de Dados Pessoais (LGPD)}},
  journal      = {Di{\'a}rio Oficial da Uni{\~a}o},
  section      = {se{\c{c}}{\~a}o 1},
  address      = {Bras{\'i}lia, DF},
  volume       = {155},
  number       = {157},
  pages        = {59},
  month        = {15 ago.},
  year         = {2018}
}
```

### BibTeX behaviours that bite (all verified with abntex2-alf.bst)

- **Accents in author/organization fields must be TeX escapes**
  (`Ara{\'u}jo`, `Gon{\c{c}}alves`, `T{\'e}cnicas`). The `.bst` uppercases
  surnames and entity names with BibTeX's ASCII `change.case$`: typed as UTF-8
  they come out as `ARAúJO`, `ASSOCIAçãO`. Titles and other fields may stay
  UTF-8 when the document is `inputenc`/UTF-8.
- **Compound surnames** (`Van Horn`, `Dadrass Javan`, `Raja Abdullah`,
  `Castelo Branco`): BibTeX takes only the last token as the surname, so
  `Grant Van Horn` prints `HORN, G. V.` and cites as `(Beery; Horn; Perona,
  2018)`. Group with `{\relax Van Horn}, Grant` — braces alone (`{Van Horn}`)
  keep the group but do not uppercase; `{\relax ...}` groups **and** uppercases.
- **Portuguese particles** (`de`, `da`, `dos`, `e`) go **before** the surname as
  BibTeX's *von* part: `de Freitas, Ernani Cesar` or `Ernani Cesar de Freitas`
  → `FREITAS, E. C. de` (correct). The tempting `Freitas, Ernani Cesar de`
  abbreviates the particle: `FREITAS, E. C. d.` (wrong with the default
  `abnt-full-initials=no`).
- **Entity/corporate authors:** `{{\relax Brasil}}`, `{{\relax Associa{\c{c}}{\~a}o
  Brasileira de Normas T{\'e}cnicas}}` — CAPS in the list and the document's
  citation case in the text (`(Brasil, 2018)` under the 2023 style). Plain
  double braces `{{Brasil}}` print **as typed in the list too** (`Brasil.`,
  violating NBR 6023); `{{BRASIL}}` is fine only for documents using the 2002
  all-caps citations. `organization = {Brasil}` gives CAPS in both places
  regardless of style — use it for legislation when the 2002 case is wanted.
  Acronyms (`{{IBGE}}`) are caps anyway.
- **Titles are lowercased after the first word** by the style: protect proper
  nouns, acronyms and a second sentence with braces — `{Terra Incognita}`,
  `{GPU}`, `{Python}`, `{Lei Geral de ...}`.
- **`edition = {3}`** renders as `3. ed.`; write the number only.
- **`url` + `urlaccessdate`** produce `Disponível em: … Acesso em: …`; the
  access date is printed as typed, so write the month with its period
  (`27 abr. 2015`; `maio` unabbreviated). Do not repeat "Disponível em" in `note`.
- **`[S.l.]`** (no space) is hard-coded in the `.bst` for missing places; the
  2018 form is `[S. l.]` — give the real `address` whenever it is knowable, or
  write `address = {[S. l.]}` explicitly.
- **Duplicate keys** are case-insensitive for BibTeX (`Silva2020` = `silva2020`
  → `Repeated entry`); near-duplicate entries (`silva2020` vs `silva2020norm`)
  inflate the list — keep the cited key, delete the other.
- **`@` inside a `%` comment line** still starts an entry for BibTeX (it does
  not know `%` comments): comment with `@Comment{...}` or keep `@` out of notes.
- **Template demo entries** (`knuth`, `lamport`, `tresautores`, `NBR...`
  samples) must not survive in the final `.bib`.
- **Keys** never print; renaming them for cosmetics is pure risk — only before
  writing, never before a deposit.

## BibTeX vs biber

- `abntex2cite` + `.bst` → run **bibtex** (`bibtex main`).
- `biblatex-abnt` (`\usepackage[style=abnt]{biblatex}`) → run **biber**.

Never mix them. Check the preamble before adding references and use the
matching compile chain (`compilacao-e-erros.md`).

## Verification before finalizing

`scripts/audit-tex.py` automates the first check (missing/uncited/duplicate/
placeholder keys) and flags multi-key citations out of author order; the rest
is read in the compiled PDF.

- Every `\cite` key exists in the `.bib`; every `.bib` entry is cited; no
  duplicate keys; no placeholder entries (`20XX`, `TODO`, `?`).
- Author-date list alphabetical; numeric list in citation order.
- Online sources have `Acesso em:`; DOIs correct (resolve them once).
- Compound surnames, particles, accents and entity authors print correctly in
  the compiled list and in citations (`{\relax Van Horn}`, `de Freitas`,
  `Ara{\'u}jo`, `{{\relax Brasil}}`) — read the PDF's REFERÊNCIAS page, do not
  trust the `.bib` alone.
- Each entry's data verified against the source (title, year, venue, pages,
  volume/number); the year in the key is not evidence.
- No `[S. l.: s. n.]` where the place/publisher is knowable; no `<URL>`
  brackets if the institution follows the 2018 edition.
