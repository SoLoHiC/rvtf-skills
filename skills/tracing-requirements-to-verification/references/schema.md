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
      - id: P16-REPLAY-001-A
        criterion: Replays cannot read mutable live run state.
        verification:
          method: automated-test
          command: pnpm test:p1.6 -- replay-isolation
          expected: exits 0 and fails if live state is read
    tasks:
      - Task 3
    evidence:
      - artifact: tests/replay-isolation.test.ts
        quality: strong
        covers:
          - sealed input replay
          - live state rejection
        normal_gate: true
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
      - id: P16-TENANT-001-A
        criterion: Tenant A cannot read tenant B records.
        verification:
          method: automated-test
          command: pnpm test:p1.6 -- tenant-isolation
          expected: exits 0
    status: pending
```

## Gap Ledger

```yaml
gaps:
  - id: GAP-P16-001
    requirement: P16-REPLAY-002
    type: evidence-gap
    summary: Production replay trust anchor is not implemented.
    impact: Replay evidence can prove local isolation but not production provenance.
    decision: deferred
    owner: next-phase-planning
    close_condition: Add provenance verification and a failing acceptance test.

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
      applicability: not_applicable
      rationale: No asynchronous work, retry path, or multi-writer behavior.
  expected_batches:
    - id: requirements-review
      host_kind: requirement-coverage-review
      dimensions: [requirement-fidelity, impact-and-ownership]
    - id: closure-risk-review
      host_kind: verification-gap-review
      dimensions: [verification-and-closure]
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
  deferred:
    - GAP-P16-001
  blocked: []
  rejected: []
  accepted_amendments:
    - AMEND-P16-001
  verification_runs:
    - command: pnpm test:p1.6
      result: pass
      date: 2026-07-18
  residual_risk:
    - Production provenance still needs an external trust anchor.
  next_phase_entry:
    - Decide whether P1.7 owns production provenance.
```

## Status Rules

- `verified` requires evidence.
- `implemented` is not enough for completion.
- Partial evidence is `implemented` plus one or more `evidence-gap` entries.
- `deferred` requires a reason and close condition.
- `blocked` requires a specific missing input or external state.
- `rejected` requires a scope decision.
- Review lifecycle and dimension coverage statuses are not requirement statuses.
  Do not use them in the `requirements[].status` field.

## Closure Statuses

- `complete`: all required rows verified and no unresolved blocking findings.
- `complete_with_deferred_gaps`: required deferrals are explicit, owned, and non-blocking.
- `complete_with_residual_risk`: risk remains but is accepted with owner and rationale.
- `incomplete`: required work or evidence is missing.
- `blocked`: external input or state prevents closure.
- `invalid_requirements`: requirements must be corrected before implementation or verification can be trusted.
