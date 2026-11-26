# Templates — profiles that ship with the skill, and how to profile any other

Almost every venue and many universities ship their own LaTeX template: a
class (`.cls`) or style (`.sty`), a sample `main.tex` full of macros, sometimes
a `.bst`. The generic rules in this skill are the floor; **the template is the
law of the project**. A profile records what the template does, so that the
rules can be applied through it and its quirks are not rediscovered every
session.

## Profiles in this folder

| File | Covers | Identify by |
|---|---|---|
| `publisher-classes.md` | IEEEtran, acmart, elsarticle, llncs, REVTeX 4.2, amsart — verified preambles, citation setup, rules, pitfalls | `\documentclass{IEEEtran}`, `{acmart}`, `{elsarticle}`, `{llncs}`, `{revtex4-2}`, `{amsart}` |
| `thesis-classes.md` | standard classes + geometry/setspace (the bundled skeleton), memoir, KOMA-Script, classicthesis, university classes on CTAN | `book`/`report`/`memoir`/`scrbook`/`scrreprt`, `\usepackage{classicthesis}`, a `*thesis*.cls` |

Brazilian abnTeX2 templates (UniforTeX2 and other university forks): the
dedicated `tcc-abnt` skill has full profiles.

## Where templates come from

- Journals and conferences: the author instructions page (often an Overleaf
  template link). Use the **current** version — old copies from colleagues
  carry old rights blocks and options.
- Universities: the graduate school, the library or the department (look for
  "thesis template LaTeX" on their site); Overleaf's gallery (search the
  university's name — check whether it is official or student-made); CTAN hosts
  several official classes (see `thesis-classes.md`).
- Unofficial templates are common: verify against the official formatting
  guide, which wins when they disagree.

## Profiling procedure (about 15 minutes, once per project)

1. **Inventory.** `scripts/audit-tex.py <project>`: main file, `\documentclass`
   and where it lives, local `.cls`/`.sty`, `.bib` files, citation stack,
   engine, extra tools (makeglossaries, shell escape).
2. **Read the template's own documentation**: README, the comments at the top
   of the sample `main.tex`, sample chapters, the class's PDF manual
   (`texdoc <class>` for CTAN classes). Copy the exact figure/table/abstract
   snippets it prescribes.
3. **List the macros** the template defines, grouped:
   - metadata setters (title, author, degree, department, supervisor,
     committee, dates) and where each is printed;
   - assembly commands for front matter (title page, declaration, abstract,
     lists) and their required order;
   - content commands (float wrappers, caption/source macros, theorem styles);
   - options (draft/final, print/online, language, anonymity).
   `grep -nE '\\(new|renew|provide)command|\\newenvironment|\\DeclareOption|\\newif' *.cls *.sty`
   gives the raw list. While there, look for user-facing setters built on
   `\ifthenelse{…}{…}` **with only two arguments**: the missing "else" branch
   swallows the next token in `main.tex` (one university template silently ate
   the command after each boolean setter and printed its argument on the cover
   page; the fix was `{}` after each call in `main.tex`).
4. **Compile once, cleanly**, and classify every `!` line and warning as genuine
   or benign (benign = the PDF is complete and correct and the cause is
   understood). Put benign patterns in `.academic-workflow/benign-notices.txt`.
5. **Record binding rules**: files never to edit (the class), where overrides go
   (`main.tex` after the preamble), required passes and tools, fonts, page
   limits, caption style, citation style, mandatory sections and statements.
6. **Note demo residue** the template ships with — sample text, example
   references, placeholder names/dates/degree, demo glossary or abbreviation
   entries, lorem ipsum appendices — so the audit can look for it.
7. Save it as `.academic-workflow/TEMPLATE.md` (skeleton:
   `assets/TEMPLATE-profile.md`) and note the identification cue in
   `STATUS.md`. If it may help others, contribute it back to the skill's
   repository (one file, same skeleton, everything verified).

## Rules for working inside any template

- **Never edit the class or style file** — not for the venue (they replace it
  with theirs), not for the university (the next template update overwrites it).
  Overrides go in the preamble of `main.tex`, after the template is loaded, and
  only for real defects or explicit institutional requirements.
- Use the template's commands for its elements (title page, abstract, floats),
  even when a standard LaTeX command would also work.
- Do not load packages that fight the class's layout (`geometry`, `titlesec`,
  `setspace`, font packages in publisher classes) unless the instructions say so.
- Report template defects to the user with the evidence (log line, page) and
  the minimal fix; leave the decision to them.

## What a good profile looks like

Short, factual, verified by grep and by a compile — not a summary of the style
guide. Its reader is a future session that must write a figure block correctly
on the first try, know which messages to ignore, and know which knobs the author
still has to set before submission.
