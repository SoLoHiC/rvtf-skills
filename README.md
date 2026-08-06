# RVTF Skills

Requirements-to-Verification Traceability Framework (RVTF) is a skill set for
controlling the gap between requirements, implementation, review findings, and
delivery claims.

It is designed for agentic software work where a plan may be detailed, tests may
pass, and implementation tasks may be checked off, but the actual delivery still
needs evidence that each requirement was satisfied without unbounded scope creep.

RVTF `0.4.0` is the first formal release. It retains the `0.3.0` Requirement
Trace, canonical Acceptance Item, and Journey Trace truth model, and adds an
Operational Economy Plane for organizing proof and execution without weakening
that truth. The `v0.4.0` tag and GitHub Release identify the published revision;
version metadata in an arbitrary checkout does not by itself prove publication.

English | [中文](./README-CN.md)

## What RVTF Helps With

RVTF turns delivery work into a traceable decision ledger:

- Requirements become stable IDs, not loose bullets.
- Each acceptance criterion becomes one canonical nested Acceptance Item with a
  stable ID, verification method, status, item evidence, and gap references.
- Journey applicability follows actor-goal-path triggers, not technical-domain
  labels. An isolated change with exact item evidence may record
  `not_required` instead of creating a synthetic Journey.
- When applicable, Journey Trace records the actor, goal, expected outcome,
  ordered observable Steps, canonical Acceptance Item references, and path
  evidence.
- Implementation tasks map to Requirement, Acceptance Item, Journey, and Journey
  Step IDs while their host workflow keeps control of task grouping and roles.
- `implemented` and `verified` stay separate.
- Weak evidence becomes an evidence gap, not a passing claim.
- Review findings are classified before they become work.
- Formal review can be bounded through applicability decisions, review
  contracts, coverage batches, frozen finding sets, remediation cycles, and
  controlled reopens.
- New required work enters through a scope amendment decision.
- Cross-cutting constraints such as security, privacy, data integrity, compatibility, migrations, and regression risk are tracked explicitly.
- Completion is stated through a closure packet with separate Requirement,
  Acceptance Item, and Journey dispositions. `complete` requires every required
  Requirement and every applicable Journey to be verified; all Items being
  verified does not replace path evidence.

The core rule:

```text
No review finding becomes implementation work until it is classified and linked
to a requirement decision.
```

## RVTF 0.4.0 Capabilities

- Delivery truth remains authoritative. Economy policy may reduce duplicate
  work, but the exact gate set is `host-native mandatory gates ∪ RVTF-required
  gates`; the stronger freshness, full-suite, review, or specialist requirement
  wins.
- `goal`, `milestone`, and `unit` express closure containment. Execution,
  verification, and review batches are orthogonal groups, not closure parents.
  A blocked or incomplete required child, or a host `done`, `archived`,
  `shipped`, or override status, cannot automatically close its RVTF parent.
- Reusable Evidence Artifacts may support multiple target-specific Evidence
  Claims. Every claim states what it proves and records an independent
  `evidence_claims[].validity.status`; cross-revision reuse requires an auditable
  assessment, and invalidation propagates only to affected claims and trace
  objects.
- Claim reuse does not assert that current tests pass. It cannot skip a host's
  mandatory fresh, current-tree, full-suite, or review gate.
- Verification uses `worker`, `batch`, `milestone`, and `completion` tiers. The
  Completion Gate is a complete semantic audit of required truth, evidence,
  reviews, gaps, gates, and continuation, not an unconditional command to run
  every repository test suite.
- Review dimensions define coverage, not reviewer or batch count. Parent review
  moves a child from `pending_at_parent` to `covered_at_parent` only after an
  exact-revision receipt exists. Strict independence, required specialists, and
  host-native fan-out remain mandatory; historical batches stay immutable, with
  assessed carry-forward, delta review, or controlled reopen used across
  revisions.
- The Goal Continuation Contract records
  `durable_host|artifact_only|advisory` mode and
  `continue|stop|await_owner|host_boundary` action. It is not a scheduler or
  persistent runtime: the host, user, or orchestrator retains authority.
- Artifact depth stays proportional: `lite` keeps compact trace/evidence notes
  and explicit rationale; `standard` adds scope, policy, validity, review, and
  continuation records; `strict` adds auditable comparison basis, independent
  review, and carry-forward assessment for the affected risk scope.

For concrete fields and gates, use the [core Skill](./skills/tracing-requirements-to-verification/SKILL.md),
[schema reference](./skills/tracing-requirements-to-verification/references/schema.md),
[gate reference](./skills/tracing-requirements-to-verification/references/gates.md),
and [review-governance reference](./skills/tracing-requirements-to-verification/references/review-governance.md).

## When To Use It

Use RVTF when work has multiple requirements, phases, acceptance criteria,
implementation tasks, verification evidence, review findings, scope changes,
delivery gaps, residual risks, or claims of completion.

Common triggers:

- A phase is "done" because tasks are complete, but requirement coverage is unclear.
- Tests pass, but some acceptance criteria were not checked line by line.
- Code review starts producing extra work that may be useful but was not required.
- Multiple review rounds keep introducing new findings after each remediation
  pass, and you need a stable review boundary.
- Review discovers a safety, privacy, compatibility, or data-integrity issue missing from the original spec.
- Multiple agents or phases need a shared evidence object instead of prose summaries.
- You need to decide whether a delivery is complete, incomplete, blocked, or complete with accepted residual risk.

## Usage Modes

RVTF can be light or strict depending on risk:

| Mode | Use when |
| --- | --- |
| `discovery` | Exploring or prototyping without a completion claim. |
| `lite` | Small bounded changes with low risk. |
| `standard` | Multi-step delivery, phase work, review, or handoff. Requires Journey and review applicability decisions. |
| `strict` | Security, privacy, migrations, compatibility, money, production risk, or cross-agent execution. Requires bounded review governance and independent review evidence for the affected risk scope. |

Do not lower the mode to justify an unsupported completion claim.

## Included Skills

| Skill | Purpose |
| --- | --- |
| `tracing-requirements-to-verification` | Core RVTF method: Requirement, Acceptance Item, and Journey truth; Operational Economy; evidence validity; verification/review governance; gaps, amendments, and closure. |
| `adapting-rvtf-to-superpowers` | Maps RVTF scopes, gates, review coverage, and continuation onto Superpowers planning, task review, verification, and branch finishing without replacing host requirements. |
| `adapting-rvtf-to-agent-skills` | Maps RVTF onto Agent Skills planning, build/review/ship boundaries, specialist fan-out, evidence, and continuation while preserving host authority. |
| `adapting-rvtf-to-gsd` | Maps RVTF containment and economy onto GSD goals, phases, PLANs, Waves, validation, shipping, and durable `.planning` authority. |
| `adapting-rvtf-to-bmad` | Maps RVTF onto BMAD specs, Stories, Build/build-auto, review/triage, memlogs, and orchestrator continuation without treating a Build run as closure. |

The adapter skills do not replace their host methods. They map native tasks,
stories, phases, or increments to RVTF IDs and feed back item evidence, path
evidence, and gaps while preserving each host lifecycle.

## What RVTF Is Not

RVTF does not prove that original requirements are correct. It also does not
replace product judgment, security review, domain expertise, automated testing,
or code review. Bounded review governance does not suppress legitimate late
required gaps; it makes late findings carry an explicit traceability and
delivery-decision record.

## Install

List available skills:

```bash
npx skills add SoLoHiC/rvtf-skills --list
```

Install all RVTF skills for Codex:

```bash
npx skills add SoLoHiC/rvtf-skills --skill '*' -a codex -y --copy
```

Install only the core RVTF skill:

```bash
npx skills add SoLoHiC/rvtf-skills --skill tracing-requirements-to-verification -a codex -y --copy
```

Add `-g` to install globally. Use the SSH source if your environment requires
SSH authentication:

```bash
npx skills add git@github.com:SoLoHiC/rvtf-skills.git --skill '*' -g -a codex -y --copy
```

## Repository Layout

```text
skills/
  tracing-requirements-to-verification/
  adapting-rvtf-to-superpowers/
  adapting-rvtf-to-agent-skills/
  adapting-rvtf-to-gsd/
  adapting-rvtf-to-bmad/
scripts/
  validate.sh
  validate-schema-examples.py
  fixtures/schema/
    positive/
    negative/
  install.sh
  package.sh
package.json
```

## Release Automation

Release preparation is a reviewed source change; publishing is a separate
workflow decision. For a future release, update the project version and
`CHANGELOG.md` in a pull request:

```bash
python3 scripts/release.py --root . version --set 0.4.1
# edit CHANGELOG.md and commit the release preparation
```

After the pull request is merged, capture the exact `main` commit and run the
dry-run candidate gate:

```bash
release_sha="$(git ls-remote origin refs/heads/main | cut -f1)"
gh workflow run release.yml --ref main \
  -f version=0.4.1 -f expected_sha="${release_sha}" -f dry_run=true
```

Inspect the run summary and use the same `release_sha` for the formal run:

```bash
gh workflow run release.yml --ref main \
  -f version=0.4.1 -f expected_sha="${release_sha}" -f dry_run=false
gh run list --workflow release.yml --limit 1
gh run watch RUN_ID --exit-status
```

The formal workflow creates or resumes the annotated tag and GitHub Release,
uploads the package and `SHA256SUMS`, then downloads the published assets and
verifies the checksum. A tag or Release that points to a different commit is a
hard failure and is never deleted automatically. This release-automation change
does not change `0.4.0` or create a new tag.

## Development

Validate all five Skills plus the deterministic positive/negative schema and
invariant fixtures:

```bash
scripts/validate.sh
```

Run only the schema/invariant fixture validator when working on the additive
artifact contracts:

```bash
python3 scripts/validate-schema-examples.py
```

If the default Python does not have `PyYAML`, pass a Python from a prepared
environment:

```bash
PYTHON_BIN=/tmp/rvtf-skill-validate-venv/bin/python scripts/validate.sh
```

Install from a local checkout:

```bash
npx skills add ./rvtf-skills --skill '*' -a codex -y --copy
```

Create an npm-style package archive under `dist/`:

```bash
scripts/package.sh
```

## License

RVTF Skills is available under the [MIT License](./LICENSE). Compatibility
references, pinned upstream revisions, third-party license notices, and the
BMAD trademark boundary are documented in
[THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md).
