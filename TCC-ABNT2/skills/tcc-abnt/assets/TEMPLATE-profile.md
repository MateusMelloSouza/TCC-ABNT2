# TEMPLATE profile — {{TEMPLATE_NAME}}

> What this project's institutional template does, verified by grep and by a
> clean compile — so no session rediscovers it. Skill profiles for known
> templates: `references/templates/` (UniforTeX2, canonical abnTeX2).

## Identification
- Files: <e.g. `lib/xxx.sty`, `xxx.cls`>; `\documentclass` located in: <file>
- Citation stack: <abntex2cite [options] / biblatex-abnt> → compile chain: <pdflatex→bibtex→(makeglossaries)→pdflatex×2>
- Distribution: <Overleaf/GitHub URL, version/date>; institutional manual: <URL>

## Binding rules
- Files never edited: <…>; overrides go in: <main.tex after the preamble>
- Fonts / caps in titles / caption style / list titles: <…>
- Norm editions the template assumes: NBR 10520: <2002/2023> · NBR 6023: <2002/2018> · NBR 6028 keywords: <. or ;>

## Metadata macros (main file)
| Macro | Meaning | Printed on |
|---|---|---|
| `\autor{}` | … | capa, folha de rosto |

## Assembly commands (pre/post-textual)
- `\imprimirXxx{file}` … (order as required)

## Content commands
```latex
% figure / table / quadro / algorithm blocks exactly as the template prescribes
```

## Known-benign compile notices (`benign-notices.txt`)
- <message> — why it is benign

## Genuine quirks and sanctioned fixes
- <symptom → cause → fix (where)>

## Demo residue shipped with the template (audit for it)
- <sample siglas/glossary/appendix files, placeholder dates and banca names>
