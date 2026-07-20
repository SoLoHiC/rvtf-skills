# RVTF Skills

Requirements-to-Verification Traceability Framework (RVTF) is a skill set for
controlling the gap between requirements, implementation, review findings, and
delivery claims.

It is designed for agentic software work where a plan may be detailed, tests may
pass, and implementation tasks may be checked off, but the actual delivery still
needs evidence that each requirement was satisfied without unbounded scope creep.

## What RVTF Helps With

RVTF turns delivery work into a traceable decision ledger:

- Requirements become stable IDs, not loose bullets.
- Acceptance criteria are linked to verification methods.
- Implementation tasks are mapped back to requirement IDs.
- `implemented` and `verified` stay separate.
- Weak evidence becomes an evidence gap, not a passing claim.
- Review findings are classified before they become work.
- New required work enters through a scope amendment decision.
- Cross-cutting constraints such as security, privacy, data integrity, compatibility, migrations, and regression risk are tracked explicitly.
- Completion is stated through a closure packet with verified rows, deferred gaps, blocked work, rejected extras, accepted amendments, and residual risk.

The core rule:

```text
No review finding becomes implementation work until it is classified and linked
to a requirement decision.
```

## When To Use It

Use RVTF when work has multiple requirements, phases, acceptance criteria,
implementation tasks, verification evidence, review findings, scope changes,
delivery gaps, residual risks, or claims of completion.

Common triggers:

- A phase is "done" because tasks are complete, but requirement coverage is unclear.
- Tests pass, but some acceptance criteria were not checked line by line.
- Code review starts producing extra work that may be useful but was not required.
- Review discovers a safety, privacy, compatibility, or data-integrity issue missing from the original spec.
- Multiple agents or phases need a shared evidence object instead of prose summaries.
- You need to decide whether a delivery is complete, incomplete, blocked, or complete with accepted residual risk.

## Usage Modes

RVTF can be light or strict depending on risk:

| Mode | Use when |
| --- | --- |
| `discovery` | Exploring or prototyping without a completion claim. |
| `lite` | Small bounded changes with low risk. |
| `standard` | Multi-step delivery, phase work, review, or handoff. |
| `strict` | Security, privacy, migrations, compatibility, money, production risk, or cross-agent execution. |

Do not lower the mode to justify an unsupported completion claim.

## Included Skills

| Skill | Purpose |
| --- | --- |
| `tracing-requirements-to-verification` | Core RVTF method: requirement IDs, acceptance criteria, verification, evidence quality, review intake, gap ledger, scope amendments, and closure packets. |
| `adapting-rvtf-to-superpowers` | Adds RVTF traceability to Superpowers workflows such as brainstorming, writing plans, code review, verification, branch finishing, and skill writing. |
| `adapting-rvtf-to-agent-skills` | Adds RVTF to agent-skill planning, incremental implementation, doubt handling, code review, and definition-of-done practices. |
| `adapting-rvtf-to-gsd` | Connects RVTF to GSD goal convergence, phase validation, ship decisions, and gap-control workflows. |
| `adapting-rvtf-to-bmad` | Connects RVTF to BMAD specs, memlogs, adversarial review, edge-case review, verification-gap review, and preservation checks. |

The adapter skills do not replace their host methods. They add a requirement and
evidence thread through those existing workflows.

## What RVTF Is Not

RVTF does not prove that original requirements are correct. It also does not
replace product judgment, security review, domain expertise, automated testing,
or code review. It makes those decisions explicit enough to audit and revisit.

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
  install.sh
  package.sh
package.json
```

## Development

Validate skill metadata:

```bash
scripts/validate.sh
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
