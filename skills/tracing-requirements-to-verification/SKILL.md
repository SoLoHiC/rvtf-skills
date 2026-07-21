---
name: tracing-requirements-to-verification
description: Use when work has multiple requirements, phases, acceptance criteria, implementation tasks, verification evidence, review findings, review governance, scope changes, delivery gaps, residual risks, or claims of completion that need traceable delivery decisions.
---

# Tracing Requirements To Verification

## Overview

Use Requirements-to-Verification Traceability Framework (RVTF) to keep delivery work anchored from intent to evidence and delivery decision. Completion means every requirement, review finding, and meaningful gap has an explicit decision: verified, fixed, deliberately deferred, blocked, rejected, or converted into an approved scope amendment.

When review can block closure or expand scope, use bounded review governance to
make applicability, coverage, remediation scope, and reopen decisions explicit.
Review governance controls review intake; it never replaces requirement truth or
the final Completion Gate.

## Core Rule

Never let "implemented" mean only "code exists" or "tests pass." It means each requirement can be traced to acceptance criteria, implementation work, verification evidence, and any remaining gap decision.

```
No review finding becomes implementation work until it is classified and linked
to a requirement decision.
```

If a finding cannot be linked to an existing requirement, accepted amendment, or existing cross-cutting constraint, it is not automatic scope. Record the decision before doing the work.

## Usage Modes

Choose the lightest mode that controls delivery risk:

| Mode | Use when | Minimum artifact |
| --- | --- | --- |
| `discovery` | Exploring or prototyping without a completion claim. | Assumptions, candidate requirements, known unknowns. |
| `lite` | Small bounded change with low risk. | Requirement IDs, evidence notes, gap decisions. |
| `standard` | Multi-step delivery, phase work, review, or handoff. | Trace matrix, review applicability, review finding intake, gap ledger, closure packet. |
| `strict` | Security, privacy, migrations, compatibility, money, production risk, or cross-agent execution. | Standard artifacts plus bounded review governance, independent review evidence, evidence quality, and scope amendment records. |

Do not lower the mode to justify unsupported completion. If review discovers safety, privacy, compliance, data-loss, compatibility, or regression risk, move at least that concern through `strict` handling.

## Workflow

1. Select a usage mode.
2. Build a capability tree for the requested scope.
3. Assign stable requirement IDs to every required behavior, constraint, migration, compatibility promise, documentation change, and non-functional requirement.
4. Mark cross-cutting constraints explicitly when they apply across multiple capabilities.
5. Attach acceptance criteria and verification methods to each requirement ID.
6. Map implementation tasks to the requirement IDs they cover.
7. Decide whether review governance applies. If it does, record a review contract, epoch, batches, freeze, remediation cycles, closure, and controlled reopens as needed.
8. During execution and review, classify every gap or finding before turning it into work.
9. Update requirement status from evidence quality, not from worker reports.
10. Before completion, produce a closure packet listing verified requirements, deferred requirements, blocked requirements, rejected extras, accepted amendments, review closure, residual risk, and next-phase entry conditions.

## Artifact Chain

Use this chain for every non-trivial delivery unit:

```text
Capability tree
  -> requirement IDs
    -> acceptance criteria
      -> verification methods
        -> implementation tasks
          -> evidence
            -> review governance artifacts when applicable
              -> review findings
              -> gap ledger
                -> closure decision
```

Read `references/schema.md` when creating or reviewing concrete RVTF artifacts.
Read `references/gates.md` when running design, plan, implementation, review, or completion gates.
Read `references/review-governance.md` when review applicability, review contracts, batches, freeze, remediation review, late findings, or reopen decisions matter.
Read `references/pressure-scenarios.md` when creating or updating this skill, or when forward-testing whether an agent actually follows RVTF.

## Status Taxonomy

Use these statuses consistently:

| Status | Meaning |
| --- | --- |
| `pending` | Requirement exists but implementation has not started. |
| `implemented` | Code or docs exist, but verification evidence is not complete. |
| `verified` | Required evidence exists and was checked. |
| `deferred` | Deliberately postponed with reason, owner, and follow-up trigger. |
| `blocked` | Cannot proceed without external input or state change. |
| `rejected` | Explicitly out of scope or no longer required. |

Do not invent additional requirement statuses such as `partially verified`. Partial proof stays `implemented`; record missing coverage as evidence gaps.

## Review Finding Intake

Classify every review finding before implementation:

| Class | Decision rule |
| --- | --- |
| `required-gap` | Existing requirement or acceptance criterion is missing or partial. Fix now unless explicitly deferred or blocked. |
| `evidence-gap` | Implementation may exist but evidence does not prove the acceptance criterion. Keep status `implemented`; add evidence or record a gap. |
| `cross-cutting-constraint` | Safety, privacy, security, compatibility, data integrity, performance, observability, or regression concern. Do not reject only because the original spec omitted it. |
| `scope-amendment` | Legitimate new requirement not in the original scope. Add an amendment decision before implementation. |
| `optional-enhancement` | Useful but not required. Reject or defer unless an owner accepts it into scope. |
| `quality-defect` | Code quality issue that threatens an existing requirement or maintainability standard. Link it to that constraint or record it as non-blocking review debt. |

For governed review, also record the finding's epoch, batch, dimension, subject
revision, and whether it was discovered after freeze. Late findings can reopen
only through trace impact and owner decision, not severity labels alone.

## Bounded Review Governance

Use bounded review governance when formal reviewers, multiple review passes,
blocking findings, strict risk, or prior remediation review are part of the
delivery decision.

The governance flow is:

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

Baseline dimensions are `requirement-fidelity`, `impact-and-ownership`, and
`verification-and-closure`. Triggered dimensions cover state/compatibility,
concurrency/recovery, trust/security/privacy, performance/resources, and
operations/observability.

Freeze only after every expected batch covers its assigned dimensions on the
same subject revision and every finding has RVTF classification plus required
owner decisions. Freeze bounds remediation scope; it is not delivery completion.

Closure review checks frozen findings, changed evidence, and direct remediation
risk. Reopen only for `required_gap`, `evidence_invalidated`,
`remediation_regression`, `cross_cutting_risk`, or
`accepted_scope_amendment`, with affected requirements, dimensions, owner
decision, and next epoch recorded.

## Requirement Validity

Check whether requirements are still valid when new information appears. Invalid, obsolete, contradictory, or infeasible requirements need a source, owner, rationale, and decision: amend, reject, defer, or block. RVTF tracks delivery fidelity; it does not prove the original requirement was correct.

## Evidence Quality

Evidence is strong only when it proves the stated acceptance criterion, covers named edge cases, is fresh or still applicable, and is part of the normal verification gate or has an explicit manual record. Weak evidence cannot support `verified`.

## Gap Ledger

Every gap needs:

- requirement ID or affected capability
- observed gap
- impact
- decision: fix now, defer, block, reject, or split
- owner or next responsible workflow
- verification needed to close it

Do not hide gaps in prose summaries. If it matters, put it in the ledger.

## Scope Amendment

Use a scope amendment when review or implementation discovers necessary work not present in the original requirements. Record source, rationale, impacted requirements, owner decision, expected verification, and whether it blocks completion. Unapproved amendments are not implementation tasks.

## Completion Gate

Before claiming a phase, feature, plan, or task is complete:

1. Re-read the latest requirements and plan.
2. Check every requirement ID line by line.
3. Confirm evidence exists for every `verified` item.
4. Confirm every unverified item is `deferred`, `blocked`, or `rejected` with a reason.
5. Check review findings and scope amendments are classified.
6. If bounded review governance applies, confirm review closure or a controlled reopen, deferral, block, or residual-risk decision.
7. State the actual closure status: `complete`, `complete_with_deferred_gaps`, `complete_with_residual_risk`, `incomplete`, `blocked`, or `invalid_requirements`.
8. If required gaps remain, do not call the work complete.

## Common Failures

| Failure | Correction |
| --- | --- |
| Plan has tasks but no requirement IDs | Add IDs before implementation starts. |
| Tests pass but requirements are unchecked | Build the trace matrix and inspect each row. |
| Review only checks code quality | Run a requirement coverage review first. |
| Review finding turns into work automatically | Classify it and link it to an existing requirement, accepted amendment, or constraint first. |
| Reviewer reports one blocker and omits other dimensions | Accept the finding, mark the batch incomplete, and do not freeze. |
| Re-review restarts open-ended review after every fix | Bound it to frozen findings, changed evidence, and direct remediation risk. |
| Freeze treated as completion | Close review if valid, then still run the full Completion Gate. |
| Late optional finding blocks closure | Defer/reject unless an owner accepts an amendment. |
| Weak evidence marked `verified` | Keep the row `implemented` and record evidence gaps. |
| Deferred work is mentioned informally | Move it into the gap ledger with owner and close condition. |
| Next phase starts with hidden leftovers | Convert leftovers into next-phase entry criteria or explicit exclusions. |
