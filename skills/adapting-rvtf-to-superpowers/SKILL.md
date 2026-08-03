---
name: adapting-rvtf-to-superpowers
description: Use when applying requirements-to-verification traceability to Superpowers workflows, including brainstorming, writing plans, subagent-driven development, review, verification, branch finishing, or skill writing.
---

# Adapting RVTF To Superpowers

**REQUIRED BACKGROUND:** Use `tracing-requirements-to-verification`.

## Principle

Do not replace Superpowers. Add RVTF as the evidence thread running through the existing Superpowers lifecycle. RVTF defines Requirement, canonical Acceptance Item, Journey, evidence, gap, and closure semantics; Superpowers still decides task grouping, implementer/reviewer roles, and whether or how to delegate work.

## Mapping

| Superpowers skill | RVTF addition |
| --- | --- |
| `superpowers:brainstorming` | Choose RVTF mode; define canonical Acceptance Items; decide Journey applicability from actor-goal-path triggers; when required, define actor, goal, expected outcome, and observable Steps. Also record requirement validity, constraints, assumptions, non-goals, and review applicability. |
| `superpowers:writing-plans` | Each task lists applicable Requirement, Acceptance Item, Journey, and Journey Step IDs, verification commands, planned item/path evidence, approved amendments, and any planned review contract. |
| `superpowers:subagent-driven-development` | Implementer reports state advanced Requirements, Acceptance Items, and Journeys; item and path evidence added; findings discovered; and gaps opened or closed. A task report never mutates copied Item state. |
| `superpowers:requesting-code-review` | Map spec compliance and code quality reviews to expected batches over one stable subject revision; require dimension coverage and limitations. |
| `superpowers:receiving-code-review` | Classify each comment before implementation; freeze only after expected batches are complete and subject revisions match. |
| `superpowers:verification-before-completion` | Treat re-review as bounded closure over frozen findings, changed evidence, and direct remediation risk, then run the full Completion Gate with explicit Item aggregation and Journey path/outcome proof. |
| `superpowers:finishing-a-development-branch` | Merge or PR options require review closure, a closure packet, amendment decisions, and explicit treatment of required gaps. |
| `superpowers:writing-skills` | Treat RVTF changes as process TDD: pressure scenario first, skill change second, forward-test third. |

## Prompt Additions

For every planned task, add the host mapping without changing Superpowers task
boundaries:

```yaml
requirement_ids: []
acceptance_item_ids: []
journey_ids: []
journey_step_ids: []
```

For implementer subagents, add:

```text
Track RVTF coverage. Report which Requirement, Acceptance Item, Journey, and
Journey Step IDs advanced; which item or path evidence was added; and which
gaps, review findings, or scope amendments need a decision. Do not infer a
verified parent or Journey from task completion.
```

For spec reviewers, add:

```text
Review Requirement and Acceptance Item IDs line by line. Do not approve based
only on task text, worker report, or passing tests. Every required Item needs
target-specific evidence or a gap decision. For each applicable Journey, check
Step-to-Item mapping plus path order, connection, and expected-outcome evidence.
Classify each review finding before recommending implementation.
If bounded review governance applies, report the review epoch subject revision,
assigned dimensions covered, dimensions with no findings, and limitations.
```

## Completion Rule

In Superpowers, "all tasks complete" and "review closed" are not the final
condition. The final condition is: all required Acceptance Items aggregate
consistently to their Requirements; every applicable Journey has valid path and
outcome evidence; all remaining objects have explicit dispositions; and any
governed review epoch is closed or has a controlled reopen, deferral, block, or
residual-risk decision.

## Review Feedback Rule

When using Superpowers review skills, no review finding becomes work until it is linked to an existing requirement, accepted scope amendment, or cross-cutting constraint. Optional improvements stay deferred or rejected unless an owner changes the scope.

Do not let remediation review become a fresh unrestricted review loop. After
freeze, review only frozen findings, changed evidence, and direct remediation
risk unless a late finding justifies controlled reopen through RVTF trace impact.
