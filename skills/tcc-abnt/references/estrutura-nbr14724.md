# Structure of the academic work (NBR 14724) with abnTeX2

Order of elements and the abnTeX2 commands that produce them.
**O = obrigatório, Op = opcional.** Institutional templates wrap these commands
in their own (`\imprimirresumo{file}`, `\imprimirlistadeilustracoes`, …); use
the template's wrapper when one exists (see `templates/`).

## Elementos pré-textuais

| Element | Status | abnTeX2 command / note |
|---|---|---|
| Capa | O | `\imprimircapa` |
| Lombada | Op | not provided by abnTeX2 (printed/bound copies only; the library or printer usually handles it) |
| Folha de rosto | O | `\imprimirfolhaderosto` or `\imprimirfolhaderosto*` (adds the natureza block) |
| Ficha catalográfica | O in the final version | verso of the folha de rosto (print) or right after it (electronic); the **library** produces it, usually as a PDF — include with `\includepdf` (package `pdfpages`) or type it in `\begin{fichacatalografica}` |
| Errata | Op | after the folha de rosto; `\begin{errata}` (class environment) |
| Folha de aprovação | O | banca members and date; often replaced by the signed, scanned PDF in the final version |
| Dedicatória | Op | `\begin{dedicatoria}` |
| Agradecimentos | Op | `\begin{agradecimentos}` |
| Epígrafe | Op | `\begin{epigrafe}` — the pre-textual one need not follow NBR 10520 |
| Resumo (pt-BR) | O | `\begin{resumo} … \end{resumo}` + keywords (NBR 6028:2021) |
| Abstract | O | `\begin{resumo}[Abstract]` + `\begin{otherlanguage*}{english}` |
| Lista de ilustrações / figuras | Op | `\listoffigures*`; one list per type when there are several (figuras, quadros, gráficos) |
| Lista de tabelas | Op | `\listoftables*` |
| Lista de abreviaturas e siglas | Op | `siglas` environment or `glossaries` — **only siglas used in the text**, alphabetical |
| Lista de símbolos | Op | `simbolos` environment — **in order of first appearance** in the text |
| Sumário | O | `\tableofcontents*` (starred: the sumário does not list itself) |

The **natureza do trabalho** block on the folha de rosto ("Trabalho de
Conclusão de Curso apresentado ao Curso de … da … como requisito parcial para
obtenção do título de …") is set with `\preambulo{...}` in the canonical model
and rendered at 12 pt, single-spaced, from the middle of the page to the right
margin.

Pre-textual pages are counted but not numbered; the ficha catalográfica on the
verso of the folha de rosto is neither counted nor numbered (libraries differ
on the electronic version — ask).

## Elementos textuais

The body is organised in **seções** with progressive numbering (NBR 6024; the
2024 edition of NBR 14724 no longer uses the word "capítulo"). In abnTeX2 a
primary section is `\chapter` (new page, number + title in caps according to
the class options) and the counter starts here (`\textual`). The conventional
shape:

1. **Introdução** — context, problema de pesquisa, justificativa, objetivo
   geral and objetivos específicos, and how the work is organised. No
   literature review here.
2. **Desenvolvimento** — one or more primary sections: fundamentação teórica /
   referencial teórico, trabalhos relacionados, metodologia (materiais e
   métodos), resultados, discussão. The split depends on the field and the
   orientador.
3. **Conclusão / Considerações finais** — answers each objective, states the
   contribution and limitations, proposes future work. **No new citations,
   data or figures.**

## Elementos pós-textuais

| Element | Status | Note |
|---|---|---|
| Referências | O | `\bibliography{file}` (abntex2cite) or `\printbibliography` (biblatex); only works actually cited; `\postextual` before it |
| Glossário | Op | alphabetical; abnTeX2 has none built in — templates use `glossaries` |
| Apêndice(s) | Op | `\begin{apendicesenv}` + `\chapter{...}` — material **produced by the author**; lettered `APÊNDICE A – Título` |
| Quadros (float + list) | — | the canonical model defines the `quadro` float and `\listofquadros*` (memoir `\newfloat`); see `formatacao.md` |
| Anexo(s) | Op | `\begin{anexosenv}` + `\chapter{...}` — material **not produced by the author**; references cited only here stay with the anexo (2024) |
| Índice | Op | índice remissivo, `\printindex` |

Apêndice = made by you (questionário, código, deduções); anexo = third-party
material you attach (lei, norma, formulário). Separator pages ("APÊNDICES",
"ANEXOS") are optional and produced by `\partapendices` / `\partanexos`.

## Minimal abnTeX2 preamble (reference, generic placeholders)

```latex
\documentclass[
  12pt, oneside, a4paper,        % twoside,openright for printed/bound copies
  chapter=TITLE, section=TITLE,  % caps on primary/secondary titles (institutional choice)
  english, brazil                % last language = document language; the default
                                 % sumario=abnt-6027-2012 makes the sumário mirror the titles
]{abntex2}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}             % or \usepackage{mathptmx} for Times (many institutions)
\usepackage{lastpage}
\usepackage{indentfirst}         % first paragraph of a section is indented (ABNT)
\usepackage{graphicx}
\usepackage{microtype}
\usepackage[brazilian,hyperpageref]{backref} % optional: "Citado na página X"
\usepackage[alf]{abntex2cite}    % author-date; [num] for numeric

\titulo{Título do trabalho: subtítulo}
\autor{Nome Completo do Autor}
\local{Cidade}
\data{2026}
\orientador{Prof. Dr. Nome do Orientador}
\coorientador{Prof. Me. Nome do Coorientador}   % omit if none
\instituicao{Nome da Universidade -- SIGLA}
\tipotrabalho{Trabalho de Conclusão de Curso (Graduação)}
\preambulo{\imprimirtipotrabalho{} apresentado ao Curso de Nome do Curso da
  \imprimirinstituicao{} como requisito parcial para obtenção do título de
  Bacharel em Nome do Curso.}
```

(`\imprimirtipotrabalho`, `\imprimirinstituicao`, `\imprimirautor`,
`\imprimirtitulo`, `\imprimirorientador`, `\imprimirlocal`, `\imprimirdata` are
the getters abnTeX2 defines for the metadata above; there is no `\curso` macro
in the class — institutional templates add their own, e.g. UniforTeX2's
`\graduacaoem`.)

The canonical model file is `abntex2-modelo-trabalho-academico.tex` (ships in
`doc/latex/abntex2/examples/` of any TeX distribution with abnTeX2 and on
Overleaf as "abnTeX2 – Modelo Canônico de Trabalho Acadêmico"). When
scaffolding, copy it and strip the demo text; do not write a preamble from
memory.

## Regions and pagination behaviour

`\pretextual` (default after `\begin{document}`), `\textual` and `\postextual`
control numbering: keep every element inside the right region. A common defect
is content placed after `\postextual` that should be textual (or vice versa),
which shifts page numbers and the sumário.

## Common structural defects (found in real audits)

- Template demo text left in resumo/abstract/agradecimentos/errata/glossário/
  siglas (a "neonatal mortality" siglas list in a computing thesis prints
  happily).
- Lists that are enabled but empty (lista de algoritmos with no algorithm) —
  disable the list rather than print an empty page.
- `\dataaprovacao`, banca members, curso and habilitação still with the
  template's placeholder values.
- Apêndices with `\lipsum`, or `apendices/` and `anexos/` demo files still
  `\input`ed.
- Figures never called out in the text; floats printed 10+ pages after their
  call-out because one oversized float blocked the queue (see `formatacao.md`).
