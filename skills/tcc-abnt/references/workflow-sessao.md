# Thesis writing-session workflow (5 phases)

A repeatable loop for steady, low-friction progress on a long document across
many days. Every session starts with full context and ends with the project
compiling and a written record of what changed and what is next. Run the
phases in order. Keep the conversation in the user's language; keep the thesis
content in pt-BR.

State lives in the project under **`.tcc-workflow/`** (create it with
`scripts/init-workflow.py <project>`; nothing in it enters the PDF):

| File | Role |
|---|---|
| `STATUS.md` | Living tracker: template profile, per-chapter state, decisions taken (norm editions, conventions), open debts. **Single source of truth between sessions.** |
| `TODO.md` | Numbered debt list with status, owner (author/Claude/orientador) and the session that closed each item. |
| `TEMPLATE.md` | Profile of the institutional template (commands, quirks, rules) — see `templates/README.md`. |
| `session-log/YYYY-MM-DD-sessao-NN.md` | One narrative per session, from `session-log/_TEMPLATE.md`. |
| `tools/` | Copies of `setup-sandbox-latex.sh`, `compile-check.sh`, `audit-tex.py` so the project is self-contained. |

> A **debt** is anything that must change before the document is final: empty
> chapter, placeholder or template text, missing/invalid reference, compile
> error, formatting deviation, unanswered orientador comment, unread section.

---

## Phase 1 — Start: read, re-measure, reconcile

1. Read `STATUS.md`, `TODO.md` and the **most recent** session log; its
   "Next steps" is the starting agenda.
2. **Re-measure the project instead of trusting the trackers.** Run
   `scripts/audit-tex.py <project>` (placeholders, citation/bib integrity,
   labels, floats without source, unused siglas, word counts) and, if a build
   is possible, `scripts/compile-check.sh` (pages, errors, undefined refs,
   overfull, float-too-large). Record the invariants:

   | Invariant | Where it comes from |
   |---|---|
   | Pages | `main.log` "Output written" |
   | LaTeX errors (`^!`) | `main.log` |
   | Undefined citations / references | `main.log` warnings |
   | Floats: captions = sources | audit script |
   | `.bib` entries = cited keys (no orphans either way) | audit script |
   | Overfull boxes, `Float too large` | `main.log` |

3. **Reconcile.** Trackers drift: sessions do the work, write the log and
   forget to tick the box (a real project had its open-debt list inflated by
   ~40 %, one item marked open that had been closed three sessions earlier,
   and one item numbered with an id already used). Close what the files prove
   closed, add what the audit found, fix contradictions, and keep ids unique.
4. Present a short triage: where the document stands (invariants), the open
   debts by weight, and what the last session wanted to do next.

## Phase 2 — Decide the target and gather material

1. Ask what to work on **this session** (offer the top debts as options). One
   focused target per session beats touching ten files.
2. Ask the questions needed to write it well: scope, key references, results
   to report, orientador instructions, target length. Ask for source material
   (papers, data, notes, feedback, prior drafts) and read it before drafting.
3. Never invent sources or results. If a citation is needed and no reference
   exists, ask for the bibliographic data or insert `% TODO: referência`.

## Phase 3 — Plan and propose the edits

1. Turn the target into a concrete edit plan: files, sections/labels, what
   each paragraph will cover, which references, which figures/tables/equations.
2. Show the plan before large writes and get a go-ahead; small fixes (a
   caption, a typo, one paragraph) just get done.
3. Write in formal pt-BR (see `escrita-academica.md`) with the template's
   commands (see `templates/`). Edit the real files in place; keep diffs
   surgical.
4. Every claim that needs a source uses a real `.bib` key; new sources get a
   proper NBR 6023 entry (`referencias-nbr6023.md`) and are cited.
5. **Safety of edits.** If the project is not under git, snapshot the files you
   will touch (`.tcc-workflow/ARCHIVE-<date>/`) before bulk edits. When
   scripting an edit, encode to bytes first, write to `file.new`, then rename
   over the original — a naive `open(path, "w")` that fails mid-way on an
   encoding error leaves a **zero-byte chapter** (it happened; the snapshot
   saved it). Prefer `git init` + commits over snapshots when the user agrees.

## Phase 4 — Review and compile

1. **Compile** (`compilacao-e-erros.md`): locally/Overleaf as the user does,
   or in the sandbox with `tools/setup-sandbox-latex.sh` once per session and
   `tools/compile-check.sh`.
2. **Triage the log** — report only actionable problems: undefined citations
   (`(????)` → key), undefined references (`??` → label), `!` errors, `Float
   too large`, new overfull boxes. A message is "benign" only after you have
   shown the PDF is complete and correct; record such patterns in
   `TEMPLATE.md` and in `.tcc-workflow/benign-notices.txt` for the script. (The
   classic UniforTeX2 "benign" `Missing \begin{document}` turned out to be a
   real bug that printed a word on the cover — see the template profile.)
3. **Review the prose and the norms** for what changed: citation format and
   case, long-quote block, section numbering, figure/table identification and
   source, keyword format, resumo/abstract consistency with the body.
4. **Verify before acting on any claimed problem** — yours, the trackers', or
   an automated reviewer's. Multi-agent reviews produce confident false
   positives (agents searched for an English expansion of an acronym that was
   expanded in Portuguese; flagged "uncited floats" that were cited by range).
   Read the line in the `.tex`, grep, recompile. Refuting a finding is a
   legitimate outcome; log it.
5. Report what changed (file by file) and the compile result with the
   invariants.

## Phase 5 — Close: log and next steps

1. Update `STATUS.md` (per-chapter state, decisions, invariants) and
   `TODO.md` (close items with the session number, add new ones, keep ids
   unique, never lose an item — diff the id list before/after).
2. Write `session-log/YYYY-MM-DD-sessao-NN.md` from `_TEMPLATE.md`: goal,
   material, what changed (files + summary), decisions, refuted findings, open
   questions for the orientador, compile result (invariants), and an explicit
   **Next steps** list.
3. Give the user a two-line recap and the path to the updated PDF.

---

## Operating principles

- One focused target per session; the PDF compiles at the end of every
  session (or the log says why not and how to fix it).
- `STATUS.md` is the truth between sessions; the log is the narrative of one.
- Surgical, reversible edits; explain what changed and why.
- Never fabricate. Placeholders are explicit (`% TODO`) and tracked.
- The `.tex` files and `main.log` are ground truth; trackers and reviewers are
  claims to verify.
- Decisions that belong to the author or the institution (norm edition,
  keyword separator, list titles, banca names, ficha catalográfica) are
  recorded as decisions, not silently taken.
- Ficha catalográfica is produced by the library from the final page count —
  request it last; it is the usual deposit blocker.
