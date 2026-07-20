---
name: adapting-rvtf-to-superpowers
description: Use when applying requirements-to-verification traceability to Superpowers workflows, including brainstorming, writing plans, subagent-driven development, review, verification, branch finishing, or skill writing.
---

# Adapting RVTF To Superpowers

**REQUIRED BACKGROUND:** Use `tracing-requirements-to-verification`.

## Principle

Do not replace Superpowers. Add RVTF as the evidence thread running through the existing Superpowers lifecycle.

## Mapping

| Superpowers skill | RVTF addition |
| --- | --- |
| `superpowers:brainstorming` | Choose RVTF mode; add requirement validity, cross-cutting constraints, assumptions, and non-goals to the design doc. |
| `superpowers:writing-plans` | Each task must list covered requirement IDs, verification commands, and any approved scope amendments. |
| `superpowers:subagent-driven-development` | Implementer reports must include requirement IDs advanced, evidence quality, findings discovered, and gaps found. |
| `superpowers:requesting-code-review` | Run requirement coverage and review-finding-intake checks before code quality review. |
| `superpowers:receiving-code-review` | Classify each comment before implementation; do not treat review feedback as automatic scope. |
| `superpowers:verification-before-completion` | Completion claims require fresh, strong evidence for each verified requirement ID. |
| `superpowers:finishing-a-development-branch` | Merge or PR options require a closure packet, amendment decisions, and explicit treatment of required gaps. |
| `superpowers:writing-skills` | Treat RVTF changes as process TDD: pressure scenario first, skill change second, forward-test third. |

## Prompt Additions

For implementer subagents, add:

```text
Track RVTF coverage. Report which requirement IDs were implemented, which were
verified, what evidence was added, and which gaps, review findings, or scope
amendments need a decision.
```

For spec reviewers, add:

```text
Review requirement IDs line by line. Do not approve based only on task text,
worker report, or passing tests. Every required ID needs evidence or a gap decision.
Classify each review finding before recommending implementation.
```

## Completion Rule

In Superpowers, "all tasks complete" is not the final condition. The final condition is: all required RVTF rows are verified, deferred, blocked, or rejected with evidence and rationale.

## Review Feedback Rule

When using Superpowers review skills, no review finding becomes work until it is linked to an existing requirement, accepted scope amendment, or cross-cutting constraint. Optional improvements stay deferred or rejected unless an owner changes the scope.
