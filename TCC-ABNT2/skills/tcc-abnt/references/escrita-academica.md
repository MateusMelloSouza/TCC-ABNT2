# Escrita acadêmica (pt-BR) — register, sections, resumo, pitfalls

ABNT governs structure and format; the writing conventions below are what
Brazilian bancas expect. Always defer to the orientador's stated preferences
and to the register already established in the document.

## Register and tone

- **Impessoalidade.** Prefer impersonal/third-person constructions:
  "Neste trabalho, analisa-se…", "Observou-se que…", "Os resultados indicam…".
  First-person plural ("Propomos…") is accepted in some fields — match the
  orientador. Avoid first-person singular.
- **Objetividade e clareza.** One idea per sentence where possible; no vague
  intensifiers ("muito", "bastante", "extremamente"), no colloquialisms, no
  rhetorical questions, no "internet-ese" ("como podemos ver", "vamos falar").
- **Precisão.** Every measured number carries its denominator or uncertainty
  (`67,0\% (402/600)`, `12,3 ± 0,4 ms`), and every claim carries its source
  or its evidence. Distinguish what was **built and measured** from what was
  **designed or proposed**; overstating either is the fastest way to lose a
  defense.
- **Tempo verbal.** Metodologia and resultados in the past ("aplicou-se",
  "obteve-se"); fundamentação and discussão in the present; conclusão mixes
  present (findings) and future (trabalhos futuros).
- **Coesão.** Link paragraphs ("Além disso", "Por outro lado", "Dessa forma",
  "Portanto", "Em contrapartida") without overusing them.
- **Formalidade.** No slang, no emojis, no "etc." closing an enumerable list,
  no contractions of register; foreign words in italics; acronyms expanded on
  first use in each of resumo, texto and lists.

## Paragraph structure

Topic sentence → development (evidence, argument, citation) → closing or
bridge. Avoid one-sentence paragraphs and page-long ones. Define every term
and acronym on first use.

## Resumo and abstract (NBR 6028:2021)

- One paragraph, **150–500 words** (TCC, dissertação, tese), concise
  sentences, third person, no bullet points, no citations, no figures, no
  undefined acronyms.
- Order: contexto/problema → objetivo → método → principais resultados →
  conclusão. Numbers with denominators; nothing that is not in the body.
- Then `Palavras-chave: termo um; termo dois; termo três.` — 3 to 5 terms,
  semicolons, lowercase initials (proper nouns excepted), final period. (Older
  templates separate by periods — follow the institution, keep resumo and
  abstract consistent.)
- The Abstract is a **faithful translation** (same claims, same numbers), then
  `Keywords: ...`. Rewrite both together whenever the results change — a
  resumo that cites numbers from an earlier draft is a classic audit finding.
- Count words with one fixed method (`scripts/audit-tex.py` reports it) so the
  number is comparable between sessions.

## How to write each section

**Introdução** — funnel from broad context to the specific problem:
contextualização; **problema de pesquisa** (often a question); **justificativa**
(why it matters, for whom); **objetivo geral** (one) and **objetivos
específicos** (short list, each starting with an infinitive verb — Analisar,
Avaliar, Comparar, Desenvolver, Identificar, Implementar, Investigar, Mensurar,
Propor, Validar, Verificar); a closing paragraph on the organisation of the
work ("Este trabalho está organizado em… A Seção 2 apresenta…"). No literature
review here; no results here.

**Fundamentação teórica / Referencial teórico** — synthesise what others have
established, organised by theme, not a parade of isolated summaries. Every
claim from a source is cited; position your work relative to the literature.

**Trabalhos relacionados** — closest works, what each did, what remains open,
and one comparative quadro if it helps; end by stating the gap this work fills.

**Metodologia / Materiais e métodos** — enough detail to be **reproducible**:
type of research, materials/tools with versions, procedure, data collection,
metrics and how they were computed, threats to validity. Past tense.

**Resultados** — what was found, objectively, with figures/tables that are
called out and sourced; interpretation goes to the discussion unless the field
merges them. Report negative results as results.

**Discussão** — interpret, compare with the literature, explain divergences,
acknowledge limitations.

**Conclusão / Considerações finais** — answer each objetivo específico
explicitly, state the contribution and the limitations, propose trabalhos
futuros. **No new citations, data or figures.**

## Common pitfalls (fix on sight)

- First-person singular ("eu fiz", "acho que").
- Unsupported claims ("é sabido que…", "a literatura mostra…") without a
  citation, or a citation that does not actually support the claim.
- Contradictions between sections after a rewrite (a component "concluído" in
  one appendix and "em desenvolvimento" in the conclusion). Propagate every
  status change to resumo, abstract, introdução, conclusão and appendices.
- Quoting at length when a paraphrase is stronger.
- Mixing citation systems or citation-case styles in one document.
- Ambiguous pronouns ("ele", "isso") and false exhaustiveness ("os três
  citados" when four are cited).
- Figures with English labels in a Portuguese thesis without a note.
- "Capítulo" vs "Seção": the 2024 edition of NBR 14724 speaks of seções; follow
  the institution and be consistent.

## Integrity

Never fabricate data, results or sources. When asked for prose around a claim
that needs a source, use a real reference the user provided or insert a
visible `% TODO: citar fonte` and say so. Plagiarism and invented references
invalidate a TCC; unmarked AI-generated text may violate the institution's
policy — the author must read, understand and own every paragraph.
