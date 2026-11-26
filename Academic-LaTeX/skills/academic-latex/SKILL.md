---
name: academic-latex
description: >-
  Write, structure, cite, format, compile, debug and audit academic documents in
  LaTeX: theses and dissertations, journal articles, conference papers,
  proposals, reports and rebuttal letters, in any language, citation style (APA,
  IEEE, Chicago, Harvard, Vancouver, MLA, ACM, Nature, ISO 690, ABNT) and
  template (university classes, IEEEtran, acmart, elsarticle, llncs, REVTeX,
  Overleaf). Use it whenever the user works on a .tex or .bib file or mentions
  LaTeX, Overleaf, BibTeX, biblatex, biber, natbib, citations, bibliography,
  figures, tables, cross-references, acronyms, compile errors (undefined
  citations, ??, missing .sty), submission, camera-ready, arXiv or PDF/A, or asks
  to draft or revise a chapter, section or abstract, even if LaTeX is not named.
  Also use it to run structured thesis-writing sessions and pre-submission audits.
license: MIT
metadata:
  version: "1.0.0"
  homepage: https://github.com/MateusMelloSouza/TCC-ABNT2
  derived-from: tcc-abnt 2.0.0 (ABNT/abnTeX2 skill)
---

# Academic LaTeX — write, cite, format, compile and audit theses and papers

This skill makes Claude a competent co-author, typesetter and build engineer for
academic documents written in LaTeX: bachelor/master/PhD theses, journal
articles, conference papers, research proposals, technical reports and
response-to-reviewer letters, in any language and with any citation style.

It is LaTeX-first on purpose. Most "formatting problems" in a LaTeX document are
really compile problems, template misuse or bad bibliographic data, so fix them
at the source (`.tex`, `.bib`, preamble, build chain) instead of hand-formatting
output. Talk to the user in their language; write the document in the
document's language and register.

Paths such as `scripts/audit-tex.py` and the `references/` files are relative to this
skill's folder; from the user's project, call the scripts with that folder's
full path (`python3 <skill-folder>/scripts/audit-tex.py .`).

## Two ways to use this skill

1. **One-off task** — "fix this citation", "why do I get [?]", "make this table
   look professional", "convert to IEEE style", "write the abstract". Do Step 0,
   then read the reference the routing table points to.
2. **Writing session** — a repeatable loop for steady progress on a long
   document over weeks: "start a writing session", "let's continue the thesis",
   "where did we stop?", "end the session". Follow
   **`references/workflow.md`**. If the project has an `.academic-workflow/`
   folder, read its `STATUS.md` and the latest `session-log/` file **before
   anything else**; to create it, run `scripts/init-workflow.py <project-dir>`.

## Step 0 — Discover the project before touching it

`python3 scripts/audit-tex.py <project-dir>` prints most of this in seconds:
main file, class, template family, engine, citation stack and the tool it
needs, included and orphan files, and every integrity problem it can measure.

1. **Who sets the rules?** A thesis answers to a graduate school or department
   formatting guide (and often a template); a paper answers to the venue's
   author instructions and class. Ask for them if they are not in the project:
   template, citation style **and edition**, page/word limits, abstract limit,
   anonymity, required statements, paper size. Record the answers.
2. **The template.** Find `\documentclass` (it may live in an `\input` file) and
   any project-local `.cls`/`.sty`. Known families have profiles in
   `references/templates/`; an unknown one gets profiled once
   (`references/templates/README.md`) and saved to `.academic-workflow/TEMPLATE.md`.
3. **The citation stack** — biblatex + biber, natbib/cite + a BibTeX `.bst`,
   or a class-specific system (abntex2cite, apacite). They are not
   interchangeable: commands, `.bib` rules and the compile chain differ. Never
   mix them, and never switch a publisher template's stack.
4. **The engine** — pdfLaTeX (most templates), LuaLaTeX or XeLaTeX (needed by
   `fontspec`, `unicode-math`, `polyglossia`). Keep the one the template uses.
5. **Conventions already in use** — file layout, label prefixes, macros, key
   style, spelling variant (US/UK), how figures are included. Match them; do not
   restructure a working project unless asked.
6. **No project yet?** Use the institution's or venue's official template. Only
   when none exists, scaffold a tested skeleton:
   `python3 scripts/new-project.py <dir> --type thesis|article|letter --style apa`
   (`--list-styles` shows all styles; `--engine`, `--language`, `--paper`).

## Who wins when rules conflict

**Venue or institution instructions > the template > the style guide (APA, IEEE,
Chicago, ...) > this skill's defaults.** Examiners and editors judge compliance
with *their* rules. When a template deviates from its style guide, tell the user
once, recommend asking the editor/graduate school, and record the decision in
`STATUS.md`. Do not "fix" a publisher class to match a style manual.

## Routing — read the reference you need

| Task | Read |
|---|---|
| Writing-session workflow (start → triage → plan → write → compile → log) | `references/workflow.md` |
| Structure of a thesis, article, conference paper, proposal, report, rebuttal; front/main/back matter | `references/document-types.md` |
| Citation commands, choosing biblatex vs natbib, multiple/page citations, footnote styles | `references/citations.md` |
| Writing and fixing `.bib` entries (names, capitals, DOIs, Unicode, entry types, reference managers) | `references/bibliography.md` |
| A specific style guide: APA, IEEE, Chicago, Harvard, Vancouver, MLA, ACM, Nature, ISO 690, ABNT, … | `references/style-guides.md` |
| Layout, fonts, spacing, sections, figures, tables, captions, cross-references, math, units, code, algorithms, acronyms, languages | `references/formatting.md` |
| Academic prose: register, section-by-section guidance, abstract, title, integrity | `references/academic-writing.md` |
| Compiling anywhere (Overleaf, VS Code, TeXstudio, TeXShop, CLI, Windows, sandbox) and the error table | `references/compilation-and-errors.md` |
| Submitting: journals, conferences (anonymity, camera-ready, fonts), arXiv, thesis deposit (PDF/A) | `references/submission.md` |
| Pre-submission / pre-defense audit checklist and the multi-agent review pattern | `references/final-review.md` |
| IEEEtran, acmart, elsarticle, llncs, REVTeX, amsart: verified preambles and rules | `references/templates/publisher-classes.md` |
| Thesis classes (standard classes, memoir, KOMA-Script, classicthesis, university classes), the bundled skeleton | `references/templates/thesis-classes.md` |
| Profiling any other template | `references/templates/README.md` |

Read only what the task needs — each reference stands alone, and reading all of
them costs time without improving the result. Typical combinations:
- **new thesis or paper** → `templates/thesis-classes.md` (§6 turns a formatting
  guide into a preamble) or `templates/publisher-classes.md`, plus the guide's
  section of `style-guides.md`;
- **citations or build broken** → `compilation-and-errors.md` (+ `bibliography.md`
  when the `.bib` is involved);
- **check before submitting or defending** → `final-review.md` + `submission.md`;
- **drafting or revising prose** → `academic-writing.md` (+ `document-types.md`
  for structure).

## Choosing a citation stack

| Situation | Use |
|---|---|
| Journal or conference with its own class or `.bst` | exactly what the template ships (usually natbib/cite + `.bst`, run **bibtex**) |
| Thesis or preprint with no mandated stack | **biblatex + biber** with the style package for the required guide (`style=apa`, `ieee`, `numeric-comp`, `authoryear`, `biblatex-chicago`, …) |
| arXiv submission | either works if you upload the generated `.bbl`; a biblatex `.bbl` must match arXiv's biblatex version, a BibTeX `.bbl` is portable — see `references/submission.md` |
| Brazilian ABNT documents | abntex2cite (BibTeX) or biblatex-abnt — `references/style-guides.md` (and the dedicated `tcc-abnt` skill) |

Details, command crosswalk and pitfalls: `references/citations.md`.

## Quick rules (the most-asked ones)

- **`\label` after `\caption`** (or inside it). A label placed before the
  caption silently picks up the section number: "Figure 3" for figure 2.
- **Cross-references**: `Figure~\ref{fig:x}` with a non-breaking space, or
  cleveref's `\cref{fig:x}`. Load hyperref late and cleveref after it — the
  reverse order is a hard error. Never type a figure, table or section number.
- **Citation commands**: biblatex `\textcite` (Author (2020)), `\parencite`
  ((Author, 2020) / [1]), `\autocite` (lets the style decide);
  natbib `\citet` / `\citep`. In natbib author-year mode plain `\cite` is
  *textual* — use `\citep` for parentheses. Page: `\parencite[45]{key}`,
  `\citep[p.~45]{key}`.
- **Never invent a source, a number or a result.** Missing reference → ask for
  it or leave a visible `% TODO: citation needed — <claim>` and say so.
- **`.bib` hygiene** (`python3 scripts/bib-check.py refs.bib`): one entry per
  work; ` and ` between names (a comma means "Last, First"); organisations in
  double braces `{{World Health Organization}}`; bare DOI `10.xxxx/yyy`;
  braces around words that must keep capitals `{GPU}`, `{Bayesian}`;
  escape `\& \% \# \_` outside url/doi; no `%`-commented entries (BibTeX
  still reads them).
- **Figures**: vector PDF for plots and diagrams, PNG for screenshots, JPEG
  only for photos; `width=\linewidth`; `[htbp]` placement; every float
  referenced in the text. Caption position follows the style (most: figure
  captions below, table captions above; APA puts figure number and title
  above).
- **Tables**: booktabs rules (`\toprule`, `\midrule`, `\bottomrule`), no
  vertical lines, siunitx `S` columns for numbers; fit wide tables with `p{}` /
  `tabularx` columns or a smaller font, not `\resizebox`.
- **Math**: amsmath environments (`equation`, `align`); never `$$ … $$` or
  `eqnarray`; punctuate displayed equations as part of the sentence; words in
  math via `\text{}`; units via siunitx `\qty{3.5}{\milli\second}`.
- **Abbreviations**: define once (`\newacronym` / `\DeclareAcronym`), write
  `\gls{key}` / `\ac{key}`; first use expands automatically and only used
  entries are listed.
- **Do not hand-format what the class controls** — margins, fonts, spacing,
  title page, heading styles. In a publisher template, never change layout
  (`\vspace{-…}` hacks and font changes get papers returned).

## Compiling

```
latexmk main.tex                              # with the project's .latexmkrc (engine, glossaries rules)
latexmk -pdf main.tex                         # pdfLaTeX   (-lualatex / -xelatex for the Unicode engines)
pdflatex main && biber main && pdflatex main && pdflatex main   # by hand; bibtex instead of biber for .bst styles
```
latexmk runs biber/bibtex and makeindex itself; `makeglossaries` needs the rule
in `assets/latexmkrc`. In sandboxes or CI without TeX:
`bash scripts/setup-sandbox-latex.sh` once (apt, tlmgr or CTAN — whichever the
network allows), then `bash scripts/compile-check.sh main.tex` for a build plus
an actionable summary: pages and paper size, undefined citations/references,
duplicate labels, real errors, bibliography-tool messages, overfull boxes,
unembedded/Type 3 fonts, leftover `??`/`[?]` in the PDF, and placeholders.

Symptoms → causes (full table in `references/compilation-and-errors.md`):
`[?]`, bold keys or `(?)` → the bibliography tool did not run, ran the wrong
tool (bibtex vs biber), or the key is wrong · `??` → missing pass or wrong label
· `Cannot find 'refs'!` (biber) → `\addbibresource` needs the `.bib` extension ·
empty list of abbreviations → `makeglossaries` did not run · `File 'x.sty' not
found` → install the package (`setup-sandbox-latex.sh --from-log build/main.log`)
or wrong root file · `I can't write on file 'chapters/x.aux'` → output directory
lacks the sub-folder (compile-check.sh creates it).

## How to work with the user

- Confirm the document type, the binding rules and the citation stack before
  producing references or restructuring anything.
- Edit the real files in place; keep diffs surgical and reversible; explain what
  changed and why, file by file.
- Never fabricate sources, data, quotes or results; flag unsupported claims.
  The author must read, understand and own every paragraph; respect the
  institution's or venue's policy on AI assistance.
- Before bulk edits in a project that is not under git, snapshot the files;
  when scripting edits, write to a temporary file and rename it over the
  original (a failed `open(path, "w")` can leave a zero-byte chapter).
- Verify before acting on a claimed problem — yours, a tracker's or a
  reviewer's: recompile, grep the log, read the line. The `.tex`, `.bib` and
  `.log` files are the ground truth.
- In a writing session, always update `STATUS.md` and write the session log
  before ending, with explicit next steps.
