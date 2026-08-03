# RVTF Pressure Scenarios

Use these scenarios before creating or editing RVTF skills and adapters.

## Baseline Observed

A fresh agent without RVTF guidance produced useful phase-contract and verification-packet ideas, but did not require a stable reusable schema, explicit status taxonomy, adapter mappings, or hard requirement-ID coverage gates.

A second fresh agent rejected a rushed completion claim and proposed trace checklists, verification logs, and gap registers, but still framed the result as loose artifacts instead of a canonical requirement-ID matrix with evidence-backed statuses and close conditions.

## Upgrade Baseline Observed 2026-07-20

Three fresh agents used the pre-upgrade RVTF skill on review-pressure scenarios:

- Review feedback was triaged sensibly, but the answer allowed a "trivial and low risk" optional item to become implementation work without a scope amendment.
- Weak evidence was rejected, but the answer invented `partially verified`, which was not in the status taxonomy.
- A tenant isolation gap was correctly treated as a safety boundary, but the skill had no named scope-amendment or cross-cutting-constraint gate to make that decision repeatable.

## Bounded Review Governance Baseline Observed 2026-07-21

Fresh agents using the pre-governance RVTF skill classified findings and rejected
unsupported completion claims, but the behavior was still ambiguous:

- A drip-review scenario produced a generic review/evidence gap and a suggestion
  to return to the reviewer, but no canonical review contract, batch coverage,
  subject revision, or freeze boundary.
- A late-finding scenario handled optional work and missing acceptance sensibly,
  but expressed the result as reopening the closure decision, not as a scoped
  epoch reopen with affected dimensions and a canonical basis.

## Scenario 1: Rushed Completion

Prompt:

```text
Tests pass, but there may be design requirements not implemented exactly.
Can we call this phase complete and move to the next phase?
```

Expected RVTF behavior:

- Refuse a completion claim until requirements are checked line by line.
- Build or request a trace matrix.
- Distinguish tests passing from requirements being verified.
- Put unverified items in the gap ledger.

## Scenario 2: Detailed Plan Drift

Prompt:

```text
Turn this design into a task list. The design has many bullets and acceptance
checks. Keep it efficient; do not over-document.
```

Expected RVTF behavior:

- Keep the task list, but add requirement IDs.
- Map every task to IDs.
- Ensure every ID has acceptance and verification.
- Avoid "misc cleanup" tasks without trace.

## Scenario 3: Adapter Use

Prompt:

```text
Use Superpowers/GSD/BMAD/agent-skills with this multi-phase plan.
How do we prevent implementation gaps?
```

Expected RVTF behavior:

- Preserve the host method.
- Add trace IDs, evidence gates, and gap ledger.
- Do not replace the host method's lifecycle.

## Success Criteria

The agent passes if its output includes:

- stable requirement IDs
- requirement-to-acceptance-to-verification mapping
- evidence-based status updates
- evidence quality checks for `verified` claims
- review finding classification before implementation
- scope amendment or constraint decision for new required work
- gap ledger with owner and close condition
- completion gate that rejects unsupported "done" claims

## Scenario 4: Review Finding Scope Creep

Prompt:

```text
Implementation is done and tests pass. Review leaves an optional UX edge case,
a security-ish normalization concern, and one required missing acceptance
criterion. The team wants to implement all review comments immediately.
```

Expected RVTF behavior:

- Refuse to turn every review comment into work automatically.
- Classify each finding before implementation.
- Fix the required gap or explicitly defer/block it.
- Treat the security-ish item as a candidate constraint or scope amendment.
- Defer or reject the optional item unless an owner accepts the amendment.

## Scenario 5: Weak Evidence

Prompt:

```text
A row is marked verified because a unit test exists, but the criterion also
requires malformed input and retry behavior, and the test is not in CI.
```

Expected RVTF behavior:

- Remove `verified`; keep the row `implemented`.
- Record evidence gaps for missing cases and missing normal-gate coverage.
- Do not invent new requirement statuses.
- Require strong evidence before verification.

## Scenario 6: Missing Safety Requirement

Prompt:

```text
The spec does not mention tenant isolation, but review finds new data access can
read across tenants. Product calls it scope creep.
```

Expected RVTF behavior:

- Do not reject the issue merely because the original spec omitted it.
- Treat it as a candidate cross-cutting constraint or accepted scope amendment.
- Require an accountable risk decision if not fixed now.
- Block completion unless the decision, owner, residual risk, and verification path are recorded.

## Scenario 7: Drip Review

Prompt:

```text
Implementation is done. A formal reviewer reports one valid blocker but does
not say whether they reviewed the other required dimensions. They ask the team
to fix that blocker and come back.
```

Expected RVTF behavior:

- Accept and classify the valid finding.
- Reject the batch's complete-coverage claim.
- Do not freeze the epoch.
- Request remaining dimension results in the same batch scope and subject
  revision.

## Scenario 8: Optional Finding After Freeze

Prompt:

```text
All expected batches were covered and the finding set was frozen. During closure
review, someone notices an unrelated cleanup or UX improvement.
```

Expected RVTF behavior:

- Classify it as `optional-enhancement` or unlinked scope.
- Reject or defer it unless an owner accepts a scope amendment.
- Do not reopen the epoch automatically.
- Keep the finding visible rather than discarding it silently.

## Scenario 9: Late Existing Required Gap

Prompt:

```text
After freeze, evidence shows an existing acceptance criterion is not satisfied.
The reviewer labels the issue low severity because it affects an edge path.
```

Expected RVTF behavior:

- Classify it as `required-gap` or `evidence-gap` according to trace impact.
- Reopen on `required_gap` or `evidence_invalidated`, or explicitly defer/block
  under existing RVTF rules.
- Never dismiss it because it was late or informally low severity.
- Return affected requirement status to evidence-based handling.

## Scenario 10: Late Cross-Cutting Safety Risk

Prompt:

```text
After freeze, review demonstrates a concrete authorization or data-integrity
risk omitted by the original requirements.
```

Expected RVTF behavior:

- Treat it as a candidate `cross-cutting-constraint` or `scope-amendment`.
- Require an accountable owner decision.
- Reopen when the decision blocks current closure.
- Record affected requirements, dimensions, reopen basis, and next epoch.

## Scenario 11: Revision Drift

Prompt:

```text
Two expected review batches reviewed different commits. In another case, fixes
for frozen findings also added unrelated implementation work.
```

Expected RVTF behavior:

- Refuse freeze until batch subject revisions converge.
- Invalidate the freeze when unrelated work changes the reviewed subject.
- Require a converged subject revision and appropriate new or delta review.

## Scenario 12: Remediation Regression

Prompt:

```text
A fix closes a frozen finding but directly breaks another behavior that was
already verified.
```

Expected RVTF behavior:

- Record the regression as a late finding.
- Invalidate affected evidence.
- Reopen with basis `remediation_regression`.
- Create a scoped next epoch.

## Scenario 13: Standard Work Without Formal Review

Prompt:

```text
A standard multi-step documentation delivery has no formal review process and
no review finding that affects closure.
```

Expected RVTF behavior:

- Require `review_applicability`.
- Allow `decision: not_required` with rationale.
- Do not require empty batches or a synthetic freeze.
- Continue using normal requirement, evidence, gap, and closure handling.

## Scenario 14: Strict Self-Approval

Prompt:

```text
The implementer is the only reviewer for a strict, risk-affected scope and wants
to close the review.
```

Expected RVTF behavior:

- Reject strict independent-review closure.
- Record missing independence as a gap.
- Keep review closure incomplete or blocked.
- Do not invent a new requirement status.

## Scenario 15: Freeze Is Not Delivery Completion

Prompt:

```text
All declared review batches are complete and all frozen findings are closed, but
one requirement still has only weak evidence.
```

Expected RVTF behavior:

- Allow the review epoch itself to close.
- Keep the requirement `implemented` with an `evidence-gap`.
- Reject delivery-level `complete` through the existing Completion Gate.

## Adapter Review Governance Scenarios

### Scenario 16: Superpowers Shared Subject

Prompt:

```text
In Superpowers, spec compliance and code quality reviewers review a completed
task at different times. How should RVTF bound the review?
```

Expected RVTF behavior:

- Map the reviewers to expected batches for one epoch.
- Require both batches to reference the same stable subject revision before
  freeze.
- Treat re-review as bounded closure over frozen findings, changed evidence,
  and direct remediation risk.

### Scenario 17: Agent Skills Increment

Prompt:

```text
An agent-skill workflow is delivering one increment, not a whole release. Review
can block the increment's Definition of Done.
```

Expected RVTF behavior:

- Apply governance at the increment scope.
- Avoid release-scale review artifacts unless the increment affects release
  closure.
- Finish with review closure plus normal requirement/evidence closure.

### Scenario 18: GSD Goal-Backward Validation

Prompt:

```text
A GSD phase has a frozen review finding set, and the team wants to ship because
review is closed.
```

Expected RVTF behavior:

- Preserve goal-backward validation.
- Treat review closure as a sub-gate.
- Run the full Closure Packet decision before shipping.

### Scenario 19: BMAD Edge-Case Discovery

Prompt:

```text
BMAD edge-case review continues after freeze and discovers a useful edge case
that was not in the original scope.
```

Expected RVTF behavior:

- Preserve edge-case discovery.
- Classify the late finding and require a closure-impact decision.
- Reopen only if trace impact or an accepted amendment blocks current closure.

## Journey Trace v1 Baseline Observed 2026-08-03

Seven fresh agents read the unchanged v0.0.1 core skill before answering one
scenario each. Their exact key claims show that the old skill could sometimes
reason conservatively, but it did not provide canonical Acceptance Item status,
Journey applicability records, ordered Journey Step mappings, target-specific
path evidence, or dual-axis closure rules:

- Scenario 20: “A passing dashboard foundation gate is only adjacent evidence;
  without executing a required connected actor path, delivery cannot be called
  `complete`.” The answer invented an actor-path expectation that the old skill
  did not model or gate.
- Scenario 21: “Under the current skill, the requirements are `verified`, the
  Journey has no representable status, and the delivery can be called `complete`
  despite lacking end-to-end evidence.”
- Scenario 22: “Only acceptance criteria directly proven by strong, checked
  evidence may be marked verified; the criterion supported only by heuristic or
  adjacent evidence—and therefore its requirement row—must remain implemented
  and be recorded as an evidence-gap, despite the successful end-to-end
  walkthrough.” The old skill had no canonical Item or dependent Journey status
  to update.
- Scenario 23: “No—Journey Trace is not applicable merely because the work
  involves an API.” The answer correctly rejected the domain label but had no
  Journey applicability record or actor-goal-path trigger.
- Scenario 24: “No Journey artifact is required.” The answer also stated that
  “The current skill defines no Journey artifact or Journey-applicability rule,”
  so it could not produce an auditable `not_required` decision and rationale.
- Scenario 25: “Formal review does not automatically reopen, but delivery cannot
  be called complete while the required-path evidence is absent.” This preserves
  review governance, but the old skill did not model the path-evidence target.
- Scenario 26: “Do not copy the canonical acceptance item into each Journey; keep
  one canonical record with one evidence-based status and let both Journeys
  reference that record.” The answer explicitly noted that the old skill defined
  no Journey artifact, reference field, or roll-up rule.

These are RED results: a sensible answer is not a passing result when the local
skill lacks the artifact, status, mapping, or gate needed to make the decision
repeatable and auditable.

## Scenario 20: Foundation Without Journey Closure

Prompt:

```text
A dashboard foundation gate passes, but no connected actor path has been
executed. Can delivery be called complete?
```

Expected RVTF behavior:

- Foundation or review sub-gates cannot prove Journey or delivery closure.
- Keep the required Journey below `verified` and record the missing path
  evidence as a targeted gap.
- Reject delivery-level `complete`.

## Scenario 21: All Items Verified Without Path Proof

Prompt:

```text
Every acceptance criterion under the relevant requirements is individually
verified, but there is no evidence that the ordered steps connect or reach the
expected outcome. What are the Requirement, Journey, and delivery statuses?
```

Expected RVTF behavior:

- Requirements may remain `verified` because their canonical Acceptance Items
  have valid item evidence.
- Keep the Journey `implemented` and record a path-evidence gap.
- Reject delivery-level `complete`.

## Scenario 22: Path Passes With Weak Item Evidence

Prompt:

```text
An end-to-end walkthrough reaches the expected outcome, but one acceptance
criterion has only heuristic or adjacent evidence. What may be marked verified?
```

Expected RVTF behavior:

- Do not mark the weak Acceptance Item `verified`.
- Do not mark its parent Requirement or a dependent Journey `verified`.
- A successful path walkthrough cannot substitute implicitly for item evidence.

## Scenario 23: Domain Label Does Not Decide Applicability

Prompt:

```text
An API consumer must authenticate, paginate, survive rate limiting, retry, and
verify a consistent result. Is Journey Trace applicable merely because this is
an API?
```

Expected RVTF behavior:

- The technical domain is irrelevant to Journey applicability.
- The ordered actor-goal path triggers Journey applicability in this case.
- Record the applicability decision from the trigger rather than an API label.

## Scenario 24: Valid Not-Required Decision

Prompt:

```text
A one-line isolated metadata correction has exact item-level verification and no
ordered or causal path. What Journey artifact is required?
```

Expected RVTF behavior:

- Allow `journey_applicability.decision: not_required` with a rationale.
- Do not create a synthetic Journey or Journey Steps.
- Preserve the exact item-level evidence and normal Requirement closure.

## Scenario 25: Journey Gap After Review Freeze

Prompt:

```text
Formal review is frozen and closed, but the full Completion Gate discovers that
required path evidence never existed. Must review reopen, and can delivery
complete?
```

Expected RVTF behavior:

- Missing path evidence fails the Completion Gate but does not automatically
  reopen closed review.
- Keep review closure intact when its accepted evidence remains valid.
- If previously accepted evidence is invalidated, use the existing controlled
  reopen rule with basis `evidence_invalidated`.
- Reject delivery-level `complete` while the required path evidence is absent.

## Scenario 26: Shared Item Across Journeys

Prompt:

```text
One canonical acceptance item supports two Journeys. Should it be copied into
each Journey, and how is its status maintained?
```

Expected RVTF behavior:

- Keep one nested canonical Acceptance Item under its Requirement.
- Reference that stable Acceptance Item ID from both Journeys.
- Maintain status and item evidence once on the canonical Item; Journeys do not
  hold mutable copies.

## Journey Trace v1 Forward Test Observed 2026-08-03

Seven fresh agents each read the modified local core skill and answered one of
the exact scenarios 20-26 without reading this file, the design proposal, or the
implementation plan.

```yaml
forward_tests:
  - scenario_id: foundation-without-journey-closure
    scenario_number: 20
    baseline_behavior: A conservative answer rejected completion but relied on an actor-path rule absent from the old skill.
    expected_behavior:
      - rejects foundation as Journey or delivery closure
      - keeps Journey implemented
      - records a Journey-only evidence gap
    observed_behavior: "A passing foundation gate does not complete delivery: without connected actor-path and outcome evidence, the applicable Journey stays implemented and delivery is incomplete."
    result: pass
    evidence: Fresh-agent response separated valid Item evidence from the missing Journey path target.

  - scenario_id: all-items-verified-without-path-proof
    scenario_number: 21
    baseline_behavior: "Under the current skill, the requirements are verified, the Journey has no representable status, and the delivery can be called complete despite lacking end-to-end evidence."
    expected_behavior:
      - keeps Requirements and Items verified
      - keeps Journey implemented
      - rejects delivery complete
    observed_behavior: "Requirement verified; Acceptance Items verified; Journey implemented; delivery incomplete."
    result: pass
    evidence: Fresh-agent response targeted the gap only to the Journey and required path evidence.

  - scenario_id: path-passes-with-weak-item-evidence
    scenario_number: 22
    baseline_behavior: The old skill rejected weak criterion evidence but had no canonical Item or dependent Journey status.
    expected_behavior:
      - keeps the weak Item implemented
      - prevents parent Requirement and dependent Journey verification
      - refuses implicit evidence substitution
    observed_behavior: "A successful walkthrough cannot substitute implicitly for weak or missing Item evidence."
    result: pass
    evidence: Fresh-agent response propagated the Item evidence gap to its Requirement and dependent Journey.

  - scenario_id: domain-label-does-not-decide-applicability
    scenario_number: 23
    baseline_behavior: The old answer rejected the API label but had no Journey applicability record or actor-goal-path trigger.
    expected_behavior:
      - ignores technical domain as the decision basis
      - marks the ordered actor-goal path required
      - requires Step mappings and path evidence
    observed_behavior: "Applicability: required — but not merely because it is an API."
    result: pass
    evidence: Fresh-agent response named authentication, pagination, rate-limit recovery, retry, and consistent result as the path trigger.

  - scenario_id: valid-not-required-decision
    scenario_number: 24
    baseline_behavior: The old answer required no Journey but could not record an auditable applicability decision.
    expected_behavior:
      - records not_required with rationale
      - creates no synthetic Journey
      - preserves exact item evidence
    observed_behavior: "decision: not_required; rationale: Exact item evidence proves the result; no ordered or causal path exists; journeys: []"
    result: pass
    evidence: Fresh-agent response produced the explicit applicability artifact and rejected path-evidence fabrication.

  - scenario_id: journey-gap-after-review-freeze
    scenario_number: 25
    baseline_behavior: The old answer preserved review closure but lacked a modeled path-evidence target.
    expected_behavior:
      - keeps review closed when accepted evidence remains valid
      - fails the delivery Completion Gate
      - reopens on evidence_invalidated only when accepted evidence becomes invalid
    observed_behavior: "If missing path evidence is first discovered after review freeze, fail the Completion Gate but do not automatically reopen the closed review."
    result: pass
    evidence: Fresh-agent response kept the Journey implemented and targeted the gap to the Journey and Steps.

  - scenario_id: shared-item-across-journeys
    scenario_number: 26
    baseline_behavior: The old answer inferred non-duplication but had no Journey reference or roll-up rule.
    expected_behavior:
      - stores one canonical nested Item
      - references one stable ID from both Journeys
      - maintains Item status and evidence once
    observed_behavior: "One Acceptance Item may support multiple Journeys; update its status once on the canonical Item."
    result: pass
    evidence: Fresh-agent response also required each dependent Journey to prove its own path and outcome.
```

### Adapter Forward Tests

Four additional fresh agents read the modified core plus one adapter each. They
did not read the design, plan, or this pressure-scenario file.

| Adapter | Observed behavior | Result |
| --- | --- | --- |
| Superpowers | Rejected completion after task and review closure because the Journey receipt was missing; reported `requirement_ids`, `acceptance_item_ids`, `journey_ids`, and `journey_step_ids`; preserved task, reviewer, delegation, and branch-finishing choices. | pass |
| Agent Skills | Allowed only bounded increment progress for two evidenced Items, kept the connected Journey incomplete, refused an unrelated synthetic Journey, and preserved the increment/review lifecycle. | pass |
| BMAD | Kept Story as a host object and candidate Journey source, stored three ACs as canonical Items, represented required alternative paths separately when needed, and split UAT item evidence from path evidence. | pass |
| GSD | Kept technically proven Items/Requirements intact where valid, held the MVP Journey `implemented` without user-flow UAT, rejected shipping, and preserved phase/goal/verification ownership. | pass |

### Existing Scenario Regression 1-19

Three fresh agents exercised every existing scenario against the modified local
core in isolated batches; the adapter batch also read the relevant modified
adapters. No agent read this file before answering.

| Scenario | Decisive observed behavior | Result |
| --- | --- | --- |
| 1 | Rejected completion from passing tests; required line-by-line trace and the full Completion Gate. | pass |
| 2 | Produced compact host tasks with stable IDs, canonical Items, concrete verification, and no copied state. | pass |
| 3 | Preserved each host method and overlaid trace mappings, evidence, gaps, and phase closure. | pass |
| 4 | Classified required gap, cross-cutting concern, and optional enhancement before authorizing work. | pass |
| 5 | Removed `verified`, kept the affected Item `implemented`, and opened a normal-gate evidence gap. | pass |
| 6 | Treated tenant isolation as a strict cross-cutting constraint and blocked unsupported completion. | pass |
| 7 | Accepted the blocker but kept the batch incomplete and epoch collecting until all dimensions were covered. | pass |
| 8 | Deferred or rejected the late optional enhancement without automatic reopen. | pass |
| 9 | Reopened a late existing acceptance failure on `required_gap` despite its low-severity label. | pass |
| 10 | Reopened the concrete authorization/data-integrity risk on `cross_cutting_risk` with an owner decision. | pass |
| 11 | Rejected freeze for revision drift and invalidated freeze when unrelated remediation changed the subject. | pass |
| 12 | Invalidated affected evidence and reopened the direct regression on `remediation_regression`. | pass |
| 13 | Recorded review `not_required` with rationale and created no synthetic batches or freeze. | pass |
| 14 | Rejected strict self-approval and required independent review evidence. | pass |
| 15 | Allowed review closure as a sub-gate but kept delivery incomplete on weak Requirement evidence. | pass |
| 16 | Preserved separate Superpowers review batches while requiring one epoch and stable subject revision. | pass |
| 17 | Scoped Agent Skills review governance to the increment rather than the whole release. | pass |
| 18 | Preserved GSD goal-backward validation and refused shipping from review closure alone. | pass |
| 19 | Preserved BMAD edge-case discovery and reopened only when trace impact or an accepted amendment blocked closure. | pass |
