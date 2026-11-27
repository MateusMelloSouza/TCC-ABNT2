#!/usr/bin/env python3
"""audit-tex.py — re-measure an abnTeX2 thesis project instead of trusting its trackers.

    python3 audit-tex.py [PROJECT_DIR] [--main main.tex] [--out report.md] [--json data.json]
                         [--log build/main.log] [--quiet]

What it reports (Markdown on stdout, optionally to files):
  * project inventory: main file, template profile, citation stack, included files, .bib files
  * placeholders: lipsum / lorem ipsum, TODO / FIXME / XXX, stray "\\\\" before sectioning
  * citations <-> .bib: missing keys, uncited entries, duplicate keys, placeholder entries
  * labels <-> refs: undefined references, floats/equations never referenced, floats that appear
    before their first call-out (NBR 14724: cite the illustration before it appears)
  * floats: figures / tables / quadros without caption, without source (\\fonte, \\Fonte, \\legend)
  * acronyms (glossaries \\newacronym or abnTeX2 siglas) defined but never used; \\glsaddall present
  * resumo / abstract: word counts (NBR 6028: 150-500) and keyword separator (2021: ';')
  * word counts per textual file, with the counting method stated so numbers are comparable
  * log triage when a .log is found: pages, errors, undefined citations/references, overfull

Pure standard library, Python 3.8+. Never modifies project files; report files are written
atomically (temp file + rename) so a failure cannot truncate an existing report.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from collections import Counter, OrderedDict
from pathlib import Path

SKIP_DIRS = {"build", ".git", ".tcc-workflow", "node_modules", "__pycache__", ".vscode"}
SKIP_PREFIX = ("ARCHIVE",)

CITE_CMDS = (
    r"cite|citeonline|citeauthor|citeauthoronline|citeautoronline|citeyear|citetext|nocite|"
    r"textcite|parencite|autocite|footcite|fullcite|citet|citep|citealp|citealt|Cite|Citeonline|"
    r"smartcite|supercite|cites|textcites|parencites"
)
RE_CITE = re.compile(r"\\(?:" + CITE_CMDS + r")\*?(?:\[[^\]]*\]){0,2}\{([^}]*)\}")
RE_APUD = re.compile(r"\\apud(?:online)?\*?(?:\[[^\]]*\])?\{([^}]*)\}\{([^}]*)\}")
RE_INPUT = re.compile(r"\\(?:input|include|subfile|imprimir[a-zA-Z]+)\{([^}]+)\}")
RE_LOCAL_STY = re.compile(r"\\(?:usepackage|RequirePackage)(?:\[[^\]]*\])?\{([^}]+)\}")
RE_BIBFILES = re.compile(r"\\(?:bibliography|imprimirreferencias)\{([^}]+)\}|\\addbibresource\{([^}]+)\}")
RE_LABEL = re.compile(r"\\label\{([^}]+)\}")
RE_REF = re.compile(r"\\(?:ref|autoref|eqref|pageref|cref|Cref|vref|nameref|fref|Fref)\*?\{([^}]+)\}|\\hyperref\[([^\]]+)\]")
RE_NEWACRONYM = re.compile(r"\\newacronym(?:\[[^\]]*\])?\{([^}]+)\}\{([^}]+)\}\{([^}]*)\}")
RE_GLS = re.compile(r"\\(?:gls|glspl|Gls|Glspl|GLS|acrshort|acrlong|acrfull|Acrshort|Acrlong|Acrfull|ac|acs|acl|acf|Ac|glsxtrshort|glsxtrlong|glsxtrfull)\*?\{([^}]+)\}")
RE_SIGLA_ITEM = re.compile(r"\\item\[\{?([^\]\}]+)\}?\]")
RE_FLOAT_BEGIN = re.compile(r"\\begin\{(figure|table|quadro|figure\*|table\*|algorithm|sidewaysfigure|sidewaystable|longtable)\}")
RE_EQ_BEGIN = re.compile(r"\\begin\{(equation|align|gather|multline|eqnarray)\}")
RE_SECTION = re.compile(r"\\(chapter|section|subsection|subsubsection|subsubsubsection|apendice|anexo)\*?\{")
RE_PLACEHOLDER_CI = re.compile(r"lipsum|lorem ipsum", re.I)
RE_PLACEHOLDER_CS = re.compile(r"\bTODO\b|\bFIXME\b|\bXXX\b")
RE_STRAY_BREAK = re.compile(r"\\\\\s*\\(chapter|section|subsection|subsubsection)")
RE_KEYWORDS = re.compile(
    r"\\(?:palavraschave|keywords)\{((?:[^{}]|\{[^{}]*\})*)\}"
    r"|\\textbf\{(?:Palavras-chave|Keywords)\}\s*:?\s*([^\n]+)"
    r"|(?:Palavras-chave|Keywords)\s*:\s*([^\n]+)",
    re.I,
)


# ----------------------------------------------------------------------------- helpers

def read_text(path: Path) -> str:
    for enc in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def strip_comments(text: str) -> str:
    """Remove % comments (not \\%). Keeps line structure for line numbers."""
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


def is_skipped(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    for part in rel.parts[:-1]:
        if part in SKIP_DIRS or part.startswith(SKIP_PREFIX):
            return True
    return False


def resolve_tex(base_dir: Path, root: Path, name: str) -> Path | None:
    name = name.strip()
    cands = []
    for d in (base_dir, root):
        cands.append(d / name)
        if not name.endswith(".tex"):
            cands.append(d / (name + ".tex"))
    for c in cands:
        if c.is_file():
            return c.resolve()
    return None


def find_main(root: Path, explicit: str | None) -> Path | None:
    if explicit:
        p = (root / explicit) if not os.path.isabs(explicit) else Path(explicit)
        return p.resolve() if p.is_file() else None
    pref = root / "main.tex"
    if pref.is_file() and re.search(r"^[^%\n]*\\begin\{document\}", read_text(pref), re.M):
        return pref.resolve()
    for p in sorted(root.rglob("*.tex")):
        if is_skipped(p, root):
            continue
        if re.search(r"^[^%\n]*\\begin\{document\}", read_text(p), re.M):
            return p.resolve()
    return None


def collect_included(main: Path, root: Path):
    """Return ordered dict path -> stripped text for main + every file it pulls in (recursive)."""
    files: "OrderedDict[Path, str]" = OrderedDict()
    stack = [main]
    while stack:
        p = stack.pop(0)
        if p in files or not p.is_file():
            continue
        text = strip_comments(read_text(p))
        files[p] = text
        for m in RE_INPUT.finditer(text):
            target = resolve_tex(p.parent, root, m.group(1))
            if target and target not in files:
                stack.append(target)
        # project-local .sty files (institutional templates) may \input pre-textual files themselves
        for m in RE_LOCAL_STY.finditer(text):
            for name in m.group(1).split(","):
                name = name.strip()
                for cand in (p.parent / (name + ".sty"), root / (name + ".sty")):
                    if cand.is_file() and cand.resolve() not in files:
                        stack.append(cand.resolve())
                        break
    return files


def words_in(text: str) -> int:
    """Word count method (stated in the report): drop comments, math, \\begin/\\end lines,
    citations/labels/refs/graphics commands; strip remaining command names but keep their
    brace contents; count Unicode word tokens."""
    t = re.sub(r"\$\$.*?\$\$", " ", text, flags=re.S)
    t = re.sub(r"\\\[.*?\\\]", " ", t, flags=re.S)
    t = re.sub(r"\\begin\{(equation|align|gather|multline|eqnarray)\*?\}.*?\\end\{\1\*?\}", " ", t, flags=re.S)
    t = re.sub(r"\$[^$]*\$", " ", t)
    t = re.sub(r"\\(?:" + CITE_CMDS + r")\*?(?:\[[^\]]*\]){0,2}\{[^}]*\}", " ", t)
    t = re.sub(r"\\(?:label|ref|autoref|eqref|pageref|cref|Cref|includegraphics|input|include|usepackage|documentclass|newacronym|gls[a-zA-Z]*|acrshort|acrlong|acrfull)\*?(?:\[[^\]]*\])?\{[^}]*\}", " ", t)
    t = re.sub(r"\\(?:begin|end)\{[^}]*\}(?:\[[^\]]*\])?", " ", t)
    t = re.sub(r"\\[a-zA-Z@]+\*?", " ", t)
    t = re.sub(r"[{}\[\]&~]", " ", t)
    return len(re.findall(r"\w+(?:[-'’]\w+)*", t))


# ----------------------------------------------------------------------------- bib

RE_BIB_ENTRY = re.compile(r"@([A-Za-z][A-Za-z-]*)\s*[{(]\s*([^,\s]+)\s*,", re.M)


def parse_bib(path: Path):
    text = read_text(path)
    entries = []
    for m in RE_BIB_ENTRY.finditer(text):
        etype, key = m.group(1).lower(), m.group(2).strip()
        if etype in ("comment", "string", "preamble"):
            continue
        # crude field grab up to the matching closing brace of the entry
        start = m.end()
        depth, i = 1, start
        while i < len(text) and depth > 0:
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
            i += 1
        body = text[start:i - 1]
        fields = {}
        for fm in re.finditer(r"([A-Za-z-]+)\s*=\s*(\{(?:[^{}]|\{[^{}]*\})*\}|\"[^\"]*\"|[^,\n]+)", body):
            fields[fm.group(1).lower()] = fm.group(2).strip().strip("{}\"")
        entries.append({"type": etype, "key": key, "fields": fields, "file": str(path),
                        "line": text.count("\n", 0, m.start()) + 1})
    return entries


# ----------------------------------------------------------------------------- audit

def audit(root: Path, main_arg: str | None, log_arg: str | None):
    R: dict = {"root": str(root), "problems": [], "info": []}
    main = find_main(root, main_arg)
    if not main:
        R["problems"].append("No main .tex (with \\begin{document}) found — pass --main.")
        return R
    R["main"] = str(main.relative_to(root)) if str(main).startswith(str(root)) else str(main)
    files = collect_included(main, root)
    all_text = "\n".join(files.values())
    rel = lambda p: str(p.relative_to(root)) if str(p).startswith(str(root)) else str(p)
    R["included"] = [rel(p) for p in files]

    # template / stack detection
    profile = "other/unknown"
    if (root / "lib" / "unifortex2.sty").is_file() or "unifortex2" in all_text:
        profile = "unifortex2"
    elif re.search(r"\\documentclass(?:\[[^\]]*\])?\{abntex2\}", all_text):
        profile = "abntex2-modelo (or a fork)"
    R["template_profile"] = profile
    m = re.search(r"\\usepackage\[([^\]]*)\]\{abntex2cite\}", all_text)
    if m:
        R["citation_stack"] = "abntex2cite [" + " ".join(m.group(1).split()) + "] (BibTeX)"
    elif re.search(r"\\usepackage(?:\[[^\]]*\])?\{abntex2cite\}", all_text):
        R["citation_stack"] = "abntex2cite (BibTeX, numeric default)"
    elif re.search(r"\\usepackage\[[^\]]*style\s*=\s*abnt[^\]]*\]\{biblatex\}", all_text):
        R["citation_stack"] = "biblatex-abnt (biber)"
    elif "biblatex" in all_text:
        R["citation_stack"] = "biblatex (biber) — style not abnt?"
    else:
        R["citation_stack"] = "not detected"
    R["uses_glossaries"] = bool(re.search(r"\\makeglossaries", all_text))
    R["glsaddall"] = bool(re.search(r"\\glsaddall", all_text))
    if profile == "unifortex2" and re.search(r"\\usepackage\{float\}", all_text):
        R["problems"].append("\\usepackage{float} loaded with UniforTeX2 — it redefines \\newfloat and breaks the template's quadro float; remove it.")
    if re.search(r"\\usepackage\{lipsum\}", all_text):
        R["info"].append("\\usepackage{lipsum} still loaded (harmless, but remove before deposit).")

    # orphan .tex files (in the tree but never included)
    orphans = []
    for p in sorted(root.rglob("*.tex")):
        if is_skipped(p, root) or p.resolve() in files:
            continue
        orphans.append(rel(p))
    R["orphan_tex_files"] = orphans

    # ------------------------------------------------------------- placeholders
    ph = []
    for p, text in files.items():
        for i, line in enumerate(text.split("\n"), 1):
            if RE_PLACEHOLDER_CI.search(line) or RE_PLACEHOLDER_CS.search(line):
                ph.append(f"{rel(p)}:{i}: {line.strip()[:110]}")
        for m in RE_STRAY_BREAK.finditer(text):
            ln = text.count("\n", 0, m.start()) + 1
            ph.append(f"{rel(p)}:{ln}: stray \\\\ before \\{m.group(1)} (produces 'There's no line here to end')")
    R["placeholders"] = ph

    # ------------------------------------------------------------- citations vs bib
    cited: Counter = Counter()
    cite_multi_unsorted = []
    for p, text in files.items():
        for m in RE_CITE.finditer(text):
            keys = [k.strip() for k in m.group(1).split(",") if k.strip()]
            keys = [k for k in keys if "=" not in k and k != "*" and "#" not in k]   # skip options and macro params (#1)
            for k in keys:
                cited[k] += 1
            if len(keys) > 1 and keys != sorted(keys, key=str.lower):
                ln = text.count("\n", 0, m.start()) + 1
                cite_multi_unsorted.append(f"{rel(p)}:{ln}: \\cite{{{','.join(keys)}}}")
        for m in RE_APUD.finditer(text):
            for k in (m.group(1), m.group(2)):
                for kk in k.split(","):
                    if kk.strip() and "#" not in kk:
                        cited[kk.strip()] += 1
    bibfiles = []
    for m in RE_BIBFILES.finditer(all_text):
        spec = m.group(1) or m.group(2)
        for name in spec.split(","):
            name = name.strip()
            if not name or "#" in name or name.startswith("abntex2-options") or name.startswith("abnt-options"):
                continue   # skip macro definitions in .sty files (\bibliography{#1}) and the options database
            cands = [main.parent / name, main.parent / (name + ".bib"), root / name, root / (name + ".bib")]
            found = next((c for c in cands if c.is_file()), None)
            if found:
                bibfiles.append(found.resolve())
            else:
                R["problems"].append(f".bib file '{name}' referenced but not found")
    if not bibfiles:
        bibfiles = [p.resolve() for p in root.rglob("*.bib") if not is_skipped(p, root)]
    R["bib_files"] = [rel(p) for p in bibfiles]
    entries = []
    for b in bibfiles:
        entries.extend(parse_bib(b))
    option_keys = {e["key"] for e in entries if e["type"] == "abnt-options"}
    bib_keys = [e["key"] for e in entries if e["type"] != "abnt-options"]
    lower_counts = Counter(k.lower() for k in bib_keys)
    dupes = sorted({k for k in bib_keys if lower_counts[k.lower()] > 1}, key=str.lower)
    bib_set = set(bib_keys)
    missing = sorted(k for k in cited if k not in bib_set and k not in option_keys)
    uncited = sorted(k for k in bib_keys if k not in cited)
    placeholders_bib = []
    for e in entries:
        f = e["fields"]
        y = f.get("year", "")
        if re.search(r"[xX?]", y) or re.search(r"\bTODO\b", json.dumps(f)) or not f.get("title") and e["type"] != "abnt-options":
            placeholders_bib.append(f"{e['key']} ({Path(e['file']).name}:{e['line']}) year='{y}' title={'present' if f.get('title') else 'MISSING'}")
    # multi-key \cite order: compare by (first author's surname, year) taken from the .bib, not by key
    def sort_key_for(key: str):
        e = next((x for x in entries if x["key"].lower() == key.lower()), None)
        if not e:
            return (key.lower(), "")
        f = e["fields"]
        who = f.get("author") or f.get("organization") or f.get("editor") or f.get("title") or key
        first = re.split(r"\s+and\s+", who, maxsplit=1)[0]
        first = re.sub(r"[{}\\]|\\relax|'|\"", "", first)
        surname = first.split(",")[0].strip() if "," in first else first.strip().split(" ")[-1]
        return (surname.lower(), f.get("year", ""))
    real_unsorted = []
    for item in cite_multi_unsorted:
        keys = re.search(r"\\cite\{([^}]*)\}", item).group(1).split(",")
        if [sort_key_for(k) for k in keys] != sorted(sort_key_for(k) for k in keys):
            real_unsorted.append(item)
    R["citations"] = {
        "distinct_cited": len(cited), "bib_entries": len(bib_keys),
        "missing_in_bib": missing, "uncited_entries": uncited, "duplicate_keys_ci": dupes,
        "placeholder_entries": placeholders_bib, "multi_cite_not_alphabetical": real_unsorted,
    }

    # ------------------------------------------------------------- labels, refs, floats
    labels: dict = {}
    refs: Counter = Counter()
    ref_first_pos: dict = {}
    floats = []
    equations = []
    order_issues = []
    global_offset = 0
    for p, text in files.items():
        for m in RE_LABEL.finditer(text):
            labels.setdefault(m.group(1).strip(), (rel(p), text.count("\n", 0, m.start()) + 1, global_offset + m.start()))
        for m in RE_REF.finditer(text):
            for k in (m.group(1) or m.group(2)).split(","):
                k = k.strip()
                refs[k] += 1
                ref_first_pos.setdefault(k, global_offset + m.start())
        # floats
        for m in RE_FLOAT_BEGIN.finditer(text):
            env = m.group(1)
            end = re.compile(r"\\end\{" + re.escape(env) + r"\}").search(text, m.end())
            block = text[m.start(): end.end() if end else m.end() + 2000]
            lab = RE_LABEL.search(block)
            has_caption = bool(re.search(r"\\(?:caption|Caption)\b", block))
            has_source = bool(re.search(r"\\(?:fonte|Fonte|legend|nota|Nota)\b|Fonte\s*:", block))
            floats.append({
                "file": rel(p), "line": text.count("\n", 0, m.start()) + 1, "env": env,
                "label": lab.group(1).strip() if lab else None, "caption": has_caption,
                "source": has_source, "pos": global_offset + m.start(),
            })
        for m in RE_EQ_BEGIN.finditer(text):
            end = re.compile(r"\\end\{" + re.escape(m.group(1)) + r"\}").search(text, m.end())
            block = text[m.start(): end.end() if end else m.end() + 500]
            lab = RE_LABEL.search(block)
            equations.append({"file": rel(p), "line": text.count("\n", 0, m.start()) + 1,
                              "label": lab.group(1).strip() if lab else None})
        global_offset += len(text) + 1
    undefined_refs = sorted(k for k in refs if k not in labels)
    floats_no_caption = [f"{f['file']}:{f['line']} ({f['env']})" for f in floats if not f["caption"]]
    floats_no_source = [f"{f['file']}:{f['line']} ({f['env']})" for f in floats if not f["source"] and f["env"] != "algorithm"]
    floats_no_label = [f"{f['file']}:{f['line']} ({f['env']})" for f in floats if not f["label"]]
    floats_unref = [f"{f['file']}:{f['line']} ({f['env']}, {f['label']})" for f in floats if f["label"] and refs[f["label"]] == 0]
    for f in floats:
        if f["label"] and refs[f["label"]] and ref_first_pos.get(f["label"], 0) > f["pos"]:
            order_issues.append(f"{f['file']}:{f['line']} ({f['env']}, {f['label']}) — first call-out comes after the float")
    eq_unref = [f"{e['file']}:{e['line']} ({e['label']})" for e in equations if e["label"] and refs[e["label"]] == 0]
    eq_nolabel = sum(1 for e in equations if not e["label"])
    R["floats"] = {
        "count_by_env": dict(Counter(f["env"] for f in floats)),
        "without_caption": floats_no_caption, "without_source": floats_no_source,
        "without_label": floats_no_label, "never_referenced": floats_unref,
        "appear_before_first_callout": order_issues,
    }
    R["equations"] = {"count": len(equations), "numbered_never_referenced": eq_unref, "without_label": eq_nolabel}
    R["refs"] = {"undefined": undefined_refs, "labels": len(labels)}

    # ------------------------------------------------------------- acronyms
    acr_defs = {}
    for p, text in files.items():
        for m in RE_NEWACRONYM.finditer(text):
            acr_defs[m.group(1).strip()] = (m.group(2).strip(), rel(p))
    sigla_items = []
    for p, text in files.items():
        if re.search(r"\\begin\{siglas\}", text):
            blk = re.search(r"\\begin\{siglas\}(.*?)\\end\{siglas\}", text, re.S)
            if blk:
                sigla_items += [(s.strip(), rel(p)) for s in RE_SIGLA_ITEM.findall(blk.group(1))]
    used_keys = Counter()
    for m in RE_GLS.finditer(all_text):
        for k in m.group(1).split(","):
            used_keys[k.strip()] += 1
    body_text = "\n".join(t for p, t in files.items() if not re.search(r"siglas|abreviaturas|glossario", p.name, re.I))
    unused_acr = []
    for key, (short, where) in acr_defs.items():
        if used_keys[key]:
            continue
        if re.search(r"(?<![\w\\])" + re.escape(short) + r"(?!\w)", body_text):
            continue
        unused_acr.append(f"{key} ({short}) — defined in {where}")
    unused_siglas = []
    for short, where in sigla_items:
        short_txt = re.sub(r"\\[a-zA-Z]+|[${}]", "", short).strip()
        if short_txt and not re.search(r"(?<![\w\\])" + re.escape(short_txt) + r"(?!\w)", body_text):
            unused_siglas.append(f"{short_txt} — listed in {where}")
    R["acronyms"] = {"defined_newacronym": len(acr_defs), "siglas_items": len(sigla_items),
                     "unused": unused_acr + unused_siglas, "glsaddall": R["glsaddall"]}

    # ------------------------------------------------------------- resumo / abstract / keywords
    ra = []
    for p, text in files.items():
        name = p.name.lower()
        blocks = []
        if p.suffix == ".sty":
            continue
        if re.search(r"resumo|abstract", name):
            blocks.append((name, text))
        for m in re.finditer(r"\\begin\{resumo\}(\[[^\]]*\])?(.*?)\\end\{resumo\}", text, re.S):
            blocks.append(((m.group(1) or "resumo").strip("[]").lower(), m.group(2)))
        for label, body in blocks:
            kw_all = list(RE_KEYWORDS.finditer(body))
            kw_m = kw_all[-1] if kw_all else None   # keywords close the resumo; prose may mention the label earlier
            kw_raw = ""
            if kw_m:
                kw_raw = next(g for g in kw_m.groups() if g) if any(kw_m.groups()) else ""
                body_wo = body[:kw_m.start()] + body[kw_m.end():]
            else:
                body_wo = body
            body_wo = re.sub(r"\\begin\{otherlanguage\*?\}\{[^}]*\}|\\end\{otherlanguage\*?\}", " ", body_wo)
            wc = words_in(body_wo)
            kw_clean = re.sub(r"\\[a-zA-Z]+\{|[{}]", "", kw_raw).strip()
            sep = ";" if ";" in kw_clean else ("." if kw_clean.count(".") >= 2 else "?")
            terms = [t.strip(" .") for t in re.split(r"[;.]", kw_clean) if t.strip(" .")] if kw_clean else []
            ra.append({"file": rel(p), "block": label, "words": wc, "keywords": terms,
                       "keyword_separator": sep, "keywords_found": bool(kw_raw)})
    R["resumo_abstract"] = ra

    # ------------------------------------------------------------- word counts
    wc = OrderedDict()
    for p, text in files.items():
        is_preamble = bool(re.search(r"^\s*\\documentclass", text, re.M)) and not RE_SECTION.search(text)
        if p == main or p.suffix == ".sty" or is_preamble:
            continue
        n = words_in(text)
        if n:
            wc[rel(p)] = n
    R["word_counts"] = wc
    R["word_count_method"] = ("comments, math, \\begin/\\end lines, citation/label/ref/graphics commands removed; "
                              "other command names dropped but their braces kept; Unicode \\w+ tokens counted")

    # ------------------------------------------------------------- log triage
    log = None
    if log_arg:
        log = Path(log_arg)
    else:
        for c in (main.parent / "build" / (main.stem + ".log"), main.parent / (main.stem + ".log")):
            if c.is_file():
                log = c
                break
    if not (log and log.is_file()):
        R["info"].append("no build log found (build/<main>.log or <main>.log) — run compile-check.sh first for the log triage")
    if log and log.is_file():
        lt = read_text(log)
        pages = re.findall(r"Output written on .*?\((\d+) pages?", lt)
        R["log"] = {
            "file": rel(log) if str(log).startswith(str(root)) else str(log),
            "pages": int(pages[-1]) if pages else None,
            "errors": sorted(set(l.strip() for l in lt.split("\n") if l.startswith("!"))),
            "undefined_citations": sorted(set(re.findall(r"Citation `([^']+)' on page", lt))),
            "undefined_references": sorted(set(re.findall(r"Reference `([^']+)' on page", lt))),
            "overfull": len(re.findall(r"Overfull \\[hv]box", lt)),
            "float_too_large": len(re.findall(r"Float too large", lt)),
        }
    return R


# ----------------------------------------------------------------------------- report

def bullet(items, empty="(none)", limit=60):
    if not items:
        return f"   {empty}\n"
    out = "".join(f"   - {x}\n" for x in items[:limit])
    if len(items) > limit:
        out += f"   - … {len(items) - limit} more\n"
    return out


def render(R: dict) -> str:
    L = []
    L.append(f"# TCC audit — `{R['root']}`\n")
    if "main" not in R:
        L.append("\n".join(R["problems"]))
        return "\n".join(L)
    L.append(f"- Main file: `{R['main']}` · template profile: **{R['template_profile']}** · citation stack: {R['citation_stack']}")
    L.append(f"- Included files ({len(R['included'])}): " + ", ".join(f"`{f}`" for f in R["included"][:40]) + (" …" if len(R["included"]) > 40 else ""))
    L.append(f"- .bib files: " + (", ".join(f"`{b}`" for b in R["bib_files"]) or "(none found)"))
    L.append(f"- glossaries: {'yes' if R['uses_glossaries'] else 'no'}" + (" (`\\glsaddall` present — every defined sigla prints, used or not)" if R["glsaddall"] else ""))
    if R["orphan_tex_files"]:
        L.append(f"- .tex files never included ({len(R['orphan_tex_files'])}): " + ", ".join(f"`{f}`" for f in R["orphan_tex_files"][:25]))
    if R["problems"]:
        L.append("\n**Problems:**\n" + bullet(R["problems"]))
    if R["info"]:
        L.append("\n**Notes:**\n" + bullet(R["info"]))

    if "log" in R:
        g = R["log"]
        L.append(f"\n## Last build (`{g['file']}`)\n")
        L.append(f"- Pages: **{g['pages']}** · errors: **{len(g['errors'])}** · undefined citations: **{len(g['undefined_citations'])}** · undefined references: **{len(g['undefined_references'])}** · overfull boxes: {g['overfull']} · float too large: {g['float_too_large']}")
        if g["errors"]:
            L.append(bullet(g["errors"]))
        if g["undefined_citations"]:
            L.append("Undefined citations: " + ", ".join(g["undefined_citations"]))
        if g["undefined_references"]:
            L.append("Undefined references: " + ", ".join(g["undefined_references"]))

    L.append("\n## Placeholders and template residue\n")
    L.append(bullet(R["placeholders"]))

    c = R["citations"]
    L.append("\n## Citations ↔ references\n")
    L.append(f"- Distinct keys cited: **{c['distinct_cited']}** · entries in .bib: **{c['bib_entries']}**")
    L.append("- Cited but missing in .bib:\n" + bullet(c["missing_in_bib"]))
    L.append("- In .bib but never cited:\n" + bullet(c["uncited_entries"]))
    L.append("- Duplicate keys (case-insensitive — BibTeX treats them as the same):\n" + bullet(c["duplicate_keys_ci"]))
    L.append("- Placeholder-looking entries:\n" + bullet(c["placeholder_entries"]))
    L.append("- Multi-key \\cite not in alphabetical author order (NBR 10520; order taken from the .bib author/year):\n" + bullet(c["multi_cite_not_alphabetical"]))

    f = R["floats"]
    L.append("\n## Floats (figures, tables, quadros)\n")
    L.append("- Count by environment: " + (", ".join(f"{k}: {v}" for k, v in f["count_by_env"].items()) or "none"))
    L.append("- Without caption:\n" + bullet(f["without_caption"]))
    L.append("- Without source (\\fonte / \\Fonte / \\legend / Fonte:):\n" + bullet(f["without_source"]))
    L.append("- Without label:\n" + bullet(f["without_label"]))
    L.append("- Never referenced in the text:\n" + bullet(f["never_referenced"]))
    L.append("- Appear before their first call-out:\n" + bullet(f["appear_before_first_callout"]))
    e = R["equations"]
    L.append(f"\n## Equations\n\n- Numbered environments: {e['count']} (without label: {e['without_label']})")
    L.append("- Labelled but never referenced:\n" + bullet(e["numbered_never_referenced"]))
    L.append("\n## Cross-references\n")
    L.append(f"- Labels defined: {R['refs']['labels']}")
    L.append("- Referenced but undefined:\n" + bullet(R["refs"]["undefined"]))

    a = R["acronyms"]
    L.append(f"\n## Siglas / acronyms\n\n- Defined with \\newacronym: {a['defined_newacronym']} · items in `siglas` environment: {a['siglas_items']}")
    L.append("- Defined but not used in the text (NBR 14724: list only siglas used):\n" + bullet(a["unused"]))

    L.append("\n## Resumo / abstract (NBR 6028:2021: 150–500 words; keywords separated by ';')\n")
    if R["resumo_abstract"]:
        for r in R["resumo_abstract"]:
            flag = "" if 150 <= r["words"] <= 500 else " ⚠️ outside 150–500"
            kw = f"{len(r['keywords'])} keywords, separator '{r['keyword_separator']}'" if r["keywords_found"] else "keywords line not found"
            L.append(f"- `{r['file']}` ({r['block']}): **{r['words']} words**{flag}; {kw}")
    else:
        L.append("   (no resumo/abstract block found)")

    L.append("\n## Word counts per file\n")
    L.append(f"_Method: {R['word_count_method']}._\n")
    for k, v in R["word_counts"].items():
        L.append(f"- `{k}`: {v}")
    L.append("")
    return "\n".join(L)


def atomic_write(path: Path, data: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".new", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data.encode("utf-8"))
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
    ap.add_argument("--main", help="main .tex file (default: main.tex or the first with \\begin{document})")
    ap.add_argument("--out", help="write the Markdown report to this file (atomic)")
    ap.add_argument("--json", help="write the raw data as JSON to this file (atomic)")
    ap.add_argument("--log", help="LaTeX .log to triage (default: build/<main>.log or <main>.log)")
    ap.add_argument("--quiet", action="store_true", help="do not print the report to stdout")
    args = ap.parse_args()
    root = Path(args.project).resolve()
    if not root.is_dir():
        sys.exit(f"not a directory: {root}")
    R = audit(root, args.main, args.log)
    report = render(R)
    if args.out:
        atomic_write(Path(args.out), report)
    if args.json:
        atomic_write(Path(args.json), json.dumps(R, ensure_ascii=False, indent=2, default=str))
    if not args.quiet:
        try:
            sys.stdout.write(report)
        except UnicodeEncodeError:  # Windows consoles without UTF-8
            sys.stdout.buffer.write(report.encode("utf-8", errors="replace"))


if __name__ == "__main__":
    main()
