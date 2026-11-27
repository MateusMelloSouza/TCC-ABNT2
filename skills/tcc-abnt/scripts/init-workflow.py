#!/usr/bin/env python3
"""init-workflow.py — scaffold the `.tcc-workflow/` session-workflow folder in a thesis project.

    python3 init-workflow.py [PROJECT_DIR] [--build-helpers] [--force]

Creates (never overwriting existing files unless --force):
  .tcc-workflow/STATUS.md            living tracker, pre-filled from an audit of the project
  .tcc-workflow/TODO.md              numbered debt list, seeded from the audit
  .tcc-workflow/TEMPLATE.md          profile skeleton for the institutional template
  .tcc-workflow/benign-notices.txt   regexes of LaTeX error lines proven harmless (empty by default)
  .tcc-workflow/session-log/_TEMPLATE.md
  .tcc-workflow/tools/{setup-sandbox-latex.sh, compile-check.sh, audit-tex.py}   copies of the skill scripts
--build-helpers additionally drops, at the project root when absent:
  .latexmkrc (only if the sources use \\makeglossaries), .gitignore, compilar.bat, .vscode/settings.json

Pure standard library. Files are written atomically (temp + rename).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
ASSETS = SKILL / "assets"


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
    try:
        out = subprocess.run([sys.executable, str(HERE / "audit-tex.py"), str(root), "--quiet",
                              "--json", str(root / ".tcc-workflow" / "_audit.json")],
                             capture_output=True, text=True, timeout=120)
        j = root / ".tcc-workflow" / "_audit.json"
        if j.is_file():
            data = json.loads(j.read_text(encoding="utf-8"))
            j.unlink()
            return data
        print("   (audit produced no data: " + (out.stderr or out.stdout).strip()[:200] + ")")
    except Exception as exc:  # pragma: no cover
        print(f"   (audit skipped: {exc})")
    return {}


def fill(template: str, values: dict) -> str:
    for k, v in values.items():
        template = template.replace("{{" + k + "}}", str(v))
    return template


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", nargs="?", default=".")
    ap.add_argument("--build-helpers", action="store_true", help="also drop .latexmkrc/.gitignore/compilar.bat/.vscode settings at the root")
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    args = ap.parse_args()
    root = Path(args.project).resolve()
    if not root.is_dir():
        sys.exit(f"not a directory: {root}")
    wf = root / ".tcc-workflow"
    wf.mkdir(exist_ok=True)
    (wf / "session-log").mkdir(exist_ok=True)
    (wf / "tools").mkdir(exist_ok=True)
    created: list = []
    print(f"== scaffolding {wf}")

    # tools first (the audit below uses the skill copy, but the project copy must exist too)
    for name in ("setup-sandbox-latex.sh", "compile-check.sh", "audit-tex.py"):
        copy(HERE / name, wf / "tools" / name, args.force, created)

    audit = run_audit(root)
    today = dt.date.today().isoformat()
    profile = audit.get("template_profile", "unknown")
    main_file = audit.get("main", "main.tex")
    chain = "pdflatex → bibtex → " + ("makeglossaries → " if audit.get("uses_glossaries") else "") + "pdflatex ×2"
    if "biblatex" in audit.get("citation_stack", ""):
        chain = "pdflatex → biber → pdflatex ×2"
    rows = []
    for f, n in (audit.get("word_counts") or {}).items():
        if "/elementos-textuais/" in "/" + f or f.startswith("elementos-textuais") or "cap" in f or "chapter" in f:
            state = "empty" if n < 50 else "draft"
            rows.append(f"| `{f}` | | {n} | {state} | |")
    if not rows:
        rows = [f"| `{f}` | | {n} | draft | |" for f, n in (audit.get("word_counts") or {}).items()][:20]
    log = audit.get("log") or {}
    floats = audit.get("floats") or {}
    cits = audit.get("citations") or {}
    values = {
        "TITLE": root.name, "DATE": today, "SESSION": "00", "AUTHOR": "?", "COURSE": "?", "INSTITUTION": "?",
        "DOCTYPE": "?", "TEMPLATE": profile, "MAIN": main_file, "CHAIN": chain,
        "CITATION_STACK": audit.get("citation_stack", "?"), "ED10520": "? (2002 caps / 2023 initial caps)",
        "KWSEP": "?", "ED14724": "?", "DECIDED_BY": "?", "ORIENTADOR": "?", "BANCA": "?", "DEFESA": "?", "DEPOSITO": "?",
        "VCS": "git" if (root / ".git").is_dir() else "none",
        "PAGES": log.get("pages", "?"), "ERRORS": len(log.get("errors", [])) if log else "?", "BENIGN": "?",
        "UNDEF_CITES": len(log.get("undefined_citations", [])) if log else "?",
        "UNDEF_REFS": len(log.get("undefined_references", [])) if log else "?",
        "FLOATS": f"{sum((floats.get('count_by_env') or {}).values())} floats, {len(floats.get('without_source', []))} without source" if floats else "?",
        "BIB": f"{cits.get('bib_entries', '?')} entries / {cits.get('distinct_cited', '?')} cited; missing {len(cits.get('missing_in_bib', []))}, uncited {len(cits.get('uncited_entries', []))}" if cits else "?",
        "OVERFULL": log.get("overfull", "?"), "FLOAT_TOO_LARGE": log.get("float_too_large", "?"),
        "RESUMO": next((r["words"] for r in audit.get("resumo_abstract", []) if "resumo" in r["block"]), "?"),
        "ABSTRACT": next((r["words"] for r in audit.get("resumo_abstract", []) if "abstract" in r["block"]), "?"),
        "CHAPTER_ROWS": "\n".join(rows) if rows else "| | | | | |",
        "META_STATE": "?", "RESUMO_STATE": "?", "LISTS_STATE": "?", "BIB_STATE": "?", "APPENDICES_STATE": "?",
        "PLACEHOLDER_COUNT": len(audit.get("placeholders", [])),
        "TEMPLATE_NAME": profile,
    }
    put(wf / "STATUS.md", fill((ASSETS / "STATUS-template.md").read_text(encoding="utf-8"), values), args.force, created)
    put(wf / "TODO.md", fill((ASSETS / "TODO-template.md").read_text(encoding="utf-8"), values), args.force, created)
    put(wf / "TEMPLATE.md", fill((ASSETS / "TEMPLATE-profile.md").read_text(encoding="utf-8"), values), args.force, created)
    put(wf / "session-log" / "_TEMPLATE.md", (ASSETS / "session-log-template.md").read_text(encoding="utf-8"), args.force, created)
    put(wf / "benign-notices.txt", (ASSETS / "benign-notices.txt").read_text(encoding="utf-8"), args.force, created)
    if profile == "unifortex2":
        print("   note    UniforTeX2 detected — read references/templates/unifortex2.md (quirk 1: add {} after the"
              " boolean setters in main.tex) and fill TEMPLATE.md from it")

    if args.build_helpers:
        print("== build helpers at the project root")
        if audit.get("uses_glossaries") and not (root / ".latexmkrc").exists() and not (root / "latexmkrc").exists():
            copy(ASSETS / "latexmkrc", root / ".latexmkrc", args.force, created)
        if not (root / ".gitignore").exists():
            copy(ASSETS / "gitignore-latex", root / ".gitignore", args.force, created)
        copy(ASSETS / "compilar.bat", root / "compilar.bat", args.force, created)
        copy(ASSETS / "vscode-settings.json", root / ".vscode" / "settings.json", args.force, created)

    print(f"== done: {len(created)} file(s) written. Next: open STATUS.md, fill the '?' fields with the user, "
          f"then run tools/compile-check.sh and log sessão 01.")


if __name__ == "__main__":
    main()
