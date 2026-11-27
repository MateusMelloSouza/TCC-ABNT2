# Pre-deposit review: ABNT audit checklist and the multi-agent pattern

Use this when the user asks to "review the whole thesis", "check ABNT before
deposit", "audit sources and citations", or before the defense. It condenses
what real audits of complete theses found, in the order that catches the most
with the least effort. Run `scripts/audit-tex.py` and `scripts/compile-check.sh`
first — half of the checklist is mechanical.

## A. Mechanical integrity (script first, then eyes)

- Build from scratch: 0 `!` errors (benign template notices excepted), 0
  undefined citations, 0 undefined references, no `Float too large`; record
  pages and overfull count as the baseline.
- `.bib` ↔ text: every `\cite` resolves; every entry cited; no duplicates; no
  demo/placeholder entries; no `TODO`.
- Floats: every figure/table/quadro has identification above **and** source
  below; every one is called out in the text before it appears; captions and
  sources balanced (count them).
- Labels: no orphan labels on floats/equations that were meant to be cited;
  three equations "numbered but never cited" is a typical finding.
- Placeholders: no `lipsum`, "Lorem ipsum", template demo text (errata, ficha,
  agradecimentos, glossário, siglas of another discipline), `XXX`, `??`.

## B. Sources and citations (NBR 6023 / 10520)

- Each reference verified against an authoritative source (publisher page,
  DOI, DOU for legislation): authors and order, title, year, venue, volume/
  number/pages, edition. Keys and prior notes are not evidence.
- Compound surnames and entity authors print correctly in the compiled list
  and in citations (`{\relax Van Horn}`, `{{BRASIL}}`).
- Imprenta of proceedings complete (`Piscataway: IEEE`, `New York: ACM`,
  `Cham: Springer`); no `[S. l.: s. n.]` where avoidable; place names as in
  the source.
- Every claim attributed to a source is actually supported by that source at
  the cited location (spot-check the load-bearing ones; downgrade or remove
  attributions you cannot confirm — better an explicit "[assumed]" than a
  fabricated attribution).
- Citation form uniform (2002 caps or 2023 initial caps); multiple citations
  alphabetical; *et al.* policy consistent; direct quotes have pages; no bold
  inside quotes without `grifo nosso`; no citations in the Conclusão unless the
  institution allows normative boundary conditions there.
- No `<URL>` brackets if the institution follows NBR 6023:2018; `Acesso em`
  dates present for online sources.

## C. Structure and presentation (NBR 14724 / 6024 / 6027 / 6028)

- Pre-textual elements in order; folha de aprovação real (or the signed PDF);
  ficha catalográfica real (requested from the library with the final page
  count — do it last); dedicatória/epígrafe either real or removed.
- Resumo/abstract: 150–500 words, faithful to each other and to the body's
  current numbers; keywords 3–5, separator per institution, consistent between
  languages.
- Sumário: entries match the titles; no entry with the page number glued to
  the title (shorten the title); no blank page in the pre-textual block
  (`\glsaddall`/`\phantomsection` whatsits can expel one).
- Lists: siglas only the ones used; símbolos in order of appearance; empty
  lists disabled; list titles per type ("Lista de figuras" when quadros have
  their own list — or the template's title if the institution says so).
- Sections: numbering without trailing period, five levels maximum, no
  single-child subsections, primary sections on a new page.
- Margins respected by every float and table (overfull boxes into the right
  margin are visible violations); font reductions never below 10 pt for
  readable tables; sources in 10 pt.
- Tabela vs quadro classification; IBGE open sides for tabelas; closed borders
  for quadros; both listed in their own lists.
- PDF bookmarks/anchors correct (an "APÊNDICES" bookmark pointing at the
  glossário is a `\phantomsection` omission in the template's command —
  override it in `main.tex`, never in the `.sty`).

## D. Content coherence

- Status of every artefact ("concluído", "em desenvolvimento", "projetado")
  identical across resumo, abstract, introdução, metodologia, resultados,
  conclusão, appendices — a rewrite that changed one file and not the others
  is the most common serious defect.
- Objetivos específicos ↔ conclusão: each objective answered; every "trabalho
  futuro" traces to a stated limitation.
- Numbers: same figure everywhere it is quoted (resumo, tables, text);
  denominators present; decimal comma.
- Terminology and acronyms consistent; foreign words italicised; figures with
  English labels annotated.

## The multi-agent review pattern (Claude Code / Cowork)

For a complete thesis, one reviewer misses things and a hundred findings
overwhelm the author. What worked on real documents:

1. **Independent reviewers with one lens each** (read-only, no edits):
   technical/numeric consistency · ABNT sources & citations · ABNT structure &
   presentation · language/register · coherence with the body · visual QA of
   the rendered PDF (page images). Give each the checklist above, the template
   profile and the project's binding rules ("`.sty` is never edited", "text
   approved by the banca on <date> is not to be rewritten").
2. **Adversarial verification**: for every high/medium finding, one skeptic
   instructed to *refute* it against the `.tex`, the `.bib` and the log.
   Expect a third of confident findings to be refuted (an acronym "not
   expanded" that was expanded in Portuguese; "uncited floats" cited by range;
   a "wrong author order" that was the sister paper).
3. **Apply in small batches, recompile, compare invariants** (pages, errors,
   undefined refs, overfull, captions = sources, `.bib` = `.bbl`). A fix that
   lengthens a caption can push floats and change pages — re-check.
4. **Log refuted findings** with the reason, so the next wave does not
   rediscover them, and record decisions that belong to the author or the
   library as decisions.

Keep sessions short and scoped (one lens per run); very large fan-outs die on
context limits — cluster the skeptics by theme instead of one per finding.
