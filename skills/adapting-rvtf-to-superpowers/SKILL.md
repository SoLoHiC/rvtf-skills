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
| `superpowers:brainstorming` | Choose RVTF mode; add requirement validity, cross-cutting constraints, assumptions, non-goals, and review applicability to the design doc. |
| `superpowers:writing-plans` | Each task must list covered requirement IDs, verification commands, approved scope amendments, and any review contract needed for planned formal review. |
| `superpowers:subagent-driven-development` | Implementer reports must include requirement IDs advanced, evidence quality, findings discovered, and gaps found. |
| `superpowers:requesting-code-review` | Map spec compliance and code quality reviews to expected batches over one stable subject revision; require dimension coverage and limitations. |
| `superpowers:receiving-code-review` | Classify each comment before implementation; freeze only after expected batches are complete and subject revisions match. |
| `superpowers:verification-before-completion` | Treat re-review as bounded closure over frozen findings, changed evidence, and direct remediation risk before the full Completion Gate. |
| `superpowers:finishing-a-development-branch` | Merge or PR options require review closure, a closure packet, amendment decisions, and explicit treatment of required gaps. |
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
If bounded review governance applies, report the review epoch subject revision,
assigned dimensions covered, dimensions with no findings, and limitations.
```

## Completion Rule

In Superpowers, "all tasks complete" and "review closed" are not the final
condition. The final condition is: all required RVTF rows are verified, deferred,
blocked, or rejected with evidence and rationale, and any governed review epoch
is closed or has a controlled reopen, deferral, block, or residual-risk decision.

## Review Feedback Rule

When using Superpowers review skills, no review finding becomes work until it is linked to an existing requirement, accepted scope amendment, or cross-cutting constraint. Optional improvements stay deferred or rejected unless an owner changes the scope.

Do not let remediation review become a fresh unrestricted review loop. After
freeze, review only frozen findings, changed evidence, and direct remediation
risk unless a late finding justifies controlled reopen through RVTF trace impact.
