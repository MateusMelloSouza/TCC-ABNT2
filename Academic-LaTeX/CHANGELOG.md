# Changelog

## 1.0.0 — 2026-11-26

First release: a generalized fork of `tcc-abnt` 2.0.0 (TCC-ABNT2) for academic LaTeX
documents in any language, style guide and template.

- **Scope**: theses and dissertations, journal articles, conference papers, proposals,
  technical reports, rebuttal letters (`references/document-types.md`).
- **Citations and bibliographies**: stack choice (biblatex + biber vs natbib/cite +
  `.bst`), a command crosswalk, and the pitfalls reproduced in TeX Live 2023:
  textual `\cite` in natbib author-year mode, natbib punctuation coming from the
  `.bst`, `\citet` with author-less numeric styles, biblatex dropping name prefixes.
  `.bib` behaviours were reproduced with BibTeX and biber: case-insensitive duplicate
  keys, %-commented entries read by BibTeX but not by biber, a duplicated field kept
  first by BibTeX and last by biber, UTF-8 initials breaking under BibTeX,
  organisations parsed as people.
- **Style guides**: availability and loading lines for 30+ guides, compiled. Tested
  ABNT fixes: NBR 10520:2023 citation case for abntex2cite (`@ABNT-options`) and, newly
  verified, for biblatex-abnt (`\renewcommand*{\mkbibnamefamily}[1]{#1}`).
- **Templates**: verified preambles for IEEEtran, acmart, elsarticle, llncs, REVTeX 4.2
  and amsart, covering abstract-before-`\maketitle` classes, llncs + amsthm, acmart's
  fonts and biblatex styles, elsarticle's citation variants. Thesis setups for memoir
  (the madsen style needs graphicx), KOMA-Script and classicthesis, and a guide-to-preamble
  checklist.
- **Skeletons** (`new-project.py`): a book-based thesis, an article and a response
  letter; 15 citation styles × 3 engines, languages, paper sizes, spacing; all 41
  tested variants compile with zero errors and zero undefined citations or references
  (the only warning is biblatex-abnt's harmless language-file notice).
- **Scripts**: `audit-tex.py` generalized to any class and stack (new: `\label` before
  `\caption`, hard-coded references, wrong-case graphics, abbreviations typed literally,
  lint, texcount); new `bib-check.py`; `compile-check.sh` with engine detection,
  `pdffonts` and leftover-`??` checks and sub-folders mirrored into the output
  directory (fixes `I can't write on file 'chapters/x.aux'` with `\include`);
  `setup-sandbox-latex.sh` with apt/apt-file, tlmgr and CTAN routes and `--from-log`;
  `init-workflow.py` with `.academic-workflow/`.
- **Tests and CI**: unit tests on fixture projects, the LaTeX matrix, template
  documents; a GitHub Actions workflow that installs TeX through the setup script.
- **Evals**: test prompts in `skills/academic-latex/evals/` (the `claude plugin eval`
  layout). First round: 3 cases (fix broken biblatex citations, set up a thesis from a
  formatting guide, audit a double-blind IEEE submission), each run with and without
  the skill. All 30 assertions passed in both configurations, so the base model
  already handles these tasks. With the skill, mean time was 23% lower (the thesis
  setup started from the tested skeleton) and tokens were 5% higher. The round found
  two bugs, fixed with regression tests: generated files were mode 0600, and the
  skeleton's glossary style advanced the table counter. It also showed that a setup
  run read references it did not need, so SKILL.md now has a reading guide.
