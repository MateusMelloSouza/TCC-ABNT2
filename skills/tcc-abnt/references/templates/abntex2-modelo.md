# Canonical abnTeX2 model (`abntex2-modelo-trabalho-academico`) — profile

The reference implementation of NBR 14724 in LaTeX, maintained by the abnTeX2
team (v1.9.7, 2018). Use it when the institution has no template of its own,
when the user's template is a thin fork of it, or to scaffold a new project.
Location: `doc/latex/abntex2/examples/` in any TeX distribution that ships
abnTeX2 (`kpsewhich --format=doc abntex2-modelo-trabalho-academico.tex`), on
CTAN, and on Overleaf ("abnTeX2 – Modelo Canônico de Trabalho Acadêmico").
Sibling models: `abntex2-modelo-artigo` (NBR 6022), `-projeto-pesquisa`
(NBR 15287), `-relatorio-tecnico` (NBR 10719), `-livro`, `-glossarios`.

**Identify:** `\documentclass[...]{abntex2}` in the main file itself,
`\imprimircapa`, `\imprimirfolhaderosto*`, `\begin{resumo}`, `\textual`,
`\postextual`, `\begin{apendicesenv}`; demo text from `lipsum`; the
`abntex2-modelo-include-comandos.tex` helper.

## Preamble as shipped (what each line is for)

```latex
\documentclass[12pt, openright, twoside, a4paper, english, french, spanish, brazil]{abntex2}
%              ^ oneside for electronic-only; twoside/openright for bound copies
%              chapter=TITLE, section=TITLE, subsection=TITLE... → titles in caps (institutional choice)
\usepackage{lmodern}                  % Latin Modern; institutions asking Times: \usepackage{mathptmx}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{indentfirst}              % ABNT indents the first paragraph
\usepackage{color}
\usepackage{graphicx}
\usepackage{microtype}
\usepackage{lipsum}                   % demo text — REMOVE in a real project
\usepackage[brazilian,hyperpageref]{backref}   % "Citado na página X" in references (optional)
\usepackage[alf]{abntex2cite}         % author-date; [num] numeric

\titulo{...} \autor{...} \local{...} \data{...}
\orientador{...} \coorientador{...}   % omit coorientador line if none
\instituicao{Universidade ... \par Faculdade ... \par Programa ...}
\tipotrabalho{Trabalho de Conclusão de Curso (Graduação)}
\preambulo{<natureza do trabalho: "... apresentado ao ... como requisito parcial para ...">}
```
`hyperref` is loaded by the class; `\hypersetup{pdftitle={\@title}, ...}` in the
model needs `\makeatletter`/`\makeatother`. `\ABNTEXchapterfont` etc. can be
redefined for title fonts. The model's preamble also sets
`\setlength{\parindent}{1.3cm}`, `\setlength{\parskip}{0.2cm}`, an `\@fptop`
tweak for floats at the page top, `\makeindex`, and defines the **quadro**
float — `\newfloat[chapter]{quadro}{loq}{\quadroname}`,
`\newlistof{listofquadros}{loq}{\listofquadrosname}`,
`\setfloatlocations{quadro}{hbtp}` — keep all of that when scaffolding.

## Assembly (order = NBR 14724)

```latex
\begin{document}
\frenchspacing
\imprimircapa
\imprimirfolhaderosto*                 % * prints the natureza block
% ficha catalográfica: \begin{fichacatalografica} ... \end{fichacatalografica} (or \includepdf)
\begin{errata} ... \end{errata}       % optional
% folha de aprovação: \begin{folhadeaprovacao} ... \end{folhadeaprovacao} (assinaturas)
\begin{dedicatoria} ... \end{dedicatoria}
\begin{agradecimentos} ... \end{agradecimentos}
\begin{epigrafe} ... \end{epigrafe}
\begin{resumo} ... \textbf{Palavras-chave}: a; b; c. \end{resumo}   % the shipped model still uses periods (NBR 6028:2003)
\begin{resumo}[Abstract] \begin{otherlanguage*}{english} ... \textbf{Keywords}: a; b; c. \end{otherlanguage*} \end{resumo}
\pdfbookmark[0]{\listfigurename}{lof} \listoffigures* \cleardoublepage
\pdfbookmark[0]{\listtablename}{lot}  \listoftables*  \cleardoublepage
\pdfbookmark[0]{\listofquadrosname}{loq} \listofquadros* \cleardoublepage
\begin{siglas} \item[ABNT] Associação Brasileira de Normas Técnicas \end{siglas}
\begin{simbolos} \item[$\Gamma$] Letra grega Gama \end{simbolos}
\pdfbookmark[0]{\contentsname}{toc} \tableofcontents* \cleardoublepage

\textual
\chapter{Introdução} ...                          % primary sections
\postextual
\bibliography{abntex2-modelo-references}           % REFERÊNCIAS
\begin{apendicesenv} \partapendices \chapter{Título} ... \end{apendicesenv}
\begin{anexosenv}    \partanexos    \chapter{Título} ... \end{anexosenv}
\phantompart \printindex                           % optional índice
\end{document}
```

## Content commands

- Figures: `\begin{figure}[htb] \caption{...}\label{} \includegraphics[]{...} \fonte{...} \end{figure}`
  (caption above the graphic; `\fonte{}` prints "Fonte: …" reduced — the
  model's `\legend{}` prints at 12 pt).
- Tables IBGE-style: `\IBGEtab{\caption{...}\label{}}{\begin{tabular}...\end{tabular}}{\fonte{...}}`
  inside `\begin{table}`; `\fonte{}` and `\nota{}` print the reduced-font source/note.
- Quadros: defined in the model's preamble (see above); `\begin{quadro}` with
  `\caption`, closed-border `tabular`, `\fonte{}`; never load `float`.
- Long quotes: `\begin{citacao} ... \end{citacao}` (`[english]` optional).
- Alíneas: `\begin{alineas} \item ...; \begin{subalineas} ... \end{subalineas} \end{alineas}`
  and `\begin{incisos}` for incisos.
- Citations: `\cite`, `\citeonline`, `\citeauthor`, `\citeyear`, `\apud`.

## Scaffolding a new project from the model

1. Copy `abntex2-modelo-trabalho-academico.tex` → `main.tex`,
   `abntex2-modelo-references.bib` → `referencias.bib` (then empty it of demo
   entries), and drop `abntex2-modelo-include-comandos.tex` unless the user
   wants the demo section.
2. Remove `\usepackage{lipsum}` and every `\lipsum`; replace the demo metadata.
3. Split chapters into files (`elementos-textuais/introducao.tex`, …) and
   `\input` them from `main.tex`; add `% !TEX root = ../main.tex` to each.
4. Add `assets/gitignore-latex` as `.gitignore`, `assets/latexmkrc` only if
   glossaries are used, and run `scripts/init-workflow.py` for the session
   workflow.
5. Compile the full chain once and record the baseline in `STATUS.md`.

## Quirks

- `twoside,openright` inserts blank pages before chapters — expected for print,
  switch to `oneside` for the electronic deposit if the library allows.
- The `backref` package prints "Citado na página X" after each reference; some
  libraries do not want it — drop the package and the three `\renewcommand`s.
- With `chapter=TITLE` the sumário also shows caps; NBR 6027 wants the sumário
  to mirror the text's typography, which the class handles.
- The model's `\hypersetup` colours links (blue); for printing set
  `colorlinks=false` or `hidelinks`.
- No `makeglossaries` needed (siglas/símbolos are plain environments). If you
  add `glossaries`, add the `.latexmkrc` rule.
