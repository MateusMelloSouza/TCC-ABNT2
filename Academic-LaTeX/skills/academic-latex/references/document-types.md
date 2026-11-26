# Document types — structure and how to build each one in LaTeX

The structures below are the common shape; the binding version is always the
graduate school's guide, the funder's call or the venue's author instructions.
Terminology varies: in the US a *dissertation* is doctoral and a *thesis* is
master's; in the UK and much of Europe it is the reverse or both are "thesis".

## Contents
1. Thesis / dissertation (monograph)
2. Thesis by publication (compilation, "kappa")
3. Journal article
4. Conference paper
5. Research or thesis proposal
6. Technical report, working paper, preprint
7. Extended abstract, poster, slides
8. Response to reviewers
9. LaTeX building blocks for long documents

## 1. Thesis / dissertation (monograph)

**Front matter** (roman page numbers; order per the graduate school):
title page (exact wording prescribed) · copyright page · declaration /
statement of originality / approval or signature page · dedication (optional) ·
abstract (often also in a second language) · acknowledgements (funding with
grant numbers) · table of contents · lists of figures, tables, abbreviations,
symbols · preface or list of publications (optional).

**Main matter** (arabic numbers from 1):
1. Introduction — context, problem and gap, aim and research questions or
   hypotheses, contributions, scope, outline of the thesis.
2. Background / literature review — the state of knowledge organised by theme,
   ending with the gap.
3. Methodology / materials and methods — design, data, instruments, tools,
   procedure, analysis, ethics, threats to validity.
4. Results (one or several chapters), often one per study or research question.
5. Discussion — interpretation, comparison with the literature, implications,
   limitations.
6. Conclusion — answers to the research questions, contributions, future work.
(Humanities theses are often thematic chapters instead of IMRaD; follow the
field and the supervisor.)

**Back matter**: references/bibliography · appendices (questionnaires,
proofs, extra results, code) · index · curriculum vitae (some US schools) ·
the published papers (some programmes).

LaTeX: book-like classes (`book`, `memoir`, `scrbook`) give `\frontmatter`,
`\mainmatter`, `\backmatter`; the bundled skeleton
(`scripts/new-project.py --type thesis`) is a tested starting point when the
university has no class. Title pages that must match a Word template exactly:
build them in a `titlepage` environment from the guide's sample, or include the
signed PDF with `\includepdf` (pdfpages).

## 2. Thesis by publication

Introduction/summary chapter ("kappa", "comprehensive summary") + the papers
(published, accepted or submitted) + a concluding chapter. Specific needs:
- Per-paper bibliographies: biblatex `\begin{refsection} … \printbibliography[heading=subbibintoc] \end{refsection}` per paper; one style for all.
- Papers as published PDFs: `\includepdf[pages=-]{papers/paper1.pdf}` —
  check the publisher's reuse policy (most allow inclusion in the author's
  thesis, some require the accepted manuscript instead of the publisher PDF,
  all require the citation and copyright line).
- Papers re-typeset in the thesis format: keep each paper's content, unify
  numbering (`\chapter` per paper) and cross-references.
- A statement of the candidate's contribution to each co-authored paper (often
  mandatory; CRediT roles are a convenient format).

## 3. Journal article

Title · authors and affiliations (ORCID) · abstract (structured in medicine:
Background, Methods, Results, Conclusions) · keywords (sometimes a controlled
vocabulary: MeSH, ACM CCS, MSC, JEL) · highlights / graphical abstract
(Elsevier and others) · IMRaD body (Introduction, Methods, Results, Discussion;
or Introduction, Related Work, Approach, Evaluation, Conclusion in computing) ·
statements: data availability, code availability, funding, conflicts of
interest, author contributions (CRediT), ethics approval and consent ·
acknowledgements · references · appendices / supplementary material.

Use the journal's class when it has one (`templates/publisher-classes.md`);
for journals without a LaTeX template the article skeleton
(`new-project.py --type article`) is acceptable at submission — production
re-typesets accepted papers.

Article types change limits and structure: research article, letter / short
communication (strict length), review (systematic reviews follow PRISMA:
flow diagram, search strategy, risk-of-bias tables), methods paper, data
paper, comment/reply.

## 4. Conference paper

Same core as an article, under harder constraints: a page limit (check whether
references and appendices count), the venue's class unmodified, **anonymity**
for double-blind review (no names, no identifying acknowledgements, self-citations
in the third person, anonymised links, clean PDF metadata), supplementary
material rules, and a camera-ready version with authors, copyright notice and
DOI added after acceptance. Details: `submission.md`.

## 5. Research or thesis proposal

Title · summary/abstract · background and significance · research questions
or aims · preliminary work · methods and work plan · timeline (a Gantt chart:
`pgfgantt`) · risks and mitigation · ethics · budget and justification (grant
proposals) · references. Funders prescribe page limits, fonts and margins
strictly — implement them with geometry and the font packages, then check the
PDF. Thesis proposals / qualifying documents usually reuse the thesis template.

## 6. Technical report, working paper, preprint

Report number and institution on the title page (`report` or `article`
class, or the institution's series template); executive summary for
non-specialist readers; numbered sections; references; appendices. Preprints
(arXiv, SSRN, bioRxiv, institutional repositories) use the article skeleton or
the target journal's template with a "preprint" note — check the journal's
preprint policy first.

## 7. Extended abstract, poster, slides

- Extended abstract: 1–4 pages in the venue's template; one figure, the key
  result, references.
- Posters: `tikzposter`, `beamerposter` (beamer class), `baposter`; design for
  reading at 2 m — large fonts, few words, one message.
- Slides: `beamer` (with the institution's theme if one exists) — slides are a
  separate document; do not copy thesis paragraphs onto them.

## 8. Response to reviewers

A separate document (`new-project.py --type letter`): thank the editor and
reviewers; quote every comment verbatim, numbered (R1.1, R1.2, …); answer each
one; state exactly what changed and where (section, page and line numbers of
the revised manuscript — compile it with `lineno`); quote the revised text;
disagree politely with evidence when a request would not improve the work;
never ignore a comment. Provide a marked-up manuscript (`latexdiff`) when the
journal asks.

## 9. LaTeX building blocks for long documents

- One file per chapter (`chapters/introduction.tex`), each starting with
  `% !TEX root = ../main.tex`; `\include` (page break, `\includeonly` support) or
  `\input` (no page break) from `main.tex`.
- Keep the preamble in `main.tex` (or a `preamble.tex` that `main.tex` inputs)
  — editors guess the root file from `\documentclass`, and a preamble compiled
  alone fails.
- Figures in `figures/` (`\graphicspath{{figures/}}`), bibliography in one
  `.bib`, project macros in one place (`\newcommand` for notation used
  throughout: change once, consistent everywhere).
- `\includeonly{chapters/results}` while writing; `draft` class option for fast
  builds; full build before every hand-off.
- Version control (git) with a `.gitignore` for build products
  (`assets/gitignore-latex`); Overleaf has git and GitHub sync.
