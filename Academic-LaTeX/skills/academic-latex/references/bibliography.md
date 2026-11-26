# The `.bib` file — entries that print correctly in every style

You write the data; the style (biblatex style or BibTeX `.bst`) formats it. Most
"wrong references" are wrong data. Every behaviour marked *(verified)* was
reproduced with BibTeX 0.99d / biber 2.19 in TeX Live 2023; `scripts/bib-check.py`
detects all of them.

## Contents
1. How names are parsed
2. Titles and capitalisation
3. Special characters and Unicode
4. Entry types and required fields (BibTeX vs biblatex)
5. Identifiers: DOI, URL, ISBN, arXiv
6. Dates
7. Keys, duplicates, comments
8. Reference managers and exported data
9. Verifying every entry

## 1. Names

BibTeX and biber split a name list on ` and ` and parse each name as
`First von Last`, `von Last, First` or `von Last, Jr, First`.

| You want | Write | Not |
|---|---|---|
| two authors | `Smith, John and Doe, Jane` | `John Smith, Jane Doe` — read as **one** person, surname "John Smith" *(verified)* |
| many authors, truncated | `Smith, John and others` (style prints et al.) | `Smith, John et al.` |
| organisation as author | `{{World Health Organization}}` | `World Health Organization` — parsed as surname "Organization" *(verified)* |
| compound surname | `García Márquez, Gabriel` / `{Van Horn}, Grant` | `Gabriel García Márquez` (surname would be "Márquez") |
| particle | `van Dijk, Teun A.` / `de Beauvoir, Simone` (lowercase particle = "von" part) | `Dijk, Teun A. van` |
| suffix | `King, Jr, Martin Luther` | `Martin Luther King Jr.` |
| initials | `Tolkien, J. R. R.` (spaces) | `J.R.R.` (one token: abbreviating styles print "J.") |

- Use the full given names when known: the style abbreviates, it cannot expand.
- Names exported in ALL CAPS cannot be fixed by the style — retype them.
- Name prefixes in citations: biblatex drops them unless `useprefix=true`
  (`citations.md` §5).
- Brace a whole name only for organisations or names that must not be parsed;
  braces also stop initials and sorting from working on that name.

## 2. Titles and capitalisation

Many styles **change the case of titles** — BibTeX's `plain`, `abbrv`,
`plainnat`, `IEEEtran`, ACM, most numeric `.bst`; biblatex-apa (sentence case).
Text inside braces is protected *(verified: `Deep Learning on GPUs` →
"Deep learning on gpus"; `{GPUs}` survives)*.

- Store titles as published (usually Title Case in English) and brace only what
  must keep its capitals: acronyms `{GPU}`, `{DNA}`, `{COVID-19}`; proper nouns
  `{Bayesian}`, `{Fourier}`, `{Python}`, `{Brazil}`; CamelCase `{LaTeX}`
  (`{\LaTeX}`), `{iPhone}`; chemical formulas; a capital after a colon if the
  style does not keep it.
- Do not wrap the **whole** title in double braces: it blocks the style's case
  rules (APA wants sentence case, Chicago title case — the style needs the
  freedom).
- Journal names are not case-changed; write them in full title case. Some styles
  (IEEE, Vancouver, ACS) want ISO 4/NLM abbreviations — use the journal's
  official abbreviation (`IEEEabrv.bib` provides `@string` macros for IEEE
  journals: `\bibliography{IEEEabrv,refs}`), or biblatex `shortjournal` +
  `\DeclareSourcemap`.
- Non-English titles: biblatex `langid = {german}` lets the style apply the right
  rules (and hyphenation); `usera`/`titleaddon = {[English translation]}` if the
  guide asks for one.

## 3. Special characters and Unicode

- In normal fields escape LaTeX specials: `\&`, `\%`, `\#`, `\_`, `\$`, and
  math `$x^2$`. An unescaped `&` is `Misplaced alignment tab character &`
  *(verified)*; an unescaped `%` silently deletes the rest of the line under
  BibTeX and breaks the whole biblatex bibliography (`File ended while scanning
  use of \field`) *(verified)*. `url`, `doi`, `eprint` and `file` are verbatim:
  do **not** escape there under biber.
- **biber** reads UTF-8 natively: `Émile Durkheim`, `Łukasz`, `Ångström`,
  Chinese or Cyrillic names sort and abbreviate correctly (choose a font/engine
  that has the glyphs).
- **BibTeX is 8-bit**: UTF-8 letters in *names* break initials — `Durkheim,
  Émile` in an abbreviating style gives `Invalid UTF-8 byte sequence` *(verified)*
  — and can misplace entries when sorting. With BibTeX, write names with TeX
  escapes inside braces: `{\'E}mile`, `G{\"o}del`, `Gon{\c{c}}alves`, `{\L}ukasz`,
  `{\AA}ngstr{\"o}m`. Titles in UTF-8 usually print fine with pdfLaTeX.
- Quotes in titles: `\enquote{}` (csquotes) or `` ``…'' ``; never straight `"`
  (it ends a `"…"`-delimited field).

## 4. Entry types and required fields

| Type | BibTeX needs | biblatex equivalent / extra |
|---|---|---|
| `@article` | author, title, journal, year (+ volume, number, pages, doi) | `journaltitle` = journal, `date` = year |
| `@inproceedings` | author, title, booktitle, year (+ pages, publisher, address, doi) | `eventtitle`, `venue`, `eventdate` |
| `@book` | author or editor, title, publisher, year (+ address, edition) | `location` = address; `edition = {2}` (number only) |
| `@incollection` | author, title, booktitle, publisher, year (+ editor, pages) | — |
| `@phdthesis` / `@mastersthesis` | author, title, school, year | `@thesis` + `type = {phdthesis}`, `institution` |
| `@techreport` | author, title, institution, year (+ number) | `@report` + `type` |
| `@misc` | anything (title, howpublished, year, note, url) | — |
| web page, software, dataset | `@misc` with `howpublished = {\url{…}}` and `note = {Accessed …}` | `@online` (url, urldate), `@software`, `@dataset` (version, doi) |

Under **BibTeX**, biblatex-only types (`@online`, `@software`, `@dataset`,
`@report`, `@thesis`) are unknown to standard `.bst` files (`entry type for "x"
isn't style-file defined`) and biblatex-only fields (`date`, `urldate`,
`journaltitle`, `location`) are ignored — a `date` without `year` prints no year
(`empty year`) *(verified)*. Under **biber**, the BibTeX field names are mapped
automatically (journal → journaltitle, address → location, school →
institution).

Pages: `pages = {97--111}` (double hyphen, or a single one — styles convert);
article numbers: biblatex `eid = {e1002}` or `pages = {e1002}`.

## 5. Identifiers

- **DOI**: bare, `doi = {10.1093/comjnl/27.2.97}`. Not `https://doi.org/…` or
  `doi:…` — styles add the prefix and link (`doi: https://doi.org/https://…`
  otherwise) *(verified)*. Do not repeat the DOI in `url`.
- **URL**: only when there is no DOI or the style guide wants it; never
  `\url{}` inside the field; no spaces (biber percent-encodes them) *(verified)*;
  add `urldate = {2026-11-26}` (biblatex) for online sources.
- **arXiv**: biblatex `eprint = {2101.00001}`, `eprinttype = {arxiv}`,
  `eprintclass = {cs.CL}`; under BibTeX many `.bst` print `eprint` or use
  `howpublished = {arXiv:2101.00001}`. Google Scholar exports preprints as
  `@article` with `journal = {arXiv preprint arXiv:…}` — fix the type, and check
  whether a peer-reviewed version exists (cite it instead, or both if the venue
  wants).
- **ISBN/ISSN**: optional; most styles hide them.

## 6. Dates

- BibTeX: `year = {2020}`, `month = jan` (macro, no braces — styles abbreviate
  or translate it; `{January}` prints as typed).
- biblatex: `date = {2020-01-15}`, ranges `2019/2020`, `urldate = {…}`.
- Forthcoming work: `pubstate = {forthcoming}` (biblatex) or `year = {in
  press}` — check the style guide; never invent a year.
- Same author and year: the style adds `a`/`b`; do not type them.

## 7. Keys, duplicates, comments

- Keys: ASCII, no spaces or `, { } # % ~ \`; a stable scheme
  (`knuth1984literate`, `smith2020deep`). Keys never print; renaming them is pure
  risk late in a project.
- **Duplicates**: BibTeX compares keys case-insensitively and stops at the
  second (`Repeated entry`); biber treats `Smith2020` and `smith2020` as
  different keys and only warns of a case mismatch *(verified)* — so a citation
  with the wrong case works under one tool and fails under the other. Near
  duplicates (same DOI or title under two keys; preprint + published version)
  inflate the list.
- A field given twice: BibTeX keeps the **first** (with a warning), biber
  silently keeps the **last** *(verified)*.
- **BibTeX has no `%` comments**: an entry on a line starting with `%` is still
  read by BibTeX (and printed if cited), while biber ignores it *(verified)*.
  Delete old entries, or wrap them in `@comment{…}`.
- `@string{ieeetpami = "IEEE Transactions on Pattern Analysis and Machine
  Intelligence"}` + `journal = ieeetpami` (no braces) for repeated values;
  `crossref = {key}` / biblatex `xdata` for shared proceedings data.

## 8. Reference managers and exported data

- **Zotero + Better BibTeX**: stable citation keys, automatic export of a
  collection to the project's `.bib` (keep it in sync instead of editing by
  hand); choose the "Better BibLaTeX" format for biber, "Better BibTeX" for
  `.bst` styles. Use its options to brace acronyms and to omit fields you do not
  want (`abstract`, `file`, `keywords`).
- **JabRef**, **Mendeley**, **EndNote**, **Paperpile**: export to BibTeX, then
  run `bib-check.py` — typical damage: ALL-CAPS names, missing `and`, titles in
  double braces, `abstract` fields with `%` or `&`, `month = {January}`, DOIs
  stored as URLs.
- **Google Scholar** BibTeX is a starting point, not data: abbreviated
  venues, missing DOIs and pages, preprints as journals, conference papers as
  `@article`. Prefer the publisher's export or the DOI itself:
  `curl -LH "Accept: application/x-bibtex" https://doi.org/<DOI>` returns
  Crossref's BibTeX (when the network allows) — still check names and capitals.
- Keep one `.bib` per project (or a shared library plus `\nocite`-free
  citing); biblatex/BibTeX print only cited entries, so a large library file is
  fine.

## 9. Verifying every entry (before submission or deposit)

- Each entry checked against an authoritative source (publisher page, DOI,
  library catalogue, official gazette for legislation): authors and their
  order, title, year, venue, volume/number/pages, edition, DOI. The year in the
  key is not evidence.
- Retractions and corrections: check the DOI's publisher page (Crossref shows
  "updated by" notices); do not cite retracted work without saying so.
- Preprints superseded by published versions are updated.
- Read the compiled reference list in the PDF — not only the `.bib`: names with
  particles, organisations, accents, capitalisation and URLs print the way the
  style guide wants.
- `python3 scripts/bib-check.py refs.bib` reports structure, names, titles,
  identifiers, encoding, dates and type problems; `scripts/audit-tex.py`
  cross-checks the citations against the `.bib`.
