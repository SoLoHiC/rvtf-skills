---
name: adapting-rvtf-to-agent-skills
description: Use when applying requirements-to-verification traceability to agent-skill planning, incremental implementation, doubt handling, code review, or definition-of-done practices.
---

# Adapting RVTF To Agent Skills

**REQUIRED BACKGROUND:** Use `tracing-requirements-to-verification`.

## Principle

Agent Skills provide execution habits. RVTF provides the Requirement, canonical Acceptance Item, Journey, evidence, gap, and closure objects those habits update. The host increment and review lifecycle remain authoritative for execution shape.

## Mapping

| Agent Skills area | RVTF addition |
| --- | --- |
| Planning and task breakdown | Convert goals into stable Requirement and Acceptance Item IDs; decide Journey applicability from actor-goal-path triggers; map each increment to the applicable four trace ID types; record review applicability when review can block completion. |
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
