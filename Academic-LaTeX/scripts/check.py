#!/usr/bin/env python3
"""check.py — sanity checks for the repository (run by scripts/package.sh and by CI).

* SKILL.md frontmatter: only the keys claude.ai accepts (name, description, license,
  compatibility, metadata, allowed-tools); name kebab-case, <= 64 chars, equal to the folder;
  description 50..1024 chars; no tabs.
* SKILL.md body <= 500 lines; reference files longer than 300 lines have a "## Contents" section.
* Every `references/...`, `scripts/...`, `assets/...` or `templates/...` path mentioned in
  SKILL.md and the references exists.
* Manifests parse; plugin and marketplace names and versions agree with SKILL.md metadata.version.
* Scripts compile (python) / parse (bash -n); eval cases have prompt.md, case.yaml and graders/.
* No leftovers of personal data that must not ship in a public skill (a small denylist).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "academic-latex"
ALLOWED_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
errors: list[str] = []


def err(msg: str):
    errors.append(msg)


# --- frontmatter -----------------------------------------------------------------------------
text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
m = re.match(r"---\n(.*?)\n---\n", text, re.S)
version = None
if not m:
    err("SKILL.md: missing YAML frontmatter")
else:
    fm = m.group(1)
    if "\t" in fm:
        err("SKILL.md: tab character inside the frontmatter")
    keys = set(re.findall(r"^([A-Za-z][\w-]*):", fm, re.M))
    if keys - ALLOWED_KEYS:
        err(f"SKILL.md: frontmatter keys not accepted by claude.ai uploads: {sorted(keys - ALLOWED_KEYS)}")
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
        print(f"check.py: description {len(desc)} chars")
    vm = re.search(r'^\s+version:\s*"?([\d.]+)"?\s*$', fm, re.M)
    version = vm.group(1) if vm else None
body = text[m.end():] if m else text
if len(body.splitlines()) > 500:
    err(f"SKILL.md body has {len(body.splitlines())} lines (> 500): move detail into references/")

# --- referenced paths and long references -------------------------------------------------------
md_files = [SKILL / "SKILL.md"] + sorted((SKILL / "references").rglob("*.md"))
for md in md_files:
    t = md.read_text(encoding="utf-8")
    if md.parent.name != "academic-latex" and len(t.splitlines()) > 300 and "## Contents" not in t:
        err(f"{md.relative_to(ROOT)}: longer than 300 lines without a '## Contents' section")
    for ref in re.findall(r"`((?:references|scripts|assets|templates)/[^`\s]+)`", t):
        ref = ref.rstrip(".,;:)")
        if any(ch in ref for ch in "<>*{"):
            continue
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
        if p.get("version") and p["version"] != plugin.get("version"):
            err("plugin.json and marketplace.json versions differ")
    if version and plugin.get("version") != version:
        err(f"SKILL.md metadata.version {version} differs from plugin.json {plugin.get('version')}")
    for k in ("name", "owner", "plugins"):
        if k not in market:
            err(f"marketplace.json: missing '{k}'")
except Exception as exc:  # noqa: BLE001
    err(f"manifest error: {exc}")

# --- scripts -----------------------------------------------------------------------------------
pys = list((SKILL / "scripts").glob("*.py")) + list((ROOT / "scripts").glob("*.py")) + list((ROOT / "tests").glob("*.py"))
for py in pys:
    r = subprocess.run([sys.executable, "-m", "py_compile", str(py)], capture_output=True, text=True)
    if r.returncode:
        err(f"{py.relative_to(ROOT)}: does not compile: {r.stderr.strip()[:200]}")
for sh in list((SKILL / "scripts").glob("*.sh")) + list((ROOT / "scripts").glob("*.sh")) + list((ROOT / "tests").glob("*.sh")):
    r = subprocess.run(["bash", "-n", str(sh)], capture_output=True, text=True)
    if r.returncode:
        err(f"{sh.relative_to(ROOT)}: bash -n failed: {r.stderr.strip()[:200]}")

# --- eval cases ---------------------------------------------------------------------------------
evals = SKILL / "evals"
if evals.is_dir():
    for case in sorted(p for p in evals.iterdir() if p.is_dir()):
        for need in ("prompt.md", "case.yaml"):
            if not (case / need).is_file():
                err(f"evals/{case.name}: missing {need}")
        graders = case / "graders"
        if not graders.is_dir() or not list(graders.glob("*.md")):
            err(f"evals/{case.name}: no graders/*.md")
        y = (case / "case.yaml").read_text(encoding="utf-8") if (case / "case.yaml").is_file() else ""
        if f"name: {case.name}" not in y or 'schema_version: "1.1"' not in y:
            err(f"evals/{case.name}: case.yaml must have schema_version \"1.1\" and name: {case.name}")

# --- personal-data denylist (a public skill must be generic) ------------------------------------
DENY = [r"OneDrive", r"TCC_01_11_2025", r"C:\\\\Users", r"Drone_Detection", r"mateu\b", r"@gmail\.com"]
for f in SKILL.rglob("*"):
    if f.is_file() and f.suffix in {".md", ".py", ".sh", ".bat", ".json", ".txt", ".tex", ".bib", ".yaml"}:
        t = f.read_text(encoding="utf-8", errors="replace")
        for pat in DENY:
            if re.search(pat, t):
                err(f"{f.relative_to(ROOT)}: contains denylisted personal reference /{pat}/")

if errors:
    print("CHECK FAILED:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print(f"check.py: OK ({len(md_files)} markdown files, manifests, scripts, evals, denylist)")
