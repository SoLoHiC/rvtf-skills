# RVTF Journey Trace v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the minimum semantically closed Acceptance Item and Journey Trace model to RVTF without adding Execution Units, owner registries, automatic extraction, or completion percentages.

**Architecture:** Keep `requirements[].acceptance[]` as the canonical Acceptance Item store and let Journey Steps reference globally stable Acceptance Item IDs. Add a separate path-evidence axis, explicit Journey applicability, constrained status aggregation, and a dual-axis Completion Gate while preserving bounded review governance as an independent sub-gate. Host-method adapters map their native tasks, stories, phases, or increments directly to requirement, acceptance-item, journey, and journey-step IDs.

**Tech Stack:** Markdown skill packages, YAML examples, Bash validation scripts, Python `quick_validate.py`, npm packaging, fresh-agent pressure tests.

---

## RVTF Delivery Contract

**Mode:** `standard`

**Review applicability:** `required`; the change updates a public skill schema and completion semantics, and formal requirements and closure review can block delivery.

| Requirement ID | Required behavior | Verification |
| --- | --- | --- |
| `JTV1-ITEM-001` | Existing nested acceptance rows become canonical Acceptance Items with stable IDs, status, evidence, source provenance, and gap references. | Schema inspection, validation, pressure scenarios 20 and 26. |
| `JTV1-APPLY-001` | Journey applicability uses actor-path triggers rather than technical-domain labels and supports justified `not_required`. | Gates inspection, pressure scenarios 23 and 24. |
| `JTV1-JOURNEY-001` | Actor Journey and Journey Step model actor, goal, expected outcome, ordered steps, item references, and path evidence. | Schema inspection and pressure scenarios 20, 21, and 26. |
| `JTV1-EVID-001` | Item evidence and path evidence are target-specific and cannot substitute for each other implicitly. | Evidence gate inspection and pressure scenarios 20-22. |
| `JTV1-STATUS-001` | Acceptance Item, Requirement, and Journey statuses obey explicit aggregation constraints without adding `partial`. | Status rules inspection and pressure scenarios 21-22. |
| `JTV1-GAP-001` | Gaps may target Requirement, Acceptance Item, Journey, and Journey Step, with correct propagation and no false Requirement downgrade for Journey-only gaps. | Schema/gate inspection and pressure scenario 25. |
| `JTV1-ADAPT-001` | All four adapters map host units to the four trace ID types and preserve host lifecycles. | Adapter line-by-line review and adapter pressure prompts. |
| `JTV1-REG-001` | Existing requirement trace, status taxonomy, gap ledger, and bounded review governance remain valid. | Existing scenarios 1-19 and package validation. |
| `JTV1-DOCS-001` | README files describe only shipped v1 behavior and package metadata is consistently `0.3.0`. | README comparison, version checks, package contents. |

**Expected review batches:**

1. `requirements-review`: cover `requirement-fidelity` and `impact-and-ownership` on one stable commit.
2. `closure-risk-review`: cover `verification-and-closure` and `state-and-compatibility` on the same commit.

Freeze only after both batches report covered dimensions, limitations, findings, and the same subject revision. Review closure remains a sub-gate; the full requirement, Acceptance Item, Journey, evidence, gap, and package checks still control delivery completion.

## File Responsibility Map

| File | Responsibility |
| --- | --- |
| `docs/design/2026-08-01-journey-trace-and-acceptance-item.md` | Approved v1 design and non-goals. |
| `skills/tracing-requirements-to-verification/SKILL.md` | Core workflow, artifact chain, statuses, evidence rules, gap propagation, completion semantics, and common failures. |
| `skills/tracing-requirements-to-verification/references/schema.md` | Canonical nested Acceptance Item, Journey applicability, Journey, gap targets, and closure examples. |
| `skills/tracing-requirements-to-verification/references/gates.md` | Applicability, design, plan, implementation, evidence, review, and completion checks. |
| `skills/tracing-requirements-to-verification/references/pressure-scenarios.md` | Pre-change baseline, new scenarios 20-26, expected behavior, forward-test receipts, and old-scenario regression expectations. |
| `skills/adapting-rvtf-to-superpowers/SKILL.md` | Superpowers task-to-trace mapping and path-evidence checks. |
| `skills/adapting-rvtf-to-agent-skills/SKILL.md` | Increment and vertical-slice mapping without forcing every increment to have a Journey. |
| `skills/adapting-rvtf-to-bmad/SKILL.md` | Story/AC/UAT/memlog mapping without assuming Story-to-Journey is one-to-one. |
| `skills/adapting-rvtf-to-gsd/SKILL.md` | Goal/MVP UAT/phase mapping and Journey outcome verification. |
| `README.md`, `README-CN.md` | User-facing description of the implemented dual-axis model and applicability rule. |
| `VERSION`, `package.json` | Release version `0.3.0`. |

### Task 1: Preserve the approved design and implementation contract

**Requirements:** `JTV1-DOCS-001`

**Files:**
- Add: `docs/design/2026-08-01-journey-trace-and-acceptance-item.md`
- Add: `docs/superpowers/plans/2026-08-03-journey-trace-v1.md`

- [ ] **Step 1: Verify the baseline tag and branch point**

Run:

```bash
git rev-list -n 1 v0.0.1
git rev-parse main
```

Expected: both commands print `250a36c86e419cfe3d1ce15915cfb246f7c59373`.

- [ ] **Step 2: Check the approved design for scope markers**

Run:

```bash
rg -n 'Approved v1 design|canonical Acceptance Item|Metrics Deferred|Execution Unit object 延后|v1 实施顺序' docs/design/2026-08-01-journey-trace-and-acceptance-item.md
```

Expected: each approved marker is present and no marker claims Skill implementation has started.

- [ ] **Step 3: Check design and plan formatting**

Run:

```bash
git diff --no-index --check /dev/null docs/design/2026-08-01-journey-trace-and-acceptance-item.md
git diff --no-index --check /dev/null docs/superpowers/plans/2026-08-03-journey-trace-v1.md
```

Expected: no whitespace diagnostics. Exit status `1` is expected because each untracked file differs from `/dev/null`.

- [ ] **Step 4: Commit the approved design and plan on the feature branch**

```bash
git add docs/design/2026-08-01-journey-trace-and-acceptance-item.md docs/superpowers/plans/2026-08-03-journey-trace-v1.md
git commit -m "docs: approve journey trace v1 design"
```

Expected: one commit containing only the approved design and this plan.

### Task 2: Record RED pressure baselines and specify scenarios 20-26

**Requirements:** `JTV1-ITEM-001`, `JTV1-APPLY-001`, `JTV1-JOURNEY-001`, `JTV1-EVID-001`, `JTV1-STATUS-001`, `JTV1-GAP-001`

**Files:**
- Modify: `skills/tracing-requirements-to-verification/references/pressure-scenarios.md`

- [ ] **Step 1: Run fresh-agent baseline prompts against the unchanged v0.0.1 skill**

Use a fresh agent for each prompt and require it to read the local v0.0.1 `tracing-requirements-to-verification` skill before answering. Use these exact prompts:

```text
Scenario 20: A dashboard foundation gate passes, but no connected actor path has been executed. Can delivery be called complete?

Scenario 21: Every acceptance criterion under the relevant requirements is individually verified, but there is no evidence that the ordered steps connect or reach the expected outcome. What are the Requirement, Journey, and delivery statuses?

Scenario 22: An end-to-end walkthrough reaches the expected outcome, but one acceptance criterion has only heuristic or adjacent evidence. What may be marked verified?

Scenario 23: An API consumer must authenticate, paginate, survive rate limiting, retry, and verify a consistent result. Is Journey Trace applicable merely because this is an API?

Scenario 24: A one-line isolated metadata correction has exact item-level verification and no ordered or causal path. What Journey artifact is required?

Scenario 25: Formal review is frozen and closed, but the full Completion Gate discovers that required path evidence never existed. Must review reopen, and can delivery complete?

Scenario 26: One canonical acceptance item supports two Journeys. Should it be copied into each Journey, and how is its status maintained?
```

Expected RED evidence: the current skill may reason sensibly, but it lacks canonical Acceptance Item status, Journey applicability, ordered Journey Step mapping, target-specific path evidence, or dual-axis closure rules. Record exact excerpts rather than inferred summaries.

- [ ] **Step 2: Append the dated baseline section and scenarios 20-26**

Add a `Journey Trace v1 Baseline Observed 2026-08-03` section followed by scenarios 20-26. Every scenario must include its prompt and these exact expected decisions:

```text
20: foundation or review sub-gates cannot prove Journey or delivery closure.
21: Requirements may remain verified; Journey stays implemented with an evidence gap; delivery is incomplete.
22: the weak Item, parent Requirement, and dependent Journey cannot be verified.
23: technical domain is irrelevant; the ordered actor-goal path triggers Journey applicability.
24: allow journey_applicability.decision not_required with rationale; do not create a synthetic Journey.
25: missing evidence fails Completion Gate but does not automatically reopen closed review; invalidated previously accepted evidence uses existing controlled-reopen rules.
26: keep one nested canonical Item and reference its stable ID from both Journeys.
```

- [ ] **Step 3: Verify the RED scenarios are present before core changes**

Run:

```bash
rg -n '^## Scenario (20|21|22|23|24|25|26):|Journey Trace v1 Baseline Observed 2026-08-03' skills/tracing-requirements-to-verification/references/pressure-scenarios.md
```

Expected: one baseline heading and seven scenario headings.

- [ ] **Step 4: Commit the RED pressure contract**

```bash
git add skills/tracing-requirements-to-verification/references/pressure-scenarios.md
git commit -m "test: define journey trace pressure scenarios"
```

### Task 3: Implement the core dual-axis workflow

**Requirements:** `JTV1-ITEM-001`, `JTV1-APPLY-001`, `JTV1-JOURNEY-001`, `JTV1-EVID-001`, `JTV1-STATUS-001`, `JTV1-GAP-001`, `JTV1-REG-001`

**Files:**
- Modify: `skills/tracing-requirements-to-verification/SKILL.md`

- [ ] **Step 1: Extend the workflow and artifact chain**

Add Acceptance Item baseline modeling after requirement validity and add Journey applicability before task mapping. The artifact chain must become:

```text
Capability tree
  -> requirement IDs
    -> canonical acceptance items
      -> verification methods
        -> journey applicability and Journey Trace when required
          -> host implementation tasks
            -> item evidence and path evidence
              -> review governance artifacts when applicable
                -> review findings
                  -> gap ledger
                    -> closure decision
```

- [ ] **Step 2: Add canonical Item, Journey, and evidence invariants**

Document these normative rules:

```text
Acceptance Items remain nested under exactly one Requirement and have globally stable IDs within the delivery scope.
Journeys and Journey Steps reference Acceptance Item IDs and never copy Item status or evidence.
Journey Trace applies when an actor must traverse ordered or causally connected observable steps to reach an outcome.
Item evidence proves one criterion; path evidence proves step order, connection, and expected outcome.
All Items verified does not imply Journey verified.
```

- [ ] **Step 3: Add aggregation, propagation, and completion rules**

Require all active required Items to be verified before a Requirement can be verified. A required deferred Item makes the parent Requirement deferred; a blocked Item makes it blocked; rejected Items require validity or scope decisions. Journey-only path gaps keep the Journey implemented and delivery incomplete without falsely downgrading otherwise valid Requirement evidence.

- [ ] **Step 4: Add common-failure corrections**

Add rows for foundation-as-completion, copied Item state, all-Items-implies-Journey, technical-domain applicability, synthetic Journey creation, and missing-path-evidence-after-review-freeze.

- [ ] **Step 5: Run core metadata validation**

Run:

```bash
PYTHON_BIN=/tmp/rvtf-skill-validate-venv/bin/python scripts/validate.sh
```

Expected: all five skills report valid metadata. If that venv is unavailable, create a task-specific temporary venv, install PyYAML there, and rerun with its Python; do not edit validation scripts.

- [ ] **Step 6: Commit the core workflow**

```bash
git add skills/tracing-requirements-to-verification/SKILL.md
git commit -m "feat: add journey trace core semantics"
```

### Task 4: Implement schema and gates

**Requirements:** `JTV1-ITEM-001`, `JTV1-APPLY-001`, `JTV1-JOURNEY-001`, `JTV1-EVID-001`, `JTV1-STATUS-001`, `JTV1-GAP-001`, `JTV1-REG-001`

**Files:**
- Modify: `skills/tracing-requirements-to-verification/references/schema.md`
- Modify: `skills/tracing-requirements-to-verification/references/gates.md`

- [ ] **Step 1: Update the canonical schema example**

Keep Acceptance Items nested under `requirements[].acceptance[]` and give each Item `id`, `criterion`, `source_ref`, `verification`, `status`, target-specific `evidence`, and gap references. Add `journey_applicability`, `journeys[].steps[].acceptance_item_ids`, `path_evidence`, Journey `status`, and Journey gap references. Do not add top-level `acceptance_items`, `owners`, or `execution_units` arrays.

- [ ] **Step 2: Extend gap and closure examples**

Allow a gap to name `requirement`, `acceptance_item`, `journey`, and `journey_step`. Add closure disposition lists for Acceptance Items and Journeys while retaining existing review closure, amendments, verification runs, residual risk, and next-phase entry.

- [ ] **Step 3: Add Journey Applicability Gate**

Place it after Usage Mode Gate. Require candidate Journeys only in discovery, trigger-based decisions in lite, and explicit `required` or `not_required` in standard and strict. State that strict risk does not automatically imply Journey applicability.

- [ ] **Step 4: Extend Design, Plan, Implementation, Evidence, and Completion gates**

Require stable Item IDs and source refs, Step-to-Item mapping, host task trace IDs, target-specific evidence, path/outcome proof, status consistency, and dual-axis closure. Missing path evidence found after review freeze must fail Completion Gate without automatically reopening review.

- [ ] **Step 5: Verify forbidden v1 structures are absent**

Run:

```bash
rg -n '^acceptance_items:|^owners:|^execution_units:|executor_strategy|journey strict verified rate|owner integrity rate' skills/tracing-requirements-to-verification/SKILL.md skills/tracing-requirements-to-verification/references/schema.md skills/tracing-requirements-to-verification/references/gates.md
```

Expected: no output.

- [ ] **Step 6: Validate and commit schema/gates**

```bash
PYTHON_BIN=/tmp/rvtf-skill-validate-venv/bin/python scripts/validate.sh
git diff --check
git add skills/tracing-requirements-to-verification/references/schema.md skills/tracing-requirements-to-verification/references/gates.md
git commit -m "feat: add journey trace schema and gates"
```

Expected: validation passes, no whitespace errors, and the commit contains only schema and gates.

### Task 5: Adapt the four host workflows

**Requirements:** `JTV1-ADAPT-001`, `JTV1-REG-001`

**Files:**
- Modify: `skills/adapting-rvtf-to-superpowers/SKILL.md`
- Modify: `skills/adapting-rvtf-to-agent-skills/SKILL.md`
- Modify: `skills/adapting-rvtf-to-bmad/SKILL.md`
- Modify: `skills/adapting-rvtf-to-gsd/SKILL.md`

- [ ] **Step 1: Update the Superpowers adapter**

Map brainstorming to Journey applicability, writing plans to the four trace ID types, implementer reports to Item/Journey evidence and gaps, and verification-before-completion to explicit path/outcome proof. Preserve Superpowers task grouping and subagent choices.

- [ ] **Step 2: Update the Agent Skills adapter**

Map increments to Acceptance Items and optional Journey Steps, map thin vertical slices to connected paths when applicable, and require both Item and path evidence in Definition of Done. Do not force every increment to create a Journey.

- [ ] **Step 3: Update the BMAD adapter**

Treat Story as a candidate Journey source rather than a one-to-one mapping, Story AC as Acceptance Items, UAT/edge-case execution as target-specific evidence, and memlog/preservation checks as protection for Item/Journey/gap decisions.

- [ ] **Step 4: Update the GSD adapter**

Map MVP user flow to Journey Steps, goal-backward validation to expected outcome, phase plans to the four trace ID types, and phase verification to separate Item and Journey gaps. Keep non-MVP phases trigger-based.

- [ ] **Step 5: Run adapter consistency checks**

Run:

```bash
rg -i --files-without-match 'acceptance item' skills/adapting-rvtf-to-*/SKILL.md
rg -i --files-without-match 'journey' skills/adapting-rvtf-to-*/SKILL.md
rg -n 'Execution Unit|executor_strategy|must use.*subagent|one-to-one' skills/adapting-rvtf-to-*/SKILL.md
```

Expected: the first two commands produce no file paths; the third produces no normative v1 requirement for Execution Units, executor strategy, mandatory subagents, or one-to-one Story mapping.

- [ ] **Step 6: Validate and commit adapters**

```bash
PYTHON_BIN=/tmp/rvtf-skill-validate-venv/bin/python scripts/validate.sh
git diff --check
git add skills/adapting-rvtf-to-superpowers/SKILL.md skills/adapting-rvtf-to-agent-skills/SKILL.md skills/adapting-rvtf-to-bmad/SKILL.md skills/adapting-rvtf-to-gsd/SKILL.md
git commit -m "feat: map host workflows to journey traces"
```

### Task 6: Run GREEN behavior tests

**Requirements:** `JTV1-EVID-001`, `JTV1-STATUS-001`, `JTV1-GAP-001`, `JTV1-ADAPT-001`, `JTV1-REG-001`

**Files:**
- Modify: `skills/tracing-requirements-to-verification/references/pressure-scenarios.md`

- [ ] **Step 1: Run fresh-agent forward tests for scenarios 20-26**

Use the exact Task 2 prompts with a fresh agent per scenario, now requiring the agent to read the modified local core skill. Record exact excerpts showing each expected decision; do not pass a scenario from structural keyword presence.

- [ ] **Step 2: Run regression prompts for scenarios 1-19**

Exercise each existing scenario against the modified local skill. Confirm requirement IDs, evidence-based status, scope amendment discipline, bounded review freeze, controlled reopen, strict independence, and host-method preservation still match their documented expected behavior.

- [ ] **Step 3: Run adapter-specific forward tests**

Use one fresh prompt for each adapter:

```text
Superpowers: A task is complete and review is closed, but no actor-path receipt exists. Decide completion and report the four trace ID types.
Agent Skills: A thin vertical slice advances two Items but not the connected outcome. Decide increment DoD without forcing an unrelated Journey.
BMAD: A Story has three ACs and two alternative user paths. Map Story, ACs, paths, and UAT evidence without assuming one Story equals one Journey.
GSD: An MVP phase passes technical checks but its user-flow UAT is missing. Run goal-backward closure using Requirement and Journey axes.
```

Expected: all adapters preserve host lifecycles, use canonical Item references, and distinguish Item evidence from path evidence.

- [ ] **Step 4: Record behavior receipts and commit**

```bash
git add skills/tracing-requirements-to-verification/references/pressure-scenarios.md
git commit -m "test: verify journey trace behavior"
```

### Task 7: Publish accurate documentation and package version

**Requirements:** `JTV1-DOCS-001`, `JTV1-REG-001`

**Files:**
- Modify: `README.md`
- Modify: `README-CN.md`
- Modify: `VERSION`
- Modify: `package.json`

- [ ] **Step 1: Update the English README**

Add concise bullets stating that Acceptance Items are canonical nested rows, Journey applicability is trigger-based, Journey Trace adds actor/goal/ordered Step/path evidence, and completion checks both Requirement and Journey axes. State that adapters preserve host workflows.

- [ ] **Step 2: Update the Chinese README with equivalent claims**

Mirror the English scope exactly. Do not advertise automatic extraction, Execution Units, owner metrics, Journey percentages, or mandatory Journey use for every project.

- [ ] **Step 3: Set package version to 0.3.0**

Set `VERSION` to `0.3.0` and `package.json` `version` to `0.3.0` only after Task 6 behavior and review evidence passes.

- [ ] **Step 4: Verify documentation claims and version consistency**

Run:

```bash
rg -n 'Acceptance Item|Journey Trace|path evidence|not_required' README.md README-CN.md
rg -n 'Execution Unit|executor_strategy|owner_count|journey.*percentage|自动抽取|automatic extraction' README.md README-CN.md
test "$(tr -d '[:space:]' < VERSION)" = "$(node -p "require('./package.json').version")"
```

Expected: shipped v1 terms appear in both READMEs; deferred-feature search has no promotional claims; versions match `0.3.0`.

- [ ] **Step 5: Run the full validation and packaging gate**

```bash
PYTHON_BIN=/tmp/rvtf-skill-validate-venv/bin/python scripts/validate.sh
PYTHON_BIN=/tmp/rvtf-skill-validate-venv/bin/python scripts/package.sh
git diff --check
tar -tzf dist/rvtf-skills-0.3.0.tgz
```

Expected: five skills validate, npm packaging succeeds, no whitespace errors appear, and the archive contains README files, VERSION, scripts, all five skills, updated references, and no `docs/` directory.

- [ ] **Step 6: Commit the release-ready v1 package**

```bash
git add README.md README-CN.md VERSION package.json
git commit -m "docs: release journey trace v1"
```

Expected: final feature branch is clean except ignored `dist/`, and no push or publication occurs automatically.

### Task 8: Run bounded review and the final Completion Gate

**Requirements:** `JTV1-ITEM-001`, `JTV1-APPLY-001`, `JTV1-JOURNEY-001`, `JTV1-EVID-001`, `JTV1-STATUS-001`, `JTV1-GAP-001`, `JTV1-ADAPT-001`, `JTV1-REG-001`, `JTV1-DOCS-001`

**Files:**
- Review: all files changed since `v0.0.1`
- Modify only when a classified required finding, accepted amendment, or cross-cutting constraint requires remediation.

- [ ] **Step 1: Bind the review subject to the release-ready commit**

Run:

```bash
git status --short --branch
git rev-parse HEAD
git diff --stat v0.0.1...HEAD
```

Expected: the feature branch has no uncommitted tracked or untracked files, and the commit hash becomes the review epoch subject revision.

- [ ] **Step 2: Collect both expected review batches on that revision**

Run an independent requirements reviewer for `requirement-fidelity` and `impact-and-ownership`, then an independent closure-risk reviewer for `verification-and-closure` and `state-and-compatibility`. Each batch must state the exact commit, covered dimensions including no-finding results, limitations, findings, and relationship to the implementer.

- [ ] **Step 3: Classify findings and freeze only complete coverage**

Link every finding to an existing `JTV1-*` requirement, accepted amendment, or cross-cutting constraint. Do not freeze if either batch omits a dimension or names a different revision. Reject or defer optional enhancements unless the delivery owner accepts an amendment.

- [ ] **Step 4: Remediate only frozen required findings**

If required findings exist, edit only affected files, rerun their targeted verification, commit the remediation, and run bounded closure review over frozen findings, changed evidence, and direct remediation risk. If unrelated work changes the subject, start a new scoped review epoch.

- [ ] **Step 5: Run fresh full verification on the final revision**

```bash
PYTHON_BIN=/tmp/rvtf-skill-validate-venv/bin/python scripts/validate.sh
PYTHON_BIN=/tmp/rvtf-skill-validate-venv/bin/python scripts/package.sh
git diff --check
test "$(tr -d '[:space:]' < VERSION)" = "$(node -p "require('./package.json').version")"
git status --short --branch
```

Expected: five skills validate, packaging succeeds for `0.3.0`, versions match, no whitespace diagnostics appear, and the feature worktree is clean except ignored `dist/`.

- [ ] **Step 6: Produce the closure packet**

Record every `JTV1-*` requirement as verified or with an explicit deferred/blocked/rejected decision. Include fresh behavior-test receipts, review batches and closure, validation commands, package archive, residual risk, and the fact that publication, push, installation, merge, and tag creation are outside this implementation unless separately requested.
