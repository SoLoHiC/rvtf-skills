# RVTF Bounded Review Governance Design

**Status:** Approved design for implementation planning

**Date:** 2026-07-21

**Repository baseline:** `f74f162`

**Affected project:** `rvtf-skills`

**Implementation owner:** A follow-up session; this document does not implement the Skill changes.

## 1. Executive Summary

RVTF already controls whether a review finding is legitimate delivery work: a
finding must be classified and linked to an existing requirement, an accepted
scope amendment, or a cross-cutting constraint before implementation. It does
not, however, govern how a set of reviews becomes complete, when the resulting
finding set is stable enough for remediation, or what evidence permits a closed
review to be reopened.

That missing lifecycle can produce a "drip review" pattern:

1. implementation is reviewed;
2. one or a few findings are fixed;
3. the next review starts again from an open-ended perspective;
4. a new class of findings appears;
5. the completion boundary keeps moving even when the requested capability has
   not changed.

This design adds an adapter-neutral **Bounded Review Governance** capability to
RVTF. It introduces review applicability, a review contract, review epochs,
coverage-complete review batches, a frozen remediation finding set, bounded
closure review, and controlled reopening. The mechanism does not stop reviewers
from discovering valid problems and does not allow a frozen review to override
requirement truth. It makes late findings carry an explicit traceability and
delivery-decision burden.

The capability is additive. Existing requirement statuses, finding
classifications, gap decisions, scope amendments, evidence rules, closure
statuses, and host-method ownership remain unchanged.

## 2. Context And Origin

### 2.1 Immediate Trigger

The design discussion began after observing a long-running, high-risk storage
cutover task in a downstream project. The task was inherently broad: it changed
canonical runtime state, multiple writers and readers, concurrency behavior,
failure recovery, and authorization-sensitive state. Much of the review work
was justified.

The inefficient part was not simply that reviewers found many issues. It was
that independent review rounds repeatedly introduced a new review angle after
the previous angle had been remediated. Specification findings, code-quality
findings, concurrency findings, stale-authorization findings, and bounded-read
findings arrived in separate serial rounds. Each round required a fresh fix,
build, focused verification, evidence update, and re-review.

This exposed a general process gap:

- the implementation method required review, but did not require the first
  review pass to declare which risk dimensions it had covered;
- reviewers could stop after finding one blocker without making omitted review
  dimensions visible;
- remediation review could silently become another unrestricted full review;
- RVTF correctly classified each new finding, but did not group findings into a
  review epoch or define when a finding set had been frozen;
- no generic rule distinguished a legitimate late required gap from a useful
  but non-blocking late enhancement.

The downstream task is only the motivating example. The resulting design must
not encode that project's storage model, agent target, task structure, or risk
vocabulary.

### 2.2 Why This Belongs In RVTF

The implementation method may decide how many reviewers to dispatch, whether
they run sequentially or concurrently, which model they use, and how they
communicate. Those are host-workflow concerns.

RVTF owns a different question:

> What evidence shows that the declared review surface was covered, what
> findings belong to the current delivery scope, when is remediation scope
> stable, and what traceable decision permits reopening?

This is a requirements-to-verification concern because it directly affects:

- whether findings become implementation work;
- whether new work is an existing required gap or a scope amendment;
- whether evidence still supports `verified`;
- whether a delivery can truthfully claim closure;
- whether residual risk and deferred work remain visible across handoffs.

RVTF can enforce these delivery boundaries without replacing code review,
security review, product judgment, or any host method.

## 3. Existing RVTF System Review

The design was formed after reviewing the complete repository at `f74f162`, not
only the Superpowers adapter.

### 3.1 Existing Core

The core `tracing-requirements-to-verification` Skill currently provides:

- usage modes: `discovery`, `lite`, `standard`, and `strict`;
- capability trees and stable requirement IDs;
- acceptance criteria and verification methods;
- task-to-requirement mapping;
- an explicit distinction between `implemented` and `verified`;
- evidence-quality rules;
- requirement-validity decisions;
- review-finding classification;
- gap ledgers and scope amendments;
- closure packets and stable closure statuses.

Its canonical delivery chain is:

```text
Capability tree
  -> requirement IDs
    -> acceptance criteria
      -> verification methods
        -> implementation tasks
          -> evidence
            -> review findings
              -> gap ledger
                -> closure decision
```

Bounded Review Governance must extend the `review findings` portion of this
chain. It must not replace the chain or create a parallel definition of delivery
completion.

### 3.2 Existing Finding Semantics To Preserve

The current finding classifications remain authoritative:

- `required-gap`
- `evidence-gap`
- `cross-cutting-constraint`
- `scope-amendment`
- `optional-enhancement`
- `quality-defect`

The central RVTF rule also remains unchanged:

```text
No review finding becomes implementation work until it is classified and linked
to a requirement decision.
```

A review freeze cannot downgrade an existing `required-gap`, make weak evidence
strong, or dismiss a valid cross-cutting risk. It governs the review lifecycle,
not requirement truth.

### 3.3 Existing Host Adapters

RVTF currently adapts to four host families:

| Adapter | Existing host strength | Existing RVTF addition |
| --- | --- | --- |
| Superpowers | Task planning, fresh implementers, specification and quality review | Requirement coverage, evidence, finding intake, closure packet |
| Agent Skills | Incremental execution habits and Definition of Done | Trace matrix, doubt/gap handling, evidence-backed completion |
| GSD | Goal convergence, phase validation, shipping | Requirement-level proof, goal-backward verification, gap control |
| BMAD | Spec preservation, memlogs, adversarial and edge-case review | Canonical requirement rows, finding classification, preservation checks |

The core design therefore cannot assume:

- the reviewed unit is always a Task;
- the reviewed subject is always code;
- the revision is always a Git commit;
- every host has exactly one specification reviewer and one quality reviewer;
- closure review always means code-diff review.

### 3.4 Existing Validation Boundary

`scripts/validate.sh` validates Skill metadata through the platform's
`quick_validate.py`. It does not execute behavioral scenarios or validate an
RVTF artifact schema.

Behavioral changes must therefore follow the existing Skill-development model:

1. define pressure scenarios and expected behavior;
2. capture the pre-change failure or ambiguity;
3. change the Skill and references;
4. forward-test fresh agents;
5. run repository metadata validation.

This design does not require a new runtime, parser, or executable schema engine.

## 4. Problem Statement

RVTF can answer whether an individual finding is required, optional, weakly
evidenced, or new scope. It cannot currently answer the following questions in a
stable, reusable form:

1. Which review dimensions apply to this delivery scope?
2. Which review batches are expected from the host workflow?
3. Did a reviewer traverse the declared review surface, including dimensions
   where no finding was discovered?
4. Are multiple reviewers evaluating the same subject revision?
5. When is the finding set stable enough to begin bounded remediation?
6. Is a remediation review closing known findings or starting another
   unrestricted review?
7. Does a late finding invalidate an existing requirement/evidence decision, or
   is it an optional addition that belongs outside the current scope?
8. If a review is reopened, which requirements and dimensions are affected, and
   why?

Without these answers, a detailed trace matrix can still be trapped in an
unbounded review loop.

## 5. Goals And Non-Goals

### 5.1 Goals

The design must:

- work across tasks, increments, phases, releases, designs, documentation, and
  other delivery scopes;
- work across Superpowers, Agent Skills, GSD, BMAD, and future adapters;
- require explicit review-surface coverage before a finding set is frozen;
- aggregate findings before remediation instead of rewarding one-finding review
  loops;
- constrain remediation review to known findings, changed evidence, and direct
  remediation risk;
- preserve a controlled path for legitimate late findings;
- prevent optional late findings from silently becoming blocking scope;
- preserve the full RVTF Completion Gate after review closure;
- scale according to RVTF usage mode and actual review applicability;
- remain usable as Markdown/YAML guidance without introducing a runtime service.

### 5.2 Non-Goals

The design does not:

- guarantee that reviewers discover every defect;
- define code-review techniques for a specific language or framework;
- replace security, privacy, architecture, domain, or product review;
- prescribe reviewer model selection, token budgets, or subagent count;
- require parallel review execution;
- impose a fixed maximum number of remediation attempts;
- suppress a late finding that proves an existing requirement is not satisfied;
- turn generic code-style preferences into RVTF delivery requirements;
- define project-specific review profiles or policies;
- change existing requirement or closure status taxonomies.

## 6. Decision Drivers

The selected design is guided by the following priorities, in order:

1. Preserve requirement and evidence truth.
2. Prevent unclassified scope growth.
3. Make review coverage explicit without pretending review can be complete in an
   absolute sense.
4. Bound remediation and re-review without hiding serious late findings.
5. Remain host-neutral.
6. Keep low-risk use lightweight.
7. Reuse existing RVTF classifications and decisions instead of inventing a
   second delivery taxonomy.

## 7. Alternatives Considered

### 7.1 Status Quo Plus Stronger Reviewer Prompts

This approach would ask reviewers to "be comprehensive" and return all findings
at once, without introducing traceable review artifacts.

**Advantages:** Minimal documentation change and no new schema concepts.

**Rejected because:** There is no evidence that all declared dimensions were
traversed, no stable subject revision, no freeze boundary, and no controlled
reopen decision. Different adapters would continue to interpret the prompt
differently.

### 7.2 Fixed Review Round Or Cost Budget

This approach would cap review rounds, elapsed time, findings, or tokens.

**Advantages:** Predictable operational cost and simple enforcement.

**Rejected as the primary mechanism because:** A budget can suppress a real
required gap, data-loss risk, or invalidated verification result. Cost limits may
remain host-level guardrails, but they cannot determine delivery truth.

### 7.3 Superpowers-Specific Workflow Change

This approach would modify only the Superpowers adapter to make specification
and code-quality reviewers inspect the same Git head and return one batch.

**Advantages:** Directly addresses the motivating workflow and is easy to map to
existing reviewer roles.

**Rejected because:** It overfits Tasks, Git revisions, and exactly two review
types. It would not govern GSD phase review, BMAD adversarial review, Agent Skill
increments, documentation review, or future hosts.

### 7.4 Adapter-Neutral Review Governance Layer

This approach adds generic review applicability, dimensions, contracts, epochs,
batches, freezes, remediation boundaries, and reopens to the RVTF core. Adapters
map host reviews into those concepts.

**Selected because:** It addresses the process gap at the same abstraction level
as RVTF's existing finding and closure decisions while preserving host-method
ownership.

## 8. Architectural Decision

RVTF will have two cooperating planes.

### 8.1 Delivery Trace Plane

The existing plane remains authoritative:

```text
Requirement -> Acceptance -> Verification -> Task -> Evidence
            -> Finding Decision -> Gap/Amendment -> Closure
```

### 8.2 Review Governance Plane

The new plane controls review intake:

```text
Delivery Scope
  -> Review Applicability
    -> Review Contract
      -> Review Epoch
        -> Review Batches
          -> Finding Freeze
            -> Remediation Cycle(s)
              -> Review Closure or Controlled Reopen
```

The planes meet at `review_findings`. Every finding continues through the
existing classification and requirement-decision rules.

Review closure is a sub-gate. It never replaces the full RVTF Completion Gate.

## 9. Delivery-Scope-Neutral Subject Model

Review Governance attaches to a stable `scope_ref`, not specifically to a Task.

Examples include:

- `task:storage-cutover-4`
- `increment:authentication-retry`
- `phase:p1.6`
- `release:2.0.0`
- `document:architecture-decision-17`
- `skill:tracing-requirements-to-verification`

The reviewed subject uses one or more abstract revision references:

```yaml
subject_refs:
  - kind: git-commit
    ref: repository
    revision: def456
  - kind: document
    ref: docs/design.md
    revision: sha256:0123abcd
```

RVTF does not prescribe revision generation. It only requires a stable value
that allows reviewers and later closure checks to identify what was reviewed.

The Review Contract is normally prepared before implementation and therefore
does not need to know the final revision. The review epoch binds the completed,
stable subject revision immediately before review collection begins. If a host
already has a stable planned artifact, the contract may reference it, but the
epoch remains the authoritative reviewed-subject binding.

## 10. Universal Review Dimension Catalog

Dimensions are review lenses, not requirements. Selecting a dimension does not
automatically create implementation work. A finding discovered through a
dimension must still use existing RVTF classification.

### 10.1 Baseline Dimensions

These dimensions apply whenever bounded review governance is active:

| Dimension | Review question |
| --- | --- |
| `requirement-fidelity` | Does the subject satisfy the intended requirements without missing or unapproved extra behavior? |
| `impact-and-ownership` | Which states, interfaces, writers, readers, callers, consumers, and owners are affected? |
| `verification-and-closure` | Does evidence directly prove acceptance, and are gaps and residual risks explicitly decided? |

### 10.2 Triggered Dimensions

These dimensions require an applicability decision:

| Dimension | Typical trigger |
| --- | --- |
| `state-and-compatibility` | Persistent state, schemas, public APIs, protocols, migrations, or compatibility promises |
| `concurrency-and-recovery` | Multiple writers, asynchronous work, retries, locks, partial success, crashes, or recovery |
| `trust-security-and-privacy` | Identity, authorization, external input, secrets, sensitive data, or cross-boundary access |
| `performance-and-resources` | Hot paths, large inputs, batching, potentially unbounded data, memory, disk, network, or latency constraints |
| `operations-and-observability` | Rollout, rollback, background processing, telemetry, audit, diagnosis, or production operation |

An applicability entry uses:

- `required`
- `not_applicable` with a concise rationale

A reviewer may challenge `not_applicable` only by identifying a concrete trigger
in the reviewed subject or governing requirements. The challenge is a contract
gap to resolve before the batch can claim complete coverage; it is not automatic
feature scope.

Generic naming, formatting, and refactoring preferences remain host code-quality
concerns unless they threaten an existing requirement, cross-cutting constraint,
or maintainability standard already accepted into scope.

## 11. Review Applicability And Modes

The review-governance burden must not make RVTF itself a source of over-review.

| RVTF mode | Review Governance behavior |
| --- | --- |
| `discovery` | Not required because there is no completion claim. Risks and candidate review needs may be recorded as assumptions. |
| `lite` | Optional compact batch. Existing finding classification remains sufficient for small, low-risk work. |
| `standard` | A review-applicability decision is required. Bounded governance is required when host review is planned, multiple review passes exist, or review findings may block closure or expand scope. |
| `strict` | Bounded governance and independent-from-implementer review evidence are required for the risk-affected delivery scope. Missing independence keeps review closure incomplete or blocked. |

Review Governance activates when one or more of these conditions hold:

- the host workflow invokes one or more formal reviewers;
- multiple review passes or review roles are expected;
- review findings can change scope or block a completion claim;
- the affected strict-mode risk requires independent evidence;
- a prior review has already produced findings requiring remediation.

For `standard`, `not_required` is valid only with a rationale showing that no
formal review lifecycle is part of the delivery decision. This keeps ordinary
multi-step delivery from inheriting unnecessary review bureaucracy.

## 12. Core Artifacts

The concrete schema may be represented in YAML, Markdown tables, or equivalent
host-native artifacts. The semantic fields below are canonical; formatting is
not.

### 12.1 Review Applicability

```yaml
review_applicability:
  scope_ref: phase:p1.6
  decision: required
  mode: bounded
  rationale: Multiple independent reviews can block phase closure.
```

Suggested `mode` values are review-governance modes, not requirement statuses:

- `bounded`
- `independent`

When review is not required, record `decision: not_required` and omit the
contract.

### 12.2 Review Contract

```yaml
review_contract:
  id: RC-P16-001
  scope_ref: phase:p1.6
  impact_surface:
    states: [sealed-replay-input]
    interfaces: [replay-runner]
    writers: [dataset-builder]
    readers: [evaluation-runner]
    callers: [optimization-command]
    consumers: [closure-report]
  dimensions:
    - id: requirement-fidelity
      applicability: required
      requirements: [P16-REPLAY-001]
    - id: concurrency-and-recovery
      applicability: not_applicable
      rationale: The reviewed change has no asynchronous or multi-writer behavior.
  expected_batches:
    - id: requirements-review
      host_kind: goal-backward-validation
      dimensions: [requirement-fidelity, impact-and-ownership]
    - id: quality-risk-review
      host_kind: adversarial-review
      dimensions: [verification-and-closure]
  exclusions:
    - Performance optimization not required by current acceptance criteria.
```

The contract defines the expected impact and review surface before implementation.
It does not predict concrete findings or require a final subject revision. Impact
surface categories may be empty with a rationale, but they must not be silently
omitted when the baseline `impact-and-ownership` dimension is active.

### 12.3 Review Epoch

A review epoch groups one stable subject, its expected batches, one frozen
finding set, zero or more remediation cycles, and one closure or reopen decision.

```yaml
review_epochs:
  - id: RE-P16-001
    contract: RC-P16-001
    subject_refs:
      - kind: git-commit
        ref: repository
        revision: def456
    status: collecting
```

Review lifecycle statuses are separate from requirement statuses. Suggested
values are:

- `collecting`
- `frozen`
- `remediating`
- `closed`
- `reopened`

### 12.4 Review Batch

```yaml
review_batches:
  - id: RB-P16-REQ-001
    epoch: RE-P16-001
    host_kind: goal-backward-validation
    subject_refs:
      - kind: git-commit
        ref: repository
        revision: def456
    reviewer:
      role: requirements-reviewer
      relationship_to_implementer: independent
      reviewer_ref: optional-opaque-reference
    dimension_coverage:
      - dimension: requirement-fidelity
        status: covered
        findings: [RF-P16-001]
      - dimension: verification-and-closure
        status: covered
        findings: []
    coverage_status: complete
    limitations: []
```

Coverage statuses are review-record statuses, not requirement statuses:

- `covered`
- `partial`
- `blocked`

`coverage_status: complete` means every dimension assigned to that batch was
traversed and limitations were disclosed. It does not assert that no unknown
defect exists.

### 12.5 Finding Freeze

The coordinator may freeze only when:

- every expected batch exists;
- all assigned required dimensions are covered;
- every finding uses the existing RVTF classification;
- every required owner decision is recorded before remediation begins;
- all batches refer to the expected subject revision;
- no undisclosed review limitation prevents the declared coverage.

```yaml
review_freeze:
  id: RFR-P16-001
  epoch: RE-P16-001
  subject_refs:
    - kind: git-commit
      ref: repository
      revision: def456
  accepted_batches: [RB-P16-REQ-001, RB-P16-RISK-001]
  frozen_findings: [RF-P16-001, RF-P16-002]
  decision_owner: delivery-coordinator
  frozen_at: 2026-07-21T08:00:00Z
```

The freeze defines bounded remediation scope for the epoch. It does not declare
the delivery complete.

### 12.6 Remediation Cycle

An epoch may have multiple remediation cycles when fixes fail verification or
need correction. The process does not impose a numeric round limit.

Each cycle records:

- the frozen findings addressed;
- the new subject revision;
- verification evidence produced;
- direct regressions or changed assumptions;
- whether unrelated scope was introduced.

Unrelated implementation invalidates the current freeze because the subject has
changed beyond the declared remediation surface. The coordinator must amend the
contract before freeze or create/reopen an epoch after freeze.

### 12.7 Review Closure

Review closure checks:

- every frozen required finding has a valid close decision;
- remediation evidence directly addresses the finding;
- evidence supporting affected requirements remains valid;
- the remediation delta introduced no blocking regression;
- any late finding has an explicit intake and reopen decision;
- no unrelated subject change bypassed contract review.

After review closure, the normal RVTF Completion Gate still re-reads all current
requirements, evidence, gaps, amendments, residual risk, and next-phase entry
conditions.

### 12.8 Controlled Reopen

Reopening creates a new review epoch with an explicit affected surface. It does
not silently convert the closed epoch back into unrestricted review.

```yaml
review_reopens:
  - id: RRO-P16-001
    prior_epoch: RE-P16-001
    basis: evidence_invalidated
    source_finding: RF-P16-009
    affected_requirements: [P16-REPLAY-001]
    affected_dimensions: [verification-and-closure]
    owner_decision: reopen
    next_epoch: RE-P16-002
```

Canonical reopen bases are:

- `required_gap`
- `evidence_invalidated`
- `remediation_regression`
- `cross_cutting_risk`
- `accepted_scope_amendment`

A subject revision that changed outside declared remediation invalidates the
freeze and also requires a new epoch or an explicit contract decision.

### 12.9 Existing Review Finding Integration

The existing `review_findings` ledger remains the canonical finding record. The
new capability adds provenance and lifecycle fields; it does not create a second
finding taxonomy.

```yaml
review_findings:
  - id: RF-P16-009
    source: closure-review
    epoch: RE-P16-001
    batch: null
    dimension: verification-and-closure
    discovered_after_freeze: true
    classification: evidence-gap
    linked_requirement: P16-REPLAY-001
    decision: reopen
    blocks_completion: true
    reopen_basis: evidence_invalidated
    rationale: The original evidence did not exercise the required retry path.
```

For findings produced before freeze, `batch` links to the declaring review
batch. A late finding may have no batch because it arose during remediation or
closure review, but it must still identify the current epoch, affected dimension,
classification, requirement decision, completion impact, and any reopen basis.

The existing `blocks_completion` field remains authoritative; the design does
not add a competing severity or completion-impact taxonomy.

## 13. Finding Intake After Freeze

Every late finding still uses the existing classification table.

### 13.1 Findings That Can Reopen

A late finding can reopen when it demonstrates one of the following:

- an existing requirement or acceptance criterion is not satisfied;
- evidence previously supporting `verified` is invalid, stale, or inapplicable;
- remediation directly introduced a regression;
- a safety, privacy, security, compatibility, data-integrity, performance, or
  observability constraint requires a new owner decision;
- a scope amendment has been accepted and explicitly blocks the current closure.

Severity labels alone are not the authority because different host methods use
different scales. Reopen authority comes from trace impact and owner decision.

### 13.2 Findings That Do Not Automatically Reopen

The following remain recorded but do not automatically block the current review
epoch:

- optional enhancements without an accepted amendment;
- style preferences not linked to a requirement or accepted standard;
- speculative hardening without a concrete affected constraint;
- unrelated refactoring opportunities;
- findings outside the declared delivery scope whose risk does not invalidate
  current evidence or requirements.

They must be rejected, deferred, or accepted through the existing RVTF decision
mechanisms. Freeze is not permission to discard them silently.

## 14. Roles And Authority

The design defines logical roles, not specific humans or agent runtimes.

| Role | Authority |
| --- | --- |
| `implementer` | Implements and remediates; cannot alone declare strict review coverage complete |
| `reviewer` | Traverses assigned dimensions and reports findings and limitations; cannot alone accept new scope |
| `coordinator` | Checks contract and batch completeness, freezes the finding set, and detects revision drift |
| `delivery_owner` | Accepts or rejects scope amendments, residual risk, exceptional deferral, and controlled reopen decisions |

One actor may hold multiple roles in `lite` or selected `standard` workflows.
Strict review must preserve reviewer independence for the affected risk scope.

Reviewer references should be opaque and optional. RVTF should not require raw
prompts, full session transcripts, personal identity, or host-specific session
IDs.

## 15. Host Adapter Mapping

### 15.1 Superpowers

| Host activity | RVTF mapping |
| --- | --- |
| Brainstorming and writing plans | Review applicability and Review Contract |
| Spec compliance review | One expected review batch |
| Code quality review | One expected review batch |
| Implementer fixes | Remediation cycle |
| Re-review | Bounded review closure, not a new open-ended review |
| Verification and branch finishing | Full RVTF Completion Gate after review closure |

The adapter should request complete dimension coverage for one stable subject
head. Whether the two reviewers run sequentially or concurrently remains a
Superpowers decision.

### 15.2 Agent Skills

| Host activity | RVTF mapping |
| --- | --- |
| Increment planning | Delivery scope and review applicability |
| Increment review | Review batch for the increment revision |
| Doubt handling | Assumption, gap, or finding intake |
| Definition of Done | Review closure plus full requirement/evidence closure |

The adapter must avoid forcing release-scale review artifacts onto every small
increment. Review Governance applies at the smallest delivery scope whose review
can change the completion decision.

### 15.3 GSD

| Host activity | RVTF mapping |
| --- | --- |
| Plan review | Contract and requirement-fidelity batch |
| Phase validation | Goal-backward and verification-closure batch |
| Gap control | Existing finding/gap decisions within the epoch |
| Ship review | Review closure followed by full Closure Packet decision |

The review freeze must not replace goal-backward verification. GSD still starts
from desired outcomes and walks evidence backward.

### 15.4 BMAD

| Host activity | RVTF mapping |
| --- | --- |
| Spec kernel | Delivery scope, requirements, and Review Contract |
| Adversarial review | Declared review batch |
| Edge-case review | Declared or controlled-late review batch |
| Verification-gap review | Verification-and-closure batch |
| Preservation validation | Subject-revision and prior-decision preservation |
| Append-only memlog | Review lifecycle transitions and decisions as events |

BMAD remains free to discover new edge cases. Freeze controls whether a newly
discovered edge case reopens current delivery, becomes an amendment, or is
deferred; it does not suppress edge-case discovery.

## 16. Invariants

The implementation must preserve these invariants:

1. No finding becomes implementation work without existing RVTF classification
   and a requirement decision.
2. Review dimensions are lenses, not new requirements.
3. A frozen finding set cannot override a required gap or invalid evidence.
4. Every batch in an epoch reviews the declared subject revision.
5. Freeze requires complete declared-dimension coverage, including explicit
   no-finding results.
6. Reviewer limitations and blocked dimensions remain visible.
7. Remediation may iterate, but may not silently expand unrelated scope.
8. Closure review is bounded; the full RVTF Completion Gate remains global.
9. Reopen affects explicit requirements and dimensions and creates a new epoch.
10. Existing requirement statuses and closure statuses remain unchanged.
11. Existing RVTF artifacts without Review Governance remain valid when the
    applicability gate does not require it.
12. Adapters preserve host lifecycle ownership.

## 17. Failure And Edge-Case Handling

| Condition | Required behavior |
| --- | --- |
| Expected batch missing | Keep epoch `collecting`; do not freeze |
| Required dimension `partial` or `blocked` | Record limitation/gap; do not claim complete coverage |
| Batches reference different revisions | Reject freeze until subject revisions converge |
| Reviewer finds only one blocker and omits remaining dimensions | Batch is incomplete regardless of finding validity |
| Reviewers disagree | Preserve both findings/decisions and require coordinator or owner resolution |
| Contract marks a triggered dimension `not_applicable` | Return contract for correction before freeze |
| Remediation fails verification | Continue bounded remediation for the frozen finding |
| Remediation introduces direct regression | Record late finding and reopen on `remediation_regression` |
| Unrelated work changes reviewed subject | Invalidate freeze and start/amend a review epoch |
| Optional late improvement appears | Defer/reject unless owner accepts an amendment |
| Existing required behavior is discovered missing after freeze | Reopen on `required_gap`, regardless of informal severity label |
| Evidence supporting `verified` becomes invalid | Reopen on `evidence_invalidated`; requirement returns to evidence-based status handling |
| Independent review unavailable in strict scope | Record an explicit gap and keep review closure `incomplete` or `blocked`; an owner decision cannot turn self-review into independent evidence |

## 18. Repository Change Surface

The follow-up implementation is expected to modify:

- `skills/tracing-requirements-to-verification/SKILL.md`
- `skills/tracing-requirements-to-verification/references/gates.md`
- `skills/tracing-requirements-to-verification/references/schema.md`
- `skills/tracing-requirements-to-verification/references/pressure-scenarios.md`
- `skills/adapting-rvtf-to-superpowers/SKILL.md`
- `skills/adapting-rvtf-to-agent-skills/SKILL.md`
- `skills/adapting-rvtf-to-gsd/SKILL.md`
- `skills/adapting-rvtf-to-bmad/SKILL.md`
- `README.md`
- `README-CN.md`

The implementation should add:

- `skills/tracing-requirements-to-verification/references/review-governance.md`

Agent metadata may be updated only if the public short descriptions no longer
accurately represent the expanded capability. The install and package scripts
do not require behavioral changes.

## 19. Requirements And Acceptance Map

| Requirement | Statement | Acceptance summary |
| --- | --- | --- |
| `BRG-CORE-001` | Review Governance extends rather than replaces the existing RVTF trace plane | Existing status, finding, gap, amendment, and closure semantics remain unchanged |
| `BRG-SCOPE-001` | Governance is delivery-scope and subject-revision neutral | Examples cover code, phase, document, and non-Git revisions |
| `BRG-DIM-001` | The 3 baseline plus 5 triggered dimensions have explicit applicability rules | Agents select only triggered dimensions and justify `not_applicable` |
| `BRG-IMPACT-001` | Review planning identifies the affected ownership and interaction surface without project-specific policy | Contract records relevant states, interfaces, writers, readers, callers, and consumers |
| `BRG-MODE-001` | Governance scales with RVTF mode and actual review applicability | Lite work stays light; standard has an applicability decision; strict risk scope requires independent evidence |
| `BRG-BATCH-001` | Review batches prove declared surface traversal on a stable subject | Missing dimensions or revision drift prevent freeze |
| `BRG-FREEZE-001` | A finding set can be frozen for bounded remediation without hiding requirement truth | Optional late work does not block; existing required gaps still reopen |
| `BRG-REMEDIATION-001` | Remediation can iterate without restarting unrestricted review | Re-review checks frozen findings, evidence impact, and direct delta risk |
| `BRG-REOPEN-001` | Reopen decisions are trace-backed and create a scoped new epoch | Every reopen records basis, affected requirements/dimensions, and owner decision |
| `BRG-ADAPTER-001` | Every existing adapter maps its host review lifecycle without being replaced | Superpowers, Agent Skills, GSD, and BMAD mappings are documented and pressure-tested |
| `BRG-PRIVACY-001` | Governance records do not require raw prompts or personal/session detail | Reviewer identity is optional and opaque; role/independence is sufficient |
| `BRG-TEST-001` | Fresh-agent pressure tests prove bounded review behavior and preserve old behavior | Existing scenarios remain green and new scenarios demonstrate pre-change gaps and post-change compliance |
| `BRG-DOCS-001` | Public English and Chinese documentation describe the capability consistently | README capability, scope, and non-goals remain aligned |

## 20. Verification Design

### 20.1 Preserve Existing Pressure Scenarios

The current six pressure scenarios remain required regression coverage:

1. rushed completion;
2. detailed plan drift;
3. adapter use;
4. review-finding scope creep;
5. weak evidence;
6. missing safety requirement.

The new design fails if it allows review freeze to bypass any existing expected
behavior.

### 20.2 New Core Pressure Scenarios

Add at least the following scenarios with explicit pass/fail assertions.

#### Scenario A: Drip Review

A reviewer reports one valid blocker but does not report coverage for the other
required dimensions.

Expected behavior:

- accept/classify the finding;
- reject the batch's complete-coverage claim;
- do not freeze the epoch;
- request the remaining dimension results in the same batch scope.

#### Scenario B: Optional Finding After Freeze

A closure reviewer notices an unrelated cleanup or UX enhancement.

Expected behavior:

- classify it as optional or unlinked;
- defer/reject unless an owner accepts an amendment;
- do not reopen the epoch automatically.

#### Scenario C: Late Existing Required Gap

After freeze, evidence shows an existing acceptance criterion is not satisfied,
even though the issue is informally labeled low severity.

Expected behavior:

- classify as `required-gap`;
- reopen on `required_gap` or explicitly defer/block under existing RVTF rules;
- never dismiss it solely because the finding was late or low severity.

#### Scenario D: Late Cross-Cutting Safety Risk

After freeze, review demonstrates a concrete authorization or data-integrity
risk omitted by the original requirements.

Expected behavior:

- treat it as a candidate cross-cutting constraint or scope amendment;
- require an accountable owner decision;
- reopen when the decision blocks current closure.

#### Scenario E: Revision Drift

Two expected batches review different revisions, or unrelated implementation is
added after freeze.

Expected behavior:

- refuse freeze or invalidate it;
- require a converged subject revision and appropriate new/delta review.

#### Scenario F: Remediation Regression

A fix closes a frozen finding but directly breaks another verified behavior.

Expected behavior:

- record the regression as a late finding;
- invalidate affected evidence;
- open a scoped new epoch.

#### Scenario G: Standard Work Without Formal Review

A standard multi-step documentation delivery has no formal review process and no
review finding affecting closure.

Expected behavior:

- require an applicability decision;
- allow `not_required` with rationale;
- do not require empty batches or a synthetic freeze.

#### Scenario H: Strict Self-Approval

The implementer is the only reviewer for a strict, risk-affected scope.

Expected behavior:

- reject strict independent-review closure;
- record the missing independence as a gap and keep review closure incomplete or blocked;
- do not invent a new requirement status.

#### Scenario I: Freeze Is Not Delivery Completion

All declared review batches and frozen findings are closed, but one requirement
still has only weak evidence.

Expected behavior:

- allow the review epoch itself to close;
- keep the requirement `implemented` with an evidence gap;
- reject a delivery-level `complete` claim through the existing Completion Gate.

### 20.3 Adapter Pressure Scenarios

At least one scenario per adapter must prove that the core does not encode
Superpowers-specific assumptions:

- Superpowers: spec and quality batches share one review subject;
- Agent Skills: an increment can be governed without forcing release-scale
  review;
- GSD: review freeze does not replace goal-backward validation;
- BMAD: an edge-case hunter may continue discovery while late finding intake
  controls closure impact.

### 20.4 Validation Commands

The implementation plan should include:

```bash
scripts/validate.sh
```

and a documented fresh-agent pressure-test run. If packaging metadata or public
files change, also run:

```bash
scripts/package.sh
```

Package generation is supporting evidence, not behavioral proof.

## 21. Rollout And Compatibility

The change is additive and should be introduced without invalidating existing
RVTF artifacts.

- Existing trace matrices remain valid.
- Existing requirement statuses remain valid.
- Existing finding classification remains valid.
- Existing gap ledgers, amendments, and closure packets remain valid.
- Review Governance is required only according to its applicability/mode gate.
- Existing adapters continue to own their host lifecycle.

Because the capability materially expands the public framework, the follow-up
implementation should consider a minor version increment rather than presenting
it as a wording-only patch. Version selection remains a release decision, not a
design invariant.

## 22. Implementation Handoff Guidance

The implementation session should use process TDD for Skill changes:

1. Read this design and the current core/adapters in full.
2. Add the new pressure scenarios and record where the current Skill is ambiguous
   or fails the expected behavior.
3. Add `references/review-governance.md` as the detailed canonical reference.
4. Make concise core `SKILL.md` changes that point to the reference rather than
   copying the entire design into the activation path.
5. Extend gates and schema while preserving existing vocabularies.
6. Update all four adapters, not only Superpowers.
7. Update English and Chinese README files consistently.
8. Forward-test fresh agents against old and new pressure scenarios.
9. Run metadata validation and package verification.
10. Produce an RVTF closure packet for the Skill change itself.

The implementation plan must not:

- add a new requirement status;
- replace finding classification with review severity;
- hardcode Git, Task, or two-reviewer assumptions in the core;
- treat freeze as authority to ignore a required gap;
- require project-specific policy files;
- change host implementation methods from inside RVTF.

## 23. Design Outcome

The accepted direction is:

> RVTF will provide an adapter-neutral, delivery-scope-neutral governance
> protocol for declaring review applicability and coverage, batching findings,
> freezing bounded remediation scope, and controlling late-finding reopen
> decisions, while preserving requirement truth and the host method's ownership
> of review execution.

This addresses the original serial-review problem without turning RVTF into a
code-review engine or a universal mandate to review every task in every risk
dimension.
