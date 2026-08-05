---
name: adapting-rvtf-to-agent-skills
description: Use when applying requirements-to-verification traceability to agent-skill planning, incremental implementation, doubt handling, code review, or definition-of-done practices.
---

# Adapting RVTF To Agent Skills

**REQUIRED BACKGROUND:** Use `tracing-requirements-to-verification`.

## Host Contract Snapshot

- Host repo/method: Agent Skills planning, `/build`, `/build auto`, `/review`,
  and `/ship`.
- Branch: `main`.
- Revision: `7829ffd90d973b6325f5f12f1b1226dcace74443`.

This mapping is pinned to that exact host revision. Re-audit it before use if
Agent Skills task, review, build, or ship behavior changes.

## Principle

Agent Skills provide execution habits. RVTF provides the Requirement, canonical Acceptance Item, Journey, evidence, gap, and closure objects those habits update. The host increment and review lifecycle remain authoritative for execution shape.

## Shared RVTF Boundary

Use the required core Skill's schema, gate, and review-governance references for
detailed fields and algorithms; this adapter only maps host boundaries.

- Use `goal`, `milestone`, and `unit` only for containment. Use
  `delivery_groups` with `execution_batch`, `verification_batch`, or
  `review_batch` for execution, verification, and review grouping. Closing a
  group or Unit never auto-closes its parent Milestone or Goal.
- Effective gates are the union of host-native mandatory gates and RVTF-required
  gates. Reused `evidence_claims[].validity.status: valid` never removes a
  fresh/full host gate or claims current tests pass; record `host_gate_status`
  and `current_test_status_claim` independently.
- Keep worker self-check, verification, and formal review distinct. Dimensions
  do not imply reviewer or batch count. Parent coverage remains
  `review_state: pending_at_parent` until an actual receipt exists. Preserve
  strict independence and required specialist or segregation-of-duties fan-out.
- Historical review subject revisions are immutable. Use assessed
  `review_coverage_carry_forward`, a delta review, or controlled reopen rather
  than rebinding an old batch.
- The Goal Continuation Contract is declarative: use one host authority and
  record `continuation_mode: durable_host|artifact_only|advisory`, locator,
  remaining scopes, and actual
  `execution_action: continue|stop|await_owner|host_boundary`. RVTF never invokes
  `/build`, `/review`, `/ship`, or a next task and never overrides the user or
  orchestrator.
- Any Agent Skills `/build`, `/review`, or `/ship` lifecycle outcome remains
  `host_status`; RVTF parent closure follows trace truth.

## Host Scope And Gate Mapping

- Map the plan or release objective to a Goal and a plan checkpoint/phase to a
  Milestone. Map the smallest independent thin vertical Task to a Unit. Only
  when one Task truly contains multiple independently closable increments may
  that Task be a Milestone and its increments Units; record the rationale.
- Focused RED/GREEN checks and increment checks are `worker` tier. Task
  completion still runs all host-required task gates: the full test suite and
  the build, plus E2E when required. Shared valid evidence may avoid an extra
  RVTF rerun but cannot skip any of these host-native gates.
- Place Journey evidence at the smallest scope that can claim the actor-goal
  outcome. Compose it at a parent only when the Journey truly crosses slices.
- `/review` pre-merge review is host-native mandatory and cannot be skipped by
  parent coverage.
- For non-trivial production-bound `/ship`, preserve the code-reviewer,
  security-auditor, and test-engineer as three host-native specialist batches,
  then preserve synthesis, the GO/NO-GO decision, and the rollback plan. GO
  closes only `ship_readiness`; it does not prove `deployed`,
  `post_launch_verified`, or release Goal closure.
- When both are recorded, preserve host severity separately from the RVTF
  finding classification; neither overwrites the other.

## Mapping

| Agent Skills area | RVTF addition |
| --- | --- |
| Planning and task breakdown | Convert goals into stable Requirement and Acceptance Item IDs; decide Journey applicability from actor-goal-path triggers; map each Unit to the applicable four trace ID types; record review applicability when review can block completion. |
| Thin vertical slices | A slice may cover one or more connected Journey Steps when a Journey is required, but a slice or increment does not create a Journey when no path trigger exists. |
| Incremental implementation | Each increment advances specific Acceptance Items and their parent Requirements from evidence; when it covers a required path, it also records Journey Step coverage and path/outcome evidence. |
| Doubt-driven development | Convert doubts into assumptions, blocked rows, or gap ledger entries. |
| Code review and quality | Classify findings before work; when governed review applies, record epoch, subject revision, batch coverage, limitations, and freeze decision. |
| Definition of Done | Done requires consistent Item-to-Requirement status, Journey path/outcome proof when applicable, review closure when required, and explicit decisions for deferred, blocked, or rejected objects. |

## Working Pattern

1. Start with the agent-skill workflow normally.
2. Add an RVTF Requirement/Acceptance Item trace and decide Journey applicability before implementation.
3. Map each increment using `requirement_ids`, `acceptance_item_ids`, `journey_ids`, and `journey_step_ids`; leave Journey fields empty when a justified applicability decision makes them unnecessary.
4. Update canonical Item and Requirement status after each increment. Update Journey status only from referenced Item status plus target-specific path evidence.
5. Convert every uncertainty into a tracked assumption or gap.
6. Convert new scope into approved amendments before implementation.
7. For reviewed increments, freeze findings only after declared dimensions are
   covered on the same subject revision.
8. End with review closure plus a dual-axis closure packet, not only a summary.

For ordinary `/build`, continuation is `artifact_only` or `advisory`: after one
Task, record the continuation contract with `execution_action: stop` and return
control. Only user-approved `/build auto` may record
`execution_action: continue` within the approved scope, and it must stop or await
the owner on host-defined ambiguity, failure, or risk. Task/increment closure
never implies release Goal closure.

## Anti-Pattern

Do not let a broad Definition of Done replace requirement-level evidence. A DoD can say the release is healthy; RVTF says which exact requirements were proven.

Do not let review findings become a shadow backlog. Link each finding to a requirement decision or reject/defer it explicitly.

Do not force release-scale review artifacts onto every small increment. Apply
bounded review governance at the smallest delivery scope whose review can change
the completion decision.

Do not force every increment to construct a Journey. Apply Journey Trace only
when acceptance depends on ordered or causally connected actor-observable Steps.
When it applies, distinguish item evidence from path evidence in the increment's
Definition of Done.
