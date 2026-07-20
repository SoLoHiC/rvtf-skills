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

## Closure Packet

```yaml
closure:
  scope: P1.6
  status: complete_with_deferred_gaps
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

## Closure Statuses

- `complete`: all required rows verified and no unresolved blocking findings.
- `complete_with_deferred_gaps`: required deferrals are explicit, owned, and non-blocking.
- `complete_with_residual_risk`: risk remains but is accepted with owner and rationale.
- `incomplete`: required work or evidence is missing.
- `blocked`: external input or state prevents closure.
- `invalid_requirements`: requirements must be corrected before implementation or verification can be trusted.
