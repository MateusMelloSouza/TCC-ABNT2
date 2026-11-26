#!/usr/bin/env python3
"""init-workflow.py — scaffold the `.academic-workflow/` writing-session folder in a LaTeX project.

    python3 init-workflow.py [PROJECT_DIR] [--build-helpers] [--force]

Creates (never overwriting existing files unless --force):
  .academic-workflow/STATUS.md            living tracker, pre-filled from an audit of the project
  .academic-workflow/TODO.md              numbered debt list, seeded from the audit
  .academic-workflow/TEMPLATE.md          profile skeleton for the project's template
  .academic-workflow/benign-notices.txt   regexes of LaTeX error lines proven harmless (empty)
  .academic-workflow/session-log/_TEMPLATE.md
  .academic-workflow/tools/               copies of audit-tex.py, bib-check.py, compile-check.sh,
                                          setup-sandbox-latex.sh (the project stays self-contained)
--build-helpers additionally drops, at the project root when absent: .latexmkrc (engine and main
file set from the audit), .gitignore, build.bat (Windows) and .vscode/settings.json.

Pure standard library, Python 3.8+. Files are written atomically (temp file + rename).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
ASSETS = SKILL / "assets"
WF = ".academic-workflow"
TOOLS = ("audit-tex.py", "bib-check.py", "compile-check.sh", "setup-sandbox-latex.sh")
THESIS_CLASSES = {"book", "report", "memoir", "scrbook", "scrreprt", "abntex2", "thuthesis", "ut-thesis", "yathesis",
                  "toptesi", "msu-thesis", "uothesis", "ucthesis", "mitthesis", "umthesis", "kaobook", "tufte-book"}
PAPER_CLASSES = {"article", "IEEEtran", "acmart", "elsarticle", "llncs", "revtex4-2", "revtex4-1", "amsart", "scrartcl",
                 "aastex631", "aastex7", "mnras", "jmlr", "svjour3", "sn-jnl"}


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


def put(path: Path, data: str, force: bool, created: list):
    if path.exists() and not force:
        print(f"   keep    {path}")
        return
    atomic_write(path, data)
    created.append(path)
    print(f"   write   {path}")


def copy(src: Path, dst: Path, force: bool, created: list):
    if dst.exists() and not force:
        print(f"   keep    {dst}")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    if src.suffix in (".sh", ".py"):
        try:
            os.chmod(dst, 0o755)
        except OSError:
            pass
    created.append(dst)
    print(f"   copy    {dst}")


def run_audit(root: Path) -> dict:
    out_json = root / WF / "_audit.json"
    try:
        r = subprocess.run([sys.executable, str(HERE / "audit-tex.py"), str(root), "--quiet", "--no-texcount",
                            "--json", str(out_json)], capture_output=True, text=True, timeout=180)
        if out_json.is_file():
            data = json.loads(out_json.read_text(encoding="utf-8"))
            out_json.unlink()
            return data
        print("   (audit produced no data: " + (r.stderr or r.stdout).strip()[:200] + ")")
    except Exception as exc:  # noqa: BLE001
        print(f"   (audit skipped: {exc})")
    return {}


def fill(template: str, values: dict) -> str:
    for k, v in values.items():
        template = template.replace("{{" + k + "}}", str(v))
    return template


def title_of(root: Path, audit: dict) -> str:
    main = root / audit.get("main", "main.tex")
    try:
        t = main.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return root.name
    t = re.sub(r"(?<!\\)%.*", "", t)
    for pat in (r"\\newcommand\{\\thesistitle\}\{([^}]*)\}", r"\\title\s*(?:\[[^\]]*\])?\s*\{([^}]*)\}",
                r"\\titulo\s*\{([^}]*)\}"):
        m = re.search(pat, t)
        if m and m.group(1).strip():
            return re.sub(r"\\\\|\\[A-Za-z]+\s*|[{}]", " ", m.group(1)).strip()[:90]
    return root.name


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", nargs="?", default=".")
    ap.add_argument("--build-helpers", action="store_true",
                    help="also drop .latexmkrc/.gitignore/build.bat/.vscode settings at the root when absent")
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    args = ap.parse_args()
    root = Path(args.project).resolve()
    if not root.is_dir():
        sys.exit(f"not a directory: {root}")
    wf = root / WF
    (wf / "session-log").mkdir(parents=True, exist_ok=True)
    (wf / "tools").mkdir(exist_ok=True)
    created: list = []
    print(f"== scaffolding {wf}")
    for name in TOOLS:
        copy(HERE / name, wf / "tools" / name, args.force, created)

    a = run_audit(root)
    today = dt.date.today().isoformat()
    cls = (a.get("documentclass") or {}).get("class", "?")
    doctype = "thesis/dissertation" if cls in THESIS_CLASSES else ("article/paper" if cls in PAPER_CLASSES else "?")
    tool = a.get("bibliography_tool")
    chain = "latexmk (" + (tool or "no bibliography tool") + (", makeglossaries" if any(
        "makeglossaries" in g for g in a.get("glossary_index_tools", [])) else "") + ")"
    style = a.get("biblatex_style")
    if not style:
        sm = re.search(r"bibliographystyle\{([^}]+)\}", a.get("citation_stack", ""))
        style = sm.group(1) if sm else "?"
    rows = []
    heads = a.get("headings") or {}
    for f, n in (a.get("word_counts") or {}).items():
        if f in heads:
            state = "empty" if n < 60 else ("outline" if n < 300 else "draft")
            rows.append(f"| `{f}` | {heads[f]} | {n} | {state} | |")
    log = a.get("log") or {}
    fl = a.get("floats") or {}
    nfl = sum((fl.get("count_by_env") or {}).values())
    cit = a.get("citations") or {}
    lint_err = (cit.get("bib_lint_counts") or {}).get("error", 0)
    values = {
        "TITLE": title_of(root, a), "DATE": today, "SESSION": "00", "AUTHOR": "?", "PROGRAMME": "?",
        "INSTITUTION": "?", "DOCTYPE": doctype, "VENUE": "?", "RULES": "?",
        "TEMPLATE": a.get("template_family", "?"), "MAIN": a.get("main", "main.tex"), "ENGINE": a.get("engine", "?"),
        "CHAIN": chain, "CITATION_STACK": a.get("citation_stack", "?"), "STYLE_GUIDE": style or "?",
        "LANGUAGE": ", ".join(a.get("languages") or []) or "?", "PAGE_LIMIT": "?", "WORD_LIMIT": "?",
        "ABSTRACT_LIMIT": "?", "PEOPLE": "?", "DEADLINES": "?",
        "VCS": "git" if (root / ".git").is_dir() else "none",
        "PAGES": log.get("pages", "?"), "ERRORS": len(log.get("errors", [])) if log else "?", "BENIGN": "0",
        "UNDEF_CITES": len(log.get("undefined_citations", [])) if log else "?",
        "UNDEF_REFS": len(log.get("undefined_references", [])) if log else "?",
        "FLOATS": (f"{nfl} floats; {len(fl.get('without_caption', []))} without caption, "
                   f"{len(fl.get('without_label', []))} without label, {len(fl.get('never_referenced', []))} never "
                   "referenced") if fl else "?",
        "BIB": (f"{cit.get('bib_entries', '?')} entries / {cit.get('distinct_cited', '?')} cited / "
                f"{len(cit.get('missing_in_bib', []))} missing / {lint_err} lint errors") if cit else "?",
        "OVERFULL": log.get("overfull", "?"), "FLOAT_TOO_LARGE": log.get("float_too_large", "?"),
        "ABSTRACT": ", ".join(f"{x['words']} ({x['block']})" for x in a.get("abstracts", [])) or "?",
        "WORDS": a.get("word_count_total", "?"),
        "CHAPTER_ROWS": "\n".join(rows) if rows else "| | | | | |",
        "META_STATE": "?", "ABSTRACT_STATE": "?", "LISTS_STATE": "?", "BIB_STATE": "?", "APPENDICES_STATE": "?",
        "PLACEHOLDER_COUNT": len(a.get("placeholders", [])), "TEMPLATE_NAME": a.get("template_family", "?"),
    }
    put(wf / "STATUS.md", fill((ASSETS / "STATUS-template.md").read_text(encoding="utf-8"), values), args.force, created)
    put(wf / "TODO.md", fill((ASSETS / "TODO-template.md").read_text(encoding="utf-8"), values), args.force, created)
    put(wf / "TEMPLATE.md", fill((ASSETS / "TEMPLATE-profile.md").read_text(encoding="utf-8"), values), args.force,
        created)
    put(wf / "session-log" / "_TEMPLATE.md", (ASSETS / "session-log-template.md").read_text(encoding="utf-8"),
        args.force, created)
    put(wf / "benign-notices.txt", (ASSETS / "benign-notices.txt").read_text(encoding="utf-8"), args.force, created)
    if "abnTeX2" in values["TEMPLATE"]:
        print("   note    abnTeX2 (ABNT) detected — the tcc-abnt skill has the ABNT-specific profiles and fixes")

    if args.build_helpers:
        print("== build helpers at the project root")
        main_name = Path(values["MAIN"]).name
        if not (root / ".latexmkrc").exists() and not (root / "latexmkrc").exists():
            mode = {"lualatex": 4, "xelatex": 5}.get(str(values["ENGINE"]).split()[0], 1)
            rc = (ASSETS / "latexmkrc").read_text(encoding="utf-8")
            rc = re.sub(r"^\$pdf_mode = \d+;", f"$pdf_mode = {mode};", rc, count=1, flags=re.M)
            rc = rc.replace("$pdf_mode", f"@default_files = ('{values['MAIN']}');   # the main file\n$pdf_mode", 1)
            put(root / ".latexmkrc", rc, args.force, created)
        else:
            print("   keep    existing latexmkrc")
        if not (root / ".gitignore").exists():
            copy(ASSETS / "gitignore-latex", root / ".gitignore", args.force, created)
        else:
            print("   keep    .gitignore (merge assets/gitignore-latex by hand if needed)")
        copy(ASSETS / "build.bat", root / "build.bat", args.force, created)
        vs = (ASSETS / "vscode-settings.json").read_text(encoding="utf-8").replace("main.tex", values["MAIN"])
        put(root / ".vscode" / "settings.json", vs, args.force, created)
        if main_name != "main.tex":
            print(f"   note    build.bat defaults to main.tex: run it as  build.bat {Path(main_name).stem}")

    print(f"== done: {len(created)} file(s) written. Next: fill the '?' fields of STATUS.md with the author, then "
          f"run {WF}/tools/compile-check.sh and log session 01.")


if __name__ == "__main__":
    main()
