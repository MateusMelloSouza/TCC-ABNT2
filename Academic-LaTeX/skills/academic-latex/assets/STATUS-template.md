# STATUS — {{TITLE}}

> Single source of truth between writing sessions. Re-measured at the start of
> every session (`tools/audit-tex.py`, `tools/compile-check.sh`); never edited
> from memory. Last update: {{DATE}} (session {{SESSION}}).

## Project

<!-- Document type: bachelor/master/PhD thesis, journal article, conference paper, proposal, report.
     Venue: journal, conference, graduate school or repository. Rules: template, formatting guide or author
     instructions (link or file). Replace every ? with the author. -->

| Item | Value |
|---|---|
| Author(s) / programme / institution | {{AUTHOR}} — {{PROGRAMME}} — {{INSTITUTION}} |
| Document type | {{DOCTYPE}} |
| Target venue / deposit | {{VENUE}} |
| Rules that bind | {{RULES}} |
| Template profile | {{TEMPLATE}} (see `TEMPLATE.md`) |
| Main file / engine / build | `{{MAIN}}` — {{ENGINE}} — {{CHAIN}} |
| Citation stack / style guide | {{CITATION_STACK}} — style: {{STYLE_GUIDE}} |
| Language(s) / spelling variant | {{LANGUAGE}} |
| Limits | pages: {{PAGE_LIMIT}} · words: {{WORD_LIMIT}} · abstract: {{ABSTRACT_LIMIT}} |
| Supervisor(s) / committee / co-authors | {{PEOPLE}} |
| Deadlines | {{DEADLINES}} |
| Version control | {{VCS}} — git strongly recommended; otherwise snapshot before bulk edits |

## Invariants (last build)

| Invariant | Value | Source |
|---|---|---|
| Pages | {{PAGES}} | `main.log` |
| LaTeX errors (real) / benign notices | {{ERRORS}} / {{BENIGN}} | `compile-check.sh` |
| Undefined citations / references | {{UNDEF_CITES}} / {{UNDEF_REFS}} | `main.log` |
| Floats: captioned / labelled / referenced | {{FLOATS}} | `audit-tex.py` |
| `.bib`: entries / cited / missing / lint errors | {{BIB}} | `audit-tex.py`, `bib-check.py` |
| Overfull boxes / float too large | {{OVERFULL}} / {{FLOAT_TOO_LARGE}} | `main.log` |
| Abstract words | {{ABSTRACT}} | `audit-tex.py` |
| Total words | {{WORDS}} | `audit-tex.py` |

## Sections / chapters

| File | Section | Words | State | Notes |
|---|---|---|---|---|
{{CHAPTER_ROWS}}

State legend: `empty` · `outline` · `draft` · `revised` · `reviewed by supervisor/co-authors` · `frozen`.

## Front and back matter

| Element | State |
|---|---|
| Title page / metadata | {{META_STATE}} |
| Abstract(s) / keywords | {{ABSTRACT_STATE}} |
| Required statements (declaration, data availability, funding, conflicts, contributions) | ? |
| Lists (figures, tables, abbreviations, symbols) | {{LISTS_STATE}} |
| Bibliography (`.bib`) | {{BIB_STATE}} |
| Appendices / supplementary material | {{APPENDICES_STATE}} |

## Decisions log

| Date | Decision | Decided by |
|---|---|---|
| {{DATE}} | Workflow created; baseline measured | — |

## Open debts (summary — details and ids in `TODO.md`)

- …

## Done (moved from TODO, most recent first)

- …
