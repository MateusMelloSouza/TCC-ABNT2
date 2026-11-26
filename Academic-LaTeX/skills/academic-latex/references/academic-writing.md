# Academic writing — register, sections, abstract, integrity

Formatting rules come from the template and the style guide; the conventions
below are what supervisors, examiners and reviewers expect of the prose. Defer
to the field's norms, the venue's instructions, the supervisor's preferences
and the register already established in the document. Write in the
document's language (and spelling variant) even when talking to the user in
another.

## Register and voice

- **Precise and objective**: one claim per sentence where possible; quantify
  ("reduced latency by 18 % (120 → 98 ms)" rather than "greatly improved");
  every claim carries a citation or the evidence of this work.
- **Calibrated**: hedge to the strength of the evidence ("suggests", "is
  consistent with", "may") and state certainty where it is earned. Overclaiming
  is the fastest way to lose reviewers and examiners; so is hedging every
  sentence.
- **Person and voice** depend on the field and venue: "we" is normal in most
  STEM papers (even single-authored, in some fields); "I" is accepted in many
  humanities and social-science theses; impersonal or passive constructions
  dominate in others (and in many non-English academic traditions). Pick the
  convention of the field and the venue, then be consistent.
- **Tense**: present for established knowledge and for what the document
  contains ("Figure 3 shows", "Smith (2020) argues"); past for what was done
  and found in this work (methods, results); present perfect for research
  trends ("has been studied extensively").
- **Terminology**: define each term at first use and keep it; do not vary words
  for elegance ("model", "network", "architecture" for the same thing confuse
  readers). Define every abbreviation at first use (glossaries/acro do it).
- **No** colloquialisms, rhetorical questions, intensifiers ("very", "extremely",
  "clearly"), "etc." closing an enumerable list, unexplained jargon, or vague
  "this" without a noun ("this approach", not "this").

## Paragraphs

Topic sentence → evidence, argument, citation → link to the next idea. Avoid
one-sentence paragraphs and page-long ones. A section opens by saying what it
will do and why; it ends by saying what was established.

## Section by section

**Title** — specific and informative; key terms early; no "A study of",
"Towards" only when the work is genuinely preliminary; a colon subtitle for the
method or setting.

**Abstract** — one paragraph (structured where the field requires): context →
gap or problem → aim → method → main results **with numbers** → conclusion and
implication. Typical limits: 150–250 words for papers, 250–500 for theses —
the binding number is the venue's or school's. No citations, no undefined
abbreviations, no claims the body does not support. Write it last; rewrite it
whenever results change (an abstract quoting an earlier draft's numbers is a
classic audit finding). Keywords: 3–6, not repeating the title, from the field's
vocabulary when one exists.

**Introduction** — funnel from the broad context to the specific problem
(establish the territory, show the gap, state how this work fills it). State
the aim and research questions/hypotheses; list contributions concretely
(common in computing papers as a bullet list); outline the document. No
detailed literature review and no results here (papers may preview the key
result in one sentence).

**Background / related work** — synthesise by theme, comparing approaches and
their assumptions, instead of one paragraph per paper; position this work
explicitly against the closest ones; end with the gap. A comparison table is
useful when the dimensions are clear.

**Methods** — enough detail to reproduce: design; participants or data
(sources, sizes, inclusion criteria, ethics approval); materials and tools
with versions; procedure; parameters; metrics and statistical analysis;
threats to validity. Past tense. Link data and code (repository with DOI)
where the venue expects it.

**Results** — what was found, objectively, in a logical order; every figure
and table called out and interpreted in one sentence ("Table 2 shows that …");
report statistics fully (test, statistic, degrees of freedom, *p*, effect size,
confidence interval) and negative results as results. Interpretation goes to
the discussion unless the field merges them.

**Discussion** — what the results mean; comparison with prior work and
explanation of divergences; implications; **limitations** stated honestly;
directions that follow from them.

**Conclusion** — answer each research question explicitly; state the
contributions; future work traced to the limitations. No new results, data,
figures or citations.

**Thesis-specific** — chapter introductions and summaries that connect
chapters; a consistent story across chapters written at different times
(re-read the whole thesis for contradictions after any major rewrite).

## Common problems (fix on sight)

- Claims without support ("it is well known that …") or with a citation that
  does not support them.
- Contradictions after a rewrite: a method "implemented" in one chapter and
  "proposed" in another; numbers that differ between abstract, text and tables.
  Propagate every change of status or number to the abstract, introduction,
  conclusion and appendices.
- Quoting where a paraphrase with citation is stronger; long quotations in
  STEM writing.
- Figures that are never discussed; tables repeating the text.
- Ambiguous pronouns; false exhaustiveness ("the three methods cited" when four
  are cited).
- Mixed spelling variants (US/UK) or mixed citation styles.
- For writers in a second language: missing or extra articles, false friends,
  very long sentences — short, direct sentences read better in any language.

## Integrity

- **Never fabricate** data, results, quotations or references. When prose needs
  a source the user has not provided, ask for it or leave a visible
  `% TODO: citation needed — <claim>` and say so. A plausible-looking invented
  reference is worse than a gap.
- Paraphrase genuinely and cite; text recycled from the author's own published
  papers follows the venue's or school's rules (usually allowed in a thesis with
  citation and permission).
- Figures and tables from other works need permission or an open licence and a
  credit line.
- **AI assistance**: institutions and publishers have policies (disclosure,
  prohibited uses, authorship). The author must read, understand and be able to
  defend every paragraph; Claude drafts and edits under the author's direction,
  never as an author. Remind the user of disclosure duties when relevant.
- Authorship and acknowledgements follow the venue's criteria (ICMJE, CRediT);
  do not add or remove authors on your own.
