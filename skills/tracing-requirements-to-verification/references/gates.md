# RVTF Gates

## Usage Mode Gate

Before choosing artifact depth:

- Use `discovery` only when there is no completion claim.
- Use `lite` only for small, low-risk changes.
- Use `standard` for phase work, handoffs, or review.
- Use `strict` for security, privacy, data integrity, compatibility, migrations, money, production risk, or cross-agent execution.
- Raise the mode for a risky finding even if the rest of the work stays lighter.

## Journey Applicability Gate

Before planning implementation or claiming closure:

- In `discovery`, record candidate Journeys only; there is no completion claim.
- In `lite`, make a Journey applicability decision whenever an actor-goal path
  has ordered or causally connected observable Steps.
- In `standard` and `strict`, record `journey_applicability.decision` as
  `required` or `not_required` with a rationale.
- Mark Journey Trace `required` when item evidence alone cannot prove the
  outcome, Steps depend on order or state transitions, the path crosses
  boundaries, failure/recovery affects acceptance, or closure must be judged
  backward from an actor goal.
- Do not decide from technical labels. UI, CLI, API, migration, infrastructure,
  human, service, and automation work all use the same triggers.
- Strict risk does not automatically imply Journey applicability.
- Use `not_required` only when exact item-level verification fully proves the
  isolated result and no ordered or causal path exists. Do not invent a
  synthetic Journey.

## Review Governance Applicability Gate

Before review can affect closure or scope:

- In `discovery`, record candidate review needs only as assumptions.
- In `lite`, use bounded review governance only when the risk or host workflow
  justifies it.
- In `standard`, record `review_applicability`; use `not_required` only with a
  rationale showing no formal review lifecycle is part of the delivery decision.
- In `strict`, require bounded governance plus independent-from-implementer
  review evidence for the affected risk scope.
- Activate governance when formal reviewers, multiple review passes, blocking
  review findings, strict risk, or prior remediation review are present.

## Requirement Validity Gate

Before trusting a requirement:

- Confirm the requirement still matches the latest source, owner decision, and known constraints.
- Convert contradictions, obsolete assumptions, or infeasible requirements into amend/reject/defer/block decisions.
- Do not use RVTF to prove faithful delivery of a requirement that is no longer valid.

## Design Gate

Before implementation planning:

- Capability tree exists.
- Requirement IDs are stable and complete enough for the phase.
- Each requirement has canonical Acceptance Items nested under
  `requirements[].acceptance[]`.
- Every Acceptance Item has a stable delivery-scope ID, source reference,
  criterion, verification method, initial status, and gap/evidence fields.
- No task or Journey duplicates mutable Acceptance Item status or evidence.
- Journey applicability is recorded at the depth required by the usage mode.
- Every required Journey defines actor, goal, expected outcome, and ordered
  observable Steps; every required Step maps to at least one Acceptance Item ID.
- Cross-cutting constraints are represented as rows or explicit non-goals.
- Requirement validity is checked against sources, assumptions, and owner decisions.
- Assumptions, non-goals, and risk areas are explicit.
- Open questions are either answered or represented as blocked/deferred rows.
- If review governance applies, the review contract identifies baseline
  dimensions, triggered dimensions, impact surface, expected batches, and
  exclusions.

## Review Contract Gate

Before collecting formal review batches:

- Bind the contract to a delivery-scope-neutral `scope_ref`.
- Record impact surface categories: states, interfaces, writers, readers,
  callers, and consumers. Empty categories need rationale when
  `impact-and-ownership` is active.
- Include baseline dimensions: `requirement-fidelity`, `impact-and-ownership`,
  and `verification-and-closure`.
- Mark triggered dimensions as `required` or `not_applicable` with rationale.
- Map expected host review batches to dimensions.
- Do not let dimensions become requirements; findings still require RVTF
  classification and owner decisions.

## Plan Gate

Before coding:

- Every host task, story, phase, or increment lists the applicable
  `requirement_ids`, `acceptance_item_ids`, `journey_ids`, and
  `journey_step_ids`. Journey lists may be empty only when applicability does
  not require them.
- Every requirement has at least one task, explicit deferral, or rejection.
- Every Acceptance Item has at least one host work mapping, explicit deferral,
  or valid rejection and a concrete verification method.
- Required Journey Steps have host work mappings and planned path/outcome
  evidence; component or foundation checks are not path evidence by default.
- Verification commands are concrete enough to run.
- The plan does not add untraced scope.
- Optional enhancements require accepted scope amendments before implementation.

## Implementation Checkpoint

After each implementation slice:

- Update affected Acceptance Item, Requirement, and Journey statuses without
  auto-promoting parents.
- Attach item evidence to canonical Acceptance Item IDs and path evidence to
  Journey IDs and covered Step IDs.
- Check evidence quality before marking `verified`.
- Record deviations in the gap ledger.
- Propagate Item gaps to their parent Requirement and dependent Journeys. Keep a
  Journey-only path gap from falsely downgrading otherwise valid Requirement
  evidence.
- Review requirement coverage before code quality.

## Evidence Quality Gate

Before accepting evidence:

- Every evidence record names or is structurally attached to its target.
- Item evidence proves the exact Acceptance Item criterion, not only adjacent
  behavior.
- Path evidence proves required Step order and connection plus the Journey's
  expected outcome; local component presence is insufficient.
- A single artifact may support both axes only when each target and `proves`
  claim is recorded separately.
- Named edge cases and negative cases are covered or logged as gaps.
- Evidence is fresh, reproducible, and tied to a normal gate, or has an explicit manual record.
- Weak item evidence keeps the Item and parent Requirement below `verified` and
  prevents dependent Journeys from being `verified`.
- All Items being `verified` does not verify a Journey when path evidence is
  absent; keep the Journey `implemented` and record an `evidence-gap`.

## Review Finding Intake Gate

Before implementing review feedback:

- Classify each finding: `required-gap`, `evidence-gap`, `cross-cutting-constraint`, `scope-amendment`, `optional-enhancement`, or `quality-defect`.
- Link it to an existing requirement, accepted amendment, or cross-cutting constraint.
- For governed review, record epoch, batch, dimension, subject revision, and
  whether the finding was discovered after freeze.
- Record optional or unlinked findings as deferred/rejected unless an owner accepts them into scope.
- Treat safety, privacy, compliance, data-loss, compatibility, and regression findings as candidate constraints, not disposable extras.

## Review Batch And Freeze Gate

Before freezing a review finding set:

- Every expected batch exists.
- Each batch reviewed the epoch's declared subject revision.
- Every assigned required dimension is `covered`, including dimensions with no
  findings.
- Reviewer limitations are disclosed; `partial` or `blocked` dimensions prevent
  complete coverage.
- Every finding has an RVTF classification and required owner decision.
- Batches with different subject revisions do not freeze until revisions
  converge.
- A reviewer who reports one blocker but omits remaining dimensions has produced
  a valid finding but an incomplete batch.

Freeze defines bounded remediation scope only. It is not delivery completion.

## Remediation Review Gate

During remediation review:

- Check frozen findings, changed evidence, and direct remediation risk.
- Do not restart unrestricted review for each fix.
- Record the new subject revision and evidence for each remediation cycle.
- If remediation fails verification, continue bounded remediation for the frozen
  finding.
- If unrelated work changes the subject, invalidate the freeze and amend or
  reopen the epoch.
- If remediation introduces a direct regression, record a late finding and
  reopen on `remediation_regression`.

## Controlled Reopen Gate

For findings discovered after freeze:

- Reopen only when trace impact shows `required_gap`,
  `evidence_invalidated`, `remediation_regression`, `cross_cutting_risk`, or
  `accepted_scope_amendment`.
- Record affected requirements, affected dimensions, source finding, basis,
  owner decision, and next epoch.
- Do not reopen automatically for optional enhancements, style preferences,
  speculative hardening, unrelated refactoring, or out-of-scope findings that do
  not invalidate current evidence or requirements.
- Never dismiss an existing required gap only because it was discovered late or
  labeled low severity.

## Scope Amendment Gate

Before expanding scope:

- Record source finding, rationale, impacted requirements, owner decision, and verification.
- Do not implement an unapproved amendment except to stop an active safety or production incident.
- If an amendment blocks completion, reflect that in the closure packet.

## Completion Gate

Before saying complete:

- Re-read the latest requirements, plan, and gap ledger.
- Verify every active required Acceptance Item has a valid disposition and every
  `verified` Item has fresh, target-specific evidence.
- Enforce status consistency: all active required Items must be `verified`
  before their Requirement can be `verified`; deferred, blocked, and rejected
  Items require the corresponding parent decision.
- Confirm the Journey applicability decision and rationale.
- For every applicable Journey, verify Step-to-Item mappings, referenced Item
  status, strong path evidence, expected outcome proof, recovery coverage, and
  Journey/Step gaps before allowing `verified`.
- Confirm review findings and scope amendments have decisions.
- If review governance is required, confirm the epoch is closed or has a
  controlled reopen, deferral, block, or residual-risk decision.
- Treat review closure as a sub-gate: missing path evidence discovered after
  freeze fails delivery closure but does not automatically reopen review. Use
  `evidence_invalidated` only when previously accepted evidence became invalid.
- Confirm all remaining Requirements, Acceptance Items, and Journeys are
  `deferred`, `blocked`, or `rejected` with owner and rationale where required.
- Produce a closure packet with separate Requirement, Acceptance Item, Journey,
  gap, review, amendment, verification-run, and residual-risk dispositions.
- Call delivery `complete` only when every required Requirement and every
  applicable Journey is `verified`.
- Do not start the next phase until leftover work becomes next-phase scope, entry criteria, or explicit exclusion.

## Reviewer Prompt Add-On

Add this block to spec or delivery reviews:

```text
Check the RVTF trace matrix. For each requirement ID:
- Is the requirement represented by implementation work?
- Does every canonical Acceptance Item have a stable ID and source reference?
- Is each Acceptance Item satisfied by target-specific evidence, not by claims?
- Are extra behaviors traced to an approved requirement?
- Are missing or partial behaviors recorded in the gap ledger?

For Journey applicability and each required Journey:
- Does the decision follow actor-goal-path triggers rather than a technical label?
- Does every required Step reference canonical Acceptance Item IDs without copying state?
- Does path evidence prove Step order, connection, and expected outcome?
- Are Item gaps and Journey-only path gaps propagated to the correct targets?

For each review finding:
- Is it classified before implementation?
- Is it linked to an existing requirement, accepted amendment, or constraint?
- Does it represent weak evidence, missing required behavior, optional scope, or a new safety constraint?

For governed review:
- Which review contract, epoch, subject revision, and dimensions were reviewed?
- Did every expected batch cover its assigned dimensions or disclose limitations?
- Are no-finding dimensions recorded as covered rather than omitted?
- Are late findings classified with a reopen, defer, reject, block, or amendment decision?

Report missing Requirements or Acceptance Items, weak item or path evidence,
unverified implemented work, invalid Journey applicability, untraced extra
scope, unapproved amendments, and gaps without owner or close condition.
```
