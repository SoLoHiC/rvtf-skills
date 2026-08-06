# RVTF Release Automation v1 Design

## Decision

Add release infrastructure without changing the packaged Skill semantics. The
implementation is merged to `main` as ordinary repository maintenance and does
not create or move a release tag. `v0.4.0` remains the latest immutable release;
the first release workflow run that publishes a new package will use a later
version such as `0.4.1`.

## Scope

The change has four bounded responsibilities:

1. Make Skill metadata validation repository-owned and reproducible on a clean
   GitHub runner.
2. Provide structured version, changelog, package, and checksum checks used by
   both local commands and Actions.
3. Add pull-request/push CI that validates the source and the packaged archive,
   including a consumer-side skill discovery smoke test.
4. Add a manually dispatched release workflow with `version`, `expected_sha`,
   and `dry_run` inputs. It creates an annotated tag and GitHub Release only on
   a non-dry run, and verifies the published assets before reporting closure.

This scope does not modify any file under `skills/`, update `VERSION`, change
`package.json.version`, add a changelog entry, publish to npm, add prerelease
channels, or create a new Git tag/Release.

## Release State Model

The workflow distinguishes these states:

```text
source candidate
  -> CI verified
  -> dry-run verified at commit SHA
  -> tagged and staged Release
  -> published and post-verified
```

`dry_run=true` must never write a tag, Release, or repository commit. A formal
run must reject a moving `main`: `expected_sha` is compared with the checked-out
commit before any external mutation.

The publish step is resumable for partial state:

- an existing tag is accepted only when it peels to the expected SHA;
- an existing draft Release may be completed after its assets are replaced and
  rechecked;
- an already published Release is accepted only when its tag, title, and asset
  digests match the candidate;
- mismatched or published-but-invalid state fails without deleting or rewriting
  immutable external objects.

## Components

### Repository-owned Skill validator

`scripts/validate-skills.py` validates each `skills/*/SKILL.md` frontmatter with
PyYAML and the existing skill metadata contract: required `name` and
`description`, allowed keys, hyphen-case name rules, name length, description
type/length, and forbidden angle brackets. It does not copy the external Codex
validator; it owns only the contract RVTF packages and tests.

`scripts/validate.sh` invokes this validator followed by the existing schema
fixture validator. A pinned `requirements-ci.txt` supplies PyYAML so the same
interpreter contract works locally and in Actions.

### Release helper

`scripts/release.py` provides structured operations used by tests and workflow
steps:

- `version --check VERSION` verifies strict `X.Y.Z` input, `VERSION`, and
  `package.json.version` consistency;
- `version --set VERSION` updates those two project-owned version sources for
  preparing a future release;
- `notes VERSION` extracts exactly one non-empty CHANGELOG section;
- `audit-package ARCHIVE VERSION` verifies archive identity, legal files,
  expected Skill count, and safe archive paths.

JSON and YAML are parsed with their native parsers. The helper never edits a
version during a release workflow; version changes remain reviewed source
changes in a pull request.

### CI workflow

`.github/workflows/ci.yml` runs on pull requests, pushes, and manual dispatch.
It uses pinned Action commit SHAs, installs the pinned Python dependency, runs
the repository validation, builds the npm-style archive, audits it, and runs
`npx skills add <unpacked-package> --list` with a pinned `skills` CLI version.
The workflow has read-only repository permissions.

### Release workflow

`.github/workflows/release.yml` is `workflow_dispatch` only, serialized by
version. A prepare job checks that it is running from `main`, validates the
version/changelog and expected SHA, reruns CI, creates the archive/checksum, and
uploads an internal workflow artifact. A publish job with `contents: write` and
the `release` environment performs the idempotent tag/Release state transition,
uploads the archive and checksum, publishes the Release, downloads the assets,
and verifies their digests.

Release notes come from `CHANGELOG.md`; no generated or remote text is used as a
substitute when the section is missing. The workflow does not publish npm
packages or send notifications in v1.

## Verification and Closure

Local tests cover the validator, version/changelog/package helper behavior,
workflow contract, and archive smoke path. The final local gate reruns the
existing five-Skill/schema/mutation validation and package audit. Because this
change does not publish a new version, completion evidence is limited to the
merged infrastructure commit and successful CI/dry-run receipts. A real
release is complete only after the separate tag, Release asset, and download
checksum checks pass.

## Non-goals and Future Expansion

Do not introduce release branches, changesets, RC channels, npm provenance, or
push-triggered public releases until RVTF has a concrete need for those
distribution semantics. Those additions would be a separate design and release
policy change.
