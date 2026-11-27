#!/usr/bin/env python3
"""check.py — sanity checks for the repository (run by scripts/package.sh and by CI).

* SKILL.md frontmatter: name (<= 64 chars, kebab-case, equals the folder name) and description
  (<= 1024 chars) present; no tab characters in the frontmatter.
* Every relative link/path mentioned in SKILL.md and references/*.md as `references/...`,
  `scripts/...`, `assets/...` or `templates/...` exists.
* Manifests parse as JSON and the plugin/marketplace names agree.
* Scripts compile (python) / parse (bash -n).
* No leftovers of personal data that must not ship in a public skill (a small denylist).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "tcc-abnt"
errors: list[str] = []


def err(msg: str):
    errors.append(msg)


# --- frontmatter -----------------------------------------------------------------------------
text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
m = re.match(r"---\n(.*?)\n---\n", text, re.S)
if not m:
    err("SKILL.md: missing YAML frontmatter")
else:
    fm = m.group(1)
    if "\t" in fm:
        err("SKILL.md: tab character inside the frontmatter")
    nm = re.search(r"^name:\s*(\S+)\s*$", fm, re.M)
    if not nm:
        err("SKILL.md: frontmatter has no name")
    else:
        name = nm.group(1)
        if name != SKILL.name:
            err(f"SKILL.md: name '{name}' differs from folder '{SKILL.name}'")
        if len(name) > 64 or not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
            err(f"SKILL.md: name '{name}' must be kebab-case and <= 64 chars")
    dm = re.search(r"^description:\s*>-?\n((?:[ \t]+.*\n?)+)|^description:\s*(.+)$", fm, re.M)
    if not dm:
        err("SKILL.md: frontmatter has no description")
    else:
        desc = " ".join(l.strip() for l in (dm.group(1) or dm.group(2)).splitlines())
        if len(desc) > 1024:
            err(f"SKILL.md: description is {len(desc)} chars (> 1024)")
        if len(desc) < 50:
            err("SKILL.md: description too short to trigger reliably")
body = text[m.end():] if m else text
if len(body.splitlines()) > 500:
    err(f"SKILL.md body has {len(body.splitlines())} lines (> 500): move detail into references/")

# --- referenced paths --------------------------------------------------------------------------
md_files = [SKILL / "SKILL.md"] + sorted((SKILL / "references").rglob("*.md"))
for md in md_files:
    t = md.read_text(encoding="utf-8")
    for ref in re.findall(r"`((?:references|scripts|assets|templates)/[^`\s]+)`", t):
        ref = ref.rstrip(".,;:)")
        candidates = [SKILL / ref, md.parent / ref, SKILL / "references" / ref]
        if not any(c.exists() for c in candidates):
            err(f"{md.relative_to(ROOT)}: referenced path not found: {ref}")

# --- manifests ---------------------------------------------------------------------------------
try:
    plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    names = {p["name"] for p in market["plugins"]}
    if plugin["name"] not in names:
        err("marketplace.json does not list the plugin named in plugin.json")
    for p in market["plugins"]:
        if not p["source"].startswith("./"):
            err(f"marketplace.json: plugin '{p['name']}' source must be a relative path starting with ./")
    for p in market["plugins"]:
        if p.get("version") and plugin.get("version") and p["version"] != plugin["version"]:
            err("plugin.json and marketplace.json versions differ")
except Exception as exc:  # noqa: BLE001
    err(f"manifest error: {exc}")

# --- scripts -----------------------------------------------------------------------------------
for py in list((SKILL / "scripts").glob("*.py")) + list((ROOT / "scripts").glob("*.py")):
    r = subprocess.run([sys.executable, "-m", "py_compile", str(py)], capture_output=True, text=True)
    if r.returncode:
        err(f"{py.relative_to(ROOT)}: does not compile: {r.stderr.strip()[:200]}")
for sh in list((SKILL / "scripts").glob("*.sh")) + list((ROOT / "scripts").glob("*.sh")):
    r = subprocess.run(["bash", "-n", str(sh)], capture_output=True, text=True)
    if r.returncode:
        err(f"{sh.relative_to(ROOT)}: bash -n failed: {r.stderr.strip()[:200]}")

# --- personal-data denylist (the repo must be generic) ------------------------------------------
# Case-insensitive, per line. The public author name and GitHub handle are deliberately allowed.
DENY = [
    r"OneDrive",
    r"TCC_01_11_2025",
    r"C:[\\/]+Users",            # Windows profile path, backslash or forward slash
    r"Drone_Detection",
    r"Users[\\/]+mateu\b",       # the owner's user folder, e.g. Users\mateu or Users/mateu
    r"\bmateusmellosouza@",      # the owner's personal email local part
]
SKIP_DIRS = {".git", "dist", "build", "__pycache__"}
SKIP_FILES = {Path(__file__).resolve(), ROOT / "FORK-PLAN.md"}  # check.py holds the patterns
TEXT_SUFFIXES = {".md", ".py", ".sh", ".bat", ".json", ".txt", ".yml", ".yaml", ".tex", ".bib", ".sty", ".cls"}
for f in ROOT.rglob("*"):
    rel = f.relative_to(ROOT)
    if not f.is_file() or SKIP_DIRS & set(rel.parts) or f.resolve() in SKIP_FILES:
        continue
    if f.suffix and f.suffix not in TEXT_SUFFIXES:  # extensionless files (latexmkrc, ...) are scanned
        continue
    try:
        lines = f.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:  # binary file
        continue
    for pat in DENY:
        rx = re.compile(pat, re.I)
        for n, line in enumerate(lines, 1):
            if rx.search(line):
                err(f"{rel.as_posix()}:{n}: contains denylisted personal reference /{pat}/")

if errors:
    print("CHECK FAILED:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print(f"check.py: OK ({len(md_files)} markdown files, manifests, scripts, denylist)")
