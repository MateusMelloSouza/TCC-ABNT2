# STATUS — {{TITLE}}

> Single source of truth between writing sessions. Re-measured at the start of
> every session (`tools/audit-tex.py`, `tools/compile-check.sh`); never edited
> from memory. Last update: {{DATE}} (sessão {{SESSION}}).

## Project

| Item | Value |
|---|---|
| Author / course / institution | {{AUTHOR}} — {{COURSE}} — {{INSTITUTION}} |
| Document type | {{DOCTYPE}} (TCC de graduação / especialização / dissertação / tese) |
| Template profile | {{TEMPLATE}} (see `TEMPLATE.md`) |
| Main file / compile chain | `{{MAIN}}` — {{CHAIN}} |
| Citation stack | {{CITATION_STACK}} |
| Norm editions adopted | NBR 10520: {{ED10520}} · NBR 6023: 2018 · NBR 6028 keywords separator: {{KWSEP}} · NBR 14724: {{ED14724}} (decided with: {{DECIDED_BY}}) |
| Orientador / banca / dates | {{ORIENTADOR}} · banca: {{BANCA}} · defesa: {{DEFESA}} · depósito: {{DEPOSITO}} |
| Version control | {{VCS}} (git strongly recommended; otherwise snapshot before bulk edits) |

## Invariants (last build)

| Invariant | Value | Source |
|---|---|---|
| Pages | {{PAGES}} | `main.log` |
| LaTeX errors (real) / benign notices | {{ERRORS}} / {{BENIGN}} | `compile-check.sh` |
| Undefined citations / references | {{UNDEF_CITES}} / {{UNDEF_REFS}} | `main.log` |
| Floats: captions = sources | {{FLOATS}} | `audit-tex.py` |
| `.bib` entries = cited keys | {{BIB}} | `audit-tex.py` |
| Overfull boxes / float too large | {{OVERFULL}} / {{FLOAT_TOO_LARGE}} | `main.log` |
| Resumo / abstract words | {{RESUMO}} / {{ABSTRACT}} | `audit-tex.py` |

## Chapters (textual elements)

| File | Section | Words | State | Notes |
|---|---|---|---|---|
{{CHAPTER_ROWS}}

State legend: `empty` · `scaffold` · `draft` · `reviewed by orientador` · `frozen`.

## Pre-textual / post-textual elements

| Element | State |
|---|---|
| Capa / folha de rosto metadata | {{META_STATE}} |
| Ficha catalográfica | pending — request from the library with the final page count (do last) |
| Folha de aprovação | template / signed PDF |
| Resumo / Abstract | {{RESUMO_STATE}} |
| Listas (figuras, tabelas, quadros, siglas, símbolos) | {{LISTS_STATE}} |
| Referências (`.bib`) | {{BIB_STATE}} |
| Apêndices / anexos | {{APPENDICES_STATE}} |

## Decisions log

| Date | Decision | Decided by |
|---|---|---|
| {{DATE}} | Workflow created; baseline measured | — |

## Open debts (summary — details and ids in `TODO.md`)

- …

## Done (moved from TODO, most recent first)

- …
