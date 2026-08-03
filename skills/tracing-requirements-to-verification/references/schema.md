# RVTF Schema

## Requirement ID Style

Use stable IDs that survive task reordering:

```text
<AREA>-<CAPABILITY>-<NUMBER>
```

Examples: `AUTH-SESSION-001`, `CLI-RUN-003`, `DOCS-MIGRATION-002`.

For phase-oriented work, prefix with the phase only when the requirement truly belongs to that phase: `P16-REPLAY-001`.

## Trace Matrix

```yaml
scope:
  id: P1.6
  title: Offline skill optimization
  mode: standard
  sources:
    - docs/design.md
    - docs/acceptance.md

requirements:
  - id: P16-REPLAY-001
    capability: replay isolation
    type: behavior
    source: docs/design.md#replay-isolation
    validity:
      status: accepted
      owner: phase-owner
      rationale: Required for trustworthy offline comparison.
    statement: Baseline, candidate, and test replay use sealed inputs.
    acceptance:
      - id: P16-REPLAY-001-AI-001
        criterion: Baseline, candidate, and test replay load the declared sealed inputs.
        source_ref:
          path: docs/design.md
          anchor: replay-isolation
          revision: sha256:0123abcd
        verification:
          method: automated-test
          command: pnpm test:p1.6 -- replay-isolation
          expected: exits 0 with every replay bound to its declared sealed input
        status: verified
        evidence:
          - artifact: artifacts/replay-sealed-input.json
            subject_revision: def456
            quality: strong
            target: P16-REPLAY-001-AI-001
            proves: All three replay modes use their declared sealed inputs.
            normal_gate: true
        gaps: []
      - id: P16-REPLAY-001-AI-002
        criterion: Replays cannot read mutable live run state.
        source_ref:
          path: docs/acceptance.md
          anchor: live-state-rejection
          revision: sha256:5678ef01
        verification:
          method: automated-test
          command: pnpm test:p1.6 -- replay-live-state-rejection
          expected: exits 0 and fails if live state is read
        status: verified
        evidence:
          - artifact: artifacts/replay-live-state-rejection.json
            subject_revision: def456
            quality: strong
            target: P16-REPLAY-001-AI-002
            proves: The replay runner rejects mutable live state.
            normal_gate: true
        gaps: []
    status: verified
    gaps: []

  - id: P16-TENANT-001
    capability: tenant isolation
    type: cross-cutting-constraint
    applies_to:
      - data access
      - replay storage
    statement: New data access cannot expose records outside the caller tenant.
    acceptance:
      - id: P16-TENANT-001-AI-001
        criterion: Tenant A cannot read tenant B records.
        source_ref:
          path: docs/design.md
          anchor: tenant-isolation
          revision: sha256:0123abcd
        verification:
          method: automated-test
          command: pnpm test:p1.6 -- tenant-isolation
          expected: exits 0
        status: verified
        evidence:
          - artifact: artifacts/tenant-isolation.json
            subject_revision: def456
            quality: strong
            target: P16-TENANT-001-AI-001
            proves: Cross-tenant reads are rejected.
            normal_gate: true
        gaps: []
    status: verified
    gaps: []

  - id: P16-RECOVERY-001
    capability: replay recovery
    type: behavior
    source: docs/design.md#replay-recovery
    validity:
      status: accepted
      owner: phase-owner
      rationale: Recovery is required, but its path proof is intentionally deferred.
    statement: An interrupted replay can resume from sealed state and reach a consistent result.
    acceptance:
      - id: P16-RECOVERY-001-AI-001
        criterion: Resume uses the sealed checkpoint and produces the expected comparison.
        source_ref:
          path: docs/design.md
          anchor: replay-recovery
          revision: sha256:0123abcd
        verification:
          method: end-to-end-test
          command: pnpm test:p1.6 -- replay-recovery
          expected: resumed comparison matches an uninterrupted sealed replay
        status: deferred
        evidence: []
        gaps:
          - GAP-P16-001
    status: deferred
    gaps:
      - GAP-P16-001

journey_applicability:
  scope_ref: phase:P1.6
  decision: required
  rationale: Trustworthy replay acceptance depends on an ordered automation path reaching a consistent comparison result.
  triggers:
    - ordered observable steps
    - path crosses dataset and evaluation boundaries
    - item evidence alone cannot prove the expected outcome

journeys:
  - id: J-P16-REPLAY-001
    name: Produce a trustworthy sealed replay comparison
    actor: evaluation-runner
    goal: Compare baseline, candidate, and test behavior without reading live state.
    expected_outcome: The comparison result is derived only from the declared sealed inputs.
    steps:
      - id: J-P16-REPLAY-001-S1
        observable_outcome: The runner loads the declared sealed inputs for all replay modes.
        acceptance_item_ids:
          - P16-REPLAY-001-AI-001
          - P16-TENANT-001-AI-001
      - id: J-P16-REPLAY-001-S2
        observable_outcome: The runner rejects any attempt to read mutable live state.
        acceptance_item_ids:
          - P16-REPLAY-001-AI-002
    path_evidence:
      - artifact: artifacts/sealed-replay-journey.json
        subject_revision: def456
        covers_steps:
          - J-P16-REPLAY-001-S1
          - J-P16-REPLAY-001-S2
        proves_order: true
        proves_outcome: true
        quality: strong
        normal_gate: true
    status: verified
    gaps: []
  - id: J-P16-RECOVERY-001
    name: Recover an interrupted sealed replay
    actor: evaluation-runner
    goal: Resume interrupted work without reading mutable live state.
    expected_outcome: The resumed comparison matches an uninterrupted sealed replay.
    steps:
      - id: J-P16-RECOVERY-001-S1
        observable_outcome: The runner resumes from the sealed checkpoint and produces the expected comparison.
        acceptance_item_ids:
          - P16-RECOVERY-001-AI-001
    path_evidence: []
    status: deferred
    gaps:
      - GAP-P16-001

host_trace_mappings:
  - host_kind: task
    host_ref: Task 3
    requirement_ids:
      - P16-REPLAY-001
    acceptance_item_ids:
      - P16-REPLAY-001-AI-001
      - P16-REPLAY-001-AI-002
    journey_ids:
      - J-P16-REPLAY-001
    journey_step_ids:
      - J-P16-REPLAY-001-S1
      - J-P16-REPLAY-001-S2
  - host_kind: task
    host_ref: Task 4
    requirement_ids:
      - P16-TENANT-001
    acceptance_item_ids:
      - P16-TENANT-001-AI-001
    journey_ids:
      - J-P16-REPLAY-001
    journey_step_ids:
      - J-P16-REPLAY-001-S1
```

`requirements[].acceptance[]` is the only canonical Acceptance Item store. IDs
remain stable across task or source-bullet reordering; `source_ref` records
provenance and does not generate identity. Journeys reference Item IDs and never
copy Item criterion, status, or evidence. Journey Steps have no separate status.

For an isolated change without a path trigger, use the same Requirement and Item
shape and record:

```yaml
journey_applicability:
  scope_ref: change:metadata-correction
  decision: not_required
  rationale: Exact item evidence proves the result; no ordered or causal path exists.
journeys: []
```

## Gap Ledger

```yaml
gaps:
  - id: GAP-P16-001
    requirement: P16-RECOVERY-001
    acceptance_item: P16-RECOVERY-001-AI-001
    journey: J-P16-RECOVERY-001
    journey_step: J-P16-RECOVERY-001-S1
    type: evidence-gap
    summary: The recovery Item and connected Step lack fresh evidence.
    impact: The Acceptance Item, parent Requirement, and recovery Journey cannot be verified.
    decision: deferred
    owner: next-phase-planning
    close_condition: Record strong item evidence plus path evidence covering the declared Step and outcome.

review_findings:
  - id: RF-P16-001
    source: code-review
    epoch: RE-P16-001
    batch: RB-P16-REQ-001
    dimension: requirement-fidelity
    discovered_after_freeze: false
    summary: Input normalization concern may affect replay identity.
    classification: scope-amendment
    linked_requirement: null
    decision: needs-owner-decision
    rationale: Not in original scope, but may affect correctness.
    blocks_completion: true
    next_step: Decide whether to accept amendment or reject with rationale.

scope_amendments:
  - id: AMEND-P16-001
    source_finding: RF-P16-001
    statement: Normalize replay keys before persistence.
    decision: accepted
    owner: phase-owner
    impacted_requirements:
      - P16-REPLAY-001
    verification:
      method: automated-test
      command: pnpm test:p1.6 -- replay-key-normalization
    blocks_completion: true
```

## Review Governance Artifacts

Use these fields when the review-governance applicability gate requires bounded
or independent review. Omit them when `review_applicability.decision` is
`not_required`.

```yaml
review_applicability:
  scope_ref: phase:p1.6
  decision: required
  mode: bounded
  rationale: Multiple review passes can block phase closure.

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
    - id: impact-and-ownership
      applicability: required
      requirements: [P16-REPLAY-001, P16-TENANT-001]
    - id: verification-and-closure
      applicability: required
      requirements: [P16-REPLAY-001]
    - id: concurrency-and-recovery
      applicability: required
      requirements: [P16-RECOVERY-001]
      rationale: Interrupted replay recovery is part of the delivery scope.
  expected_batches:
    - id: requirements-review
      host_kind: requirement-coverage-review
      dimensions: [requirement-fidelity, impact-and-ownership]
    - id: closure-risk-review
      host_kind: verification-gap-review
      dimensions: [verification-and-closure, concurrency-and-recovery]
  exclusions:
    - Performance optimization is outside current acceptance criteria.

review_epochs:
  - id: RE-P16-001
    contract: RC-P16-001
    subject_refs:
      - kind: git-commit
        ref: repository
        revision: def456
    status: collecting

review_batches:
  - id: RB-P16-REQ-001
    epoch: RE-P16-001
    host_kind: requirement-coverage-review
    subject_refs:
      - kind: git-commit
        ref: repository
        revision: def456
    reviewer:
      role: requirements-reviewer
      relationship_to_implementer: independent
      reviewer_ref: opaque-reference
    dimension_coverage:
      - dimension: requirement-fidelity
        status: covered
        findings: [RF-P16-001]
      - dimension: impact-and-ownership
        status: covered
        findings: []
    coverage_status: complete
    limitations: []

review_freeze:
  id: RFR-P16-001
  epoch: RE-P16-001
  subject_refs:
    - kind: git-commit
      ref: repository
      revision: def456
  accepted_batches: [RB-P16-REQ-001, RB-P16-CLOSE-001]
  frozen_findings: [RF-P16-001]
  decision_owner: delivery-coordinator
  frozen_at: 2026-07-21T08:00:00Z

remediation_cycles:
  - id: RRC-P16-001
    epoch: RE-P16-001
    addresses_findings: [RF-P16-001]
    subject_refs:
      - kind: git-commit
        ref: repository
        revision: fed789
    evidence:
      - artifact: tests/replay-key-normalization.test.ts
        quality: strong
    direct_regressions: []
    unrelated_scope_introduced: false

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

### Review Governance Values

Review lifecycle statuses are separate from requirement statuses:

- `collecting`
- `frozen`
- `remediating`
- `closed`
- `reopened`

Dimension coverage statuses:

- `covered`
- `partial`
- `blocked`

Canonical reopen bases:

- `required_gap`
- `evidence_invalidated`
- `remediation_regression`
- `cross_cutting_risk`
- `accepted_scope_amendment`

For findings produced before freeze, set `epoch`, `batch`, and `dimension`.
For findings discovered after freeze, set `discovered_after_freeze: true`,
identify the affected dimension, keep the existing RVTF `classification`, and
record whether the decision reopens, defers, rejects, blocks, or accepts an
amendment.

## Closure Packet

Version 0.3 keeps the v0.2 flat `verified`, `deferred`, `blocked`, and
`rejected` fields as a derived compatibility summary. The typed Requirement,
Acceptance Item, Journey, and gap sections are additive detail. Generate both
from canonical trace objects and gap decisions; do not update either summary
independently.

```yaml
closure:
  scope: P1.6
  status: complete_with_deferred_gaps
  review_closure:
    epoch: RE-P16-001
    status: closed
    remaining_late_findings: []
  verified:
    - P16-REPLAY-001
    - P16-TENANT-001
  deferred:
    - GAP-P16-001
  blocked: []
  rejected: []
  requirements:
    verified:
      - P16-REPLAY-001
      - P16-TENANT-001
    deferred:
      - P16-RECOVERY-001
    blocked: []
    rejected: []
  acceptance_items:
    verified:
      - P16-REPLAY-001-AI-001
      - P16-REPLAY-001-AI-002
      - P16-TENANT-001-AI-001
    deferred:
      - P16-RECOVERY-001-AI-001
    blocked: []
    rejected: []
  journeys:
    verified:
      - J-P16-REPLAY-001
    deferred:
      - J-P16-RECOVERY-001
    blocked: []
    rejected: []
  gaps:
    deferred:
      - GAP-P16-001
  accepted_amendments:
    - AMEND-P16-001
  verification_runs:
    - command: pnpm test:p1.6
      result: pass
      date: 2026-07-18
  residual_risk:
    - Recovery behavior remains unavailable until its deferred evidence gap closes.
  next_phase_entry:
    - P1.7 owns the replay-recovery evidence gap.
```

## Status Rules

- Requirements, Acceptance Items, and Journeys use `pending`, `implemented`,
  `verified`, `deferred`, `blocked`, and `rejected`.
- Journey Steps do not have a formal status.
- `verified` requires target-specific evidence.
- `implemented` is not enough for completion.
- Partial evidence is `implemented` plus one or more `evidence-gap` entries.
- `deferred` requires a reason and close condition.
- `blocked` requires a specific missing input or external state.
- `rejected` requires a scope decision.
- A Requirement can be `verified` only when every active required Acceptance Item
  is `verified`, Requirement-level constraints are verified, and evidence gaps
  are closed.
- A required deferred Item makes its parent Requirement `deferred`; a blocked
  Item makes it `blocked`. Exclude a rejected Item only through a validity or
  scope decision.
- A Journey can be `verified` only when every required Step maps to verified
  Items and strong path evidence proves Step order, connection, and expected
  outcome.
- All Items being `verified` never auto-verifies a Journey.
- A Journey-only path gap keeps the Journey below `verified` and blocks delivery
  completion without downgrading otherwise valid Item or Requirement evidence.
- Review lifecycle and dimension coverage statuses are not requirement statuses.
  Do not use them in the `requirements[].status` field.

## Closure Statuses

- `complete`: all required Requirements and all applicable Journeys are verified,
  with no unresolved blocking findings.
- `complete_with_deferred_gaps`: required deferrals are explicit, owned, and non-blocking.
- `complete_with_residual_risk`: risk remains but is accepted with owner and rationale.
- `incomplete`: required work or evidence is missing.
- `blocked`: external input or state prevents closure.
- `invalid_requirements`: requirements must be corrected before implementation or verification can be trusted.
