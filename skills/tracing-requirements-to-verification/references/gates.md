# RVTF Gates

## Usage Mode Gate

Before choosing artifact depth:

- Use `discovery` only when there is no completion claim.
- Use `lite` only for small, low-risk changes.
- Use `standard` for phase work, handoffs, or review.
- Use `strict` for security, privacy, data integrity, compatibility, migrations, money, production risk, or cross-agent execution.
- Raise the mode for a risky finding even if the rest of the work stays lighter.

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
- Each requirement has acceptance criteria.
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

- Every task lists covered requirement IDs.
- Every requirement has at least one task, explicit deferral, or rejection.
- Every acceptance criterion has a verification method.
- Verification commands are concrete enough to run.
- The plan does not add untraced scope.
- Optional enhancements require accepted scope amendments before implementation.

## Implementation Checkpoint

After each implementation slice:

- Update affected requirement statuses.
- Attach evidence for newly verified items.
- Check evidence quality before marking `verified`.
- Record deviations in the gap ledger.
- Review requirement coverage before code quality.

## Evidence Quality Gate

Before accepting evidence:

- Evidence proves the exact acceptance criterion, not only adjacent behavior.
- Named edge cases and negative cases are covered or logged as gaps.
- Evidence is fresh, reproducible, and tied to a normal gate, or has an explicit manual record.
- Weak evidence keeps the requirement `implemented`; missing proof becomes an `evidence-gap`.

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
- Verify every `verified` row has fresh evidence.
- Confirm review findings and scope amendments have decisions.
- If review governance is required, confirm the epoch is closed or has a
  controlled reopen, deferral, block, or residual-risk decision.
- Confirm all remaining rows are `deferred`, `blocked`, or `rejected`.
- Produce a closure packet.
- Do not start the next phase until leftover work becomes next-phase scope, entry criteria, or explicit exclusion.

## Reviewer Prompt Add-On

Add this block to spec or delivery reviews:

```text
Check the RVTF trace matrix. For each requirement ID:
- Is the requirement represented by implementation work?
- Is the acceptance criterion satisfied by evidence, not by claims?
- Are extra behaviors traced to an approved requirement?
- Are missing or partial behaviors recorded in the gap ledger?

For each review finding:
- Is it classified before implementation?
- Is it linked to an existing requirement, accepted amendment, or constraint?
- Does it represent weak evidence, missing required behavior, optional scope, or a new safety constraint?

For governed review:
- Which review contract, epoch, subject revision, and dimensions were reviewed?
- Did every expected batch cover its assigned dimensions or disclose limitations?
- Are no-finding dimensions recorded as covered rather than omitted?
- Are late findings classified with a reopen, defer, reject, block, or amendment decision?

Report missing requirements, weak evidence, unverified implemented work,
untraced extra scope, unapproved amendments, and gaps without owner or close
condition.
```
