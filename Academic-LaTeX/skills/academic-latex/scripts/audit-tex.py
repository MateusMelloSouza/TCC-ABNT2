#!/usr/bin/env python3
"""audit-tex.py — re-measure a LaTeX thesis or paper project instead of trusting notes or memory.

    python3 audit-tex.py [PROJECT_DIR] [--main main.tex] [--out report.md] [--json data.json]
                         [--log build/main.log] [--abstract-limit N] [--require-float-source]
                         [--no-texcount] [--quiet]

What it reports (Markdown on stdout, optionally to files):
  * inventory: main file, document class and options, template family, local .cls/.sty files,
    engine (magic comment / fontspec), citation stack and the tool it needs (biber or bibtex),
    glossary/index tools, shell-escape needs, included files, .tex files never included
  * debts: TODO / FIXME / XXX / TBD markers (inside % comments too: "% TODO:" is how gaps are
    tracked), \\todo{}, lipsum/blindtext, mwe example images
  * citations <-> .bib: keys missing from the .bib, entries never cited, \\nocite{*}, plus the
    .bib lint summary of bib-check.py (duplicate keys, unescaped & %, unprotected capitals, ...)
  * cross-references: undefined, duplicate labels, \\label before \\caption (wrong number),
    floats/equations never referenced, floats placed before their first call-out, hard-coded
    "Figure 3" / "Table 2" references
  * floats without caption or label (and, with --require-float-source, without a source line)
  * \\includegraphics files that do not exist, or exist only with a different letter case
  * abbreviations (glossaries, acro, acronym, abnTeX2 siglas) defined but never used
  * abstract word count (optionally against --abstract-limit) and keywords
  * word counts per file and in total, with the method stated; texcount's total when installed
  * lint: risky or obsolete constructs ($$, eqnarray, \\bf, subfigure, times, package order, ...)
  * log triage when a .log exists: pages, errors, undefined citations/references, duplicate
    labels, rerun requests, overfull/underfull boxes, float too large, missing files, .blg errors
Pure standard library, Python 3.8+. Never modifies project files; reports are written atomically.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, OrderedDict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKIP_DIRS = {"build", "out", "output", ".git", ".academic-workflow", ".tcc-workflow", "node_modules",
             "__pycache__", ".vscode", "_minted", ".idea"}
SKIP_PREFIX = ("ARCHIVE", "_minted")

CLASS_FAMILY = {
    "IEEEtran": "IEEE (IEEEtran)", "acmart": "ACM (acmart)", "elsarticle": "Elsevier (elsarticle)",
    "llncs": "Springer LNCS/LNAI/CCIS (llncs)", "svjour3": "Springer journals, legacy (svjour3)",
    "sn-jnl": "Springer Nature journals (sn-jnl)", "revtex4-2": "APS/AIP (REVTeX 4.2)",
    "revtex4-1": "APS/AIP (REVTeX 4.1)", "amsart": "AMS (amsart)", "amsbook": "AMS (amsbook)",
    "amsproc": "AMS (amsproc)", "aastex631": "AAS journals (AASTeX 6.31)", "aastex7": "AAS journals (AASTeX 7)",
    "mnras": "MNRAS", "jmlr": "JMLR / PMLR", "aa": "Astronomy & Astrophysics", "iopart": "IOP (iopart)",
    "copernicus": "Copernicus journals", "wlscirep": "Scientific Reports (wlscirep)", "achemso": "ACS (achemso)",
    "article": "standard LaTeX class", "report": "standard LaTeX class", "book": "standard LaTeX class",
    "memoir": "memoir", "scrbook": "KOMA-Script", "scrreprt": "KOMA-Script", "scrartcl": "KOMA-Script",
    "abntex2": "abnTeX2 (Brazil, ABNT norms)", "thuthesis": "Tsinghua University (thuthesis)",
    "ut-thesis": "University of Toronto (ut-thesis)", "yathesis": "French thesis (yathesis)",
    "toptesi": "Italian thesis (toptesi)", "msu-thesis": "Michigan State University (msu-thesis)",
    "uothesis": "University of Oregon (uothesis)", "ucthesis": "University of California (ucthesis)",
    "mitthesis": "MIT (mitthesis)", "umthesis": "UMass Amherst (umthesis)", "tufte-book": "Tufte-LaTeX",
    "tufte-handout": "Tufte-LaTeX", "kaobook": "kaobook", "beamer": "beamer (slides)",
    "standalone": "standalone", "tikzposter": "tikzposter (poster)", "a0poster": "a0poster (poster)",
}
VENUE_STY = re.compile(r"^(neurips|nips|icml|iclr|aaai|acl|naacl|emnlp|cvpr|iccv|eccv|wacv|ijcai|interspeech|colm|"
                       r"icassp|spconf|chi|uist|kdd|www|sigconf|miccai|midl|corl|rss|icra|iros)[\w-]*$", re.I)

CITE_DENY = {"citestyle", "setcitestyle", "citeoption", "citetext", "citeindextrue", "citeindexfalse",
             "citesetup", "citeauthorstyle"}
RE_CITE_CMD = re.compile(r"\\([A-Za-z]*[cC]ite[A-Za-z]*|apud|apudonline)\*?")
RE_INPUT = re.compile(r"\\(?:input|include|subfile|loadglsentries)\s*\{([^}]+)\}"
                      r"|\\(?:import|subimport|inputfrom|includefrom)\*?\s*\{([^}]*)\}\s*\{([^}]+)\}")
RE_PKG = re.compile(r"\\(?:usepackage|RequirePackage)\s*(?:\[([^\]]*)\])?\s*\{([^}]+)\}", re.S)
RE_DOCCLASS = re.compile(r"\\documentclass\s*(?:\[([^\]]*)\])?\s*\{([^}]+)\}", re.S)
RE_LABEL = re.compile(r"\\label\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}")
RE_REF = re.compile(r"\\(?:ref|autoref|Autoref|eqref|pageref|cref|Cref|cpageref|Cpageref|vref|Vref|vpageref|"
                    r"nameref|Nameref|fref|Fref|labelcref|namecref|nameCref|lcnamecref|labelcpageref|zcref|zref)"
                    r"\*?\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}|\\(?:crefrange|Crefrange|cpagerefrange)\*?\s*\{([^}]+)\}"
                    r"\s*\{([^}]+)\}|\\hyperref\s*\[([^\]]+)\]")
RE_FLOAT_BEGIN = re.compile(r"\\begin\{(figure\*?|table\*?|sidewaysfigure|sidewaystable|wrapfigure|wraptable|"
                            r"algorithm\*?|listing|quadro|longtable|xltabular|SCfigure|SCtable|figwindow)\}")
RE_EQ_BEGIN = re.compile(r"\\begin\{(equation|align|gather|multline|flalign|alignat|eqnarray)\}")
RE_SECTION = re.compile(r"\\(part|chapter|section|subsection|subsubsection|paragraph|addchap|addsec)\*?\s*[\[{]")
RE_GRAPHICS = re.compile(r"\\(includegraphics|includesvg|includepdf)\*?\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}")
RE_GRAPHICSPATH = re.compile(r"\\graphicspath\s*\{((?:\s*\{[^}]*\})+)\s*\}")
RE_PLACEHOLDER = re.compile(r"\bTODO\b|\bFIXME\b|\bXXX\b|\bTBD\b|\\todo\b|\\missingfigure|\\lipsum|\\blindtext|"
                            r"\\Blindtext|[Ll]orem ipsum|example-image|\[citation needed\]")
RE_STRAY_BREAK = re.compile(r"\\\\\s*\n\s*\\(chapter|section|subsection|subsubsection)")
RE_HARDREF = re.compile(r"(?<![\\\w])(Figures?|Figs?\.|Tables?|Tabs?\.|Sections?|Secs?\.|Chapters?|Ch\.|Equations?|"
                        r"Eqs?\.|Appendix|Algorithm|Listing|Figura|Tabela|Tabla|Se[çc][ãa]o|Cap[íi]tulo|Equa[çc][ãa]o|"
                        r"Abbildung|Tabelle|Kapitel|Abschnitt|Gleichung)(?:~|\s)+\(?([0-9]+(?:\.[0-9]+)*)\)?(?![\w}])")
RE_NEWACRONYM = re.compile(r"\\new(?:acronym|abbreviation)\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}\s*\{([^}]+)\}")
RE_DECLAREACRONYM = re.compile(r"\\DeclareAcronym\s*\{([^}]+)\}\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}", re.S)
RE_ACRO_PKG = re.compile(r"\\acro(?:def)?\s*\{([^}]+)\}\s*(?:\[([^\]]*)\])?")
RE_GLS_USE = re.compile(r"\\(?:[Gg][Ll][Ss][A-Za-z]*|[Aa]cr(?:short|long|full)[a-z]*|glsxtr[A-Za-z]*)\*?\s*"
                        r"(?:\[[^\]]*\])?\s*\{([^}]+)\}")
RE_AC_USE = re.compile(r"\\(?:ac|Ac|AC|acs|acl|acf|acp|Acp|acsp|aclp|Aclp|acfp|Acfp|acsu|aclu|iac|Iac|acsingle|"
                       r"acused|acreset|acuse)\*?\s*\{([^}]+)\}")
RE_SIGLA_ITEM = re.compile(r"\\item\s*\[\{?([^\]\}]+)\}?\]")
RE_KEYWORDS = re.compile(
    r"\\keywords\s*\{((?:[^{}]|\{[^{}]*\})*)\}"
    r"|\\begin\{keyword\}(.*?)\\end\{keyword\}"
    r"|\\begin\{IEEEkeywords\}(.*?)\\end\{IEEEkeywords\}"
    r"|\\palavraschave\s*\{((?:[^{}]|\{[^{}]*\})*)\}"
    r"|(?:\\textbf\{|\\emph\{|\\textit\{)?(?:Keywords|Key words|Index Terms|Palavras-chave|Schl[üu]sselw[öo]rter|"
    r"Mots-cl[ée]s|Palabras clave)\s*[:.}—-]*\s*\}?\s*[:.—-]?\s*([^\n]+)",
    re.S | re.I)
VERBATIM_ENVS = re.compile(r"\\begin\{(verbatim\*?|Verbatim|lstlisting|minted|comment|filecontents\*?|"
                           r"BVerbatim|LVerbatim|alltt)\}.*?\\end\{\1\}", re.S)


# ----------------------------------------------------------------------------- helpers

def read_text(path: Path) -> str:
    for enc in ("utf-8", "utf-8-sig"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="latin-1")


def strip_comments(text: str) -> str:
    """Remove % comments (not \\%), keeping line structure for line numbers."""
    out = []
    for line in text.split("\n"):
        i, n = 0, len(line)
        while i < n:
            c = line[i]
            if c == "\\":
                i += 2
                continue
            if c == "%":
                line = line[:i]
                break
            i += 1
        out.append(line)
    return "\n".join(out)


def blank_verbatim(text: str) -> str:
    """Replace verbatim-like environments by blank lines (keeps line numbers)."""
    return VERBATIM_ENVS.sub(lambda m: "\n" * m.group(0).count("\n"), text)


def line_at(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def is_skipped(path: Path, root: Path) -> bool:
    try:
        rel = path.relative_to(root)
    except ValueError:
        return False
    return any(p in SKIP_DIRS or p.startswith(SKIP_PREFIX) for p in rel.parts[:-1])


def load_bibcheck():
    p = HERE / "bib-check.py"
    if not p.is_file():
        return None
    try:
        spec = importlib.util.spec_from_file_location("bib_check", str(p))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:  # noqa: BLE001
        return None


def find_main(root: Path, explicit: str | None):
    if explicit:
        p = Path(explicit) if os.path.isabs(explicit) else root / explicit
        return (p.resolve() if p.is_file() else None), []
    cands = []
    for p in sorted(root.rglob("*.tex"), key=lambda x: (len(x.relative_to(root).parts), str(x))):
        if is_skipped(p, root):
            continue
        t = strip_comments(read_text(p))
        if re.search(r"\\begin\{document\}", t):
            cands.append(p.resolve())
    pref = root / "main.tex"
    if pref.resolve() in cands:
        return pref.resolve(), cands
    # magic comment in a chapter file: % !TEX root = ../main.tex
    if not cands:
        for p in root.rglob("*.tex"):
            m = re.search(r"%\s*!TEX\s+root\s*=\s*(\S+)", read_text(p)[:500], re.I)
            if m and (p.parent / m.group(1)).is_file():
                return (p.parent / m.group(1)).resolve(), []
        return None, []
    with_class = [c for c in cands if RE_DOCCLASS.search(strip_comments(read_text(c)))]
    return (with_class or cands)[0], cands


def resolve_tex(main_dir: Path, cur_dir: Path, name: str):
    name = name.strip()
    for d in (main_dir, cur_dir):
        for cand in (d / name, d / (name + ".tex")):
            if cand.is_file():
                return cand.resolve()
    return None


def collect_included(main: Path, root: Path):
    """Ordered dict path -> raw text, for main + every file it pulls in (recursively), plus
    project-local .sty/.cls files it loads."""
    files: "OrderedDict[Path, str]" = OrderedDict()
    stack = [(main, main.parent)]
    while stack:
        p, cur = stack.pop(0)
        if p in files or not p.is_file():
            continue
        raw = read_text(p)
        files[p] = raw
        text = strip_comments(raw)
        for m in RE_INPUT.finditer(text):
            if m.group(1):
                target = resolve_tex(main.parent, p.parent, m.group(1))
                if target and target not in files:
                    stack.append((target, p.parent))
            else:
                d = (p.parent / m.group(2)) if m.group(2) else p.parent
                target = resolve_tex(d, d, m.group(3)) or resolve_tex(main.parent, d, m.group(3))
                if target and target not in files:
                    stack.append((target, d))
        for m in list(RE_PKG.finditer(text)) + list(RE_DOCCLASS.finditer(text)):
            ext = ".cls" if m.group(0).lstrip("\\").startswith("documentclass") else ".sty"
            for name in m.group(2).split(","):
                name = name.strip()
                for cand in (main.parent / (name + ext), p.parent / (name + ext)):
                    if cand.is_file() and cand.resolve() not in files:
                        stack.append((cand.resolve(), cand.parent))
                        break
    return files


def words_in(text: str) -> int:
    """Word-count method (stated in the report): comments, math, verbatim, floats' code removed;
    citation/reference/label/graphics commands removed; other command names dropped but their
    brace contents kept; Unicode word tokens counted."""
    t = blank_verbatim(strip_comments(text))
    t = re.sub(r"\$\$.*?\$\$", " ", t, flags=re.S)
    t = re.sub(r"\\\[.*?\\\]", " ", t, flags=re.S)
    t = re.sub(r"\\begin\{(equation|align|gather|multline|eqnarray|flalign|alignat|displaymath|math)\*?\}.*?"
               r"\\end\{\1\*?\}", " ", t, flags=re.S)
    t = re.sub(r"\\\(.*?\\\)", " ", t, flags=re.S)
    t = re.sub(r"(?<!\\)\$[^$]*(?<!\\)\$", " ", t)
    t = RE_CITE_CMD.sub(" ", t)
    t = re.sub(r"\\(?:label|ref|autoref|eqref|pageref|cref|Cref|includegraphics|input|include|usepackage|"
               r"documentclass|newacronym|bibliography|addbibresource|bibliographystyle|graphicspath|"
               r"newcommand|renewcommand|setlength|hypersetup)\*?(?:\[[^\]]*\])?\{[^}]*\}", " ", t)
    t = re.sub(r"\\(?:begin|end)\{[^}]*\}(?:\[[^\]]*\])?", " ", t)
    t = re.sub(r"\\[a-zA-Z@]+\*?", " ", t)
    t = re.sub(r"[{}\[\]&~#^_]", " ", t)
    return len(re.findall(r"\w+(?:[-'’]\w+)*", t))


def parse_cites(text: str):
    """Yield (command, [keys], pos) for every citation command in text (comments stripped)."""
    for m in RE_CITE_CMD.finditer(text):
        cmd = m.group(1)
        if cmd in CITE_DENY or cmd.lower().startswith(("declare", "define", "new", "renew", "provide")):
            continue
        i, n = m.end(), len(text)
        multi = cmd.endswith("cites") or cmd in ("apud", "apudonline")
        groups = []
        while i < n:
            while i < n and text[i] in " \t":
                i += 1
            if i < n and text[i] in "[(":
                close = "]" if text[i] == "[" else ")"
                depth, j = 0, i
                while j < n:
                    if text[j] == "{":
                        depth += 1
                    elif text[j] == "}":
                        depth -= 1
                    elif text[j] == close and depth == 0:
                        break
                    j += 1
                i = j + 1
                continue
            if i < n and text[i] == "{":
                j = text.find("}", i)
                if j < 0:
                    break
                groups.append(text[i + 1:j])
                i = j + 1
                if not multi:
                    break
                continue
            break
        keys = []
        for g in groups:
            for k in g.split(","):
                k = k.strip()
                if k and "#" not in k and "\\" not in k and " " not in k and "=" not in k:
                    keys.append(k)
        if keys:
            yield cmd, keys, m.start()


def kpsewhich(name: str):
    exe = shutil.which("kpsewhich")
    if not exe:
        return None
    try:
        r = subprocess.run([exe, name], capture_output=True, text=True, timeout=20)
        return r.stdout.strip() or ""
    except Exception:  # noqa: BLE001
        return None


# ----------------------------------------------------------------------------- audit

def audit(root: Path, args) -> dict:
    R: dict = {"root": str(root), "problems": [], "notes": []}
    main, cands = find_main(root, args.main)
    if not main:
        R["problems"].append("No main .tex file (with \\begin{document}) found — pass --main.")
        return R
    rel = lambda p: str(Path(p).resolve().relative_to(root)) if str(Path(p).resolve()).startswith(str(root)) else str(p)
    R["main"] = rel(main)
    if len(cands) > 1:
        R["notes"].append("Several files contain \\begin{document}: " + ", ".join(rel(c) for c in cands[:8])
                          + f" — auditing `{rel(main)}` (pass --main to choose another).")
    files = collect_included(main, root)
    tex_files = OrderedDict((p, t) for p, t in files.items() if p.suffix not in (".sty", ".cls"))
    local_styles = [rel(p) for p in files if p.suffix in (".sty", ".cls")]
    S = OrderedDict((p, strip_comments(t)) for p, t in tex_files.items())         # comments stripped
    SV = OrderedDict((p, blank_verbatim(t)) for p, t in S.items())                 # + verbatim blanked
    all_text = "\n".join(SV.values())
    style_text = "\n".join(strip_comments(t) for p, t in files.items() if p.suffix in (".sty", ".cls"))
    R["included"] = [rel(p) for p in files]
    R["local_class_style_files"] = local_styles + sorted(
        rel(p) for p in root.rglob("*") if p.suffix in (".cls", ".sty") and not is_skipped(p, root)
        and p.resolve() not in files)

    # ---- class, template, packages
    dm = RE_DOCCLASS.search(all_text)
    cls = dm.group(2).strip() if dm else "?"
    opts = " ".join((dm.group(1) or "").split()) if dm else ""
    R["documentclass"] = {"class": cls, "options": opts}
    pkgs = OrderedDict()
    for m in RE_PKG.finditer(all_text):
        for name in m.group(2).split(","):
            pkgs.setdefault(name.strip(), " ".join((m.group(1) or "").split()))
    R["packages"] = list(pkgs)
    langs = [x.strip() for x in pkgs.get("babel", "").split(",") if x.strip() and "=" not in x]
    langs += re.findall(r"\\set(?:main|other)language\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}", all_text)
    if not langs:
        langs = [x.strip() for x in opts.split(",") if x.strip() in (
            "english", "american", "british", "ngerman", "german", "french", "spanish", "brazil", "brazilian",
            "portuguese", "italian", "dutch", "polish", "russian")]
    R["languages"] = langs
    family = CLASS_FAMILY.get(cls)
    venue = [p for p in pkgs if VENUE_STY.match(p)]
    if (root / (cls + ".cls")).is_file() or any(Path(s).name == cls + ".cls" for s in local_styles):
        family = f"local class {cls}.cls (institutional or venue template)"
    elif venue:
        family = f"{family or cls} + venue style {', '.join(venue)}"
    elif not family:
        family = f"{cls} (unknown class — profile it)"
    if "classicthesis" in pkgs:
        family += " + classicthesis"
    R["template_family"] = family

    # ---- engine
    head = "\n".join(read_text(main).split("\n")[:30])
    mm = re.search(r"%\s*!\s*TeX\s+(?:TS-)?program\s*=\s*(\w+)", head, re.I)
    needs_unicode = [p for p in ("fontspec", "unicode-math", "polyglossia", "luacode", "luatexja", "xeCJK", "xltxtra")
                     if p in pkgs]
    engine = mm.group(1).lower() if mm else None
    for rcname in (".latexmkrc", "latexmkrc"):
        rc = root / rcname
        if not engine and rc.is_file():
            pm = re.search(r"^\s*\$pdf_mode\s*=\s*(\d)", read_text(rc), re.M)
            engine = {"1": "pdflatex", "4": "lualatex", "5": "xelatex"}.get(pm.group(1)) if pm else None
    if not engine:
        engine = ("xelatex" if "xeCJK" in pkgs else "lualatex") if needs_unicode else "pdflatex (default)"
    R["engine"] = engine
    if needs_unicode and engine.startswith("pdflatex"):
        R["problems"].append(f"{', '.join(needs_unicode)} need LuaLaTeX or XeLaTeX, but the engine looks like pdfLaTeX "
                             "— set `% !TEX program = lualatex` / the editor's compiler.")
    if "inputenc" in pkgs and pkgs["inputenc"] and "utf8" not in pkgs["inputenc"].lower():
        R["problems"].append(f"inputenc option '{pkgs['inputenc']}': save the sources as UTF-8 and use utf8 "
                             "(the default since 2018).")

    # ---- citation stack
    bl = next((p for p in ("biblatex", "biblatex-chicago") if p in pkgs), None)
    bstyle = re.search(r"\\bibliographystyle\s*\{([^}]+)\}", all_text)
    stack, tool = "none detected", None
    if bl:
        o = pkgs[bl]
        backend = re.search(r"backend\s*=\s*(\w+)", o)
        backend = backend.group(1) if backend else "biber"
        style = re.search(r"(?<![a-z])style\s*=\s*([\w-]+)", o)
        stack = f"{bl} [{o or 'default options'}]"
        tool = "biber" if backend == "biber" else "bibtex"
        R["biblatex_style"] = style.group(1) if style else ("chicago" if bl == "biblatex-chicago" else "numeric")
        if "natbib" in pkgs:
            R["problems"].append("biblatex and natbib are both loaded: they are incompatible (use biblatex's "
                                 "natbib=true option for \\citep/\\citet).")
        if bstyle:
            R["problems"].append("\\bibliographystyle is ignored with biblatex (the style is a biblatex option).")
        st = R["biblatex_style"]
        if style and kpsewhich(st + ".bbx") == "":
            R["problems"].append(f"biblatex style '{st}' not found by kpsewhich ({st}.bbx): install its package or fix "
                                 "the name.")
    elif "abntex2cite" in pkgs:
        stack, tool = f"abntex2cite [{pkgs['abntex2cite']}] (BibTeX, ABNT)", "bibtex"
    elif bstyle:
        cit = "natbib" if "natbib" in pkgs else ("apacite" if "apacite" in pkgs else ("cite" if "cite" in pkgs else None))
        if not cit and cls in ("acmart", "elsarticle", "revtex4-2", "revtex4-1", "aastex631", "aastex7", "mnras", "jmlr"):
            cit = f"natbib (loaded by {cls})"
        stack = f"BibTeX with \\bibliographystyle{{{bstyle.group(1)}}}" + (f" + {cit}" if cit else "")
        tool = "bibtex"
        bs = bstyle.group(1).strip()
        if not (root / (bs + ".bst")).is_file() and kpsewhich(bs + ".bst") == "":
            R["problems"].append(f"BibTeX style '{bs}.bst' not found (not in the project, not in the TeX "
                                 "installation).")
    elif re.search(r"\\begin\{thebibliography\}", all_text):
        stack = "manual \\begin{thebibliography} (no .bib file)"
    elif re.search(r"\\(addbibresource|printbibliography)", all_text):
        stack, tool = "biblatex (loaded by the class or template)", "biber"
    R["citation_stack"] = stack
    R["bibliography_tool"] = tool

    # ---- glossaries, index, shell escape
    gl = []
    if re.search(r"\\makeglossaries\b", all_text + style_text):
        gl.append("glossaries with \\makeglossaries → run makeglossaries (latexmk needs the rule in .latexmkrc)")
    if re.search(r"\\makenoidxglossaries\b", all_text + style_text):
        gl.append("glossaries with \\makenoidxglossaries → no external tool")
    if "glossaries-extra" in pkgs and "record" in pkgs.get("glossaries-extra", ""):
        gl.append("glossaries-extra record option → run bib2gls (needs Java)")
    if "acro" in pkgs:
        gl.append("acro → no external tool")
    if "acronym" in pkgs:
        gl.append("acronym package → no external tool")
    if re.search(r"\\makenomenclature\b", all_text):
        gl.append("nomencl → makeindex with nomencl.ist (latexmk needs the rule)")
    if re.search(r"\\makeindex\b", all_text) or "imakeidx" in pkgs:
        gl.append("index → makeindex (latexmk runs it automatically)")
    R["glossary_index_tools"] = gl
    R["glsaddall"] = bool(re.search(r"\\glsaddall\b", all_text))
    shell = [p for p in ("minted", "svg", "gnuplottex", "pythontex", "sagetex", "epstopdf") if p in pkgs]
    if re.search(r"\\tikzexternalize\b", all_text):
        shell.append("tikz externalize")
    R["shell_escape_needed_by"] = [s for s in shell if s != "epstopdf"]

    # ---- orphan .tex files
    R["orphan_tex_files"] = [rel(p) for p in sorted(root.rglob("*.tex"))
                             if not is_skipped(p, root) and p.resolve() not in files]

    # ---- placeholders (raw text: "% TODO" comments are tracked debts)
    ph = []
    for p, raw in tex_files.items():
        for i, line in enumerate(raw.split("\n"), 1):
            if RE_PLACEHOLDER.search(line):
                ph.append(f"{rel(p)}:{i}: {line.strip()[:110]}")
        for m in RE_STRAY_BREAK.finditer(S[p]):
            ph.append(f"{rel(p)}:{line_at(S[p], m.start())}: \\\\ right before \\{m.group(1)} "
                      "(\"There's no line here to end\")")
    R["placeholders"] = ph

    # ---- citations vs .bib
    cited: Counter = Counter()
    for p, text in SV.items():
        for cmd, keys, pos in parse_cites(text):
            for k in keys:
                cited[k] += 1
    nocite_all = "*" in cited
    cited.pop("*", None)
    bibfiles, bib_missing = [], []
    for m in re.finditer(r"\\(?:addbibresource|addglobalbib|addsectionbib)\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}",
                         all_text):
        name = m.group(1).strip()
        if not name.endswith(".bib") and not (main.parent / name).is_file():
            R["problems"].append(f"\\addbibresource{{{name}}} without the .bib extension: biblatex needs the full "
                                 f"file name (\\addbibresource{{{name}.bib}}).")
        cands = [main.parent / name, main.parent / (name + ".bib"), root / name]
        found = next((c for c in cands if c.is_file()), None)
        (bibfiles.append(found.resolve()) if found else bib_missing.append(name))
    for m in re.finditer(r"\\bibliography\s*\{([^}]+)\}", all_text):
        for name in m.group(1).split(","):
            name = name.strip()
            if not name or "#" in name:
                continue
            cands = [main.parent / name, main.parent / (name + ".bib"), root / name, root / (name + ".bib")]
            found = next((c for c in cands if c.is_file()), None)
            if found:
                bibfiles.append(found.resolve())
            elif kpsewhich(name + ".bib") in (None, ""):
                bib_missing.append(name)
    for name in bib_missing:
        R["problems"].append(f".bib file '{name}' is referenced but not found in the project.")
    if not bibfiles and not bib_missing:
        bibfiles = [p.resolve() for p in root.rglob("*.bib") if not is_skipped(p, root)]
        if bibfiles:
            R["notes"].append("No \\addbibresource/\\bibliography found; listing every .bib in the project.")
    bibfiles = list(OrderedDict.fromkeys(bibfiles))
    R["bib_files"] = [rel(p) for p in bibfiles]
    bc = load_bibcheck()
    entries, lint = [], []
    if bc and bibfiles:
        backend = "biber" if tool == "biber" else ("bibtex" if tool == "bibtex" else "unknown")
        entries, lint, _ = bc.check_files(bibfiles, backend)
    elif bibfiles:
        for b in bibfiles:
            for m in re.finditer(r"@([A-Za-z]+)\s*[{(]\s*([^,\s]+)\s*,", read_text(b)):
                if m.group(1).lower() not in ("comment", "string", "preamble"):
                    entries.append({"type": m.group(1).lower(), "key": m.group(2), "fields": {}})
    bib_keys = [e["key"] for e in entries if e["type"] not in ("abnt-options",)]
    option_keys = {e["key"] for e in entries if e["type"] == "abnt-options"}
    bib_lower = {k.lower() for k in bib_keys}
    missing = sorted(k for k in cited if k not in set(bib_keys) and k not in option_keys)
    case_only = [k for k in missing if k.lower() in bib_lower]
    uncited = sorted(k for k in bib_keys if k not in cited) if not nocite_all else []
    R["citations"] = {
        "distinct_cited": len(cited), "bib_entries": len(bib_keys), "nocite_all": nocite_all,
        "missing_in_bib": missing, "case_mismatch": case_only, "uncited_entries": uncited,
        "bib_lint_counts": dict(Counter(x["severity"] for x in lint)),
        "bib_lint": [f"{Path(x['file']).name}:{x['line']} `{x['key']}` [{x['check']}] {x['message']}"
                     for x in lint if x["severity"] in ("error", "warning")],
    }
    if nocite_all:
        R["notes"].append("\\nocite{*} prints every .bib entry, cited or not — usually wrong for a thesis or paper.")

    # ---- labels, references, floats, equations
    labels, dup_labels, refs, ref_first = {}, [], Counter(), {}
    floats, equations, label_before_caption, hard_refs = [], [], [], []
    offset = 0
    for p, text in SV.items():
        for m in RE_LABEL.finditer(text):
            k = m.group(1).strip()
            if "#" in k:
                continue
            if k in labels:
                dup_labels.append(f"{k} ({labels[k][0]}:{labels[k][1]} and {rel(p)}:{line_at(text, m.start())})")
            else:
                labels[k] = (rel(p), line_at(text, m.start()), offset + m.start())
        for m in RE_REF.finditer(text):
            groups = [g for g in m.groups() if g]
            for g in groups:
                for k in g.split(","):
                    k = k.strip()
                    if k and "#" not in k:
                        refs[k] += 1
                        ref_first.setdefault(k, offset + m.start())
        for m in RE_FLOAT_BEGIN.finditer(text):
            env = m.group(1)
            end = re.compile(r"\\end\{" + re.escape(env) + r"\}").search(text, m.end())
            block = text[m.start(): end.end() if end else m.end() + 3000]
            cap = re.search(r"\\(?:caption|Caption|captionof)\b", block)
            lab = RE_LABEL.search(block)
            if cap and lab and lab.start() < cap.start():
                label_before_caption.append(f"{rel(p)}:{line_at(text, m.start() + lab.start())} ({env}, "
                                            f"{lab.group(1)})")
            src = re.search(r"\\(?:fonte|Fonte|source|Source|legend|nota|Nota|floatfoot|note)\b|"
                            r"(?:Source|Fonte|Fuente|Quelle)\s*:|Reprinted|Adapted from|Reproduced", block)
            floats.append({"file": rel(p), "line": line_at(text, m.start()), "env": env,
                           "label": lab.group(1).strip() if lab else None, "caption": bool(cap),
                           "source": bool(src), "pos": offset + m.start()})
        for m in RE_EQ_BEGIN.finditer(text):
            end = re.compile(r"\\end\{" + re.escape(m.group(1)) + r"\}").search(text, m.end())
            block = text[m.start(): end.end() if end else m.end() + 800]
            for lab in RE_LABEL.finditer(block):
                equations.append({"file": rel(p), "line": line_at(text, m.start()), "label": lab.group(1).strip()})
            if not RE_LABEL.search(block):
                equations.append({"file": rel(p), "line": line_at(text, m.start()), "label": None})
            if m.group(1) == "eqnarray":
                pass
        no_caps = re.sub(r"\\caption(?:of)?\s*(?:\[[^\]]*\])?\s*\{(?:[^{}]|\{[^{}]*\})*\}", " ", text)
        for m in RE_HARDREF.finditer(no_caps):
            hard_refs.append(f"{rel(p)}:{line_at(no_caps, m.start())}: \"{m.group(0).strip()}\"")
        offset += len(text) + 1
    undefined_refs = sorted(k for k in refs if k not in labels)
    R["refs"] = {"labels": len(labels), "undefined": undefined_refs, "duplicate_labels": dup_labels,
                 "label_before_caption": label_before_caption, "hard_coded": hard_refs}
    R["floats"] = {
        "count_by_env": dict(Counter(f["env"] for f in floats)),
        "without_caption": [f"{f['file']}:{f['line']} ({f['env']})" for f in floats if not f["caption"]],
        "without_label": [f"{f['file']}:{f['line']} ({f['env']})" for f in floats if not f["label"]],
        "never_referenced": [f"{f['file']}:{f['line']} ({f['env']}, {f['label']})" for f in floats
                             if f["label"] and refs[f["label"]] == 0],
        "before_first_reference": [f"{f['file']}:{f['line']} ({f['env']}, {f['label']})" for f in floats
                                   if f["label"] and refs[f["label"]] and ref_first.get(f["label"], 0) > f["pos"]],
        "without_source": [f"{f['file']}:{f['line']} ({f['env']})" for f in floats
                           if not f["source"] and not f["env"].startswith(("algorithm", "listing"))]
        if args.require_float_source else [],
    }
    R["equations"] = {"count": len({(e['file'], e['line']) for e in equations}),
                      "labelled_never_referenced": [f"{e['file']}:{e['line']} ({e['label']})" for e in equations
                                                    if e["label"] and refs[e["label"]] == 0]}

    # ---- graphics
    gpaths = [main.parent]
    for m in RE_GRAPHICSPATH.finditer(all_text):
        for d in re.findall(r"\{([^}]*)\}", m.group(1)):
            gpaths.append((main.parent / d).resolve())
    missing_gfx, case_gfx, placeholder_gfx = [], [], []
    exts = ["", ".pdf", ".png", ".jpg", ".jpeg", ".eps", ".ps", ".svg", ".PDF", ".PNG", ".JPG"]
    for p, text in SV.items():
        for m in RE_GRAPHICS.finditer(text):
            name = m.group(2).strip()
            if "#" in name or "\\" in name:
                continue
            if name.startswith("example-image"):
                placeholder_gfx.append(f"{rel(p)}:{line_at(text, m.start())}: {name}")
                continue
            hit = None
            for d in gpaths + [p.parent]:
                for ext in exts:
                    c = d / (name + ext)
                    if c.is_file():
                        hit = c
                        break
                if hit:
                    break
            if hit:
                actual = {x.name for x in hit.parent.iterdir()}
                if hit.name not in actual:
                    case_gfx.append(f"{rel(p)}:{line_at(text, m.start())}: {name}")
                continue
            low = name.lower()
            ci = None
            for d in gpaths + [p.parent]:
                tgt = (d / name).parent
                if tgt.is_dir():
                    for x in tgt.iterdir():
                        if x.stem.lower() == Path(low).stem and (Path(low).suffix in ("", x.suffix.lower())):
                            ci = x
            if ci:
                case_gfx.append(f"{rel(p)}:{line_at(text, m.start())}: {name} → exists as {rel(ci)} "
                                "(case differs: works on Windows/macOS, fails on Linux, Overleaf and arXiv)")
            elif kpsewhich(name) in (None, ""):
                missing_gfx.append(f"{rel(p)}:{line_at(text, m.start())}: {name}")
    R["graphics"] = {"missing": missing_gfx, "case_mismatch": case_gfx, "placeholder_images": placeholder_gfx}

    # ---- abbreviations
    defs = {}
    every = "\n".join(SV.values()) + "\n" + style_text
    for m in RE_NEWACRONYM.finditer(every):
        defs[m.group(1).strip()] = m.group(2).strip()
    for m in RE_DECLAREACRONYM.finditer(every):
        sm = re.search(r"short\s*=\s*\{?([^,}]+)", m.group(2))
        defs[m.group(1).strip()] = (sm.group(1).strip() if sm else m.group(1).strip())
    for m in RE_ACRO_PKG.finditer(every):
        defs[m.group(1).strip()] = (m.group(2) or m.group(1)).strip()
    used = Counter()
    for m in list(RE_GLS_USE.finditer(all_text)) + list(RE_AC_USE.finditer(all_text)):
        for k in m.group(1).split(","):
            used[k.strip()] += 1
    body = "\n".join(t for p, t in SV.items() if not re.search(r"acronym|abbreviation|glossar|sigla|symbol",
                                                                  p.name, re.I))
    body = RE_NEWACRONYM.sub(" ", body)                  # the definitions themselves are not uses
    body = re.sub(r"\\new(?:acronym|abbreviation)\s*(?:\[[^\]]*\])?\s*\{[^}]*\}\s*\{[^}]*\}\s*\{[^}]*\}", " ", body)
    body = RE_DECLAREACRONYM.sub(" ", body)
    body = re.sub(r"\\acro(?:def)?\s*\{[^}]*\}\s*(?:\[[^\]]*\])?\s*\{[^}]*\}", " ", body)
    unused, literal_only = [], []
    for key, short in defs.items():
        if used[key]:
            continue
        short_txt = re.sub(r"\\[a-zA-Z]+|[{}$]", "", short).strip()
        if short_txt and re.search(r"(?<![\w\\])" + re.escape(short_txt) + r"(?!\w)", body):
            literal_only.append(f"{key} ({short_txt}) — typed literally, never via \\gls/\\ac (no first-use expansion)")
        else:
            unused.append(f"{key} ({short_txt or key})")
    siglas = []
    for p, text in SV.items():
        for blk in re.finditer(r"\\begin\{siglas\}(.*?)\\end\{siglas\}", text, re.S):
            for s in RE_SIGLA_ITEM.findall(blk.group(1)):
                s_txt = re.sub(r"\\[a-zA-Z]+|[${}]", "", s).strip()
                if s_txt and not re.search(r"(?<![\w\\])" + re.escape(s_txt) + r"(?!\w)", body):
                    siglas.append(f"{s_txt} (siglas list in {rel(p)})")
    R["abbreviations"] = {"defined": len(defs), "unused": unused + siglas, "literal_only": literal_only,
                          "glsaddall": R["glsaddall"]}

    # ---- abstract and keywords
    abstracts = []
    for p, text in S.items():
        found = False
        for m in re.finditer(r"\\begin\{(abstract|resumo|zusammenfassung|resume|abstract\*)\}(\[[^\]]*\])?(.*?)"
                             r"\\end\{\1\}", text, re.S):
            abstracts.append((rel(p), (m.group(2) or m.group(1)).strip("[]"), m.group(3)))
            found = True
        if not found and re.search(r"abstract|resumo|summary|zusammenfassung|r[ée]sum[ée]", p.name, re.I) \
                and p != main:
            abstracts.append((rel(p), p.stem, text))
    ab = []
    for f, label, body_ in abstracts:
        kw_all = list(RE_KEYWORDS.finditer(body_))
        kwm = kw_all[-1] if kw_all else None
        kw_raw = next((g for g in kwm.groups() if g), "") if kwm else ""
        rest = body_[:kwm.start()] + body_[kwm.end():] if kwm else body_
        rest = re.sub(r"\\(?:chapter|section|addchap|addsec)\*?\s*(?:\[[^\]]*\])?\s*\{[^}]*\}", " ", rest)
        rest = re.sub(r"\\begin\{otherlanguage\*?\}\{[^}]*\}|\\end\{otherlanguage\*?\}", " ", rest)
        n = words_in(rest)
        kw_clean = re.sub(r"\\sep|\\and|\\textbf\{|\\emph\{|[{}]", ";", kw_raw)
        terms = [t.strip(" .;:,") for t in re.split(r"[;,·]|\\sep|\\and", kw_clean) if t.strip(" .;:,")]
        sep = ";" if ";" in kw_raw else ("," if "," in kw_raw else ("\\sep" if "\\sep" in kw_raw else
                                                                    ("." if kw_raw.count(".") >= 2 else "?")))
        item = {"file": f, "block": label, "words": n, "keywords": terms[:12], "keyword_separator": sep}
        if args.abstract_limit and n > args.abstract_limit:
            item["over_limit"] = True
        ab.append(item)
    R["abstracts"] = ab

    # ---- word counts
    wc = OrderedDict()
    for p, raw in tex_files.items():
        if p == main and RE_SECTION.search(S[p]) is None:
            continue
        n = words_in(raw)
        if n:
            wc[rel(p)] = n
    R["word_counts"] = wc
    heads = OrderedDict()
    for p, text in SV.items():
        hm = re.search(r"\\(chapter|section|addchap|addsec)\*?\s*(?:\[[^\]]*\])?\s*\{((?:[^{}]|\{[^{}]*\})*)\}", text)
        if hm:
            heads[rel(p)] = re.sub(r"\\[A-Za-z]+\s*|[{}]", "", hm.group(2)).strip()[:60]
    R["headings"] = heads
    R["word_count_total"] = sum(wc.values())
    R["word_count_method"] = ("comments, verbatim, math, citation/reference/label/graphics commands removed; other "
                              "command names dropped but their braces kept; Unicode word tokens counted")
    R["texcount_total"] = None
    if not args.no_texcount and shutil.which("texcount"):
        try:
            r = subprocess.run(["texcount", "-inc", "-total", "-sum", "-q", "-utf8", main.name], cwd=str(main.parent),
                               capture_output=True, text=True, timeout=120)
            tm = re.search(r"Sum count:\s*(\d+)", r.stdout)
            R["texcount_total"] = int(tm.group(1)) if tm else None
        except Exception:  # noqa: BLE001
            pass

    # ---- lint
    lint_items = []
    pos_of = {p: i for i, p in enumerate(pkgs)}
    if "cleveref" in pos_of and "hyperref" in pos_of and pos_of["cleveref"] < pos_of["hyperref"]:
        R["problems"].append("cleveref is loaded before hyperref: load cleveref after hyperref (and last).")
    if "glossaries" in pos_of and "hyperref" in pos_of and pos_of["glossaries"] < pos_of["hyperref"]:
        lint_items.append("glossaries loaded before hyperref: load it after hyperref for linked entries.")
    obsolete = {"subfigure": "obsolete: use subcaption", "subfig": "prefer subcaption (works with caption)",
                "times": "obsolete: use newtxtext/newtxmath (pdfLaTeX) or fontspec", "epsfig": "obsolete: graphicx",
                "doublespace": "obsolete: setspace", "a4wide": "obsolete: geometry", "fancyheadings": "obsolete: fancyhdr",
                "caption2": "obsolete: caption", "scrpage2": "obsolete: scrlayer-scrpage", "natbib+biblatex": ""}
    for pk, why in obsolete.items():
        if pk in pkgs and why:
            lint_items.append(f"\\usepackage{{{pk}}} — {why}")
    for p, text in SV.items():
        for pat, msg in ((r"(?<!\\)\$\$", "$$...$$ display math (use \\[...\\] or equation*)"),
                         (r"\\begin\{eqnarray\*?\}", "eqnarray (inconsistent spacing; use align)"),
                         (r"(?<![\\\w])\\(?:bf|it|rm|sl|sc|tt|sf)\b(?![a-zA-Z])", "old font switch \\bf/\\it/... "
                          "(use \\textbf{}/\\emph{} or \\bfseries)"),
                         (r"\\over\b(?![a-z])", "\\over (use \\frac)"),
                         (r"\\begin\{(?:figure|table)\*?\}\s*\[H\]", "[H] placement (forces position; leaves gaps)"),
                         (r"\\vspace\*?\s*\{\s*-", "negative \\vspace (venues may reject layout hacks)"),
                         (r"(?<![~\\])\b(?:Figure|Fig\.|Table|Section|Sec\.|Eq\.|Equation|Chapter)\s+\\(?:ref|eqref)\{",
                          "space instead of ~ before \\ref (line break between word and number)")):
            hits = sorted({line_at(text, m.start()) for m in re.finditer(pat, text)})
            if hits:
                lint_items.append(f"{rel(p)}: {msg} — line(s) {', '.join(map(str, hits[:8]))}"
                                  + (" …" if len(hits) > 8 else ""))
    R["lint"] = lint_items

    # ---- log triage
    log = Path(args.log) if args.log else next((c for c in (main.parent / "build" / (main.stem + ".log"),
                                                             main.parent / (main.stem + ".log"),
                                                             main.parent / "out" / (main.stem + ".log"))
                                                 if c.is_file()), None)
    if log and log.is_file():
        lt = read_text(log)
        pages = re.findall(r"Output written on .*?\((\d+) pages?", lt)
        L = {"file": rel(log), "pages": int(pages[-1]) if pages else None,
             "errors": sorted(set(l.strip() for l in lt.split("\n") if l.startswith("!")
                                  or re.match(r"^\S+\.tex:\d+: ", l))),
             "undefined_citations": sorted(set(re.findall(r"Citation [`']([^']+)' (?:on page|undefined)", lt))),
             "undefined_references": sorted(set(re.findall(r"Reference [`']([^']+)' on page", lt))),
             "multiply_defined": sorted(set(re.findall(r"Label [`']([^']+)' multiply defined", lt))),
             "rerun_requested": bool(re.search(r"Rerun to get|Please \(re\)run|Label\(s\) may have changed", lt)),
             "overfull": len(re.findall(r"Overfull \\[hv]box", lt)),
             "underfull": len(re.findall(r"Underfull \\[hv]box", lt)),
             "float_too_large": len(re.findall(r"Float too large", lt)),
             "missing_files": sorted(set(re.findall(r"File [`']([^']+)' not found", lt))),
             "missing_characters": len(re.findall(r"Missing character: There is no", lt))}
        blg = log.with_suffix(".blg")
        if blg.is_file():
            bt = read_text(blg)
            L["bib_tool_messages"] = [l.strip() for l in bt.split("\n")
                                      if re.search(r"ERROR|WARN|^Warning--|error message|I couldn't", l)][:30]
        R["log"] = L
    else:
        R["notes"].append("No build log found (build/<main>.log or <main>.log): run compile-check.sh for the log "
                          "triage.")
    return R


# ----------------------------------------------------------------------------- report

def bullet(items, empty="(none)", limit=40):
    if not items:
        return f"   {empty}\n"
    out = "".join(f"   - {x}\n" for x in items[:limit])
    if len(items) > limit:
        out += f"   - … {len(items) - limit} more\n"
    return out


def render(R: dict) -> str:
    L = [f"# LaTeX project audit — `{R['root']}`\n"]
    if "main" not in R:
        return "\n".join(L + R["problems"]) + "\n"
    dc = R["documentclass"]
    L.append(f"- Main file: `{R['main']}` · class: **{dc['class']}**" + (f" [{dc['options']}]" if dc["options"] else "")
             + f" · template: **{R['template_family']}**")
    L.append(f"- Engine: **{R['engine']}** · citations: **{R['citation_stack']}**"
             + (f" → run **{R['bibliography_tool']}**" if R["bibliography_tool"] else ""))
    if R["glossary_index_tools"]:
        L.append("- Glossaries/index: " + "; ".join(R["glossary_index_tools"]))
    if R["shell_escape_needed_by"]:
        L.append("- Needs `-shell-escape`: " + ", ".join(R["shell_escape_needed_by"]) +
                 " (not available on arXiv/most journal systems)")
    if R["local_class_style_files"]:
        L.append("- Local class/style files: " + ", ".join(f"`{f}`" for f in R["local_class_style_files"][:15]))
    L.append(f"- Files included ({len(R['included'])}): " + ", ".join(f"`{f}`" for f in R["included"][:30])
             + (" …" if len(R["included"]) > 30 else ""))
    L.append("- .bib files: " + (", ".join(f"`{b}`" for b in R["bib_files"]) or "(none)"))
    if R["orphan_tex_files"]:
        L.append(f"- .tex files never included ({len(R['orphan_tex_files'])}): "
                 + ", ".join(f"`{f}`" for f in R["orphan_tex_files"][:20]))
    if R["problems"]:
        L.append("\n**Problems:**\n" + bullet(R["problems"]))
    if R["notes"]:
        L.append("\n**Notes:**\n" + bullet(R["notes"]))
    if "log" in R:
        g = R["log"]
        L.append(f"\n## Last build (`{g['file']}`)\n")
        L.append(f"- Pages: **{g['pages']}** · errors: **{len(g['errors'])}** · undefined citations: "
                 f"**{len(g['undefined_citations'])}** · undefined references: **{len(g['undefined_references'])}** · "
                 f"multiply-defined labels: {len(g['multiply_defined'])} · overfull: {g['overfull']} · underfull: "
                 f"{g['underfull']} · float too large: {g['float_too_large']}"
                 + (" · **rerun requested**" if g["rerun_requested"] else ""))
        for key, title in (("errors", "Errors"), ("undefined_citations", "Undefined citations"),
                           ("undefined_references", "Undefined references"), ("missing_files", "Missing files"),
                           ("bib_tool_messages", "Bibliography tool (.blg)")):
            if g.get(key):
                L.append(f"{title}:\n" + bullet(g[key], limit=20))
        if g["missing_characters"]:
            L.append(f"- {g['missing_characters']} 'Missing character' warnings: the font lacks glyphs you typed.")
    L.append("\n## Debts and placeholders (TODO/FIXME/XXX/TBD, \\todo, lipsum, example images)\n")
    L.append(bullet(R["placeholders"], limit=60))
    c = R["citations"]
    L.append("\n## Citations ↔ bibliography\n")
    L.append(f"- Distinct keys cited: **{c['distinct_cited']}** · entries in .bib: **{c['bib_entries']}**"
             + (" · `\\nocite{*}` present" if c["nocite_all"] else ""))
    L.append("- Cited but missing from the .bib:\n" + bullet(c["missing_in_bib"]))
    if c["case_mismatch"]:
        L.append("- …of which differ only in letter case from an entry (biber treats keys case-sensitively):\n"
                 + bullet(c["case_mismatch"]))
    L.append("- In the .bib but never cited (fine for a shared library .bib; not printed unless \\nocite):\n"
             + bullet(c["uncited_entries"], limit=25))
    if c["bib_lint_counts"]:
        L.append("- .bib lint (bib-check.py): " + ", ".join(f"{k}: {v}" for k, v in sorted(c["bib_lint_counts"].items()))
                 + " — errors and warnings:\n" + bullet(c["bib_lint"], limit=30))
    r = R["refs"]
    L.append("\n## Cross-references\n")
    L.append(f"- Labels: {r['labels']}")
    L.append("- Referenced but undefined:\n" + bullet(r["undefined"]))
    L.append("- Duplicate labels:\n" + bullet(r["duplicate_labels"]))
    L.append("- \\label before \\caption in a float (the reference prints the section number, not the figure's):\n"
             + bullet(r["label_before_caption"]))
    L.append("- Hard-coded references (type the number with \\ref/\\cref so it follows renumbering; check — some "
             "refer to other works):\n" + bullet(r["hard_coded"], limit=20))
    f = R["floats"]
    L.append("\n## Floats\n")
    L.append("- Count: " + (", ".join(f"{k}: {v}" for k, v in f["count_by_env"].items()) or "none"))
    L.append("- Without caption:\n" + bullet(f["without_caption"]))
    L.append("- Without label:\n" + bullet(f["without_label"]))
    L.append("- Never referenced in the text (ranges such as \\crefrange{fig:a}{fig:c} reference the middle ones "
             "implicitly — verify before acting):\n" + bullet(f["never_referenced"]))
    L.append("- Placed in the source before their first reference:\n" + bullet(f["before_first_reference"]))
    if f["without_source"]:
        L.append("- Without a source/credit line (--require-float-source):\n" + bullet(f["without_source"]))
    e = R["equations"]
    L.append(f"\n## Equations\n\n- Numbered environments: {e['count']}")
    L.append("- Labelled but never referenced:\n" + bullet(e["labelled_never_referenced"]))
    g = R["graphics"]
    L.append("\n## Graphics files\n")
    L.append("- Missing:\n" + bullet(g["missing"]))
    L.append("- Letter case differs from the file on disk:\n" + bullet(g["case_mismatch"]))
    if g["placeholder_images"]:
        L.append("- Placeholder images (mwe example-image):\n" + bullet(g["placeholder_images"]))
    a = R["abbreviations"]
    L.append(f"\n## Abbreviations\n\n- Defined: {a['defined']}" + (" · `\\glsaddall` prints every defined entry"
                                                                   if a["glsaddall"] else ""))
    L.append("- Defined but never used:\n" + bullet(a["unused"]))
    if a["literal_only"]:
        L.append("- Used only as plain text:\n" + bullet(a["literal_only"]))
    L.append("\n## Abstract(s) and keywords\n")
    for x in R["abstracts"] or []:
        flag = " ⚠️ over the limit" if x.get("over_limit") else ""
        kw = (f"{len(x['keywords'])} keywords (separator '{x['keyword_separator']}')" if x["keywords"]
              else "no keywords line found")
        L.append(f"- `{x['file']}` ({x['block']}): **{x['words']} words**{flag}; {kw}")
    if not R["abstracts"]:
        L.append("   (no abstract found)")
    L.append("\n## Word counts\n")
    L.append(f"_Method: {R['word_count_method']}._ Total: **{R['word_count_total']}**"
             + (f" · texcount (text+headers+captions): **{R['texcount_total']}**" if R["texcount_total"] else ""))
    for k, v in R["word_counts"].items():
        L.append(f"- `{k}`: {v}")
    L.append("\n## Lint (risky or obsolete constructs)\n")
    L.append(bullet(R["lint"]))
    return "\n".join(L) + "\n"


def _target_mode(path: Path) -> int:
    """Keep an existing file's mode; new files get the usual 0666 & ~umask (mkstemp makes them 0600)."""
    try:
        return os.stat(path).st_mode & 0o7777
    except FileNotFoundError:
        mask = os.umask(0)
        os.umask(mask)
        return 0o666 & ~mask


def atomic_write(path: Path, data: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".new", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data.encode("utf-8"))
        os.chmod(tmp, _target_mode(path))
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", nargs="?", default=".", help="project directory (default: .)")
    ap.add_argument("--main", help="main .tex file (default: main.tex or the file with \\begin{document})")
    ap.add_argument("--out", help="write the Markdown report to this file (atomic)")
    ap.add_argument("--json", help="write the raw data as JSON to this file (atomic)")
    ap.add_argument("--log", help="LaTeX .log to triage (default: build/<main>.log or <main>.log)")
    ap.add_argument("--abstract-limit", type=int, help="flag abstracts longer than N words")
    ap.add_argument("--require-float-source", action="store_true",
                    help="flag floats without a source/credit line (ABNT and some institutions require one)")
    ap.add_argument("--no-texcount", action="store_true", help="do not run texcount even if installed")
    ap.add_argument("--quiet", action="store_true", help="do not print the report")
    args = ap.parse_args()
    root = Path(args.project).resolve()
    if not root.is_dir():
        sys.exit(f"not a directory: {root}")
    R = audit(root, args)
    report = render(R)
    if args.out:
        atomic_write(Path(args.out), report)
    if args.json:
        atomic_write(Path(args.json), json.dumps(R, ensure_ascii=False, indent=2, default=str))
    if not args.quiet:
        try:
            sys.stdout.write(report)
        except UnicodeEncodeError:
            sys.stdout.buffer.write(report.encode("utf-8", errors="replace"))


if __name__ == "__main__":
    main()
