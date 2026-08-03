---
name: adapting-rvtf-to-gsd
description: Use when applying requirements-to-verification traceability to GSD planning, plan review, phase validation, verification, shipping, convergence, or gap-control workflows.
---

# Adapting RVTF To GSD

**REQUIRED BACKGROUND:** Use `tracing-requirements-to-verification`.

## Principle

GSD is strong at goal convergence. RVTF makes the convergence auditable by turning goals, canonical Acceptance Items, actor Journeys, evidence, and gaps into traceable decisions. GSD retains its phase, goal, plan, verification, and shipping lifecycle.

## Mapping

| GSD concern | RVTF addition |
| --- | --- |
| Plan completeness is not goal achievement | Require evidence for each Requirement and canonical Acceptance Item before completion. |
| Task completion is not goal achievement | Close tasks only as implementation progress; update Items and Requirements from item evidence and Journeys from referenced Items plus path evidence. |
| Existence is not integration | Add integration Acceptance Items and, when an actor-goal path exists, Journey Steps with ordered path/outcome verification. |
| MVP user flow | Map the user flow to an Actor Journey and its observable Steps when path triggers apply; map GSD user-story acceptance to canonical Acceptance Items. |
| Non-MVP phase | Keep phase/goal as the host axis and decide Journey applicability from general path triggers rather than forcing a user flow. |
| Phase plan | Map each plan/task to `requirement_ids`, `acceptance_item_ids`, `journey_ids`, and `journey_step_ids`. |
| Review findings can inflate scope | Classify findings and require accepted amendments before new work. |
| Multiple phase reviews can drip new blockers | Declare review applicability, contract expected batches, and freeze only after covered dimensions share one subject revision. |
| Evidence can be weak | Check evidence quality before marking rows verified. |
| Cross-agent plan convergence | Compare plans by requirement-ID coverage, not by similar task wording. |
| Cross-cutting constraints | Track safety, privacy, compatibility, migration, and regression constraints as rows. |
| Goal-backward verification | Align the phase goal with Journey `expected_outcome`, walk backward through path evidence and Steps to canonical Items, then inspect item evidence; review freeze never replaces this walk. |
| Phase verification | Report Item evidence gaps separately from Journey path gaps, propagate each only to affected objects, and reject dual-axis closure when either required axis is open. |
| Shipping | Ship only with review closure when applicable, a closure packet, and gap ledger decisions. |

## GSD Gate Add-On

When running a GSD validation or ship review, ask:

```text
Which Requirement and Acceptance Item IDs prove the goal is achieved?
Which Items only have implementation but no target-specific evidence?
When Journey Trace applies, which Journey and Step IDs represent the MVP or
system flow, and what path evidence proves order and expected outcome?
Which verified Items or Journeys rely on weak or out-of-gate evidence?
Which review findings are required gaps, amendments, optional extras, or constraints?
If formal review applies, which review epoch, subject revision, dimensions, and
batches prove the declared review surface was traversed?
Which gaps are being carried forward, and where are they owned?
What extra work was done without a requirement?
```

## Completion Rule

GSD may decide whether a phase is fit to move forward. RVTF supplies the evidence basis for that decision.

Use `discovery` mode for goal exploration, but switch to `standard` or `strict` before a completion or ship decision.

If bounded review governance applies, a closed review epoch is only a sub-gate.
Run the full goal-backward Closure Packet decision before shipping or advancing
the phase. The packet must enforce Item-to-Requirement aggregation and list
Journey path gaps separately from Item evidence gaps.
