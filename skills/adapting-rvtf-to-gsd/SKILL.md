---
name: adapting-rvtf-to-gsd
description: Use when applying requirements-to-verification traceability to GSD planning, plan review, phase validation, verification, shipping, convergence, or gap-control workflows.
---

# Adapting RVTF To GSD

**REQUIRED BACKGROUND:** Use `tracing-requirements-to-verification`.

## Principle

GSD is strong at goal convergence. RVTF makes the convergence auditable by turning goals, claims, and gaps into traceable rows.

## Mapping

| GSD concern | RVTF addition |
| --- | --- |
| Plan completeness is not goal achievement | Require evidence for each requirement ID before completion. |
| Task completion is not goal achievement | Close tasks only as implementation progress; close requirements only from evidence. |
| Existence is not integration | Add integration acceptance criteria and verification rows. |
| Review findings can inflate scope | Classify findings and require accepted amendments before new work. |
| Multiple phase reviews can drip new blockers | Declare review applicability, contract expected batches, and freeze only after covered dimensions share one subject revision. |
| Evidence can be weak | Check evidence quality before marking rows verified. |
| Cross-agent plan convergence | Compare plans by requirement-ID coverage, not by similar task wording. |
| Cross-cutting constraints | Track safety, privacy, compatibility, migration, and regression constraints as rows. |
| Goal-backward verification | Start closure review from desired outcomes, then inspect evidence backward; review freeze never replaces this walk. |
| Shipping | Ship only with review closure when applicable, a closure packet, and gap ledger decisions. |

## GSD Gate Add-On

When running a GSD validation or ship review, ask:

```text
Which requirement IDs prove the goal is achieved?
Which IDs only have code but no evidence?
Which verified rows rely on weak or out-of-gate evidence?
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
the phase.
