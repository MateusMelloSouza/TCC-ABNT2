# Writing-session workflow (5 phases)

A repeatable loop for steady, low-friction progress on a long document — a
thesis over months, a paper through several revisions. Every session starts
with full context and ends with the project compiling and a written record of
what changed and what comes next. Run the phases in order. Talk to the user in
their language; write the document in its own language.

State lives in the project under **`.academic-workflow/`** (create it with
`scripts/init-workflow.py <project>`; nothing in it enters the PDF):

| File | Role |
|---|---|
| `STATUS.md` | Living tracker: binding rules, template profile, per-section state, decisions, invariants, open debts. **Single source of truth between sessions.** |
| `TODO.md` | Numbered debt list with priority, owner (author / Claude / supervisor / reviewers) and the session that closed each item. |
| `TEMPLATE.md` | Profile of the project's template — see `templates/README.md`. |
| `session-log/YYYY-MM-DD-session-NN.md` | One narrative per session, from `session-log/_TEMPLATE.md`. |
| `benign-notices.txt` | Regexes of error lines proven harmless (filtered by `compile-check.sh`). |
| `tools/` | Copies of `audit-tex.py`, `bib-check.py`, `compile-check.sh`, `setup-sandbox-latex.sh`, so the project is self-contained. |

> A **debt** is anything that must change before the document is final: an
> empty section, a to-do marker or template text, a missing or invalid
> reference, a compile error, a formatting deviation from the binding rules, an
> unanswered supervisor or reviewer comment, a section nobody has re-read.

---

## Phase 1 — Start: read, re-measure, reconcile

1. Read `STATUS.md`, `TODO.md` and the **most recent** session log; its "Next
   steps" is the starting agenda.
2. **Re-measure the project instead of trusting the trackers.** Run
   `tools/audit-tex.py <project>` (to-do markers, citations ↔ `.bib`, `.bib`
   lint, labels, floats, graphics, abbreviations, abstract, word counts) and,
   when a build is possible, `tools/compile-check.sh` (pages, errors,
   undefined citations/references, overfull boxes, fonts, leftover `??`).
   Record the invariants:

   | Invariant | Where it comes from |
   |---|---|
   | Pages (and page limit, if any) | `main.log` "Output written" |
   | LaTeX errors (`^!` or `file:line:`) | `main.log` |
   | Undefined citations / references, duplicate labels | `main.log` |
   | `.bib` entries = cited keys; lint errors | `audit-tex.py`, `bib-check.py` |
   | Floats captioned, labelled and referenced | `audit-tex.py` |
   | Overfull boxes, `Float too large` | `main.log` |
   | Abstract and total word counts (one fixed method) | `audit-tex.py` |

3. **Reconcile.** Trackers drift: sessions do the work, write the log and
   forget to tick the box. In one real thesis the open-debt list was inflated by
   about 40 %, one item was still open three sessions after it had been closed,
   and one id had been used twice. Close what the files prove closed, add what
   the audit found, fix contradictions, keep ids unique.
4. Present a short triage: where the document stands (invariants), the open
   debts by weight, the next deadline, and what the last session wanted to do.

## Phase 2 — Decide the target and gather material

1. Ask what to work on **this session** (offer the top debts as options). One
   focused target per session beats touching ten files.
2. Ask what is needed to write it well: scope, key references, results to
   report, supervisor or reviewer instructions, target length, deadline. Ask
   for the source material (papers, data, notes, feedback, earlier drafts) and
   read it before drafting.
3. Never invent sources or results. If a claim needs a citation and none was
   provided, ask for it or insert `% TODO: citation needed — <claim>`.

## Phase 3 — Plan and propose the edits

1. Turn the target into a concrete edit plan: files, sections and labels, what
   each paragraph will cover, which references, which figures, tables or
   equations.
2. Show the plan before large writes and get a go-ahead; small fixes (a
   caption, a typo, one paragraph) just get done.
3. Write in the document's language and register (`academic-writing.md`) with
   the template's commands (`templates/`). Edit the real files in place; keep
   diffs surgical.
4. Every claim that needs a source uses a real `.bib` key; new sources get a
   complete, verified entry (`bibliography.md`) and are cited.
5. **Safety of edits.** If the project is not under git, snapshot the files you
   will touch (`.academic-workflow/ARCHIVE-<date>/`) before bulk edits. When
   scripting an edit, encode to bytes first, write to `file.new`, then rename
   over the original — a naive `open(path, "w")` that fails half-way on an
   encoding error leaves a **zero-byte chapter** (it happened; the snapshot
   saved it). Suggest `git init` + commits when the user agrees.

## Phase 4 — Review and compile

1. **Compile** the way the user does (Overleaf, editor, CLI) or in the sandbox
   with `tools/setup-sandbox-latex.sh` (once) and `tools/compile-check.sh`.
2. **Triage the log** — report only actionable problems: undefined citations
   (key), undefined references (label), real `!` errors, `Float too large`, new
   overfull boxes. A message is "benign" only after you have shown the PDF is
   complete and correct; record such patterns in `TEMPLATE.md` and in
   `benign-notices.txt`. (A template's famous "harmless" `Missing
   \begin{document}` turned out to print a stray word on the cover page.)
3. **Review what changed**: citation form, cross-references, figure/table
   captions and call-outs, terminology, numbers against tables, abstract still
   consistent with the body.
4. **Verify before acting on any claimed problem** — yours, the trackers', or an
   automated reviewer's. Multi-agent reviews produce confident false positives
   (an acronym "never expanded" that was expanded in another language;
   "unreferenced floats" referenced through a range). Read the line, grep,
   recompile. Refuting a finding is a legitimate outcome; log it.
5. Report what changed, file by file, and the compile result with the
   invariants.

## Phase 5 — Close: log and next steps

1. Update `STATUS.md` (per-section state, decisions, invariants) and
   `TODO.md` (close items with the session number, add new ones, keep ids
   unique, never lose an item — compare the id list before and after).
2. Write `session-log/YYYY-MM-DD-session-NN.md` from `_TEMPLATE.md`: goal,
   material, what changed (files + summary), decisions, refuted findings, open
   questions for the supervisor or co-authors, compile result (invariants) and
   an explicit **Next steps** list.
3. Give the user a two-line recap and the path to the updated PDF.

---

## Operating principles

- One focused target per session; the PDF compiles at the end of every session
  (or the log says why not and how to fix it).
- `STATUS.md` is the truth between sessions; the log is the narrative of one.
- Surgical, reversible edits; explain what changed and why.
- Never fabricate. Placeholders are explicit (`% TODO`) and tracked.
- The `.tex`, `.bib` and `.log` files are ground truth; trackers and reviewers
  are claims to verify.
- Decisions that belong to the author, the supervisor, the co-authors or the
  institution (style edition, spelling variant, what goes in an appendix,
  co-author order, what to answer a reviewer) are recorded as decisions, not
  silently taken.
- Deposit and submission steps with external lead times (signatures, ethics
  approval numbers, copyright forms, graduate-school format review, library
  cataloguing) go into `TODO.md` early with their owner — they are the usual
  last-minute blockers.
