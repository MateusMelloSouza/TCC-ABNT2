# Submission and deposit — journals, conferences, arXiv, theses

Every venue publishes author instructions; they override everything here. Read
them first, list their hard requirements in `STATUS.md`, and check each one in
the final PDF — not in the source.

## Contents
1. Checks for every PDF you send
2. Journals
3. Conferences (double-blind review, page limits, camera-ready)
4. arXiv and other preprint servers
5. Thesis deposit (graduate school, library, repository)
6. Revisions

## 1. Checks for every PDF you send

```
pdfinfo main.pdf          # pages, page size (A4 595x842 pt / Letter 612x792 pt), title/author metadata
pdffonts main.pdf         # every font "emb yes"; no "Type 3" (bitmap fonts many venues reject)
pdftotext main.pdf - | grep -nE '\?\?|\[\?\]|\(\?\)|TODO|FIXME|Lorem'   # unresolved refs, citations, leftovers
```
`scripts/compile-check.sh` runs all three. Also: hyperlinks work, bookmarks
present (hyperref), no visible overfull lines in the margin, figures readable at
100 % zoom, every page in the expected orientation.

Type 3 fonts usually come from figures (matplotlib's default PDF font type is
Type 3: set `rcParams["pdf.fonttype"] = 42` and re-export) or from old bitmap
font packages. Unembedded base fonts in included PDFs: re-export the figure with
embedded fonts, or as a last resort re-distill the final PDF
(`gs -dPDFSETTINGS=/prepress -dEmbedAllFonts=true …` — check the result again).

## 2. Journals

- Use the journal's template unmodified: no changes to fonts, margins, line
  spacing, caption or heading styles; no `\vspace{-…}` to gain space. Editors
  return papers for layout hacks.
- Follow the reference style through the template's `.bst` or the requested
  biblatex style; some journals ask for the `.bbl` content pasted into the
  `.tex` (a single-file submission): run BibTeX, then replace
  `\bibliography{…}` with the contents of `main.bbl`.
- Single-file or flat submissions: `latexpand main.tex > flat.tex` (TeX Live)
  inlines `\input`/`\include` files; check that it still compiles.
- Figures as separate files when required (often PDF/EPS/TIFF/PNG at a given
  resolution), named as instructed; no spaces or special characters in file
  names.
- Typical extra items: cover letter, highlights, graphical abstract, ORCID iDs,
  data/code availability statement, funding, conflicts of interest, CRediT
  author contributions, ethics approval, suggested reviewers, supplementary
  material. Put each in `TODO.md` with its owner.
- Overleaf's "Submit" menu sends projects directly to many journals and
  repositories.

## 3. Conferences

**Page limits** — check whether references, appendices and the ethics/impact
statement count. Gain space by cutting text, not by shrinking floats below
legibility or editing the template.

**Double-blind review** — remove everything that identifies the authors:
- author names and affiliations (`acmart`: `[review,anonymous]`; other
  classes: the venue's anonymous option or placeholder authors);
- acknowledgements and funding (add back for camera-ready);
- self-citations in the first person ("our previous work [3]") → third person
  ("Smith et al. [3] showed"); cite as usual, do not omit relevant own work
  unless the venue says so;
- links to repositories under your name → anonymised services or "available
  after review"; supplementary files must be anonymous too;
- **PDF metadata**: `\hypersetup{pdfauthor={}, pdftitle={…}}`; check
  `pdfinfo main.pdf` (Author, Creator fields); figures exported from tools can
  embed user names — re-export or check with `pdfinfo` / `exiftool`.
- LaTeX source comments if sources are uploaded (they often contain names and
  private notes).

**Camera-ready** — add authors, affiliations, acknowledgements; the rights
block the publisher gives you after the copyright form (ACM: `\setcopyright{…}`,
`\acmConference`, `\acmDOI`, `\acmISBN` lines from the rights form; IEEE: the
copyright notice text and position the conference specifies); run the venue's
PDF checker (e.g. IEEE PDF eXpress, ACM's TAPS) — they check fonts, page size
and metadata; meet the deadline for the final version, which is usually strict.

## 4. arXiv and other preprint servers

- arXiv compiles TeX sources itself. Its long-documented practice is **not to
  run BibTeX or biber**: include the generated `.bbl` (named like the main
  file). A BibTeX/natbib `.bbl` is plain LaTeX and portable; a **biblatex**
  `.bbl` only loads with the biblatex version that produced it, so it fails if
  arXiv's TeX Live differs from yours — prefer natbib + `.bst` for arXiv, or
  match arXiv's TeX Live year. Check arXiv's current TeX help pages
  (info.arxiv.org/help/submit_tex) before submitting: policies change.
- pdfLaTeX documents: put `\pdfoutput=1` within the first lines of the main
  file so the automatic processing uses pdfLaTeX; image formats must suit the
  engine (PDF/PNG/JPG for pdfLaTeX; EPS for latex+dvips).
- Upload only what the build needs; keep relative paths; file names are
  case-sensitive.
- **Remove comments** — the source is public. Google's `arxiv_latex_cleaner`
  removes comments and unused files.
- No `-shell-escape` (minted, svg, externalized TikZ must be pre-generated).
- Check the target journal's preprint policy first; add the arXiv identifier to
  the `.bib` of later work as `eprint`.

## 5. Thesis deposit

- **Format review** by the graduate school or library: margins, page numbering,
  title page wording, order of front matter, spacing. Run the PDF against their
  checklist; common failures: wrong page size, numbering that restarts, missing
  lists, title page not matching the sample.
- **PDF/A** is often required (archival): `\DocumentMetadata{pdfstandard=a-2b}`
  as the first line (TeX Live 2023+) or the `pdfx` package; validate with
  veraPDF or the repository's validator — figures with transparency and
  unembedded fonts are the usual blockers. Ask which part/conformance they
  require (1b, 2b, 2u, 3b).
- Fonts embedded; bookmarks (hyperref) and PDF metadata (title, author,
  keywords) set; links not colored if the print version requires it.
- Signature/approval pages: scanned signed PDF via `\includepdf`, or digital
  signatures applied **after** the final PDF/A is produced (signing modifies the
  file).
- Published papers included in the thesis: check each publisher's reuse policy
  and include the required citation and copyright line.
- Embargo requests, licences (e.g. CC BY), abstracts in the repository's
  metadata form, ORCID, plagiarism-check submission (text must be extractable:
  `pdftotext` should produce readable text, with ligatures and accents intact).
- Library processes with lead times (catalogue record, ISBN, printed copies,
  binding) go into `TODO.md` early.

## 6. Revisions

- Keep the submitted version (git tag or copy) before changing anything.
- Response letter with every comment answered (`new-project.py --type letter`).
- Line numbers in the revised manuscript (`lineno`) and a marked-up version
  (`latexdiff submitted.tex revised.tex > diff.tex`, `--flatten` for multi-file
  projects) when the journal asks.
- Re-run the full audit (`final-review.md`): revisions are where numbers in the
  abstract stop matching the tables.
