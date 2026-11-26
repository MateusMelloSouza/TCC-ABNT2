# Contributing

This repository is a Claude skill: Markdown instructions read by the model, plus
scripts. Useful contributions, in order of value:

1. **Template profiles** for journals, conferences and universities
   (`skills/academic-latex/references/templates/`). Follow
   `references/templates/README.md`, and verify everything by grep in the class
   and by a clean compile. Add the minimal document to `tests/publisher/` or
   `tests/thesis-classes/` so CI keeps it honest.
2. **Style-guide corrections** with a source: the manual's edition and section,
   the package's documentation and version, or a compiled example.
3. **Reproducible compile pitfalls**: the exact message, its cause and a fix that does
   not edit the template's class file. Add a row to the error table.
4. **Script improvements** (`skills/academic-latex/scripts/`): Python 3.8+ standard
   library only and POSIX-ish bash. Never rewrite a user's project file, and write
   atomically (temporary file + `os.replace`). Add a fixture and a test in
   `tests/test_scripts.py` for every new check, including a test that the
   skeletons raise no false positive.

## Before opening a pull request

```bash
python3 scripts/check.py          # frontmatter, links, manifests, scripts, evals, denylist
bash tests/run-tests.sh           # unit tests + LaTeX matrix + template documents (needs TeX Live)
bash scripts/package.sh           # rebuild dist/academic-latex.zip (commit it with the change)
```
In a fresh container, `bash skills/academic-latex/scripts/setup-sandbox-latex.sh --fonts`
installs a TeX Live that runs every test.

## Editorial rules

- `SKILL.md` stays well under 500 lines; detail goes to `references/`. References
  longer than 300 lines need a "## Contents" section.
- Frontmatter: only `name`, `description`, `license`, `compatibility`, `metadata` and
  `allowed-tools` (claude.ai rejects other keys). Keep the description under 1024
  characters; the current one is about 840.
- Explain the *why* of a rule instead of piling up "NEVER/ALWAYS".
- Claim only what was verified. Mark compiled facts "(verified)" where it helps, and
  phrase what cannot be checked locally (venue policies, arXiv rules) as "check the
  current instructions".
- No personal data, real thesis titles or machine paths. `check.py` refuses some
  patterns; human review is the real filter.
- Do not redistribute institutional or publisher templates; point to the official
  source.

## Versioning

Semver in `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` and
`metadata.version` in `SKILL.md` (`check.py` checks that they agree). Record every
change in `CHANGELOG.md`. A `vX.Y.Z` tag builds the release with the ZIP attached,
once this folder is its own repository.
