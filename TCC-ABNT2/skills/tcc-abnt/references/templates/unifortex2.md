# UniforTeX2 (Universidade de Fortaleza) — template profile

UniforTeX2 is a UNIFOR customisation of abnTeX2 by Bruno Lopes (LPPL 1.3
header; distributed on Overleaf as "UNIFOR - Template Latex", CC BY 4.0). It
targets TCC de graduação, TCC de especialização, dissertação and tese; its
README says it was written mainly for the computing courses and is adaptable
to the other UNIFOR courses, and that it is an unofficial product ("produto
extra-oficial, não oficialmente vinculado à Unifor") — so the **library's
manual and the orientador still decide** on norm editions.

Do not confuse it with **unifor-abnTeX2** (Erneson Oliveira, PPGIA), a lighter
customisation with `main.tex` + `template/` — profile that one with
`templates/README.md`.

**Identify:** `lib/unifortex2.sty`, `\input{lib/preambulo}` in `main.tex`,
`\trabalhoacademico{...}`, `\UNIFORfig`/`\UNIFORtab`/`\UNIFORqua`,
`\Caption{}`/`\Fonte{}`, `\imprimirlistadeilustracoes`.

**Citation stack:** `abntex2cite` with
`[alf, abnt-emphasize=bf, bibleftalign, recuo=0cm, abnt-etal-cite=3, abnt-etal-list=0, abnt-etal-text=it]`
→ author-date, BibTeX, *et al.* from 4 authors in citations, all authors in
the list, *et al.* in italics, bold emphasis in the list. Times via `mathptmx`.

## File layout

```
main.tex                      % settings + \begin{document} assembly only
lib/preambulo.tex             % \documentclass[abntex2] + every \usepackage (editable but keep minimal)
lib/unifortex2.sty            % UNIFOR macros — NEVER EDIT (overrides go in main.tex)
lib/Imagem1.png, logo-*.png   % logos used by the cover macros
elementos-pre-textuais/       % resumo.tex abstract.tex agradecimentos.tex dedicatoria.tex epigrafe.tex
                              %   errata.tex lista-de-abreviaturas-e-siglas.tex lista-de-simbolos.tex
                              %   ficha-catalografica.pdf folha-aprovacao.pdf
elementos-textuais/           % introducao.tex fundamentacao-teorica.tex trabalhos-relacionados.tex
                              %   metodologia.tex resultados.tex conclusao.tex
elementos-pos-textuais/       % referencias.bib glossario.tex apendices/ anexos/
figuras/                      % images (subfolders per chapter are fine)
```

`unifortex2.sty` `\input`s `elementos-pos-textuais/glossario` and
`elementos-pre-textuais/lista-de-abreviaturas-e-siglas` **at load time**: both
files must exist (they hold `\newglossaryentry`/`\newacronym` definitions), even
if empty of real entries.

## `main.tex` settings (every macro, what it does)

```latex
\input{lib/preambulo}

% ---- work type: exactly ONE uncommented; anything else falls back to dissertacao ----
\trabalhoacademico{tccgraduacao}      % tccgraduacao | tccespecializacao | dissertacao | tese
% The five boolean setters below call \ifthenelse with a MISSING else-branch inside the
% .sty, so they swallow the next token as that branch. Always terminate them with an
% empty group {} (see quirk 1) — otherwise the following command is eaten and its
% argument is typeset on the cover.
% \ehqualificacao{sim}{}              % qualificação: suppresses dedicatória, errata,
                                      %   agradecimentos, epígrafe and ficha, and swaps the
                                      %   natureza text (default nao)
\removerbordasdohyperlink{sim}{}      % no coloured boxes around links (sim/nao)
\cordohyperlink{nao}{}                % sim = blue link text

% ---- institution ----
\ies{Universidade de Fortaleza}
\iessigla{UNIFOR}
\centro{Centro de Ciências Tecnológicas}          % the centro/faculdade of the course

% ---- graduação ----
\graduacaoem{Nome do Curso}                       % e.g. Engenharia de Computação
\habilitacao{bacharel}                            % bacharel | licenciada (as printed in the natureza block)

% ---- especialização ----
\especializacaoem{Nome da Especialização}

% ---- mestrado ----
\programamestrado{Programa de Pós-Graduação em ...}
\nomedomestrado{Mestrado Acadêmico em ...}
\mestreem{Área}
\areadeconcentracaomestrado{Área de concentração}

% ---- doutorado ----
\programadoutorado{...} \nomedodoutorado{...} \doutorem{...} \areadeconcentracaodoutorado{...}

% ---- the work ----
\autor{Nome Completo}
\titulo{Título: subtítulo}
\data{2026}
\local{Fortaleza -- Ceará}
\dataaprovacao{dd de mês de aaaa}                 % printed on the folha de aprovação

% ---- orientador / coorientador ----
\orientador{Prof. Dr. Nome}
\orientadories{Universidade de Fortaleza - UNIFOR}
\orientadorcentro{Centro de Ciências Tecnológicas - CCT}
\orientadorfeminino{nao}{}                        % sim → "Orientadora" ({} terminator, quirk 1)
\coorientador{}                                   % empty = no coorientador line
\coorientadories{} \coorientadorcentro{} \coorientadorfeminino{nao}{}

% ---- banca (dois..seis; empty name = member removed from the folha) ----
\membrodabancadois{Prof. Me. Nome}
\membrodabancadoiscentro{Centro ... - SIGLA}
\membrodabancadoisies{Universidade ... - SIGLA}
\membrodabancatres{...} \membrodabancatrescentro{...} \membrodabancatresies{...}
\membrodabancaquatro{} \membrodabancaquatrocentro{} \membrodabancaquatroies{}
\membrodabancacinco{}  ...   \membrodabancaseis{} ...

\begin{document}
  \imprimircapa
  \imprimirfolhaderosto{}
  \imprimirfichacatalografica{elementos-pre-textuais/ficha-catalografica}  % includes page 1 of the PDF
  % \imprimirerrata{elementos-pre-textuais/errata}
  % \includepdf{elementos-pre-textuais/folha-aprovacao.pdf}   % final version: signed scan …
  \imprimirfolhadeaprovacao                                   % … replaces the generated sheet
  % \imprimirdedicatoria{elementos-pre-textuais/dedicatoria}
  \imprimiragradecimentos{elementos-pre-textuais/agradecimentos}
  % \imprimirepigrafe{elementos-pre-textuais/epigrafe}         % needs \epigrafee / \autordaepigrafe
  \imprimirresumo{elementos-pre-textuais/resumo}
  \imprimirabstract{elementos-pre-textuais/abstract}
  \glsaddall                     % prints ALL defined siglas — see quirks
  \imprimirlistadeilustracoes    % figures
  \imprimirlistadetabelas
  \imprimirlistadequadros
  % \imprimirlistadealgoritmos   % only if the work has algorithms
  % \imprimirlistadecodigosfonte % only if it has listings
  \imprimirlistadeabreviaturasesiglas
  \imprimirlistadesimbolos{elementos-pre-textuais/lista-de-simbolos}
  \imprimirsumario

  \textual
  \input{elementos-textuais/introducao}
  ...
  \input{elementos-textuais/conclusao}

  \bibliography{elementos-pos-textuais/referencias}   % \imprimirreferencias{...} = same + \postextual
  \imprimirglossario
  \imprimirapendices
    \input{elementos-pos-textuais/apendices/apendice-a}
  \imprimiranexos
    \input{elementos-pos-textuais/anexos/anexo-a}
  \imprimirindice
\end{document}
```

Traps in the shipped `main.tex`:

- The comment offers `\trabalhoacademico{tccgraduacaoPDF}` "for a PDF folha de
  aprovação", but the `.sty` only recognises `tccgraduacao`,
  `tccespecializacao`, `dissertacao` and `tese` — **any other value silently
  selects `dissertacao`** (cover and folha de rosto of a master's). For a
  scanned approval sheet keep `tccgraduacao` and swap
  `\imprimirfolhadeaprovacao` for `\includepdf{...folha-aprovacao.pdf}`.
- Demo values survive easily: `\dataaprovacao{01 de Janeiro de 2017}`,
  `\especializacaoem{Alfabetização de Crianças}`, doutorado fields, banca
  placeholders, `\glsaddall` with a siglas file from another discipline,
  `apendices/lorem-ipsum.tex`, `anexos/` demo files. Audit them.
- `\imprimirfichacatalografica{}` includes **page 1 of a PDF** — the ficha is
  produced by the UNIFOR library from the final page count; the template's
  sample PDF prints instructions in red until replaced. Request it last.

## Content commands (use these, not raw abnTeX2 floats)

Captions are set by the template: centered, **bold**, 1.5 spacing
(`\Caption`), source in reduced font (`\Fonte`), optional `\Nota`.

**Figure**
```latex
\begin{figure}[htb]
  \centering
  \UNIFORfig{
    \Caption{\label{fig:rotulo} Legenda da figura}
  }{
    \includegraphics[width=0.98\textwidth]{figuras/pasta/arquivo}
  }{
    \Fonte{Elaborada pelo autor (2026)}      % or \Fonte{Silva (2020, p. 3)}
    % \Nota{Observação metodológica.}
  }
\end{figure}
```
`\UNIFORfig`, `\UNIFORtab` and `\UNIFORqua` are all aliases of abnTeX2's
`\IBGEtab{caption}{content}{source}`: the frame is sized to the content, so a
graphic at `width=\textwidth` overflows the text block by ~5 pt (an
`Overfull \hbox` per figure) — use `0.98\textwidth`.

**Table (tabela — numeric, open sides, booktabs)**
```latex
\begin{table}[htb]
  \centering
  \Caption{\label{tab:rotulo} Legenda da tabela}
  \UNIFORtab{}{
    \begin{tabular}{@{}l c p{0.45\textwidth}@{}}
      \toprule
      Coluna & Valor & Descrição \\ \midrule
      A & 0{,}907 & texto que quebra sozinho na coluna p{} \\
      \bottomrule
    \end{tabular}
  }{
    \Fonte{Dados da pesquisa (2026)}
  }
\end{table}
```

**Quadro (textual — closed borders, own float and list)**
```latex
\begin{quadro}[htb]
  \centering
  \Caption{\label{qua:rotulo} Legenda do quadro}
  \UNIFORqua{}{
    \begin{tabular}{|l|p{0.6\textwidth}|}
      \hline Item & Descrição \\ \hline
      A & texto \\ \hline
    \end{tabular}
  }{
    \Fonte{Elaborado pelo autor (2026)}
  }
\end{quadro}
```
Reference as `Quadro~\ref{qua:rotulo}`; enable `\imprimirlistadequadros`.

**Algorithm** (`algorithm2e`, Portuguese keywords loaded by the template:
`\Entrada`, `\Saida`, `\Inicio`, `\Enqto`, `\Para`, `\Se`…):
```latex
\begin{algorithm}[htb]
  \SetSpacedAlgorithm
  \caption{\label{alg:rotulo} Nome do algoritmo}
  \Entrada{...} \Saida{...}
  \Inicio{ passo\; \Enqto{condição}{ passo\; } }
\end{algorithm}
```

**Alíneas:** `\begin{alineas} \item ...; \begin{subalineas} \item ... \end{subalineas} \end{alineas}`;
the template adds `alineascomponto` (items end with a period) and
`alineascomnumero` (numbered) variants.

**Table body size:** `\UNIFORtab`/`\UNIFORqua` set the content in the reduced
font (`\IBGEtabfontsize` = footnotesize); do not add another `\small`.

**Sectioning:** `\chapter{}` → `\section{}` → `\subsection{}` →
`\subsubsection{}` → `\subsubsubsection{}`; always `\label{cap:...}` /
`\label{sec:...}`. Chapter and section titles print in caps
(`chapter=TITLE, section=TITLE`), subsections bold, sub-subsections normal,
fifth level italic — do not fight it in the files.

**Citations:** `\cite`, `\citeonline`, `\apud`; the template alias
`\citeautoronline{key}` prints `Autor (ano)` but takes **no page argument** —
use `\citeonline[p.~30]{key}` when a page is needed.

**Siglas** (`elementos-pre-textuais/lista-de-abreviaturas-e-siglas.tex`):
`\newacronym{TCC}{TCC}{Trabalho de Conclusão de Curso}`; the list is printed
by `\printglossary[type=\acronymtype]` — needs **`makeglossaries`**.

**Símbolos** (`lista-de-simbolos.tex`): `\begin{simbolos} \item[$\sigma$]
Desvio-padrão \end{simbolos}` — order of first appearance in the text; braces
around items containing brackets: `\item[{$x[n]$}]`.

**Resumo/abstract files:** plain paragraph then `\palavraschave{...}` /
`\keywords{...}` (bold label with the colon inside). The template's example
separates keywords with periods (NBR 6028:2003); the 2021 edition uses
semicolons — ask the library, keep both languages consistent.

**Appendices/annexes:** `\imprimirapendices` prints the separator page and
switches numbering; each appendix file starts with `\chapter{Título}` (the
template prints `APÊNDICE A – TÍTULO`). `\apendice{Título}` / `\anexo{Título}`
are aliases.

## Compiling

`pdflatex → bibtex → makeglossaries → pdflatex → pdflatex`, or
`latexmk -pdf main.tex` with the project's `.latexmkrc` (glossaries rule —
`assets/latexmkrc`). Overleaf: pdfLaTeX, main document `main.tex`. VS Code:
every `.tex` starts with `% !TEX root = ../main.tex` and the recipe targets
`main.tex` (`assets/vscode-settings.json`). Windows: `assets/compilar.bat`.
Sandbox: `scripts/setup-sandbox-latex.sh` then `scripts/compile-check.sh`
(needs `abntex2`, `babel-portuges`, `algorithm2e`, `algorithms`; `mathptmx`
and `glossaries` are in any standard TeX Live).

## Known quirks and the sanctioned fixes (never edit `unifortex2.sty`)

All overrides go in `main.tex` **after** `\input{lib/preambulo}` so the file
stays interchangeable with the Overleaf copy.

1. **`! LaTeX Error: Missing \begin{document}.` right after the settings block —
   plus a stray word (`nao`, `sim`) printed at the top of the capa.** For years
   attributed to the `quadro` `\newfloat` and treated as "benign"; it is not.
   The five boolean setters in the `.sty` (`\ehqualificacao`,
   `\removerbordasdohyperlink`, `\cordohyperlink`, `\orientadorfeminino`,
   `\coorientadorfeminino`) call `\ifthenelse{test}{then}` **without the else
   branch**, so the next token in `main.tex` becomes that branch: with
   `\removerbordasdohyperlink{sim}` followed by `\cordohyperlink{nao}`, the
   macro `\cordohyperlink` is swallowed and discarded and `{nao}` is typeset in
   the preamble — hence the error and the word on the cover. When the swallowed
   token is `\coorientador{...}` after `\orientadorfeminino{sim}`, the
   coorientador silently disappears from the folha de aprovação. **Fix (in
   `main.tex`):** give each setter an explicit empty else-group —
   `\removerbordasdohyperlink{sim}{}`, `\cordohyperlink{nao}{}`,
   `\ehqualificacao{sim}{}`, `\orientadorfeminino{nao}{}`,
   `\coorientadorfeminino{nao}{}` — verified: zero errors and a clean cover. The
   canonical model runs the identical `\newfloat[chapter]{quadro}{loq}{...}`
   with no error, so nothing about `quadro` needs filtering. A related but
   different failure is loading `\usepackage{float}`: it redefines `\newfloat`,
   prints `apter]quadroloqQuadro` on page 1 and makes `quadro` undefined — keep
   `float` out of the preamble.
2. **`glossaries` ≥ 4.50 (TeX Live 2023+, Overleaf) removed `\glossarystyle`
   and `\glossaryentryfield`**,
   which `\imprimirglossario` and the `glossario-unifor` style use. Symptom:
   `Undefined control sequence` at `\imprimirglossario`, the literal text
   `glossario-unifor` printed at the end of REFERÊNCIAS, and the glossary in a
   degraded default style. A one-line `\providecommand` is **not** enough
   (`\glossaryentryfield` then fails). Port the style in `main.tex`:
   ```latex
   \providecommand{\glossarystyle}[1]{\setglossarystyle{#1}}
   \renewglossarystyle{glossario-unifor}{%
     \renewenvironment{theglossary}%
       {\vspace{-0.3cm}\begin{description}[leftmargin=0cm]\itemsep -1pt}{\end{description}}%
     \renewcommand*{\glossaryheader}{}%
     \renewcommand*{\glsgroupheading}[1]{\vspace{0cm}\item[{\glsgetgrouptitle{##1}}] \vspace{\onelineskip}}%
     \renewcommand*{\glsgroupskip}{}%
     \renewcommand*{\glossentry}[2]{\item[\glstarget{##1}{\glossentryname{##1}}:] \glossentrydesc{##1}.}%
   }
   ```
3. **PDF bookmarks of "APÊNDICES"/"ANEXOS" pointing at the previous element**:
   `\imprimirpaginaapendices` and `\imprimirpaginaanexo` call
   `\addcontentsline` without `\phantomsection`. Override both in `main.tex`:
   ```latex
   \renewcommand{\imprimirpaginaapendices}{%
     \newpage\phantomsection
     \addcontentsline{toc}{chapter}{AP\^ENDICES}%
     \begin{vplace}[0.7]\centering\textbf{AP\^ENDICES}\end{vplace}%
     \clearpage}
   \renewcommand{\imprimirpaginaanexo}{%
     \newpage\phantomsection
     \addcontentsline{toc}{chapter}{ANEXOS}%
     \begin{vplace}[0.7]\centering\textbf{ANEXOS}\end{vplace}%
     \clearpage}
   ```
4. **Blank line between references (NBR 6023)** is lost by the template:
   ```latex
   \AfterTheBibliography{\setlength{\itemsep}{\onelineskip}\setlength{\parsep}{0pt}}
   ```
5. **`\glsaddall`** prints every acronym ever defined in the siglas file —
   including the template's demo set (TMI, SUS, SINASC… from a health-science
   sample). NBR 14724 wants only siglas used in the text: curate the file, or
   remove `\glsaddall` and mark uses with `\gls{}`.
6. **Blank page inside the pre-textual block**: `\glsaddall` placed after the
   lists emits whatsits that expel an empty page — keep it before
   `\imprimirlistadeilustracoes` (as in the assembly above).
7. **`LISTA DE ILUSTRAÇÕES` title** is hard-wired for the figure list. With
   quadros in their own list the "ilustrações" list contains only figures; the
   norm-coherent title is "Lista de figuras". The name is set inside
   `\addto\captionsbrazil`, which babel re-executes at `\begin{document}`, so a
   plain `\renewcommand` in the preamble does nothing; use
   `\addto\captionsbrazil{\renewcommand{\listfigurename}{Lista de figuras}}`
   (verified). The template's title is an institutional choice — ask before
   changing.
8. **NBR 10520:2023 citation case**: add the `@ABNT-options{nbr10520-2023,...}`
   entry to `referencias.bib` and `\AtBeginDocument{\citeoption{nbr10520-2023}}`
   in `main.tex` (see `normas-e-versoes.md`). **`<URL>` brackets**:
   `\def\UrlLeft{}\def\UrlRight{}` in `main.tex`. Both only if the library
   asks for the new editions.
9. **Wrong root file in VS Code** (`File 'lib/unifortex2.sty' not found`,
   `preambulo.log`): `% !TEX root` lines + recipe on `main.tex`.
10. **Table counter** starts at `-1` in the `.sty` so the first table is 1 —
    do not "fix" it.
11. **Margins** are set with memoir's `\setlrmarginsandblock{3cm}{2cm}{*}` /
    `\setulmarginsandblock{3cm}{2cm}{*}` + `\checkandfixthelayout`; the bottom
    margin may measure a few millimetres off because memoir rounds
    `\textheight` to whole lines — accepted; do not add `geometry`.
12. **Captions in 12 pt bold** (template `captionsetup`, on top of the class
    already printing captions at 12 pt) differ from NBR 14724's "smaller,
    uniform size" for legends and sources; `\Fonte` is reduced. Keep the
    template's choice — it is what the UNIFOR library sees in every thesis —
    and mention it only if the banca asks.

## `referencias.bib` hygiene

The shipped file bundles demo entries (`knuth`, `lamport`, `tresautores`,
`quatroautores`, generic `NBR...`). Keep only entries actually cited plus the
norms you cite; never leave a fabricated entry cited in the text. Every
`\cite{key}` must resolve to a real, verified NBR 6023 entry.

## Where to get the template

Overleaf gallery → "UNIFOR - Template Latex" (Bruno Lopes). The GitHub URL
printed in the template headers (`github.com/bruno-unifor/unifortex2`) may no
longer resolve; the Overleaf copy is the reference distribution. UNIFOR's
library publishes its own manual and norm updates (e.g. the NBR 6028:2021
note) — those decide edition questions for UNIFOR students.
