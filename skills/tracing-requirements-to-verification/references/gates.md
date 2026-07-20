# RVTF Gates

## Usage Mode Gate

Before choosing artifact depth:

- Use `discovery` only when there is no completion claim.
- Use `lite` only for small, low-risk changes.
- Use `standard` for phase work, handoffs, or review.
- Use `strict` for security, privacy, data integrity, compatibility, migrations, money, production risk, or cross-agent execution.
- Raise the mode for a risky finding even if the rest of the work stays lighter.

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
- Record optional or unlinked findings as deferred/rejected unless an owner accepts them into scope.
- Treat safety, privacy, compliance, data-loss, compatibility, and regression findings as candidate constraints, not disposable extras.

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

Report missing requirements, weak evidence, unverified implemented work,
untraced extra scope, unapproved amendments, and gaps without owner or close
condition.
```
