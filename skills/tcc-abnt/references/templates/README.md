# Template profiles — and how to build one for any institution

Almost every Brazilian university (or program, or even orientador) ships its
own abnTeX2 customisation: a `.sty`/`.cls` in the project, wrapper commands
for floats and pre-textual elements, and a `main.tex` full of institutional
macros. The generic rules in this skill are the floor; **the template is the
law of the project**. A profile records what the template does so that the
rules can be applied through it, and so that quirks are not rediscovered every
session.

Profiles that ship with this skill:

| File | Template | Identify by |
|---|---|---|
| `unifortex2.md` | UniforTeX2 — Universidade de Fortaleza (UNIFOR) | `lib/unifortex2.sty`, `\trabalhoacademico`, `\UNIFORfig` |
| `abntex2-modelo.md` | Canonical abnTeX2 model (no institution) | `\documentclass{abntex2}` + `\imprimircapa`, `\imprimirfolhaderosto*` |

Other templates you may meet (profile them on first contact): unifor-abnTeX2
(Erneson Oliveira, PPGIA/UNIFOR), uecetex2 (UECE), abntexto-ufc / ufc-tex
(UFC), ppgcctex (UFERSA/UERN), UFPE/UFPB/UFRN/UnB/USP/UFSC/UFMG/UFRGS
variants, and program-specific forks on Overleaf. Do not assume their
commands from memory — read the files.

## Profiling procedure (15 minutes, once per project)

1. **Inventory.** Run `scripts/audit-tex.py <project>`; note the main file,
   the `\documentclass` line and where it lives, every local `.sty`/`.cls`,
   the `.bib` files and the citation package with its options.
2. **Read the template's own docs**: README, comments at the top of `main.tex`,
   sample chapters. Copy the exact float/table/quadro snippets it prescribes.
3. **List the macros** the template defines, grouped:
   - metadata setters (`\autor`, `\titulo`, `\orientador`, institution, curso,
     banca, dates) and which ones are printed where (capa, folha de rosto,
     folha de aprovação, natureza do trabalho);
   - assembly commands for pre-textual elements and lists;
   - content commands (figure/table/quadro wrappers, caption/source macros,
     algorithm environments, alíneas);
   - citation aliases.
   `find . -name '*.sty' -o -name '*.cls' | xargs grep -nE '\\(new|renew|provide)command|\\newenvironment|\\newfloat|\\DeclareOption'`
   gets you the raw list. While there, look for `\ifthenelse{...}{...}` calls
   with only two arguments in user-facing setters — they swallow the next token
   (the UniforTeX2 bug) and the fix is a `{}` after each call in `main.tex`.
4. **Compile once, clean**, and classify every `!` line as genuine or benign
   (benign = the PDF is complete and the message comes from the template/class
   interaction, e.g. a `\newfloat` notice). Put benign patterns in
   `.tcc-workflow/benign-notices.txt`.
5. **Record binding rules** the template implies: files never to edit, where
   overrides go, required passes (`makeglossaries`?), fonts, caps in titles,
   caption style, keyword separator used in the sample, citation case, list
   titles.
6. **Note demo residue** that ships with the template (sample siglas, glossary
   entries, lorem appendices, placeholder banca/date/curso) so the audit can
   look for it.
7. Save all of it as `.tcc-workflow/TEMPLATE.md` using
   `assets/TEMPLATE-profile.md` as the skeleton, and add the identification
   cue to `STATUS.md`. Contribute it back to the public repository if it may
   help others (one file, same skeleton).

## What a good profile looks like

Short, factual, verified by grep and by a compile — not a norm summary. The
reader is a future session that needs to write a figure block correctly on the
first try, know which `!` messages to ignore, and know which knobs the author
must set before the deposit.
