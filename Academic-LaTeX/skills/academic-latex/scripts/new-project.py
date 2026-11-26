#!/usr/bin/env python3
"""new-project.py — start a LaTeX project from a tested skeleton (thesis, article or response letter).

    python3 new-project.py DEST [--type thesis|article|letter] [--style STYLE] [--engine ENGINE]
                           [--language LANG] [--paper a4|letter] [--spacing single|onehalf|double]
                           [--twoside] [--title TEXT] [--author TEXT] [--workflow] [--force]

Use it only when the institution or venue provides no template: an official template always wins.

  --type      thesis (book class: front/main/back matter, abbreviations, appendices; default),
              article (IMRaD paper with authblk affiliations), letter (response to reviewers)
  --style     biblatex citation style, one of the names printed by --list-styles (default:
              authoryear for theses, numeric for articles)
  --engine    pdflatex (default) | lualatex | xelatex  (Lua/XeLaTeX: Unicode text, OpenType fonts)
  --language  babel language of the document, e.g. english, british, american, ngerman, french,
              spanish, brazilian, italian; a comma list puts the main language LAST
  --workflow  also run init-workflow.py on the new project (writing-session state folder)

Writes the project, a .latexmkrc for the chosen engine and a .gitignore; never overwrites an
existing non-empty directory unless --force. Pure standard library, Python 3.8+.
"""
from __future__ import annotations

import argparse
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
SKELETONS = ASSETS / "skeletons"

# style name -> (biblatex loading line, short description). Every entry is compiled in CI.
STYLES = {
    "authoryear": (r"\usepackage[backend=biber, style=authoryear]{biblatex}",
                   "generic author-year (Harvard-like): (Knuth 1984)"),
    "numeric": (r"\usepackage[backend=biber, style=numeric-comp, sorting=none]{biblatex}",
                "numbers in order of first citation, ranges compressed: [1-3]"),
    "alphabetic": (r"\usepackage[backend=biber, style=alphabetic]{biblatex}",
                   "alphanumeric labels, common in mathematics/CS: [Knu84]"),
    "apa": (r"\usepackage[backend=biber, style=apa]{biblatex}",
            "APA 7th edition (biblatex-apa)"),
    "ieee": (r"\usepackage[backend=biber, style=ieee]{biblatex}",
             "IEEE (biblatex-ieee): [1]"),
    "chicago-authordate": (r"\usepackage[authordate, backend=biber]{biblatex-chicago}",
                           "Chicago author-date (biblatex-chicago)"),
    "chicago-notes": (r"\usepackage[notes, backend=biber]{biblatex-chicago}",
                      "Chicago notes and bibliography: citations in footnotes (biblatex-chicago)"),
    "mla": (r"\usepackage[backend=biber, style=mla]{biblatex}",
            "MLA (biblatex-mla)"),
    "nature": (r"\usepackage[backend=biber, style=nature]{biblatex}",
               "Nature: superscript numbers (biblatex-nature)"),
    "vancouver": (r"\usepackage[backend=biber, style=vancouver]{biblatex}",
                  "Vancouver / ICMJE, biomedicine (biblatex-vancouver)"),
    "iso-authoryear": (r"\usepackage[backend=biber, style=iso-authoryear]{biblatex}",
                       "ISO 690 author-date (biblatex-iso690)"),
    "iso-numeric": (r"\usepackage[backend=biber, style=iso-numeric]{biblatex}",
                    "ISO 690 numeric (biblatex-iso690)"),
    "abnt": (r"\usepackage[backend=biber, style=abnt]{biblatex}",
             "ABNT NBR 6023/10520, Brazil (biblatex-abnt)"),
    "chem-acs": (r"\usepackage[backend=biber, style=chem-acs]{biblatex}",
                 "American Chemical Society (biblatex-chem)"),
    "phys": (r"\usepackage[backend=biber, style=phys]{biblatex}",
             "AIP/APS physics journals (biblatex-phys)"),
}

ENGINE_BLOCKS = {
    "pdflatex": (1, "\\usepackage[T1]{fontenc}\n"
                    "\\usepackage{lmodern}          % or: \\usepackage{newtxtext,newtxmath} for a Times-like face"),
    "lualatex": (4, "\\usepackage{fontspec}         % Unicode input and OpenType fonts; Latin Modern by default\n"
                    "% \\setmainfont{TeX Gyre Termes}   % a Times-like face that ships with TeX Live"),
    "xelatex": (5, "\\usepackage{fontspec}         % Unicode input and OpenType fonts; Latin Modern by default\n"
                   "% \\setmainfont{TeX Gyre Termes}   % a Times-like face that ships with TeX Live"),
}

GEOMETRY = {
    ("thesis", "a4"): r"\usepackage[top=25mm, bottom=25mm, left=35mm, right=25mm]{geometry}  % wide left margin for binding",
    ("thesis", "letter"): r"\usepackage[top=1in, bottom=1in, left=1.5in, right=1in]{geometry}  % wide left margin for binding",
    ("article", "a4"): r"\usepackage[margin=25mm]{geometry}",
    ("article", "letter"): r"\usepackage[margin=1in]{geometry}",
}

SPACING = {"single": r"\singlespacing", "onehalf": r"\onehalfspacing", "double": r"\doublespacing"}

MAIN_FILE = {"thesis": "main.tex", "article": "main.tex", "letter": "response.tex"}
SKELETON_DIR = {"thesis": "thesis", "article": "article", "letter": "response-letter"}

BLOCK = re.compile(r"^%% <<academic-latex:([a-z]+)>>\n(.*?)^%% <</academic-latex:\1>>\n", re.M | re.S)


def tex_escape(s: str) -> str:
    repl = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
            "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(repl.get(c, c) for c in s)


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


def render_main(text: str, args, doc_type: str) -> str:
    def block(m: re.Match) -> str:
        name, body = m.group(1), m.group(2)
        if name == "class":
            body = body.replace("a4paper", "letterpaper") if args.paper == "letter" else body
            if args.twoside:
                body = body.replace("oneside, openany", "twoside, openright")
        elif name == "engine":
            body = ENGINE_BLOCKS[args.engine][1] + "\n"
        elif name == "language":
            body = "\\usepackage[%s]{babel}   %% last option = main language\n" % args.language
        elif name == "geometry":
            body = GEOMETRY[(doc_type, args.paper)] + "\n"
        elif name == "spacing":
            body = SPACING[args.spacing] + "   % footnotes and floats stay single-spaced (setspace)\n"
        elif name == "bibliography":
            body = STYLES[args.style][0] + "   % " + STYLES[args.style][1] + "\n"
        return body

    text = BLOCK.sub(block, text)
    text = re.sub(r"^% !TEX program = \w+", "% !TEX program = " + args.engine, text, count=1, flags=re.M)
    if args.title:
        t = tex_escape(args.title)
        text = text.replace("Title of the Thesis: An Informative Subtitle", t)
        text = text.replace("Informative Title That States the Main Finding", t)
    if args.author:
        a = tex_escape(args.author)
        text = text.replace("Author Full Name", a)
        text = text.replace(r"\author[1]{First Author", r"\author[1]{" + a)
        text = text.replace("pdfauthor={First Author, Second Author}", "pdfauthor={" + a + "}")
    return text


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dest", nargs="?", help="directory to create")
    ap.add_argument("--type", choices=sorted(MAIN_FILE), default="thesis")
    ap.add_argument("--style", choices=sorted(STYLES))
    ap.add_argument("--engine", choices=sorted(ENGINE_BLOCKS), default="pdflatex")
    ap.add_argument("--language", default="english")
    ap.add_argument("--paper", choices=["a4", "letter"], default="a4")
    ap.add_argument("--spacing", choices=sorted(SPACING), default="onehalf", help="thesis line spacing")
    ap.add_argument("--twoside", action="store_true", help="thesis: two-sided layout for printed copies")
    ap.add_argument("--title")
    ap.add_argument("--author")
    ap.add_argument("--workflow", action="store_true", help="also scaffold .academic-workflow/")
    ap.add_argument("--force", action="store_true", help="write into an existing non-empty directory")
    ap.add_argument("--list-styles", action="store_true", help="print the available citation styles")
    args = ap.parse_args()

    if args.list_styles:
        for name, (line, desc) in STYLES.items():
            print(f"{name:20} {desc}\n{'':20} {line}")
        return
    if not args.dest:
        ap.error("DEST is required")
    if not re.fullmatch(r"[A-Za-z]+(,[A-Za-z]+)*", args.language):
        ap.error("--language must be babel option names, e.g. english or ngerman,english")
    if args.style is None:
        args.style = "numeric" if args.type == "article" else "authoryear"

    dest = Path(args.dest).resolve()
    if dest.exists() and any(dest.iterdir()) and not args.force:
        sys.exit(f"!! {dest} exists and is not empty (use --force to write into it)")
    src = SKELETONS / SKELETON_DIR[args.type]
    print(f"== creating {args.type} project in {dest}  (style {args.style}, engine {args.engine}, "
          f"language {args.language}, paper {args.paper})")
    for f in sorted(src.rglob("*")):
        if f.is_dir() or "__pycache__" in f.parts:
            continue
        rel = f.relative_to(src)
        out = dest / rel
        if out.exists() and not args.force:
            print(f"   keep    {rel}")
            continue
        text = f.read_text(encoding="utf-8")
        if f.name == MAIN_FILE[args.type]:
            text = render_main(text, args, args.type)
        atomic_write(out, text)
        print(f"   write   {rel}")

    rc = (ASSETS / "latexmkrc").read_text(encoding="utf-8")
    rc = re.sub(r"^\$pdf_mode = \d+;", f"$pdf_mode = {ENGINE_BLOCKS[args.engine][0]};", rc, count=1, flags=re.M)
    rc = rc.replace("$pdf_mode", "@default_files = ('%s');   # the main file\n$pdf_mode" % MAIN_FILE[args.type], 1)
    for name, data in ((".latexmkrc", rc), (".gitignore", (ASSETS / "gitignore-latex").read_text(encoding="utf-8"))):
        if (dest / name).exists() and not args.force:
            print(f"   keep    {name}")
        else:
            atomic_write(dest / name, data)
            print(f"   write   {name}")

    if args.workflow:
        subprocess.run([sys.executable, str(HERE / "init-workflow.py"), str(dest)], check=False)

    print("== next steps\n"
          f"   cd {dest}\n"
          "   latexmk                      # builds the PDF (runs biber and all passes)\n"
          f"   bash {HERE / 'compile-check.sh'}   # build + actionable summary\n"
          "   Replace every '% TODO:' (the audit lists them), the example references and the metadata.")


if __name__ == "__main__":
    main()
