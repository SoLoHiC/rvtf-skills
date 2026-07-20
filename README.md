# RVTF Skills

Requirements-to-Verification Traceability Framework skills and adapters.

This repository is a Vercel `skills` CLI-compatible skill source. Installed
agent skill directories should be treated as deployment copies that can be
recreated from this repository.

## Layout

```text
skills/
  tracing-requirements-to-verification/
  adapting-rvtf-to-superpowers/
  adapting-rvtf-to-agent-skills/
  adapting-rvtf-to-gsd/
  adapting-rvtf-to-bmad/
scripts/
  validate.sh
  install.sh
  package.sh
package.json
```

## Vercel Skills CLI

List available skills:

```bash
npx skills add SoLoHiC/rvtf-skills --list
```

Install into the current project:

```bash
npx skills add SoLoHiC/rvtf-skills --skill '*' -a codex -y --copy
```

Install globally for Codex:

```bash
npx skills add SoLoHiC/rvtf-skills --skill '*' -g -a codex -y --copy
```

Use the SSH source when private-repo access or SSH auth is required:

```bash
npx skills add git@github.com:SoLoHiC/rvtf-skills.git --skill '*' -g -a codex -y --copy
```

Use `--copy` when installed skill directories must be independent copies. Omit
`--copy` to use the `skills` CLI symlink/canonical install mode.

## Local Development

From inside this repository, `scripts/install.sh` delegates to the same CLI:

```bash
scripts/install.sh --skill '*' -a codex -y --copy
```

From a sibling checkout:

```bash
npx skills add ./rvtf-skills --list
npx skills add ./rvtf-skills --skill '*' -a codex -y --copy
```

## Validate

```bash
scripts/validate.sh
```

If the default Python does not have `PyYAML`, pass a Python from a prepared
environment:

```bash
PYTHON_BIN=/tmp/rvtf-skill-validate-venv/bin/python scripts/validate.sh
```

## Package

Create an npm-style package archive under `dist/`:

```bash
scripts/package.sh
```
