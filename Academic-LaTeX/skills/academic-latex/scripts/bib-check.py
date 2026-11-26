#!/usr/bin/env python3
"""bib-check.py — lint .bib files for the mistakes that silently produce wrong references.

    python3 bib-check.py FILE.bib [MORE.bib ...] [--backend auto|bibtex|biber] [--json out.json]
                         [--quiet] [--min-severity info|warning|error]

Severities: error = broken or wrong output; warning = probably wrong; info = check or style.
  structure   entries that do not parse, unbalanced braces, duplicate fields, illegal key
              characters, duplicate keys (case-insensitive, as BibTeX compares them), entries
              commented out with % (BibTeX has no % comments: it still reads them)
  duplicates  the same DOI or the same normalised title in two entries
  fields      fields the standard styles need for the entry type; crossref targets; empty fields
  names       missing 'and' between names, literal 'et al.', 'others' not last, too many commas,
              organisations that will be parsed as a person, initials without spaces
  titles      acronyms/CamelCase not protected by braces (sentence-case styles lowercase them),
              unescaped & % # _ $ ^ (LaTeX errors), whole-title double braces
  identifiers DOI stored as a URL or 'doi:' string, malformed DOIs, spaces/escapes in URLs
  encoding    non-ASCII letters in name fields under BibTeX (broken initials and sorting)
  dates       missing or non-numeric year, future years, month typed as text under BibTeX
  types       biblatex-only types/fields under BibTeX; arXiv preprints exported as journals
--backend auto looks at the .tex files next to the .bib (biblatex -> biber, else BibTeX).
Pure standard library, Python 3.8+. Never modifies the .bib files. Importable: parse_bib(),
lint(entries, backend) are reused by audit-tex.py.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

SEVERITIES = ("error", "warning", "info")
VERBATIM_FIELDS = {"url", "doi", "eprint", "file", "verba", "verbb", "verbc", "pdf", "urlraw"}
NAME_FIELDS = ("author", "editor", "translator", "bookauthor", "editora", "editorb", "editorc")
TITLE_FIELDS = ("title", "booktitle", "subtitle", "maintitle", "eventtitle")
PREDEFINED_MACROS = {"jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"}

# Fields the standard styles expect ("|" = any of). BibTeX names first; biber maps the aliases
# journal->journaltitle, address->location, school->institution, year->date.
REQUIRED = {
    "article": ["author", "title", "journal|journaltitle", "year|date"],
    "book": ["author|editor", "title", "publisher", "year|date"],
    "booklet": ["title"],
    "inbook": ["author|editor", "title", "chapter|pages|booktitle", "publisher", "year|date"],
    "incollection": ["author", "title", "booktitle", "publisher", "year|date"],
    "inproceedings": ["author", "title", "booktitle", "year|date"],
    "conference": ["author", "title", "booktitle", "year|date"],
    "manual": ["title"],
    "mastersthesis": ["author", "title", "school|institution", "year|date"],
    "phdthesis": ["author", "title", "school|institution", "year|date"],
    "thesis": ["author", "title", "type", "school|institution", "year|date"],
    "proceedings": ["title", "year|date"],
    "techreport": ["author", "title", "institution", "year|date"],
    "report": ["author", "title", "type", "institution", "year|date"],
    "unpublished": ["author", "title", "note|year|date"],
    "online": ["title", "url|doi|eprint"],
    "software": ["title"],
    "dataset": ["title"],
    "misc": [],
}
BIBLATEX_ONLY_TYPES = {"online", "software", "dataset", "thesis", "report", "mvbook", "collection",
                       "mvcollection", "reference", "mvreference", "inreference", "patent", "periodical",
                       "suppbook", "suppcollection", "suppperiodical", "set", "xdata", "bookinbook", "artwork",
                       "audio", "image", "legislation", "jurisdiction", "music", "performance", "review",
                       "standard", "video", "letter", "movie"}
BIBLATEX_ONLY_FIELDS = {"date", "urldate", "journaltitle", "location", "eprinttype", "eprintclass",
                        "langid", "subtitle", "titleaddon", "maintitle", "eventtitle", "eventdate",
                        "venue", "pubstate", "origdate", "shortjournal", "addendum", "related"}
ORG_WORDS = re.compile(r"\b(Organi[sz]ation|Association|Institute|Institut|Society|Committee|Consortium|Agency|"
                       r"Ministry|Department|University|Universidade|Universidad|Group|Council|Foundation|Office|"
                       r"Team|Project|Inc|Ltd|Corporation|Corp|Commission|Bureau|Federation|Union|Board|Centre|"
                       r"Center|Service|Network|Alliance|Authority|Laboratory|Laboratories|Company|GmbH|Programme|"
                       r"Program|Nations|Panel|Initiative|Academy|Agency)\b", re.I)


# ----------------------------------------------------------------------------- parsing

class BibError(Exception):
    pass


def read_text(path: Path) -> str:
    for enc in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def _balanced(text: str, i: int, open_c: str, close_c: str):
    """text[i] == open_c; return index just after the matching close_c (brace-aware)."""
    depth, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == "\\":
            i += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth < 0:
                raise BibError("unbalanced '}'")
        if open_c != "{" and c == close_c and depth == 0:
            return i + 1
        if open_c == "{" and depth == 0:
            return i + 1
        i += 1
    raise BibError("unterminated entry (unbalanced braces?)")


def _read_value(body: str, i: int):
    """Parse 'piece # piece # ...' starting at body[i]. Returns (raw_pieces, value, end)."""
    pieces, n = [], len(body)
    while True:
        while i < n and body[i].isspace():
            i += 1
        if i >= n:
            break
        c = body[i]
        if c == "{":
            j = _balanced(body, i, "{", "}")
            pieces.append(("brace", body[i + 1:j - 1]))
            i = j
        elif c == '"':
            j, depth = i + 1, 0
            while j < n:
                if body[j] == "\\":
                    j += 2
                    continue
                if body[j] == "{":
                    depth += 1
                elif body[j] == "}":
                    depth -= 1
                elif body[j] == '"' and depth == 0:
                    break
                j += 1
            if j >= n:
                raise BibError('unterminated "..." value')
            pieces.append(("quote", body[i + 1:j]))
            i = j + 1
        else:
            m = re.match(r"[^\s,#}]+", body[i:])
            if not m:
                break
            tok = m.group(0)
            pieces.append(("number" if tok.isdigit() else "macro", tok))
            i += len(tok)
        while i < n and body[i].isspace():
            i += 1
        if i < n and body[i] == "#":
            i += 1
            continue
        break
    return pieces, i


def parse_bib(path, text: str | None = None):
    """Return (entries, strings, problems). Each entry: dict(type, key, fields{name: value},
    raw{name: pieces}, field_lines{name: line}, dup_fields[], file, line, commented)."""
    path = Path(path)
    if text is None:
        text = read_text(path)
    entries, strings, problems = [], {}, []
    i, n = 0, len(text)
    line_of = lambda pos: text.count("\n", 0, pos) + 1
    while True:
        at = text.find("@", i)
        if at < 0:
            break
        m = re.match(r"@\s*([A-Za-z][\w-]*)\s*([{(])", text[at:])
        if not m:
            i = at + 1
            continue
        etype = m.group(1).lower()
        open_pos = at + m.end() - 1
        close_c = "}" if m.group(2) == "{" else ")"
        line_start = text.rfind("\n", 0, at) + 1
        commented = text[line_start:at].lstrip().startswith("%")
        try:
            if close_c == "}":
                end = _balanced(text, open_pos, "{", "}")
            else:
                end = _balanced(text, open_pos, "(", ")")
        except BibError as exc:
            problems.append({"severity": "error", "check": "structure", "file": str(path), "line": line_of(at),
                             "key": None, "message": f"@{etype} entry cannot be parsed: {exc}"})
            i = at + 1
            continue
        body = text[open_pos + 1:end - 1]
        i = end
        if etype in ("comment", "preamble"):
            continue
        if etype == "string":
            sm = re.match(r"\s*([A-Za-z][\w:-]*)\s*=\s*", body)
            if sm:
                try:
                    pieces, _ = _read_value(body, sm.end())
                    strings[sm.group(1).lower()] = "".join(p[1] for p in pieces)
                except BibError:
                    pass
            continue
        km = re.match(r"\s*([^,\s]+)\s*(?:,|\Z)", body)
        if not km:
            problems.append({"severity": "error", "check": "structure", "file": str(path), "line": line_of(at),
                             "key": None, "message": f"@{etype} entry without a key and comma"})
            continue
        key = km.group(1)
        e = {"type": etype, "key": key, "fields": {}, "raw": {}, "field_lines": {}, "dup_fields": [],
             "file": str(path), "line": line_of(at), "commented": commented}
        j = km.end()
        body_offset = open_pos + 1
        while j < len(body):
            fm = re.match(r"\s*([A-Za-z][\w:.+-]*)\s*=\s*", body[j:])
            if not fm:
                rest = body[j:].strip().strip(",").strip()
                if rest:
                    problems.append({"severity": "error", "check": "structure", "file": str(path),
                                     "line": line_of(body_offset + j), "key": key,
                                     "message": f"unparsable text in entry: {rest[:60]!r} (missing comma or '='?)"})
                break
            name = fm.group(1).lower()
            try:
                pieces, k = _read_value(body, j + fm.end())
            except BibError as exc:
                problems.append({"severity": "error", "check": "structure", "file": str(path),
                                 "line": line_of(body_offset + j), "key": key, "message": f"field {name}: {exc}"})
                break
            value = "".join(strings.get(p[1].lower(), p[1]) if p[0] == "macro" else p[1] for p in pieces)
            if name in e["fields"]:
                e["dup_fields"].append(name)
            else:
                e["fields"][name] = value
                e["raw"][name] = pieces
                e["field_lines"][name] = line_of(body_offset + j + fm.end())
            j = k
            while j < len(body) and body[j] in " \t\r\n":
                j += 1
            if j < len(body) and body[j] == ",":
                j += 1
            elif j < len(body) and body[j:].strip():
                problems.append({"severity": "error", "check": "structure", "file": str(path),
                                 "line": line_of(body_offset + j), "key": key,
                                 "message": f"missing comma after field '{name}'"})
                break
        entries.append(e)
    return entries, strings, problems


# ----------------------------------------------------------------------------- helpers

def split_names(value: str):
    """Split a name list on ' and ' at brace depth 0."""
    names, depth, cur, i = [], 0, [], 0
    tokens = re.split(r"(\s+and\s+|[{}])", value, flags=re.I)
    for t in tokens:
        if t == "{":
            depth += 1
        elif t == "}":
            depth -= 1
        if depth == 0 and re.fullmatch(r"\s+and\s+", t or "", re.I):
            names.append("".join(cur).strip())
            cur = []
        else:
            cur.append(t or "")
    names.append("".join(cur).strip())
    return [x for x in names if x]


def strip_braced(s: str) -> str:
    """Remove brace groups (protected text) and TeX commands, keep plain words."""
    out, depth = [], 0
    for c in s:
        if c == "{":
            depth += 1
            continue
        if c == "}":
            depth = max(0, depth - 1)
            continue
        out.append(c if depth == 0 else " ")
    return "".join(out)


def unprotected_caps(title: str):
    """Words whose capitals a sentence-case style would lowercase: acronyms (GPU), CamelCase
    (LaTeX, iPhone), words with capitals after the first letter. Text inside braces is protected."""
    plain = strip_braced(re.sub(r"\\[A-Za-z]+", " ", title))
    found = []
    for w in re.findall(r"[A-Za-z][A-Za-z0-9']*", plain):   # hyphen splits Large-Scale into two words
        core = w.strip("'")
        if len(core) < 2:
            continue
        if re.search(r"[A-Z]", core[1:]):
            found.append(core)
    seen, uniq = set(), []
    for w in found:
        if w not in seen:
            seen.add(w)
            uniq.append(w)
    return uniq


def unescaped_specials(value: str):
    v = re.sub(r"\\\\", "", value)
    v = re.sub(r"\\url\{[^}]*\}|\\href\{[^}]*\}", "", v)
    issues = []
    if re.search(r"(?<!\\)&", v):
        issues.append("&")
    if re.search(r"(?<!\\)%", v):
        issues.append("%")
    if re.search(r"(?<!\\)#", v):
        issues.append("#")
    no_math = re.sub(r"(?<!\\)\$[^$]*(?<!\\)\$", "", v)
    if re.search(r"(?<!\\)_", no_math):
        issues.append("_")
    if re.search(r"(?<!\\)\^", no_math):
        issues.append("^")
    if len(re.findall(r"(?<!\\)\$", v)) % 2:
        issues.append("$")
    return issues


def norm_title(t: str) -> str:
    t = re.sub(r"\\[A-Za-z]+", "", t)
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


def has_field(e, spec: str) -> bool:
    return any(e["fields"].get(f, "").strip() for f in spec.split("|"))


def detect_backend(bib_paths):
    for b in bib_paths:
        d = Path(b).resolve().parent
        for cand in list(d.glob("*.tex")) + list(d.parent.glob("*.tex")):
            try:
                t = read_text(cand)
            except OSError:
                continue
            t = re.sub(r"(?<!\\)%.*", "", t)
            if re.search(r"\\usepackage\s*(\[[^\]]*\])?\s*\{biblatex(-chicago)?\}", t):
                m = re.search(r"backend\s*=\s*(\w+)", t)
                return (m.group(1).lower() if m else "biber").replace("bibtex8", "bibtex").replace("bibtexu", "bibtex")
            if re.search(r"\\bibliographystyle\s*\{", t):
                return "bibtex"
    return "unknown"


# ----------------------------------------------------------------------------- lint

def lint(entries, backend: str = "unknown", strings=None, today=None):
    """Return a list of findings: dict(severity, check, file, line, key, message)."""
    F = []
    today = today or dt.date.today()
    strings = strings or {}

    def add(sev, check, e, msg, field=None):
        line = e["field_lines"].get(field, e["line"]) if (e and field) else (e["line"] if e else None)
        F.append({"severity": sev, "check": check, "file": e["file"] if e else None, "line": line,
                  "key": e["key"] if e else None, "message": msg})

    bibtex = backend == "bibtex"
    biber = backend == "biber"
    keys_ci = defaultdict(list)
    for e in entries:
        keys_ci[e["key"].lower()].append(e)
    for k, es in keys_ci.items():
        if len(es) > 1:
            where = ", ".join(f"{Path(x['file']).name}:{x['line']}" for x in es)
            add("error", "structure", es[1], f"duplicate key '{es[0]['key']}': {where} — BibTeX compares keys "
                "case-insensitively and stops with 'Repeated entry'; biber treats them as different keys and only "
                "warns of a case mismatch")
    dois, titles = defaultdict(list), defaultdict(list)
    for e in entries:
        f = e["fields"]
        if e["commented"]:
            add("warning", "structure", e, "entry on a %-commented line: BibTeX has no % comments and still reads "
                "it, biber ignores it — the backends disagree; delete it or wrap it in @comment{...}")
        if re.search(r"[\s,{}()\"#%'=~\\]", e["key"]) or not e["key"]:
            add("error", "structure", e, f"illegal characters in key '{e['key']}'")
        elif re.search(r"[^\x00-\x7f]", e["key"]):
            add("warning", "structure", e, f"non-ASCII key '{e['key']}' (BibTeX is 8-bit; use ASCII keys)")
        for d in sorted(set(e["dup_fields"])):
            add("error", "structure", e, f"field '{d}' appears twice: BibTeX keeps the first (with a warning), "
                "biber silently keeps the last", d)
        etype = e["type"]
        for spec in REQUIRED.get(etype, []):
            if not has_field(e, spec):
                if etype == "online" and spec == "url|doi|eprint":
                    add("warning", "fields", e, "@online without url/doi/eprint")
                else:
                    add("warning", "fields", e, f"@{etype} without {spec.replace('|', ' or ')}")
        if etype not in REQUIRED and etype not in BIBLATEX_ONLY_TYPES:
            add("info", "types", e, f"unusual entry type @{etype}: check that your style knows it")
        if bibtex and etype in BIBLATEX_ONLY_TYPES:
            add("warning", "types", e, f"@{etype} is a biblatex type: standard BibTeX styles treat it as @misc "
                "(or warn) — use @misc with howpublished/note, or switch to biblatex+biber")
        if bibtex:
            used = sorted(x for x in f if x in BIBLATEX_ONLY_FIELDS)
            if used:
                add("info", "types", e, "biblatex-only field(s) ignored by BibTeX styles: " + ", ".join(used))
            if "date" in f and "year" not in f:
                add("warning", "dates", e, "date without year: BibTeX styles print no year — add year = {...}", "date")
        for name, value in f.items():
            if not value.strip() and name not in ("note",):
                add("info", "fields", e, f"empty field '{name}'", name)
        if "crossref" in f and f["crossref"].lower() not in keys_ci:
            add("error", "fields", e, f"crossref target '{f['crossref']}' not found", "crossref")
        for name, pieces in e["raw"].items():
            for kind, tok in pieces:
                if kind == "macro" and tok.lower() not in strings and tok.lower() not in PREDEFINED_MACROS:
                    add("warning", "structure", e, f"field '{name}' uses undefined @string macro '{tok}' (fine only "
                        "if another .bib loaded with this one defines it, e.g. IEEEabrv.bib)", name)
        # names
        for nf in NAME_FIELDS:
            if nf not in f:
                continue
            value = f[nf]
            names = split_names(value)
            top_commas = strip_braced(value).count(",")
            if len(names) == 1 and top_commas >= 2:
                add("warning", "names", e, f"{nf} looks like a comma-separated list — separate names with "
                    f"' and ': {value[:70]!r}", nf)
            elif len(names) == 1 and top_commas == 1:
                left, right = [s.split() for s in strip_braced(value).split(",", 1)]
                caps = lambda ws: len(ws) >= 2 and all(w[:1].isupper() and not re.fullmatch(r"[A-Z]\.?", w)
                                                       for w in ws)
                if caps(left) and caps(right):
                    add("warning", "names", e, f"{nf} = {value[:60]!r} is read as ONE person (surname "
                        f"'{' '.join(left)}'); if these are two people write ' and ' instead of the comma", nf)
            for idx, nm in enumerate(names):
                bare = strip_braced(nm)
                if re.search(r"\bet\.?\s*al\b", nm, re.I):
                    add("warning", "names", e, f"literal 'et al.' in {nf}: write 'and others' (the style "
                        "prints et al.)", nf)
                if nm.strip().lower() == "others" and idx != len(names) - 1:
                    add("error", "names", e, f"'others' must be the last name in {nf}", nf)
                if bare.count(",") > 2:
                    add("error", "names", e, f"name with more than two commas in {nf}: {nm[:50]!r}", nf)
                if not nm.startswith("{") and ORG_WORDS.search(bare) and len(bare.split()) >= 2 and "," not in bare:
                    add("warning", "names", e, f"'{nm.strip()[:50]}' in {nf} looks like an organisation: unbraced, "
                        f"it is parsed as a person (surname = last word) — if so, write {{{{{nm.strip()}}}}}", nf)
                if re.search(r"\b[A-Z]\.[A-Z]\.", bare):
                    add("info", "names", e, f"initials without spaces in {nf} ({nm.strip()[:40]!r}): write "
                        "'J. R. R.' so abbreviating styles keep every initial", nf)
                letters = re.sub(r"[^A-Za-z]", "", bare)
                if len(letters) > 3 and letters.isupper() and not nm.startswith("{"):
                    add("info", "names", e, f"name in ALL CAPS in {nf} ({nm.strip()[:40]!r}): styles cannot "
                        "restore the case — retype it", nf)
            if bibtex and re.search(r"[^\x00-\x7f]", value):
                add("warning", "encoding", e, f"non-ASCII letters in {nf} with BibTeX: initials, sorting and "
                    "uppercasing break — use TeX escapes ({\\'e}, {\\\"o}, {\\c{c}}) or biblatex+biber", nf)
        # titles and special characters
        for name, value in f.items():
            if name in VERBATIM_FIELDS:
                continue
            bad = unescaped_specials(value)
            if bad:
                rarely_printed = name in ("abstract", "keywords", "annote", "annotation", "comment", "review")
                add("warning" if rarely_printed else "error", "titles", e,
                    f"unescaped {' '.join(bad)} in '{name}' (LaTeX error or silently lost text"
                    + (" when the style prints this field; biber copies it into the .bbl" if rarely_printed else "")
                    + "): write \\& \\% \\# \\_ or use math mode", name)
        for tf in TITLE_FIELDS:
            if tf not in f:
                continue
            value = f[tf].strip()
            raw = e["raw"].get(tf, [])
            if len(raw) == 1 and raw[0][0] == "brace" and re.fullmatch(r"\{.*\}", raw[0][1].strip(), re.S) \
                    and _balanced_whole(raw[0][1].strip()):
                add("info", "titles", e, f"whole {tf} in double braces: the style cannot apply its case rules "
                    "— brace only the words that must keep capitals", tf)
                continue
            caps = unprotected_caps(value)
            if caps and tf in ("title", "booktitle"):
                sev = "warning" if bibtex else "info"
                add(sev, "titles", e, f"unprotected capitals in {tf}: {', '.join(caps[:6])} — sentence-case styles "
                    "lowercase them; write {" + caps[0] + "}", tf)
        # identifiers
        doi = f.get("doi", "").strip()
        if doi:
            if re.match(r"(https?://(dx\.)?doi\.org/|doi:\s*)", doi, re.I):
                add("warning", "identifiers", e, f"doi stored with a prefix ({doi[:40]}): store the bare DOI "
                    "10.xxxx/... — styles add the link", "doi")
                doi = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", doi, flags=re.I)
            if not re.fullmatch(r"10\.\d{4,9}/\S+", doi):
                add("warning", "identifiers", e, f"malformed DOI '{doi[:50]}'", "doi")
            dois[doi.lower()].append(e)
            if doi and doi.lower() in f.get("url", "").lower():
                add("info", "identifiers", e, "url repeats the DOI: most styles then print both — drop the url",
                    "url")
        url = f.get("url", "")
        if url:
            if re.search(r"\s", url.strip()):
                add("warning", "identifiers", e, "space inside url (biber percent-encodes it as %20, BibTeX "
                    "styles print it as is) — check the address", "url")
            if "\\url" in url:
                add("warning", "identifiers", e, "\\url{...} inside the url field: store the bare address", "url")
            if biber and re.search(r"\\[_%&#~]", url):
                add("warning", "identifiers", e, "escaped character in url (\\_ \\% ...): biber reads url "
                    "verbatim and would print the backslash", "url")
            if bibtex and re.search(r"(?<!\\)%", url):
                add("error", "identifiers", e, "unescaped % in url: under BibTeX it comments out the rest of the "
                    ".bbl line — write \\%", "url")
        # dates
        year = f.get("year", "").strip()
        if not year and not f.get("date", "").strip() and e["type"] not in ("online", "misc", "software",
                                                                             "manual", "booklet", "unpublished"):
            add("warning", "dates", e, "no year/date")
        if year:
            ym = re.fullmatch(r"(\d{4})[a-z]?", year)
            if not ym and not re.fullmatch(r"(n\.\s?d\.|in press|forthcoming|submitted|\d{4}[/-]\d{2,4})", year,
                                           re.I):
                add("warning", "dates", e, f"year '{year}' is not a 4-digit year", "year")
            elif ym and int(ym.group(1)) > today.year + 1:
                add("warning", "dates", e, f"year {year} is in the future", "year")
        if bibtex and "month" in f:
            raw = e["raw"].get("month", [])
            if raw and raw[0][0] in ("brace", "quote") and not raw[0][1].strip().isdigit():
                add("info", "dates", e, "month typed as text: use the macro month = jan (no braces) so the style "
                    "abbreviates/translates it", "month")
        # preprints
        venue = f.get("journal", "") + " " + f.get("journaltitle", "")
        if re.search(r"arxiv|biorxiv|medrxiv|ssrn|preprint", venue, re.I):
            add("info", "types", e, "preprint exported as a journal article (Google Scholar style): use "
                "@misc/@online with eprint = {ID}, eprinttype = {arxiv} (biblatex), and check whether a "
                "peer-reviewed version now exists")
        t = norm_title(f.get("title", ""))
        if len(t) > 12:
            titles[t].append(e)
    for d, es in dois.items():
        if len(es) > 1 and d:
            add("warning", "duplicates", es[1], f"same DOI as '{es[0]['key']}' — probably the same work twice")
    for t, es in titles.items():
        if len(es) > 1 and len({x['key'].lower() for x in es}) > 1:
            add("warning", "duplicates", es[1], f"same title as '{es[0]['key']}' — duplicate entry or "
                "preprint + published version?")
    order = {s: i for i, s in enumerate(SEVERITIES)}
    F.sort(key=lambda x: (order[x["severity"]], x["file"] or "", x["line"] or 0))
    return F


def _balanced_whole(s: str) -> bool:
    """True when s is '{...}' and the first brace closes at the very end."""
    if not (s.startswith("{") and s.endswith("}")):
        return False
    depth = 0
    for i, c in enumerate(s):
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0 and i != len(s) - 1:
                return False
    return True


# ----------------------------------------------------------------------------- report

def render(files, entries, findings, backend):
    L = [f"# bib-check — {', '.join(Path(f).name for f in files)}\n",
         f"- Entries: **{len(entries)}** · backend: **{backend}** "
         "(auto-detected from the .tex next to the .bib; pass --backend to override)"]
    counts = Counter(x["severity"] for x in findings)
    L.append("- Findings: " + " · ".join(f"{s}: **{counts.get(s, 0)}**" for s in SEVERITIES) + "\n")
    for sev in SEVERITIES:
        items = [x for x in findings if x["severity"] == sev]
        if not items:
            continue
        L.append(f"## {sev.upper()} ({len(items)})\n")
        for x in items:
            loc = f"{Path(x['file']).name}:{x['line']}" if x["file"] else "-"
            key = f" `{x['key']}`" if x["key"] else ""
            L.append(f"- {loc}{key} [{x['check']}] {x['message']}")
        L.append("")
    if not findings:
        L.append("No problems found.")
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


def check_files(paths, backend="auto"):
    entries, strings, problems = [], {}, []
    for p in paths:
        es, ss, pr = parse_bib(p)
        entries += es
        strings.update(ss)
        problems += pr
    if backend == "auto":
        backend = detect_backend(paths)
    findings = problems + lint(entries, backend, strings)
    order = {s: i for i, s in enumerate(SEVERITIES)}
    findings.sort(key=lambda x: (order[x["severity"]], x["file"] or "", x["line"] or 0))
    return entries, findings, backend


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bib", nargs="+")
    ap.add_argument("--backend", choices=["auto", "bibtex", "biber"], default="auto")
    ap.add_argument("--json", help="write findings as JSON to this file (atomic)")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--min-severity", choices=SEVERITIES, default="info")
    args = ap.parse_args()
    paths = [Path(p) for p in args.bib]
    for p in paths:
        if not p.is_file():
            sys.exit(f"not a file: {p}")
    entries, findings, backend = check_files(paths, args.backend)
    keep = SEVERITIES[:SEVERITIES.index(args.min_severity) + 1]
    findings = [x for x in findings if x["severity"] in keep]
    if args.json:
        atomic_write(Path(args.json), json.dumps({"backend": backend, "entries": len(entries),
                                                  "findings": findings}, ensure_ascii=False, indent=2))
    if not args.quiet:
        out = render([str(p) for p in paths], entries, findings, backend)
        try:
            sys.stdout.write(out)
        except UnicodeEncodeError:
            sys.stdout.buffer.write(out.encode("utf-8", errors="replace"))
    sys.exit(1 if any(x["severity"] == "error" for x in findings) else 0)


if __name__ == "__main__":
    main()
