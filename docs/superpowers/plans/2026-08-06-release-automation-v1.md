# RVTF Release Automation v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add reproducible CI and a resumable manual GitHub Release workflow without changing the packaged Skills or creating a new release tag.

**Architecture:** Keep the existing schema validator as the semantic gate and add a repository-owned Skill frontmatter validator plus a small Python release helper for version, changelog, and archive checks. CI calls these local commands and performs a package discovery smoke test. A separate manual workflow validates an exact `main` SHA, then creates or resumes the tag/Release state only when `dry_run` is false.

**Tech Stack:** Bash, Python 3.12, PyYAML, Node.js 24, npm pack, GitHub Actions pinned to commit SHAs, GitHub CLI.

---

### Task 1: Add failing validator and release-helper tests

**Files:**
- Create: `scripts/tests/test_validate_skills.py`
- Create: `scripts/tests/test_release.py`

- [x] **Step 1: Add validator behavior tests**

Cover one valid frontmatter fixture and these failures: missing `SKILL.md`, no frontmatter, unexpected key, missing `name`, invalid name, overlong name, missing description, non-string description, angle brackets, and overlong description. Import the production modules by path only after the test is present.

- [x] **Step 2: Run the validator tests before implementation**

Run:

```bash
PYTHONPATH=scripts python3 -m unittest scripts.tests.test_validate_skills -v
```

Expected: collection/import failures because `scripts/validate_skills.py` does not exist yet.

- [x] **Step 3: Add release helper behavior tests**

Use temporary directories and real JSON/YAML/tar data. Cover strict version acceptance, mismatch between `VERSION` and `package.json`, changelog section extraction, missing/empty changelog section, package identity/license/legal-file audit, and rejection of archive paths containing `..` or absolute names.

- [x] **Step 4: Run the release helper tests before implementation**

Run:

```bash
PYTHONPATH=scripts python3 -m unittest scripts.tests.test_release -v
```

Expected: collection/import failures because `scripts/release.py` does not exist yet.

### Task 2: Implement repository-owned validators

**Files:**
- Create: `scripts/validate_skills.py`
- Create: `scripts/release.py`
- Create: `requirements-ci.txt`
- Modify: `scripts/validate.sh`

- [x] **Step 1: Implement the minimal metadata validator**

Implement `validate_skill(path) -> tuple[bool, str]` with PyYAML and the existing metadata contract. Implement `main()` to validate every direct directory under `skills/`, print one result per skill, and exit nonzero on any failure. Do not import or call the external Codex validator.

- [x] **Step 2: Run validator tests and existing schema tests**

Run:

```bash
PYTHONPATH=scripts python3 -m unittest scripts.tests.test_validate_skills -v
PYTHON_BIN=/usr/bin/python3 scripts/validate-schema-examples.py
```

Expected: validator tests pass; schema fixtures remain `3 accepted, 4 expected rejected, 0 failures` and mutations remain `39 passed, 0 failures`.

- [x] **Step 3: Implement structured release operations**

Implement subcommands `version --check VERSION`, `version --set VERSION`, `notes VERSION`, and `audit-package ARCHIVE VERSION`. Use `json.load`, `yaml.safe_load`, and `tarfile`; enforce `X.Y.Z`, exact package/version consistency, exactly one non-empty changelog section, the five current Skill directories, legal files, and safe archive paths. `version --set` must update only `VERSION` and the JSON version field while preserving valid JSON.

- [x] **Step 4: Pin the CI Python dependency**

Add the reviewed PyYAML version used by the project validation environment to `requirements-ci.txt`. Do not add a runtime dependency to the package.

- [x] **Step 5: Run release helper tests and existing validation**

Run:

```bash
PYTHONPATH=scripts python3 -m unittest scripts.tests.test_release -v
PYTHONPATH=scripts python3 -m unittest discover -s scripts/tests -v
PYTHON_BIN=/usr/bin/python3 scripts/validate.sh
```

Expected: all new tests pass and the existing five-Skill/schema/mutation gate remains green.

### Task 3: Add package and consumer smoke commands

**Files:**
- Modify: `package.json`
- Modify: `scripts/package.sh`
- Create: `scripts/ci.sh`

- [x] **Step 1: Add npm scripts for test and CI**

Add `test` for the Python unittest discovery command, `validate:skills` for the repository validator, and `ci` for `scripts/ci.sh`. Keep the package version at `0.4.0`.

- [x] **Step 2: Extend packaging with structured archive audit**

After `npm pack`, call `release.py audit-package` against the generated archive. Keep `dist/` ignored and do not commit generated artifacts.

- [x] **Step 3: Implement `scripts/ci.sh`**

Run the repository validation, test suite, package build, checksum generation, and archive audit. Extract the archive into a temporary directory and run a pinned `skills` CLI with `add <unpacked-package> --list`; fail if the command fails or does not report all five package Skill names. Use `mktemp -d` and a trap for cleanup.

- [x] **Step 4: Verify the local CI path**

Run:

```bash
./scripts/ci.sh
node -e 'const p=require("./package.json"); if (p.version !== "0.4.0") process.exit(1)'
git diff -- skills VERSION package.json
```

Expected: CI exits 0, the version remains `0.4.0`, and no Skill or version diff exists.

### Task 4: Add workflow contract tests and CI workflow

**Files:**
- Create: `scripts/tests/test_workflows.py`
- Create: `.github/workflows/ci.yml`

- [x] **Step 1: Add failing workflow contract tests**

Parse both workflow YAML files with a loader that preserves the string key `on`. Assert CI has pull request, push, and manual triggers; read-only contents permission; pinned checkout/setup actions; and a command invoking `scripts/ci.sh`.

- [x] **Step 2: Run the workflow tests before adding CI**

Run:

```bash
PYTHONPATH=scripts python3 -m unittest scripts.tests.test_workflows -v
```

Expected: fail because `.github/workflows/ci.yml` does not exist.

- [x] **Step 3: Add CI workflow**

Use `ubuntu-latest`, Python 3.12, Node 24, pinned action commit SHAs, `pip install -r requirements-ci.txt`, and `./scripts/ci.sh`. Set `permissions: contents: read`. Do not trigger a Release or tag from CI.

- [x] **Step 4: Run workflow tests and local CI**

Run:

```bash
PYTHONPATH=scripts python3 -m unittest discover -s scripts/tests -v
./scripts/ci.sh
```

Expected: workflow contract tests pass and the local CI path exits 0.

### Task 5: Add manual resumable release workflow

**Files:**
- Modify: `scripts/tests/test_workflows.py`
- Create: `.github/workflows/release.yml`
- Modify: `README.md`
- Modify: `README-CN.md`

- [x] **Step 1: Extend failing workflow contract tests**

Assert release workflow is `workflow_dispatch` only with required `version`, `expected_sha`, and `dry_run` inputs; uses a per-version concurrency group; has a read-only prepare job and a write-enabled publish job; contains a SHA equality guard; gates all external mutation on `!inputs.dry_run`; and has post-publish download/checksum verification.

- [x] **Step 2: Implement the prepare job**

Checkout `main` at full depth, install pinned dependencies, reject non-`main` refs and SHA mismatch, run `release.py version --check`, `release.py notes`, and `scripts/ci.sh`, create `SHA256SUMS`, and upload the archive, checksum, and notes as an internal artifact. The job must not have `contents: write`.

- [x] **Step 3: Implement the publish job**

Require the prepare job and `!inputs.dry_run`. Give it `contents: write`, use the `release` environment, download the prepared artifact, verify the expected SHA, and implement these shell-visible states: create the annotated tag if absent; verify an existing tag peels to the expected SHA; create a draft Release if absent; replace draft assets with `--clobber`; refuse to mutate a published Release unless its title and asset digests already match; publish the draft; download both assets; and run `shasum -a 256 -c SHA256SUMS`.

- [x] **Step 4: Document operator commands and state semantics**

Add a concise “Release automation” section to both READMEs covering version PR preparation, dry-run, formal dispatch, `gh run watch`, completion evidence, and partial-state recovery. State explicitly that this infrastructure change does not bump `v0.4.0` or create a new tag.

- [x] **Step 5: Run workflow contract tests and diff checks**

Run:

```bash
PYTHONPATH=scripts python3 -m unittest scripts.tests.test_workflows -v
git diff --check
git diff -- skills VERSION package.json
```

Expected: all workflow assertions pass, no whitespace errors exist, and the final command prints no output.

### Task 6: Final verification and delivery boundary

**Files:**
- Verify all changed files; do not add generated `dist/` contents.

- [x] **Step 1: Run the complete local gate**

Run:

```bash
./scripts/ci.sh
PYTHONPATH=scripts python3 -m unittest discover -s scripts/tests -v
git diff --check
```

Expected: all tests and archive checks pass.

- [x] **Step 2: Verify no Skill or release mutation**

Run:

```bash
git diff --name-only origin/main...HEAD
git diff origin/main...HEAD -- skills VERSION package.json CHANGELOG.md
git tag --points-at HEAD
```

Expected: no changed Skill, version, package-version, or changelog files; no new tag points at the infrastructure commit.

- [ ] **Step 3: Commit implementation**

Commit the design, plan, scripts, tests, workflows, and README operator documentation with:

```bash
git add .github README.md README-CN.md requirements-ci.txt scripts docs/superpowers/specs docs/superpowers/plans
git commit -m "ci: add reproducible release automation"
```

- [ ] **Step 4: Report the exact closure boundary**

Report the implementation commit and fresh local evidence. State separately that no new version tag or GitHub Release was created; a future package release must run the new workflow with a later version and a new `expected_sha`.
