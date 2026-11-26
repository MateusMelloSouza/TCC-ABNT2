# TEMPLATE profile — {{TEMPLATE_NAME}}

> What this project's template does, verified by grep and by a clean compile —
> so no session rediscovers it. Profiles for common classes ship with the skill
> (`references/templates/`); this file records the project's own facts.

## Identification
- Class / style files: <e.g. `IEEEtran.cls` from TeX Live, or local `uni-thesis.cls`>; `\documentclass` in: <file>
- Source and version: <publisher/graduate-school URL or Overleaf template, date/version>; formatting guide: <URL/file>
- Engine: <pdfLaTeX/LuaLaTeX/XeLaTeX> · citations: <biblatex style=… / natbib + .bst / …> → tool: <biber/bibtex>
- Extra tools: <makeglossaries / makeindex / -shell-escape / none>

## Binding rules
- Files never edited: <the .cls/.sty>; overrides go in: <main.tex after the preamble>
- Fonts, margins, spacing, page limit, caption style, citation style: <fixed by the template / venue>
- Required front/back matter and statements: <…>

## Metadata macros
| Macro | Meaning | Printed on |
|---|---|---|
| `\title{}` | … | title page, PDF metadata |

## Content commands
```latex
% figure / table / algorithm / theorem blocks exactly as the template prescribes
```

## Known-benign compile notices (`benign-notices.txt`)
- <message> — why it is benign (PDF verified complete and correct)

## Genuine quirks and sanctioned fixes
- <symptom → cause → fix (where)>

## Demo residue shipped with the template (audit for it)
- <sample text, example bibliography entries, placeholder names, dates, logos>
