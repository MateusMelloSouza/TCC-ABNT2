---
name: tcc-abnt
description: >-
  Write, format, revise and compile Brazilian academic work in LaTeX with the
  abnTeX2 class following ABNT norms — TCC, monografia, dissertação, tese, artigo
  científico, projeto de pesquisa — for any Brazilian university template
  (UniforTeX2/UNIFOR and other institutional abnTeX2 customizations included).
  Use it whenever the user works on a TCC or any Brazilian academic document, or
  mentions ABNT, abnTeX2, abntex2cite, biblatex-abnt, NBR 14724, NBR 10520,
  NBR 6023, NBR 6028, citações, referências, resumo, palavras-chave, sumário,
  banca, orientador, ficha catalográfica, folha de aprovação, Overleaf, or asks to
  write/format/fix a chapter, citation, bibliography (.bib), figure/table (tabela vs
  quadro), or to compile a LaTeX thesis (errors like (????), ??, undefined
  citations). Also use it to run a structured thesis-writing session (start a
  session, triage debts, plan edits, compile, log progress) and to audit a
  finished thesis against ABNT before deposit — even when the norm is not named.
license: MIT
metadata:
  version: "2.0.0"
  homepage: https://github.com/MateusMelloSouza/TCC-ABNT2
  language: pt-BR output, English instructions
---

# TCC ABNT (abnTeX2) — writing, formatting, compiling & session workflow

This skill makes Claude a competent co-author and typesetter for **Brazilian
academic documents written in LaTeX with abnTeX2**: TCC, monografia,
dissertação, tese, artigo científico and projeto de pesquisa. The document
content is almost always **formal Brazilian academic Portuguese (pt-BR)**; write
it that way unless the user asks otherwise. Talk to the user in their language.

It is LaTeX-first on purpose: the norms are enforced by the class and the
template, so most "ABNT problems" are really compile problems, template
misuse, or bibliographic data problems. Fix those at the source (`.tex`,
`.bib`, preamble) rather than by hand-formatting output.

## Two ways to use this skill

1. **One-off task** — "fix this citation", "write the resumo", "why do I get
   (????)", "turn this table into a quadro". Do Step 0, then jump to the
   reference you need (routing table below).
2. **Writing session** — a repeatable loop for making steady progress on a long
   thesis across weeks. When the user says "start a writing session", "let's
   work on the TCC", "continue where we left off", "end the session", or asks for
   a workflow/status review, follow **`references/workflow-sessao.md`**. If the
   project has a `.tcc-workflow/` folder, read `.tcc-workflow/STATUS.md` and
   the latest `session-log/` file **before anything else**. To create that
   folder in a new project, run `scripts/init-workflow.py <project-dir>`.

## Step 0 — Discover the project and respect its template

Students almost never write on a bare abnTeX2 model; they inherit a template
from their university, program or orientador. **The template, the orientador's
instructions and the library's manual override the generic rules in this
skill** whenever they conflict — a banca rarely rewards "but the norm says".

Before writing or fixing anything:

1. Locate the main file (`\begin{document}`), the `\documentclass` (often in an
   `\input`ed preamble), the `.bib` file(s), and any README/normas the
   institution ships. `scripts/audit-tex.py <dir>` prints most of this.
2. Identify the **citation stack** — `abntex2cite` (BibTeX, `[alf]` author-date
   or `[num]` numeric) versus `biblatex-abnt` (biber). Never mix them; the
   compile chain differs (`bibtex` vs `biber`).
3. Identify the **template profile** and read the matching file — check for a
   project-local `.sty`/`.cls` (`find . -name '*.sty' -o -name '*.cls'`)
   **before** concluding it is the plain model, because university forks keep
   the model's commands and add their own on top:
   - `lib/unifortex2.sty`, `\trabalhoacademico{...}`, `\UNIFORfig` →
     **UniforTeX2 (UNIFOR)** → `references/templates/unifortex2.md`
   - another local `.sty`/`.cls`, or macros not in `abntex2.cls` → **another
     institution's template** → profile it with
     `references/templates/README.md` and save the profile in
     `.tcc-workflow/TEMPLATE.md` so the next session does not rediscover it.
   - no local style, `\documentclass{abntex2}` with `\imprimircapa`,
     `\imprimirfolhaderosto*` → **canonical abnTeX2 model** →
     `references/templates/abntex2-modelo.md`
4. Match existing conventions: file layout, custom float commands, label
   prefixes, bib key style, decimal comma, italics for foreign terms. Do not
   restructure a working project unless asked.
5. If there is no project yet, scaffold from the canonical
   `abntex2-modelo-trabalho-academico` (ships with abnTeX2, also on Overleaf)
   and strip the demo text; do not hand-roll a preamble.

## Norm editions — what changed and what abnTeX2 still does

abnTeX2's last release (v1.9.7, 2018) predates three current editions. Know
the gap, tell the user once, and let the institution decide; details and the
tested fixes are in **`references/normas-e-versoes.md`**.

| Norm | Current edition | Headline change | abnTeX2 default |
|---|---|---|---|
| NBR 10520 (citações) | **2023** | `(Silva, 2020)` — only initial capital in parentheses; *et al.* optional from 4 authors; 4 cm indent of long quotes now "recuo padronizado"; Latin terms in italics | prints `(SILVA, 2020)` — switchable without editing the `.bst` (below) |
| NBR 6023 (referências) | **2018** (+Errata 2:2020) | `Disponível em: URL.` without `< >`; `Acesso em:`; `[S. l.]` | prints `<URL>` — one-line fix (below) |
| NBR 6028 (resumo) | **2021** | keywords separated by **semicolons**, lowercase initials, final period | template prints what you type |
| NBR 14724 (estrutura) | **2024** (Dec 2024) | sources of figures/tables cite per 10520:2023; "seções", not "capítulos"; anexos keep their own references; epígrafe rules | implements 2011 (structure unchanged in practice) |
| NBR 6024 / 6027 | 2012 / 2012 | numeração progressiva / sumário | ok |
| NBR 6022 / 15287 | 2018 / 2011 | artigo / projeto de pesquisa | ok |

The two fixes, tested on the canonical model and on UniforTeX2 (apply only when
the institution wants the new editions; full explanation in
`references/normas-e-versoes.md`):

```bibtex
% in the project's .bib — an options entry read by abntex2-alf.bst (never printed)
@ABNT-options{nbr10520-2023, abnt-cite-style = "(Author, YEAR)", key = "aaaa"}
```
```latex
\usepackage[alf,nbr10520-2023]{abntex2cite}      % or, if the preamble is the template's:
\AtBeginDocument{\citeoption{nbr10520-2023}}      %   this line in main.tex after the preamble
\def\UrlLeft{}\def\UrlRight{}                     % NBR 6023:2018 — no < > around URLs (affects every \url)
```

## Routing — read the reference you need

| Task | Read |
|---|---|
| Session workflow (start → triage → plan → write → compile → log) | `references/workflow-sessao.md` |
| Which norm edition applies; abnTeX2 gaps and their fixes | `references/normas-e-versoes.md` |
| Structure and element order (capa … anexos), abnTeX2 commands | `references/estrutura-nbr14724.md` |
| Citations in the text, abntex2cite/biblatex commands | `references/citacoes-nbr10520.md` |
| Reference list and `.bib` entries (authors, entities, anais, legislação) | `references/referencias-nbr6023.md` |
| Visual formatting, figures, tabela vs quadro, lists, equations | `references/formatacao.md` |
| Academic writing in pt-BR, resumo/abstract, section-by-section guide | `references/escrita-academica.md` |
| Compiling anywhere (Overleaf, VS Code, TeXstudio, Windows, CLI, sandbox), error triage | `references/compilacao-e-erros.md` |
| Pre-deposit audit checklist and multi-agent review pattern | `references/revisao-final.md` |
| UniforTeX2 (UNIFOR) settings, commands, quirks | `references/templates/unifortex2.md` |
| Canonical abnTeX2 model | `references/templates/abntex2-modelo.md` |
| Profiling another institution's template | `references/templates/README.md` |

## Quick rules (the most-asked ones)

- **Page (NBR 14724):** A4; margins left & top 3 cm, right & bottom 2 cm; body
  font 12 pt (Times or Arial family), 1.5 line spacing. **Smaller, uniform
  size (10)** for long quotes, footnotes, page numbers, ficha catalográfica and
  the identification/source of figures and tables; **single spacing** for
  those and also for references and the natureza do trabalho (which stay
  12 pt). The class does most of this — verify, don't re-implement (it prints
  captions at 12 pt by default; `\fonte{}` is reduced, `\legend{}` is not).
- **Pagination:** counted from the folha de rosto, printed from the first
  textual page (Introdução), top right, in the same size-10 font.
- **Sections (NBR 6024):** progressive numbering `1`, `1.1`, `1.1.1` (avoid a
  sixth level); no period after the number; primary sections start a new page;
  unnumbered titles (resumo, sumário, referências, apêndices) are centered.
- **Short direct quote (≤ 3 lines):** inline, `"..."`, with page: `(Silva,
  2020, p. 15)` — or `(SILVA, 2020, p. 15)` if the institution still follows the
  2002 caps. **Long quote (> 3 lines):** `\begin{citacao}` — indent (4 cm
  conventionally), size 10, single spacing, no quotation marks, page number.
- **Author in the running text:** `Segundo Silva (2020)` → `\citeonline{key}`;
  in parentheses → `\cite{key}`. Multiple works in one parenthesis are
  alphabetical: `\cite{alves2019,silva2020}`.
- **Every `\cite` key exists in the `.bib`; every `.bib` entry is cited.** Never
  invent a source — insert `% TODO: referência` and say so.
- **`.bib` author fields** (the style uppercases them with ASCII rules): accents
  as TeX escapes (`Ara{\'u}jo`, not `Araújo`), particles before the surname
  (`de Freitas, Ernani`), compound surnames `{\relax Van Horn}, Grant`, entity
  authors `{{\relax Brasil}}` — details in `references/referencias-nbr6023.md`.
- **Figures and tables:** identification (`Figura 1 – Título`) **above**, source
  **below** in size 10 (`Fonte: elaborada pelo autor (2026).` or
  `Fonte: Silva (2020, p. 3).`), cited in the text **before** they appear and
  placed as close as possible to that citation. Numeric data → *tabela* (IBGE:
  open sides); textual/comparative content → *quadro* (closed borders).
- **Resumo (NBR 6028:2021):** one paragraph, 150–500 words for TCC/dissertação/
  tese, third person, no citations; `Palavras-chave: termo um; termo dois;
  termo três.` Abstract = faithful translation + Keywords.
- **Lists of siglas/símbolos:** only items actually used in the text; símbolos
  in order of first appearance.

## Compiling (abnTeX2 + BibTeX)

```
pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```
Add `makeglossaries main` after `bibtex` when the template uses `glossaries`
(UniforTeX2 does). `latexmk -pdf main.tex` runs the right sequence — with
glossaries only if the project has a `.latexmkrc` (see `assets/latexmkrc`).
`biblatex-abnt` projects run `biber main` instead of `bibtex`.

Sandbox without abnTeX2 (Cowork, CI): `bash scripts/setup-sandbox-latex.sh`
once, then `bash scripts/compile-check.sh main.tex` for a build plus a filtered,
actionable summary (pages, undefined citations/refs, real errors with benign
template notices filtered, overfull count, placeholder scan).

Symptoms and causes (full table in `references/compilacao-e-erros.md`):
`(????)` → BibTeX/biber did not run or the key is wrong · `??` → bad
`\label`/`\ref` or one pass missing · empty siglas list → `makeglossaries` did
not run · `Undefined control sequence` on a template macro → preamble not
loaded or compiling a chapter instead of `main.tex` · `File 'lib/xxx.sty' not
found` → the editor compiled the wrong root file (add `% !TEX root = ../main.tex`).

## How to work with the user

- Confirm the document type, template and citation system before producing
  references or restructuring anything.
- Draft into the existing chapter files; keep diffs surgical and reversible;
  explain what changed and why, file by file.
- Never fabricate sources, data or results. Missing bibliographic data → ask, or
  leave a visible `% TODO` placeholder. Unsupported claims → flag them.
- Before bulk edits in a project that is not under git, take a snapshot copy;
  when scripting edits, write to a temporary file and rename over the original
  (an encoding error in a naive `open(..., "w")` can truncate a chapter to zero
  bytes — it has happened).
- Verify before you act on a claimed problem: recompile, grep the log, read the
  line. Automated reviewers (and previous session notes) produce false
  positives; the `.tex` and the `main.log` are the ground truth.
- In a writing session, **always update `STATUS.md` and write the session log
  before ending**, with explicit next steps.
