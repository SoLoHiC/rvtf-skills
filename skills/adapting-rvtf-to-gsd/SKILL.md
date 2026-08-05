---
name: adapting-rvtf-to-gsd
description: Use when applying requirements-to-verification traceability to GSD planning, plan review, phase validation, verification, shipping, convergence, or gap-control workflows.
---

# Adapting RVTF To GSD

**REQUIRED BACKGROUND:** Use `tracing-requirements-to-verification`.

## Host Contract Snapshot

- Host repo/method: GSD Core project/milestone/phase/PLAN execution,
  verification, UAT, and ship lifecycles.
- Branch: `next`.
- Revision: `b5ce72f72992e46b31c2b02c8275cdd858a8fdce`.

This mapping is pinned to that exact host revision. Re-audit it before use if
GSD planning, Wave, verifier, review, or `.planning` authority changes.

## Principle

GSD is strong at goal convergence. RVTF makes the convergence auditable by turning goals, canonical Acceptance Items, actor Journeys, evidence, and gaps into traceable decisions. GSD retains its phase, goal, plan, verification, and shipping lifecycle.

## Shared RVTF Boundary

Use the required core Skill's schema, gate, and review-governance references for
detailed fields and algorithms; this adapter only maps host boundaries.

- Use `goal`, `milestone`, and `unit` only for containment. Use
  `delivery_groups` with `execution_batch`, `verification_batch`, or
  `review_batch` for execution, verification, and review grouping. A Wave/group
  or child Unit completion never auto-closes a Phase Milestone or parent Goal.
- Effective gates are the union of host-native mandatory gates and RVTF-required
  gates. A reused `evidence_claims[].validity.status: valid` claim never removes
  a fresh/full host gate or claims current tests pass; keep `host_gate_status`
  and `current_test_status_claim` separate.
- Keep self-check, verification, and formal review distinct. Dimensions do not
  imply batch count. Parent coverage remains
  `review_state: pending_at_parent` until actual review. Preserve strict independence
  and required specialist or segregation-of-duties fan-out.
- Review batch subject revisions are immutable. Cross-revision coverage needs
  assessed `review_coverage_carry_forward`; otherwise use delta review or
  controlled reopen.
- The Goal Continuation Contract is declarative: use one host authority and
  record `continuation_mode: durable_host|artifact_only|advisory`, locator,
  remaining scopes, and actual
  `execution_action: continue|stop|await_owner|host_boundary`. RVTF never invokes
  a GSD command/PLAN or overrides user/orchestrator control.
- Any GSD host lifecycle outcome, including `override_closeout`, remains
  `host_status`; RVTF closure is derived independently.

## Host Hierarchy And Grouping

- GSD Project is the host container. Map the current GSD Milestone to an RVTF
  Goal, GSD Phase to Milestone, and GSD PLAN to Unit. PLAN Tasks are internal
  Unit checkpoints, not delivery scopes.
- Map an execute-phase Wave through `delivery_groups` as an
  `execution_batch`; it groups PLAN Units without becoming their parent.
- Map `worker` to PLAN Task/focused checks and PLAN overall verification;
  `batch` to Wave post-merge build, tests, and hooks; `milestone` to the Phase
  verifier/`VERIFICATION` plus UAT where required; and `completion` to the GSD
  milestone audit/readiness decision. Child claims are inputs, never permission
  to skip the host Phase verifier.

## Host Review And Continuation

- Preserve the pinned split: the plan checker retains its host gate;
  capability-dependent execute-phase code review is advisory, and its failure
  does not block execution at this revision; PR review remains host-directed.
  Only separately declared blocking hooks or contracts may block. Add another
  formal RVTF review only when the actual risk contract requires it.
- GSD goal-backward verification remains authoritative. Phase closure records
  the unresolved truth of the parent Goal rather than promoting it to complete.
- Derive `durable_host` continuation from `.planning` `STATE`, `ROADMAP`, `PLAN`,
  `SUMMARY`, `VERIFICATION`, `UAT`, and `HANDOFF` under the orchestrator's
  single-authority, single-writer, and lock rules. RVTF creates no parallel state
  source; the orchestrator, not parallel workers, updates shared continuation.
- `override_closeout` changes only `host_status`. A blocked or incomplete scope
  stays RVTF blocked/incomplete unless accepted deferral or residual-risk rules
  actually close it.

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
