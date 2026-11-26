# Final review — pre-submission / pre-defense audit and the multi-agent pattern

Use this when the user asks to "review the whole thesis", "check everything
before I submit", "audit the references", or before a defense or deposit. It
condenses what audits of complete theses and papers actually found, in the
order that catches the most with the least effort. Run `scripts/audit-tex.py`,
`scripts/bib-check.py` and `scripts/compile-check.sh` first — half of the
checklist is mechanical. Report findings to the user before editing, and do
not rewrite prose that was not part of the request (an approved thesis text is
the author's).

## A. Mechanical integrity (scripts first, then eyes)

- Build from scratch: 0 real errors, 0 undefined citations and references, 0
  duplicate labels, no `Float too large`; record pages, overfull count and
  page size as the baseline.
- Citations ↔ `.bib`: every key resolves (watch letter case); every listed entry
  is cited; no duplicates (same DOI or title under two keys); `bib-check.py`
  reports no errors.
- Floats: every figure and table has a caption, a label after it, and a
  reference in the text before it appears; no floats drifting far from their
  reference (the float-queue problem, `formatting.md` §4).
- Equations: numbered only if referenced; punctuated.
- Graphics: no missing files, no letter-case mismatches (they compile on
  Windows/macOS and fail on Overleaf, Linux and arXiv), vector formats for
  plots, readable text in figures.
- Placeholders: no to-do markers, `\todo`, lipsum/blindtext, mwe example
  images, template demo text, "??" or "[?]" in the PDF text.
- PDF: fonts embedded, no Type 3, metadata right (empty for anonymous review),
  bookmarks present, page size as required.

## B. Sources and citations

- Each reference verified against an authoritative source (publisher page,
  DOI, catalogue): authors and order, title, year, venue, volume/issue/pages,
  edition. Keys and memory are not evidence.
- Every claim attributed to a source is supported by that source at the cited
  location — spot-check the load-bearing ones; downgrade or remove
  attributions you cannot confirm (an explicit "[unverified]" beats a fabricated
  attribution).
- Preprints replaced by published versions; retracted works flagged.
- One citation style, applied by the style package, matching the guide and
  edition the venue/institution requires; quotations with page numbers;
  secondary citations handled as the guide says.
- Names with particles, organisations, accents and capitalisation correct in
  the **compiled** list.

## C. Structure and presentation

- Front matter in the required order and wording (title page, declaration,
  abstract(s), acknowledgements, lists); back matter complete.
- Abstract within the limit, consistent with the body's current numbers;
  keywords present; second-language abstract a faithful translation.
- Table of contents mirrors the headings; numbering depth sensible; no
  single-child subsections.
- Captions consistent (position per style, capitalisation, final periods);
  tables with booktabs-style rules, numbers aligned, units in headers.
- Terminology, spelling variant, abbreviations (expanded once, listed only if
  used), number formatting and units consistent throughout.
- Layout untouched where the template forbids changes; margins respected by
  every float (overfull boxes in the margin are visible violations).

## D. Content coherence

- Status of every artefact ("implemented", "evaluated", "proposed") identical
  across abstract, introduction, methods, results, conclusion and appendices —
  a rewrite that changed one chapter and not the others is the most common
  serious defect.
- Research questions/objectives ↔ conclusion: each one answered; every piece of
  future work traces to a stated limitation.
- Numbers identical wherever they are quoted (abstract, text, tables, figures),
  with denominators and units.
- Figures and tables discussed in the text, not just referenced.

## E. Venue / institution compliance

- Page and word limits (with the venue's counting rule), required statements
  (data availability, ethics, funding, conflicts, contributions), anonymity
  rules, supplementary-material rules, file-format requirements, PDF/A.
- The template and class unmodified; the bibliography style the one required.
- See `submission.md` for the full lists per venue type.

## The multi-agent review pattern (Claude Code, Cowork)

For a complete thesis or a paper before a deadline, one reviewer misses things
and a hundred raw findings overwhelm the author. What worked on real
documents:

1. **Independent reviewers with one lens each** (read-only, no edits):
   technical and numeric consistency · sources and citations · structure and
   presentation against the binding rules · language and register · coherence
   across chapters · visual check of the rendered PDF (page images). Give each
   the checklist above, the template profile and the project's binding rules
   ("the class file is never edited", "text approved by the committee on <date>
   is not rewritten").
2. **Adversarial verification**: for every high/medium finding, one skeptic
   instructed to *refute* it against the `.tex`, the `.bib`, the log and the
   PDF. Expect a large share of confident findings to be refuted (an acronym
   "never expanded" that was expanded in another language; "unreferenced
   floats" referenced through a range; a "wrong author order" that was a
   different paper).
3. **Apply in small batches, recompile, compare invariants** (pages, errors,
   undefined references, floats, `.bib` = cited, overfull). A longer caption can
   push floats and change pages — re-check.
4. **Log refuted findings** with the reason, so the next round does not
   rediscover them, and record decisions that belong to the author, the
   supervisor or the venue as decisions.

Keep runs scoped (one lens per agent); very large fan-outs die on context
limits — cluster the skeptics by theme instead of one per finding.
