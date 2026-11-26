#!/usr/bin/env python3
"""Regression tests for the skill's scripts (python3 -m unittest discover -s tests -v).

Static tests need only Python 3.8+. Tests that build PDFs are skipped when latexmk is missing.
Fixtures (tests/fixtures/) are copied to temporary directories: the tests never write into them.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "skills" / "academic-latex" / "scripts"
SKELETONS = ROOT / "skills" / "academic-latex" / "assets" / "skeletons"
FIX = ROOT / "tests" / "fixtures"
HAVE_TEX = shutil.which("latexmk") is not None and shutil.which("biber") is not None


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), str(SCRIPTS / f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(*cmd, cwd=None, timeout=600):
    return subprocess.run([str(c) for c in cmd], cwd=cwd, capture_output=True, text=True, timeout=timeout)


def audit_json(project: Path, *extra) -> dict:
    out = Path(tempfile.mkdtemp()) / "a.json"
    r = run(sys.executable, SCRIPTS / "audit-tex.py", project, "--quiet", "--no-texcount", "--json", out, *extra)
    assert out.is_file(), r.stderr
    return json.loads(out.read_text(encoding="utf-8"))


class BibCheck(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bc = load("bib-check")

    def findings(self, path, backend):
        _, findings, _ = self.bc.check_files([path], backend)
        return findings

    def has(self, findings, check, key, text):
        return any(f["check"] == check and f["key"] == key and text in f["message"] for f in findings)

    def test_messy_bib_bibtex(self):
        F = self.findings(FIX / "messy-bib" / "refs.bib", "bibtex")
        expected = [
            ("structure", "Smith2020", "duplicate key"),          # BibTeX: "Repeated entry" (verified)
            ("structure", "old2019", "%-commented"),               # BibTeX still reads it (verified)
            ("structure", "who2021", "appears twice"),             # duplicate year field
            ("names", "smith2020", "ONE person"),                  # "John Smith, Jane Doe"
            ("names", "Smith2020", "'others' must be the last"),
            ("names", "who2021", "looks like an organisation"),
            ("names", "arxivpaper", "literal 'et al.'"),
            ("titles", "smith2020", "unescaped &"),
            ("titles", "smith2020", "unprotected capitals"),       # GPUs -> gpus (verified)
            ("titles", "tool2024", "unescaped %"),                 # the rest of the line vanishes (verified)
            ("titles", "arxivpaper", "double braces"),
            ("identifiers", "smith2020", "prefix"),                # https://doi.org/ inside doi
            ("identifiers", "arxivpaper", "space inside url"),
            ("dates", "arxivpaper", "not a 4-digit year"),
            ("dates", "tool2024", "date without year"),
            ("dates", "dupdoi", "month typed as text"),
            ("types", "tool2024", "biblatex type"),
            ("types", "arxivpaper", "preprint"),
            ("encoding", "tool2024", "non-ASCII"),
            ("duplicates", "dupdoi", "same DOI"),
        ]
        for check, key, text in expected:
            with self.subTest(check=check, key=key):
                self.assertTrue(self.has(F, check, key, text), f"missing finding {check}/{key}/{text}")

    def test_messy_bib_biber_differences(self):
        F = self.findings(FIX / "messy-bib" / "refs.bib", "biber")
        self.assertFalse(any(f["check"] == "encoding" for f in F), "biber handles UTF-8 names")
        self.assertFalse(any(f["check"] == "types" and "biblatex type" in f["message"] for f in F))
        self.assertTrue(self.has(F, "titles", "tool2024", "unescaped %"))

    def test_skeleton_bibs_are_clean(self):
        for bib in (SKELETONS / "thesis" / "references.bib", SKELETONS / "article" / "references.bib"):
            for backend in ("bibtex", "biber"):
                with self.subTest(bib=bib.parent.name, backend=backend):
                    F = [f for f in self.findings(bib, backend) if f["severity"] != "info"]
                    self.assertEqual(F, [])

    def test_names_without_false_positives(self):
        text = ("@book{a, author={Garc{\\'i}a M{\\'a}rquez, Gabriel}, title={T}, publisher={P}, year={1967}}\n"
                "@book{b, author={van der Berg, Jan Willem}, title={T}, publisher={P}, year={2000}}\n"
                "@book{c, author={{World Health Organization}}, title={T}, publisher={P}, year={2020}}\n")
        tmp = Path(tempfile.mkdtemp()) / "n.bib"
        tmp.write_text(text, encoding="utf-8")
        F = [f for f in self.findings(tmp, "bibtex") if f["check"] == "names"]
        self.assertEqual(F, [])

    def test_parser_handles_strings_quotes_and_parentheses(self):
        text = ('@string{jx = "Journal X"}\n'
                '@article(k1, author = "Doe, Jane", title = "A {GPU} " # "study", journal = jx, year = 2020)\n'
                '@comment{ignored @article{fake, title={x}} }\n')
        tmp = Path(tempfile.mkdtemp()) / "p.bib"
        tmp.write_text(text, encoding="utf-8")
        entries, strings, problems = self.bc.parse_bib(tmp)
        self.assertEqual([e["key"] for e in entries], ["k1"])
        self.assertEqual(entries[0]["fields"]["journal"], "Journal X")
        self.assertEqual(entries[0]["fields"]["title"], "A {GPU} study")
        self.assertEqual(problems, [])


class Audit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.R = audit_json(FIX / "messy-thesis", "--abstract-limit", "5")

    def test_inventory(self):
        R = self.R
        self.assertEqual(R["main"], "main.tex")
        self.assertEqual(R["documentclass"]["class"], "report")
        self.assertEqual(R["bibliography_tool"], "biber")
        self.assertIn("chapters/orphan.tex", R["orphan_tex_files"])
        self.assertTrue(any("makeglossaries" in g for g in R["glossary_index_tools"]))

    def test_problems(self):
        P = " ".join(self.R["problems"])
        self.assertIn("without the .bib extension", P)
        self.assertIn("cleveref is loaded before hyperref", P)

    def test_citations(self):
        c = self.R["citations"]
        self.assertEqual(c["missing_in_bib"], ["Smith2020", "missing2021"])
        self.assertEqual(c["case_mismatch"], ["Smith2020"])
        self.assertEqual(c["uncited_entries"], ["uncited2019"])

    def test_refs_and_floats(self):
        r, f = self.R["refs"], self.R["floats"]
        self.assertEqual(r["undefined"], ["sec:nowhere"])
        self.assertTrue(any(x.startswith("sec:api") for x in r["duplicate_labels"]))
        self.assertTrue(any("fig:a" in x for x in r["label_before_caption"]))
        self.assertTrue(any('"Figure 2"' in x for x in r["hard_coded"]))
        self.assertTrue(any("fig:unref" in x for x in f["never_referenced"]))
        self.assertTrue(any("fig:c" in x for x in f["before_first_reference"]))
        self.assertTrue(any("eq:unused" in x for x in self.R["equations"]["labelled_never_referenced"]))

    def test_graphics(self):
        g = self.R["graphics"]
        self.assertTrue(any("figures/missing" in x for x in g["missing"]))
        self.assertTrue(any("figures/Plot" in x for x in g["case_mismatch"]))

    def test_abbreviations(self):
        a = self.R["abbreviations"]
        self.assertTrue(any(x.startswith("cpu") for x in a["unused"]))
        self.assertTrue(any(x.startswith("api") for x in a["literal_only"]))
        self.assertFalse(any(x.startswith("gpu") for x in a["unused"] + a["literal_only"]))

    def test_abstract_and_placeholders(self):
        ab = self.R["abstracts"][0]
        self.assertEqual(ab["words"], 10)
        self.assertTrue(ab.get("over_limit"))
        self.assertEqual(ab["keywords"], ["alpha", "beta", "gamma"])
        ph = " ".join(self.R["placeholders"])
        self.assertIn("TODO: cite the survey", ph)
        self.assertIn("FIXME", ph)
        self.assertIn("There's no line here to end", ph)

    def test_lint(self):
        L = " ".join(self.R["lint"])
        for needle in ("subfigure", "times", "$$", "eqnarray", "old font switch", "[H]", "space instead of ~"):
            self.assertIn(needle, L)

    def test_skeletons_have_no_false_positives(self):
        for kind in ("thesis", "article"):
            with self.subTest(kind=kind):
                R = audit_json(SKELETONS / kind)
                self.assertEqual(R["problems"], [])
                self.assertEqual(R["citations"]["missing_in_bib"], [])
                self.assertEqual(R["refs"]["undefined"], [])
                self.assertEqual(R["refs"]["duplicate_labels"], [])
                self.assertEqual(R["refs"]["label_before_caption"], [])
                self.assertEqual(R["refs"]["hard_coded"], [])
                self.assertEqual(R["floats"]["never_referenced"], [])
                self.assertEqual(R["graphics"]["missing"], [])
                self.assertEqual(R["abbreviations"]["unused"], [])
                self.assertEqual(R["lint"], [])


class NewProjectAndWorkflow(unittest.TestCase):
    def test_every_style_renders(self):
        np_mod = load("new-project")
        for style, (line, _) in np_mod.STYLES.items():
            with self.subTest(style=style):
                dest = Path(tempfile.mkdtemp()) / "p"
                r = run(sys.executable, SCRIPTS / "new-project.py", dest, "--type", "article", "--style", style)
                self.assertEqual(r.returncode, 0, r.stderr)
                text = (dest / "main.tex").read_text(encoding="utf-8")
                self.assertIn(line, text)
                self.assertNotIn("<<academic-latex:", text)
                self.assertIn("@default_files = ('main.tex')", (dest / ".latexmkrc").read_text(encoding="utf-8"))

    def test_options_and_escaping(self):
        dest = Path(tempfile.mkdtemp()) / "t"
        r = run(sys.executable, SCRIPTS / "new-project.py", dest, "--type", "thesis", "--engine", "lualatex",
                "--paper", "letter", "--spacing", "double", "--twoside", "--language", "ngerman,english",
                "--title", "R&D 100% #1", "--author", "Ana Müller")
        self.assertEqual(r.returncode, 0, r.stderr)
        t = (dest / "main.tex").read_text(encoding="utf-8")
        for needle in ("% !TEX program = lualatex", r"\usepackage{fontspec}", "letterpaper", "twoside, openright",
                       r"\doublespacing", r"\usepackage[ngerman,english]{babel}", r"R\&D 100\% \#1", "Ana Müller",
                       "left=1.5in"):
            self.assertIn(needle, t)
        self.assertIn("$pdf_mode = 4;", (dest / ".latexmkrc").read_text(encoding="utf-8"))

    def test_generated_files_get_normal_permissions(self):
        import os
        dest = Path(tempfile.mkdtemp()) / "m"
        run(sys.executable, SCRIPTS / "new-project.py", dest, "--type", "article")
        mask = os.umask(0)
        os.umask(mask)
        for f in ("main.tex", "references.bib", ".latexmkrc"):
            self.assertEqual((dest / f).stat().st_mode & 0o777, 0o666 & ~mask, f"{f}: mkstemp's 0600 must not leak")

    def test_refuses_non_empty_destination(self):
        dest = Path(tempfile.mkdtemp())
        (dest / "keep.txt").write_text("x")
        r = run(sys.executable, SCRIPTS / "new-project.py", dest)
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(sorted(p.name for p in dest.iterdir()), ["keep.txt"])

    def test_init_workflow(self):
        dest = Path(tempfile.mkdtemp()) / "w"
        run(sys.executable, SCRIPTS / "new-project.py", dest, "--type", "article")
        r = run(sys.executable, SCRIPTS / "init-workflow.py", dest, "--build-helpers")
        self.assertEqual(r.returncode, 0, r.stderr)
        wf = dest / ".academic-workflow"
        for f in ("STATUS.md", "TODO.md", "TEMPLATE.md", "benign-notices.txt", "session-log/_TEMPLATE.md",
                  "tools/audit-tex.py", "tools/bib-check.py", "tools/compile-check.sh", "tools/setup-sandbox-latex.sh"):
            self.assertTrue((wf / f).is_file(), f)
        status = (wf / "STATUS.md").read_text(encoding="utf-8")
        self.assertIn("`main.tex`", status)
        self.assertIn("article/paper", status)
        self.assertNotIn("{{", status)
        self.assertTrue((dest / "build.bat").is_file() and (dest / ".vscode" / "settings.json").is_file())
        before = (wf / "STATUS.md").read_text(encoding="utf-8")
        (wf / "STATUS.md").write_text(before + "\nedited by the author\n", encoding="utf-8")
        run(sys.executable, SCRIPTS / "init-workflow.py", dest)
        self.assertIn("edited by the author", (wf / "STATUS.md").read_text(encoding="utf-8"), "must not overwrite")


@unittest.skipUnless(HAVE_TEX, "latexmk/biber not installed")
class CompileCheck(unittest.TestCase):
    def test_broken_build_is_reported(self):
        work = Path(tempfile.mkdtemp())
        for f in (FIX / "broken-build").iterdir():
            shutil.copy(f, work / f.name)
        r = run("bash", SCRIPTS / "compile-check.sh", "--strict", cwd=work)
        self.assertEqual(r.returncode, 3, r.stdout[-2000:])
        out = r.stdout
        for needle in ("nokey2021", "sec:missing", "duplicate labels: sec:intro", "overfull boxes: 1",
                       "bibliography tool run: biber", "0 not embedded, 0 Type 3", "Section ??"):
            self.assertIn(needle, out)

    def test_abbreviation_list_does_not_count_as_a_table(self):
        dest = Path(tempfile.mkdtemp()) / "g"
        run(sys.executable, SCRIPTS / "new-project.py", dest, "--type", "thesis")
        main = dest / "main.tex"
        main.write_text(main.read_text(encoding="utf-8").replace(
            "\\begin{document}", "\\counterwithout{table}{chapter}\n\\begin{document}", 1), encoding="utf-8")
        run("latexmk", "-pdf", "-interaction=nonstopmode", "main.tex", cwd=dest)
        text = run("pdftotext", dest / "main.pdf", "-").stdout
        self.assertIn("Table 1:", text, "glossary longtable styles advance the table counter")

    def test_generated_thesis_is_clean(self):
        dest = Path(tempfile.mkdtemp()) / "c"
        run(sys.executable, SCRIPTS / "new-project.py", dest, "--type", "thesis", "--style", "apa")
        r = run("bash", SCRIPTS / "compile-check.sh", "--strict", cwd=dest)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:])
        self.assertIn("17 pages", r.stdout)
        self.assertIn("(none: no ??, [?] or (?))", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
