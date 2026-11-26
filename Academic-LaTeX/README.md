# Academic-LaTeX — a Claude skill for theses and papers written in LaTeX

A *skill* for Claude (claude.ai, the desktop app/Cowork and Claude Code) that makes it a
competent co-author, typesetter and build engineer for **academic documents written in
LaTeX**: bachelor/master/PhD theses and dissertations, journal articles, conference
papers, research proposals, technical reports and response-to-reviewer letters, in
any language, with any citation style and any template.

It is a generalized fork of [TCC-ABNT2](https://github.com/MateusMelloSouza/TCC-ABNT2/tree/main/TCC-ABNT2) (the `tcc-abnt` skill for
Brazilian ABNT/abnTeX2 theses). It keeps everything that skill learned in dozens of
real writing and audit sessions (re-measure instead of trusting notes, verify
reviewer findings before acting, write files atomically, never fabricate sources)
and replaces the Brazil-specific parts with knowledge for international style
guides and templates.

## What it does

- **Writes and revises** sections, abstracts and rebuttals in the document's
  language and register, without inventing sources or results (gaps become
  visible `% TODO` markers that the audit tracks).
- **Cites and builds bibliographies**: chooses the right stack (biblatex + biber or
  natbib/cite + a `.bst`), uses the right commands, and writes `.bib` entries that
  print correctly: names, organisations, protected capitals, DOIs, Unicode,
  biblatex-only types.
- **Knows the style guides and templates**: APA 7, IEEE, Chicago 17, Harvard,
  Vancouver, MLA, Nature, ACS, AIP/APS, ACM, LNCS, AMS, Elsevier, ISO 690, ABNT, GB/T 7714,
  GOST, OSCOLA and more; verified preambles for IEEEtran, acmart, elsarticle, llncs,
  REVTeX 4.2 and amsart; memoir, KOMA-Script, classicthesis and university classes.
- **Formats** floats, tables (booktabs, siunitx), captions, cross-references
  (cleveref), math, units, code, algorithms, abbreviations and languages, through the
  template and never by hand.
- **Compiles and diagnoses** anywhere: Overleaf, VS Code, TeXstudio, TeXShop,
  Windows, the command line and sandboxes. An error table quotes the real messages.
- **Runs writing sessions** (5 phases) with state kept in the project
  (`.academic-workflow/`) and **audits before submission or defense**: a checklist
  plus a multi-agent review pattern with adversarial verification.

## Installation

### claude.ai and the desktop app (Cowork)
1. Download [`dist/academic-latex.zip`](dist/academic-latex.zip). Its root is the
   `academic-latex/` folder, as claude.ai requires.
2. claude.ai → **Customize → Skills → "+" → Upload a skill**, and choose the ZIP.
3. Ask something like *"Set up a LaTeX project for my PhD thesis in APA style"* or
   *"Why does my bibliography show [?]"*, with your project folder connected or
   the files attached.

### Claude Code
Copy the skill folder (personal or project skill):
```bash
git clone https://github.com/MateusMelloSouza/TCC-ABNT2.git
cp -r TCC-ABNT2/Academic-LaTeX/skills/academic-latex ~/.claude/skills/
```
Or install it as a plugin from the local clone (this folder is a plugin marketplace):
```
/plugin marketplace add ./TCC-ABNT2/Academic-LaTeX
/plugin install academic-latex@academic-latex
```
Once this folder lives in a repository of its own, `/plugin marketplace add
<owner>/<repo>` works directly, and so does the CI workflow in `.github/`.

## How to use it

Talk normally. The skill triggers on LaTeX, Overleaf, BibTeX/biblatex, theses and
papers. Typical requests:

- *"Start a writing session on my thesis"* → reads `.academic-workflow/STATUS.md`,
  re-measures the project (`audit-tex.py`, `compile-check.sh`), reconciles the debts
  and asks what to work on. Without the folder, it creates one with `init-workflow.py`.
- *"Create a thesis project: APA, double spacing, US Letter, 1.5 in left margin"* →
  `new-project.py` scaffolds a tested skeleton, then adapts it to the guide.
- *"My citations come out as [?] and there is no bibliography"* → a diagnosis
  (bibtex vs biber, keys, `.bib` errors) and the fix.
- *"Clean up my .bib"* → `bib-check.py`: duplicate keys, missing `and`, organisations
  parsed as people, unprotected capitals, `&`/`%` errors, DOI formats.
- *"Convert this paper from natbib to biblatex/IEEE style"*, *"make this table look
  professional"*, *"why is my figure three pages later"*.
- *"Check everything before I submit to the conference tomorrow (double-blind, 8
  pages)"* → the audit: page limit, anonymity (PDF metadata included), fonts,
  references, figures, leftovers.

## Scripts (they also work without Claude)

| Script | What it does |
|---|---|
| `scripts/audit-tex.py [dir]` | Re-measures a project: class/template, engine, citation stack and tool, to-do markers, citations ↔ `.bib`, labels (duplicates, `\label` before `\caption`, hard-coded "Figure 3"), floats never referenced or placed before their reference, missing or wrong-case graphics, unused abbreviations, abstract words and keywords, word counts, lint, log triage. Standard library only. |
| `scripts/bib-check.py refs.bib` | Lints `.bib` files with a real parser: structure, duplicates, required fields, names, titles, specials, identifiers, Unicode under BibTeX, dates, biblatex-only types, preprints. The BibTeX and biber behaviour it warns about was reproduced in TeX Live. |
| `scripts/compile-check.sh [main.tex]` | latexmk build into `build/` with engine detection and tool rules, then a summary: pages and paper size, undefined citations/references, duplicate labels, errors, `.blg` problems, overfull boxes, unembedded or Type 3 fonts, `??` left in the PDF, placeholders. `--strict` for CI. |
| `scripts/setup-sandbox-latex.sh` | Makes an empty machine compile: apt (with `apt-file` to map any missing file to its package), tlmgr, or CTAN into `~/texmf`. `--from-log build/main.log` installs what a failed build was missing. |
| `scripts/new-project.py dest --type thesis\|article\|letter --style …` | Tested skeletons: 15 citation styles × pdfLaTeX/LuaLaTeX/XeLaTeX, any babel language, A4/Letter, spacing, one/two-sided. |
| `scripts/init-workflow.py [dir] [--build-helpers]` | Creates `.academic-workflow/` (STATUS, TODO, TEMPLATE, session logs, tool copies) and optionally `.latexmkrc`, `.gitignore`, `build.bat`, `.vscode/settings.json`. |
| `assets/build.bat` | Windows double-click build (latexmk, or manual passes detecting biber/bibtex/makeglossaries), plus checks. |

## What was verified, and how

Everything that claims to work was compiled with TeX Live 2023 (pdfTeX 1.40.25,
biblatex 3.19, biber 2.19, latexmk 4.83) in a clean container:
`bash tests/run-tests.sh` runs the repository checks, 20 unit tests of the scripts
on fixture projects, **41 skeleton variants** (every citation style, every engine,
several languages and layouts) and the publisher and thesis-class documents behind
every preamble in the references. Error messages in
`references/compilation-and-errors.md` and the BibTeX/biber behaviours in
`references/bibliography.md` were reproduced, not recalled. Things that could not be
checked here (arXiv's current processing rules, venue-specific requirements) are
phrased as "check the current instructions".

## Repository layout

```
skills/academic-latex/
├── SKILL.md                      # what Claude reads first (router, quick rules)
├── references/                   # workflow, document types, citations, bibliography, style guides,
│   │                             # formatting, academic writing, compilation & errors, submission,
│   │                             # final review
│   └── templates/                # publisher classes, thesis classes, profiling procedure
├── scripts/                      # audit-tex.py, bib-check.py, compile-check.sh, setup-sandbox-latex.sh,
│                                 # new-project.py, init-workflow.py
├── assets/                       # skeletons (thesis, article, response letter), latexmkrc, gitignore,
│                                 # VS Code settings, build.bat, workflow templates
└── evals/                        # test prompts for the skill (claude plugin eval layout)
tests/                            # unit tests, fixtures, LaTeX matrix, template documents
scripts/check.py, scripts/package.sh
.claude-plugin/                   # plugin.json + marketplace.json (Claude Code)
dist/academic-latex.zip           # upload package for claude.ai
```

## License and credits

MIT (see [LICENSE](LICENSE)). Derived from TCC-ABNT2 by the same author. LaTeX classes,
packages and styles mentioned here belong to their authors and are not
redistributed; style manuals (APA, Chicago, IEEE, …) are described, not reproduced.
