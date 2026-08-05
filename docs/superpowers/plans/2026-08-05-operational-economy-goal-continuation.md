# RVTF Operational Economy And Goal Continuation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the minimum semantically closed RVTF `0.4.0` Operational Economy Plane and Goal Continuation Contract without turning RVTF into a scheduler, weakening delivery truth, or replacing host-native verification and review.

**Architecture:** Preserve the `0.3.0` Requirement/Acceptance Item and Journey truth plane. Add an orthogonal economy plane for delivery-scope containment, execution/verification/review grouping, evidence artifact/claim reuse, explicit validity assessment, verification and review cadence, cross-revision review carry-forward, and parent-aware continuation. Enforce the critical invariants with a deterministic YAML fixture validator, while keeping concrete commands, review fan-out, persistence, and scheduling under host authority.

**Tech Stack:** Markdown Agent Skills, additive YAML artifacts, Python 3 with PyYAML, Bash validation and packaging, npm package metadata, fresh-agent pressure tests.

---

## RVTF Delivery Contract

**Mode:** `strict`

**Review applicability:** `required`; this changes public schema, completion, evidence-reuse, review, and four host-adapter contracts. Independent requirements and quality review must converge on one candidate revision before the final Completion Gate.

**Authoritative design:** `docs/design/2026-08-05-operational-economy-and-persistent-delivery.md` at or after commit `939b556`.

### Requirement groups

| IDs | Required behavior |
| --- | --- |
| `OE-BOUNDARY-001..002` | Economy never changes delivery truth; effective gates remain the union of host-native mandatory and RVTF-required gates. |
| `OE-SCOPE-001..004` | Model `goal`/`milestone`/`unit` containment separately from execution/verification/review groups; enforce authoritative child inventory, requiredness, disposition, and host-status separation. |
| `OE-CONTINUE-001..002` | Record parent state, remaining scopes, mode, authority, locator, and actual action without scheduling the next host workflow. |
| `OE-EVIDENCE-001..004` | Separate reusable artifacts from target-specific claims; require auditable validity assessments and targeted invalidation. |
| `OE-VERIFY-001..003` | Define worker/batch/milestone/completion tiers; keep Completion Gate semantic and host freshness/full-suite requirements mandatory. |
| `OE-REVIEW-001..004` | Separate dimensions from batch count; model cadence, parent coverage, combined/specialist rules, immutable reviewed revisions, and assessed carry-forward. |
| `OE-ADAPTER-001` | Map actual Superpowers, Agent Skills, GSD, and BMAD lifecycle boundaries and authority. |
| `OE-COMPAT-001` | Accept `0.3.0` inline artifacts and additive `0.4.0` registry or mixed artifacts. |
| `OE-TEST-001` | Prove the contract through pressure tests, deterministic positive/negative fixtures, regression checks, and package inspection. |

### Host snapshots for adapter evidence

| Host | Branch | Revision |
| --- | --- | --- |
| Superpowers | `main` | `44c9b2d6e889982ac18c27d05a19fefe335194e1` |
| Agent Skills | `main` | `7829ffd90d973b6325f5f12f1b1226dcace74443` |
| GSD Core | `next` | `b5ce72f72992e46b31c2b02c8275cdd858a8fdce` |
| BMAD Method | `main` | `116491165d850e9d074554c6271f452363bb607a` |

### Compatibility invariants

- Keep `requirements[].acceptance[]` canonical.
- Keep Journey Step references and separate Item/path evidence.
- Keep all `0.3.0` status, gap, freeze, remediation, closure, and controlled-reopen rules.
- Treat new fields as additive; old inline evidence does not require migration.
- Never rewrite an old review batch's subject revision.
- Never infer current-tree test success from a reusable old claim.
- Never infer RVTF parent completion from host `done`, `archived`, `shipped`, or override closeout.

## File Responsibility Map

| File or directory | Responsibility |
| --- | --- |
| `skills/tracing-requirements-to-verification/references/pressure-scenarios.md` | RED baselines, scenarios 27-45, candidate forward-test receipts, regression decisions. |
| `scripts/fixtures/schema/positive/*.yaml` | Compatible `0.3.0`, `0.4.0`, and mixed artifacts accepted by the validator. |
| `scripts/fixtures/schema/negative/*.yaml` | Parent, closure, validity, and review-revision invariants rejected by the validator. |
| `scripts/validate-schema-examples.py` | Deterministic additive-schema and invariant validation. |
| `scripts/validate.sh` | Skill metadata validation plus deterministic fixture validation. |
| `skills/tracing-requirements-to-verification/SKILL.md` | Core truth/economy relationship, scope, evidence, cadence, continuation, and completion rules. |
| `skills/tracing-requirements-to-verification/references/schema.md` | Concrete additive artifact examples and compatibility rules. |
| `skills/tracing-requirements-to-verification/references/gates.md` | Effective-gate calculation, validity, tier selection, scope aggregation, and Completion Gate. |
| `skills/tracing-requirements-to-verification/references/review-governance.md` | Review cadence, parent coverage, combination, carry-forward, and existing closure/reopen lifecycle. |
| `skills/adapting-rvtf-to-*/SKILL.md` | Exact host mappings without replacing host authority. |
| `README.md`, `README-CN.md` | User-facing `0.4.0` capabilities and boundaries. |
| `VERSION`, `package.json` | Candidate version, updated only after implementation and acceptance evidence exist. |
| `docs/design/2026-08-05-operational-economy-and-persistent-delivery.md` | Status transition from approved design to implemented candidate after gates pass. |

## Task 1: Commit the executable implementation contract

**Requirements:** all `OE-*` through trace coverage.

**Files:**

- Add: `docs/superpowers/plans/2026-08-05-operational-economy-goal-continuation.md`

- [ ] **Step 1: Verify isolation and baseline**

Run:

```bash
git rev-parse --show-toplevel
git branch --show-current
git status --short --branch
./scripts/validate.sh
```

Expected: the linked worktree path, branch `codex/journey-trace-v1`, clean status, and five valid Skills.

- [ ] **Step 2: Check complete requirement coverage in this plan**

Run:

```bash
for id in OE-BOUNDARY-001 OE-BOUNDARY-002 OE-SCOPE-001 OE-SCOPE-002 OE-SCOPE-003 OE-SCOPE-004 OE-CONTINUE-001 OE-CONTINUE-002 OE-EVIDENCE-001 OE-EVIDENCE-002 OE-EVIDENCE-003 OE-EVIDENCE-004 OE-VERIFY-001 OE-VERIFY-002 OE-VERIFY-003 OE-REVIEW-001 OE-REVIEW-002 OE-REVIEW-003 OE-REVIEW-004 OE-ADAPTER-001 OE-COMPAT-001 OE-TEST-001; do rg -q "$id" docs/superpowers/plans/2026-08-05-operational-economy-goal-continuation.md || exit 1; done
git diff --check
```

Expected: exit `0`, no missing ID, and no whitespace diagnostics.

- [ ] **Step 3: Commit the plan**

```bash
git add docs/superpowers/plans/2026-08-05-operational-economy-goal-continuation.md
git commit -m "docs: plan operational economy implementation"
```

## Task 2: Establish RED pressure and deterministic contracts

**Requirements:** `OE-BOUNDARY-001`, `OE-BOUNDARY-002`, `OE-SCOPE-001..004`, `OE-CONTINUE-001..002`, `OE-EVIDENCE-001..004`, `OE-VERIFY-001..003`, `OE-REVIEW-001..004`, `OE-ADAPTER-001`, `OE-COMPAT-001`, `OE-TEST-001`.

**Files:**

- Modify: `skills/tracing-requirements-to-verification/references/pressure-scenarios.md`
- Add: `scripts/fixtures/schema/positive/v0.3-inline.yaml`
- Add: `scripts/fixtures/schema/positive/v0.4-registry.yaml`
- Add: `scripts/fixtures/schema/positive/mixed-representation.yaml`
- Add: `scripts/fixtures/schema/negative/invalid-parent.yaml`
- Add: `scripts/fixtures/schema/negative/blocked-parent-complete.yaml`
- Add: `scripts/fixtures/schema/negative/opaque-validity.yaml`
- Add: `scripts/fixtures/schema/negative/revision-rebinding.yaml`

- [ ] **Step 1: Run fresh-agent baseline scenarios against unchanged `0.3.0` Skills**

Run scenarios 17.1-17.19 from the design as scenarios 27-45. Give fresh agents only the baseline core or the named baseline adapter plus the scenario prompt. Record exact observed behavior, including accidental conservative answers whose artifact contract is missing.

Expected RED: the baseline lacks reusable artifact/claim records, auditable cross-revision validity, scope/group separation, continuation authority, tiered verification, parent review coverage, and accurate current host mappings.

- [ ] **Step 2: Add scenarios 27-45 and dated baseline receipts**

Cover shared evidence, unrelated revision, targeted and verifier invalidation, semantic completion, failed-suite isolation, parent continuation, blocked remaining work, parent review coverage, combined and specialist review, delta re-review, Journey-only invalidation, current Superpowers review shape, no-progress iteration, host verification floor, orthogonal host groups, host continuation capability, and Agent Skills `/ship`.

- [ ] **Step 3: Add fixture documents before the validator exists**

The positive fixtures must express:

- legacy inline Item/Journey evidence;
- registry artifacts, target-specific claims, validity assessment, hierarchy, groups, policy, review cadence/carry-forward, and continuation;
- mixed inline and registry evidence.

The negative fixtures must isolate exactly one failure each:

- a child references an unknown parent;
- a complete parent has a required blocked child;
- a cross-revision valid claim relies on an opaque fingerprint without assessment basis;
- carry-forward mutates or rebinds the historical batch revision.

- [ ] **Step 4: Observe the deterministic RED failure**

Run:

```bash
test ! -f scripts/validate-schema-examples.py
python3 scripts/validate-schema-examples.py
```

Expected: the first command exits `0`; the second fails because the validator has not been implemented. This is the code-level RED receipt.

- [ ] **Step 5: Validate the scenario contract and commit RED artifacts**

Run:

```bash
rg -n '^## Scenario (2[7-9]|3[0-9]|4[0-5]):' skills/tracing-requirements-to-verification/references/pressure-scenarios.md
find scripts/fixtures/schema -type f -name '*.yaml' | sort
git diff --check
```

Expected: nineteen scenario headings, seven fixtures, and no whitespace diagnostics.

```bash
git add skills/tracing-requirements-to-verification/references/pressure-scenarios.md scripts/fixtures/schema
git commit -m "test: define operational economy contracts"
```

## Task 3: Implement the core Operational Economy semantics

**Requirements:** `OE-BOUNDARY-001..002`, `OE-SCOPE-001..004`, `OE-CONTINUE-001..002`, `OE-EVIDENCE-001..004`, `OE-VERIFY-001..003`, `OE-REVIEW-001..004`.

**Files:**

- Modify: `skills/tracing-requirements-to-verification/SKILL.md`

- [ ] **Step 1: Add the truth/economy boundary**

Add the Operational Economy Plane after the artifact chain. State that it organizes work and proof reuse but never changes Requirement, Acceptance Item, Journey, review, gap, or closure truth. Define `effective gates = host-native mandatory gates union RVTF-required gates`.

- [ ] **Step 2: Add scope, group, and continuation rules**

Define `goal`, `milestone`, and `unit` as closure scopes; define execution/verification/review batches as orthogonal groups. Require authoritative versioned child inventory, requiredness, parent aggregation, host-status separation, and a non-scheduling continuation contract with `durable_host`, `artifact_only`, and `advisory` modes.

- [ ] **Step 3: Add artifact/claim validity and targeted propagation**

Allow one artifact to support multiple independently targeted claims. Require target, proof, applicable coverage, and validity. Cross-revision reuse in standard/strict must reference an assessment that compares target, verifier, dependency, environment, and freshness; an opaque hash alone is insufficient. Keep claim validity distinct from host current-test claims.

- [ ] **Step 4: Add verification and review economy rules**

Define worker, batch, milestone, and completion tiers. Clarify that Completion Gate is a complete semantic audit, not unconditional full-suite execution. State that dimensions do not imply batch count; future parent review is not evidence; strict independence and host specialist fan-out remain mandatory.

- [ ] **Step 5: Extend Completion Gate and common failures**

Add parent-scope closure, evidence-validity, host-gate, continuation, group/containment, future-review, stale-current-test, opaque-fingerprint, and old-review-rebinding checks while preserving all existing dual-axis rules.

- [ ] **Step 6: Validate metadata and commit core semantics**

```bash
./scripts/validate.sh
git diff --check
git add skills/tracing-requirements-to-verification/SKILL.md
git commit -m "feat: add operational economy core semantics"
```

Expected before Task 4: five Skills remain structurally valid; deterministic fixture validation is still absent by design.

## Task 4: Implement schema, invariant validator, gates, and review governance

**Requirements:** all non-adapter `OE-*`, especially `OE-COMPAT-001` and `OE-TEST-001`.

**Files:**

- Modify: `skills/tracing-requirements-to-verification/references/schema.md`
- Modify: `skills/tracing-requirements-to-verification/references/gates.md`
- Modify: `skills/tracing-requirements-to-verification/references/review-governance.md`
- Add: `scripts/validate-schema-examples.py`
- Modify: `scripts/validate.sh`
- Modify as needed: `scripts/fixtures/schema/**/*.yaml`

- [ ] **Step 1: Implement the smallest validator that makes the fixtures meaningful**

Use PyYAML and deterministic sorted diagnostics. Validate each positive fixture as accepted and each negative fixture as rejected. Enforce:

- unique scope, artifact, claim, assessment, review-batch, and carry-forward IDs;
- valid `goal|milestone|unit` scope kinds and `execution_batch|verification_batch|review_batch` group kinds;
- resolvable, acyclic parent refs and group member refs;
- parent required-child inventory consistency and forbidden complete aggregation over blocked/incomplete children;
- resolvable claim artifact and trace targets;
- passed artifacts for valid claims;
- assessment-backed standard/strict cross-revision validity with explicit comparison basis;
- immutable source batch revision and explicit from/to impact assessment for carry-forward;
- four verification tiers when a standard/strict policy is declared;
- continuation field and stop-basis consistency.

- [ ] **Step 2: Run focused GREEN tests**

```bash
python3 scripts/validate-schema-examples.py
```

Expected: three positive fixtures accepted, four negative fixtures rejected for their declared invariant, exit `0`.

- [ ] **Step 3: Make fixture validation part of the normal gate**

Call the validator from `scripts/validate.sh` with `${PYTHON_BIN}` after Skill metadata validation. A missing PyYAML dependency must fail with an actionable message; it must not silently skip schema validation.

- [ ] **Step 4: Add additive schema examples and compatibility notes**

Document delivery scopes/groups, artifact/claim registry, validity assessments, verification policy and host floor, review cadence/carry-forward, and continuation. Preserve the old inline example and explain mixed representation.

- [ ] **Step 5: Extend gates**

Add scope inventory/aggregation, evidence reuse/invalidation, effective gate union, tier selection, parent review coverage, carry-forward, continuation, and economy-warning gates. Keep the existing requirement validity, Journey, review freeze, remediation, reopen, and completion gates authoritative.

- [ ] **Step 6: Extend bounded review governance**

Add cadence and `covered_at_parent`, `pending_at_parent`, combined/separate/host-native policy, `host_native_required_batches`, immutable batch revisions, and `review_coverage_carry_forward`. Explicitly prohibit future review evidence and silent revision rebinding.

- [ ] **Step 7: Run integrated validation and commit**

```bash
./scripts/validate.sh
git diff --check
git add scripts/validate-schema-examples.py scripts/validate.sh scripts/fixtures/schema skills/tracing-requirements-to-verification/references/schema.md skills/tracing-requirements-to-verification/references/gates.md skills/tracing-requirements-to-verification/references/review-governance.md
git commit -m "feat: add economy schema and invariant gates"
```

## Task 5: Map the four host methods precisely

**Requirements:** `OE-BOUNDARY-002`, `OE-CONTINUE-001..002`, `OE-VERIFY-003`, `OE-REVIEW-001..004`, `OE-ADAPTER-001`, `OE-TEST-001`.

**Files:**

- Modify: `skills/adapting-rvtf-to-superpowers/SKILL.md`
- Modify: `skills/adapting-rvtf-to-agent-skills/SKILL.md`
- Modify: `skills/adapting-rvtf-to-gsd/SKILL.md`
- Modify: `skills/adapting-rvtf-to-bmad/SKILL.md`

- [ ] **Step 1: Update Superpowers at pinned revision**

Map plan/branch milestones and tasks without changing their boundaries. For current SDD, map each task's one combined reviewer/two verdicts and the final whole-branch review; do not invent a second task reviewer. Preserve fresh completion and branch-finishing suites. Use `execution_action: continue` between SDD tasks; persist higher-goal continuation before deleting a plan ledger. Do not add per-task review to executing-plans unless a risk contract requires it.

- [ ] **Step 2: Update Agent Skills at pinned revision**

Map plan checkpoints/phases to milestones and smallest independent thin tasks to units. Focused RED/GREEN checks are worker gates, while task full suite/build/E2E remains host-native. Preserve `/review`, `/ship` three-specialist fan-out, merge decision, and rollback plan. Keep GO distinct from deployed/post-launch verified. Ordinary `/build` is artifact-only/advisory and stops; only an approved `/build auto` scope continues.

- [ ] **Step 3: Update GSD at pinned revision**

Map GSD Milestone to goal, Phase to milestone, PLAN to unit, Wave to execution group, and PLAN tasks to internal checkpoints. Map worker/batch/milestone/completion tiers while preserving Phase verifier and milestone audit. Derive continuation from the single-writer `.planning` authority. Keep `override_closeout` as host status, not RVTF completion.

- [ ] **Step 4: Update BMAD at pinned revision**

Map Epic/SPEC to goal or milestone, Story to unit, and Build run to an execution record. Preserve every Build review/triage stage. One build-auto invocation handles one story/run; orchestrator owns backlog and continuation. BMAD `done` cannot auto-close an epic or release.

- [ ] **Step 5: Check common adapter invariants and commit**

```bash
rg -n 'host-native|continuation|revision|goal|milestone|unit' skills/adapting-rvtf-to-*/SKILL.md
./scripts/validate.sh
git diff --check
git add skills/adapting-rvtf-to-*/SKILL.md
git commit -m "feat: align host adapters with economy contracts"
```

Expected: each adapter names its host revision and preserves hierarchy/grouping, mandatory gates, status authority, and continuation capability.

## Task 6: Forward-test, review, and remediate the candidate semantics

**Requirements:** all `OE-*`, with evidence for `OE-ADAPTER-001` and `OE-TEST-001`.

**Files:**

- Modify: `skills/tracing-requirements-to-verification/references/pressure-scenarios.md`
- Modify as findings require: core, references, adapters, validator, fixtures

- [ ] **Step 1: Run fresh-agent candidate scenarios**

Use agents that did not implement the tested file. Do not give them expected answers or the design. Test core scenarios 27-45 in bounded groups, then test each adapter with the core using its pinned host revision and a realistic host prompt.

- [ ] **Step 2: Run existing scenarios 1-26 as regression groups**

Record the intentional supersession for former scenario 16: actual current Superpowers SDD uses one combined task reviewer with two verdicts plus a whole-branch review. Preserve every other Journey and bounded-review invariant.

- [ ] **Step 3: Freeze findings once on one candidate revision**

Collect spec-compliance findings first. Classify each against an `OE-*` Requirement, compatibility constraint, or explicit optional enhancement. Record covered dimensions, no-finding dimensions, limitations, and candidate revision before remediation.

- [ ] **Step 4: Remediate findings as one bounded set**

Fix required gaps, evidence gaps, and quality defects. Do not implement optional enhancements without an accepted amendment. Rerun only affected deterministic and forward tests during remediation.

- [ ] **Step 5: Perform delta quality review**

Review frozen findings, changed evidence, and direct remediation risk. If an unaffected review dimension is carried forward, record from/to revision, impact assessment, assessor, and decision; do not alter the old batch revision.

- [ ] **Step 6: Commit converged implementation evidence**

```bash
./scripts/validate.sh
git diff --check
git add skills scripts
git commit -m "test: record operational economy verification"
```

If no tracked evidence or remediation changed after Task 5, do not create an empty commit.

## Task 7: Update documentation and candidate version

**Requirements:** `OE-BOUNDARY-001..002`, `OE-CONTINUE-002`, `OE-COMPAT-001`, `OE-TEST-001`.

**Files:**

- Modify: `README.md`
- Modify: `README-CN.md`
- Modify: `VERSION`
- Modify: `package.json`
- Modify: `docs/design/2026-08-05-operational-economy-and-persistent-delivery.md`

- [ ] **Step 1: Document only implemented behavior**

Explain the truth/economy split, scope containment versus groups, reusable target claims, validity, gate tiers, host gate floor, review cadence, and non-scheduling continuation. Keep lite concise and reserve full registries for standard/strict.

- [ ] **Step 2: Align English and Chinese capability boundaries**

Both READMEs must say that claim reuse does not assert current tests pass, Completion Gate is semantic, host-native gates are a lower bound, and Goal Continuation is not a runtime scheduler.

- [ ] **Step 3: Mark the design implemented and bump the candidate**

Only after Task 6 acceptance evidence is present:

```text
VERSION: 0.4.0
package.json version: 0.4.0
design status: Implemented candidate; local validation and package evidence recorded separately
```

- [ ] **Step 4: Verify documentation and metadata consistency**

```bash
test "$(tr -d '[:space:]' < VERSION)" = "$(node -p "require('./package.json').version")"
rg -n '0\.4\.0|Operational Economy|Goal Continuation' README.md README-CN.md docs/design/2026-08-05-operational-economy-and-persistent-delivery.md
git diff --check
```

- [ ] **Step 5: Commit docs and version**

```bash
git add README.md README-CN.md VERSION package.json docs/design/2026-08-05-operational-economy-and-persistent-delivery.md
git commit -m "docs: publish operational economy candidate"
```

## Task 8: Run the final Completion Gate and inspect the package

**Requirements:** all `OE-*`.

**Files:**

- Generated, not committed: `dist/rvtf-skills-0.4.0.tgz`

- [ ] **Step 1: Run fresh local verification on the combined HEAD**

```bash
./scripts/validate.sh
git diff --check
./scripts/package.sh
```

Expected: five Skills valid, three positive fixtures accepted, four negative fixtures rejected, no whitespace errors, and `dist/rvtf-skills-0.4.0.tgz` created.

- [ ] **Step 2: Inspect package contents and metadata**

```bash
tar -tzf dist/rvtf-skills-0.4.0.tgz | sort
tar -xOf dist/rvtf-skills-0.4.0.tgz package/VERSION
tar -xOf dist/rvtf-skills-0.4.0.tgz package/package.json | node -e 'let s="";process.stdin.on("data",d=>s+=d);process.stdin.on("end",()=>console.log(JSON.parse(s).version))'
shasum -a 256 dist/rvtf-skills-0.4.0.tgz
```

Expected: all five Skills, core references, validator, fixtures, and scripts are present; both packaged versions are `0.4.0`; a final SHA-256 receipt is recorded.

- [ ] **Step 3: Audit every requirement and repository state**

Re-read the design, this plan, candidate Skills, pressure receipts, validation output, package listing, and Git status. For each `OE-*` ID, name the target-specific evidence and disposition. Reject `complete` for any missing evidence.

```bash
git status --short --branch
git log --oneline --decorate -10
```

Expected: clean feature branch with local commits only. Report separately: implementation, local validation, package build, install, merge, push, tag, and publish. Do not install, merge, push, tag, or publish without a new user instruction.

## Final Review Contract

Use the current local Superpowers workflow for implementation review: after each task, complete specification compliance before code quality review and resolve all blocking findings. After all tasks, run one independent whole-change review on the combined HEAD. This execution workflow does not alter the adapter's pinned mapping of upstream Superpowers revision `44c9b2d6e889982ac18c27d05a19fefe335194e1`.

The completion packet must state at least:

- all 22 `OE-*` Requirement dispositions;
- candidate and pinned host revisions;
- deterministic positive and negative fixture results;
- fresh-agent core, adapter, and regression results;
- review freeze/remediation/delta-review result;
- validation commands and actual outcomes;
- tarball filename, contents check, and SHA-256;
- explicit `not_run` or `not_performed` for install, merge, push, tag, and publish.
