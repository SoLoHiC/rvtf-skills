---
name: tracing-requirements-to-verification
description: Use when work has multiple requirements, phases, acceptance criteria, implementation tasks, verification evidence, review findings, review governance, scope changes, delivery gaps, residual risks, or claims of completion that need traceable delivery decisions.
---

# Tracing Requirements To Verification

## Overview

Use Requirements-to-Verification Traceability Framework (RVTF) to keep delivery work anchored from intent to evidence and delivery decision. Requirement Trace proves each criterion; Journey Trace, when applicable, proves that an actor can traverse the required path and reach the expected outcome. Completion means every required Requirement, canonical Acceptance Item, applicable Journey, review finding, and meaningful gap has an explicit evidence-backed decision.

When review can block closure or expand scope, use bounded review governance to
make applicability, coverage, remediation scope, and reopen decisions explicit.
Review governance controls review intake; it never replaces requirement truth or
the final Completion Gate.

## Core Rule

Never let "implemented" mean only "code exists" or "tests pass." Each Requirement must trace through canonical Acceptance Items to implementation work, item evidence, and gap decisions. When acceptance depends on ordered or causally connected observable steps, also require a Journey Trace with path and outcome evidence.

```
No review finding becomes implementation work until it is classified and linked
to a requirement decision.
```

If a finding cannot be linked to an existing requirement, accepted amendment, or existing cross-cutting constraint, it is not automatic scope. Record the decision before doing the work.

## Usage Modes

Choose the lightest mode that controls delivery risk:

| Mode | Use when | Minimum artifact |
| --- | --- | --- |
| `discovery` | Exploring or prototyping without a completion claim. | Assumptions, candidate requirements and Journeys, known unknowns. |
| `lite` | Small bounded change with low risk. | Requirement and Acceptance Item IDs, evidence notes, gap decisions, plus a Journey applicability decision when a path trigger exists. |
| `standard` | Multi-step delivery, phase work, review, or handoff. | Requirement Trace, explicit Journey applicability, Journey Trace when required, review applicability, gap ledger, closure packet. |
| `strict` | Security, privacy, migrations, compatibility, money, production risk, or cross-agent execution. | Standard artifacts plus bounded review governance, independent review evidence, evidence quality, and scope amendment records. |

Do not lower the mode to justify unsupported completion. If review discovers safety, privacy, compliance, data-loss, compatibility, or regression risk, move at least that concern through `strict` handling.

## Workflow

1. Select a usage mode.
2. Build a capability tree for the requested scope.
3. Assign stable requirement IDs to every required behavior, constraint, migration, compatibility promise, documentation change, and non-functional requirement.
4. Mark cross-cutting constraints explicitly when they apply across multiple capabilities.
5. Convert each acceptance criterion into one canonical Acceptance Item nested under exactly one Requirement. Give it a stable delivery-scope ID, source provenance, verification method, status, item evidence, and gap references.
6. Decide Journey applicability. Build a Journey Trace when an actor must traverse ordered or causally connected observable steps to reach an acceptance outcome; otherwise record a justified `not_required` decision when the mode requires it.
7. When Journey Trace applies, define actor, goal, expected outcome, ordered Journey Steps, Acceptance Item references, path evidence, status, and gap references.
8. Map host implementation tasks, stories, phases, or increments to the Requirement, Acceptance Item, Journey, and Journey Step IDs they cover.
9. Decide whether review governance applies. If it does, record a review contract, epoch, batches, freeze, remediation cycles, closure, and controlled reopens as needed.
10. During execution and review, classify every gap or finding before turning it into work.
11. Update Acceptance Item, Requirement, and Journey status from target-specific evidence quality, not from worker reports or parent-task completion.
12. Before completion, produce a closure packet listing Requirement, Acceptance Item, and Journey dispositions; accepted amendments; review closure; residual risk; gaps; and next-phase entry conditions.

## Artifact Chain

Use this chain for every non-trivial delivery unit:

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

Read `references/schema.md` when creating or reviewing concrete RVTF artifacts.
Read `references/gates.md` when running design, plan, implementation, review, or completion gates.
Read `references/review-governance.md` when review applicability, review contracts, batches, freeze, remediation review, late findings, or reopen decisions matter.
Read `references/pressure-scenarios.md` when creating or updating this skill, or when forward-testing whether an agent actually follows RVTF.

## Status Taxonomy

Use these statuses consistently for Requirements, Acceptance Items, and Journeys. Journey Steps do not have an independent formal status:

| Status | Meaning |
| --- | --- |
| `pending` | The object exists but implementation has not started. |
| `implemented` | Code or docs exist, but verification evidence is not complete. |
| `verified` | Required evidence exists and was checked. |
| `deferred` | Deliberately postponed with reason, owner, and follow-up trigger. |
| `blocked` | Cannot proceed without external input or state change. |
| `rejected` | Explicitly out of scope or no longer required. |

Do not invent additional statuses such as `partially verified`. Partial proof stays `implemented`; record missing coverage as evidence gaps.

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

## Canonical Acceptance Items

An Acceptance Item is an independently verifiable criterion nested under `requirements[].acceptance[]`. It is the canonical criterion record, not a copy made for a task or Journey.

- Each Acceptance Item belongs to exactly one Requirement and has a globally unique, stable ID within the delivery scope.
- Keep source provenance separate from identity. A moved bullet does not get a new ID merely because its locator changed.
- Record criterion, source reference, verification method, status, target-specific item evidence, and gap references on the Item.
- Journeys and Journey Steps reference Acceptance Item IDs. Never copy Item criterion, status, or evidence into a Journey.
- One Acceptance Item may support multiple Journeys; update its status once on the canonical Item.

Requirement status must obey the child Items:

| Active required Acceptance Item state | Parent Requirement constraint |
| --- | --- |
| Any `pending` or `implemented` Item | Requirement cannot be `verified`. |
| Any `deferred` Item | Requirement is `deferred` unless an accepted scope decision removes the Item from the required set. |
| Any `blocked` Item | Requirement is `blocked`. |
| Any `rejected` Item | Exclude it only with a recorded validity or scope decision. |
| All Items `verified` | Requirement may be `verified` only if Requirement-level constraints and evidence gaps are also closed. |

Do not derive percentages or a `partial` status. Preserve progress on the child Items while applying the parent constraint.

## Journey Applicability And Trace

Build a Journey Trace when acceptance depends on an actor reaching an outcome through ordered or causally connected observable steps. The actor may be a user, operator, developer, API consumer, external system, service, or automation. Applicability depends on the path, not on labels such as UI, CLI, API, migration, or infrastructure.

Common triggers are:

- item evidence alone cannot prove the overall outcome;
- steps have order, state-transition, or causal dependencies;
- the path crosses Requirements, components, systems, or responsibility boundaries;
- failure, recovery, rollback, or an alternative path affects acceptance;
- end-to-end closure must be judged backward from an actor goal.

In `discovery`, record candidate Journeys only. In `lite`, make an applicability decision when a trigger exists. In `standard` and `strict`, record `journey_applicability.decision` as `required` or `not_required` with rationale. Strict risk alone does not make a Journey required. When exact item-level verification fully proves an isolated change and no ordered or causal path exists, record `not_required`; do not create a synthetic Journey.

An Actor Journey records a stable ID, name, actor, goal, expected outcome, ordered Journey Steps, path evidence, status, and gaps. Each required Journey Step describes an actor-observable behavior or result and references at least one canonical Acceptance Item ID. A source-code edit is an implementation task, not a Journey Step. Scenario remains a way to describe preconditions or alternate/failure/recovery context; it is not a separate v1 trace object.

Journey verification requires all of the following:

1. Every required Step maps to at least one Acceptance Item.
2. Every referenced required Acceptance Item is `verified`.
3. Strong, fresh, applicable path evidence proves the declared Step order and connection.
4. Path evidence proves the expected outcome, not merely that local components exist.
5. Required failure or recovery paths are explicitly represented.
6. No unresolved Journey or Journey Step gap remains.

All Acceptance Items being `verified` does not imply that a Journey is `verified`. Without adequate path evidence, keep the Journey `implemented`, record an evidence gap, and reject delivery completion.

## Evidence Quality

Evidence is strong only when it proves its declared target, covers named edge cases, is fresh or still applicable, and is part of the normal verification gate or has an explicit manual record. Weak evidence cannot support `verified`.

- **Item evidence** proves one Acceptance Item criterion.
- **Path evidence** proves Journey Step order, connection, and the expected outcome.

The same artifact may support both targets only when each target and `proves` claim is recorded separately. A local assertion can be strong Item evidence yet weak Journey evidence. A successful walkthrough cannot substitute implicitly for weak or missing Item evidence.

## Gap Ledger

Every gap needs:

- affected Requirement ID or capability, plus Acceptance Item, Journey, and Journey Step IDs when applicable
- observed gap
- impact
- decision: fix now, defer, block, reject, or split
- owner or next responsible workflow
- verification needed to close it

Do not hide gaps in prose summaries. If it matters, put it in the ledger.

Propagate gaps only to affected trace objects:

```text
Item evidence gap
  -> Acceptance Item cannot be verified
    -> parent Requirement cannot be verified
      -> dependent Journeys cannot be verified
```

```text
Journey-only path gap
  -> Journey cannot be verified
    -> delivery cannot be complete
```

A Journey-only path gap does not downgrade otherwise valid Requirement or Item evidence. If missing path evidence is first discovered after review freeze, fail the Completion Gate but do not automatically reopen the closed review. Reopen through the existing `evidence_invalidated` basis only when previously accepted evidence is later invalidated and trace impact warrants a controlled reopen.

## Scope Amendment

Use a scope amendment when review or implementation discovers necessary work not present in the original requirements. Record source, rationale, impacted requirements, owner decision, expected verification, and whether it blocks completion. Unapproved amendments are not implementation tasks.

## Completion Gate

Before claiming a phase, feature, plan, or task is complete:

1. Re-read the latest requirements and plan.
2. Check every Requirement and canonical Acceptance Item ID line by line.
3. Enforce Item-to-Requirement aggregation constraints; do not auto-promote a parent from partial child evidence.
4. Confirm evidence exists and is target-specific for every `verified` Item and Requirement.
5. Check the recorded Journey applicability decision and rationale.
6. For every applicable Journey, check Step-to-Item mappings, referenced Item status, path evidence, expected outcome, and Journey/Step gaps.
7. Check review findings and scope amendments are classified.
8. If bounded review governance applies, confirm review closure or a controlled reopen, deferral, block, or residual-risk decision. Review closure remains a sub-gate.
9. State the actual closure status: `complete`, `complete_with_deferred_gaps`, `complete_with_residual_risk`, `incomplete`, `blocked`, or `invalid_requirements`.
10. Call delivery `complete` only when every required Requirement and every applicable Journey is `verified`; if required gaps remain, reject `complete`.

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
| Foundation or component gate treated as Journey completion | Require target-specific path evidence for the ordered Steps and expected outcome. |
| Acceptance Item copied into each Journey | Keep one canonical nested Item and reference its stable ID. |
| All Acceptance Items `verified`, so Journey auto-verifies | Keep Journey `implemented` until strong path and outcome evidence passes its own gate. |
| Technical domain label decides Journey applicability | Apply actor-goal-path triggers regardless of UI, API, migration, infrastructure, or actor type. |
| Isolated change gets a synthetic Journey | Record a justified `not_required` decision when item evidence fully proves the result and no path exists. |
| Missing path evidence after review freeze automatically reopens review | Fail delivery closure; reopen only when accepted evidence is invalidated under controlled-reopen rules. |
| Late optional finding blocks closure | Defer/reject unless an owner accepts an amendment. |
| Weak evidence marked `verified` | Keep the row `implemented` and record evidence gaps. |
| Owner or verifier counts presented as completion evidence | Use target-specific evidence and object dispositions; counts are diagnostic only. |
| Deferred work is mentioned informally | Move it into the gap ledger with owner and close condition. |
| Next phase starts with hidden leftovers | Convert leftovers into next-phase entry criteria or explicit exclusions. |
