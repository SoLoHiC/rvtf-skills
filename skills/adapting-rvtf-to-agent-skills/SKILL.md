---
name: adapting-rvtf-to-agent-skills
description: Use when applying requirements-to-verification traceability to agent-skill planning, incremental implementation, doubt handling, code review, or definition-of-done practices.
---

# Adapting RVTF To Agent Skills

**REQUIRED BACKGROUND:** Use `tracing-requirements-to-verification`.

## Principle

Agent Skills provide execution habits. RVTF provides the trace object those habits update.

## Mapping

| Agent Skills area | RVTF addition |
| --- | --- |
| Planning and task breakdown | Convert goals into capability tree nodes and stable requirement IDs; record review applicability for increments whose review can block completion. |
| Incremental implementation | Each increment moves specific requirement IDs from `pending` to `implemented` or `verified` using evidence quality. |
| Doubt-driven development | Convert doubts into assumptions, blocked rows, or gap ledger entries. |
| Code review and quality | Classify findings before work; when governed review applies, record epoch, subject revision, batch coverage, limitations, and freeze decision. |
| Definition of Done | Done requires review closure when applicable, verified rows, and explicit decisions for deferred, blocked, or rejected rows. |

## Working Pattern

1. Start with the agent-skill workflow normally.
2. Add an RVTF trace matrix before implementation.
3. Update the matrix after each increment.
4. Convert every uncertainty into a tracked assumption or gap.
5. Convert new scope into approved amendments before implementation.
6. For reviewed increments, freeze findings only after declared dimensions are
   covered on the same subject revision.
7. End with review closure plus a closure packet, not only a summary.

## Anti-Pattern

Do not let a broad Definition of Done replace requirement-level evidence. A DoD can say the release is healthy; RVTF says which exact requirements were proven.

Do not let review findings become a shadow backlog. Link each finding to a requirement decision or reject/defer it explicitly.

Do not force release-scale review artifacts onto every small increment. Apply
bounded review governance at the smallest delivery scope whose review can change
the completion decision.
