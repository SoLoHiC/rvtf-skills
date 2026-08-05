---
name: adapting-rvtf-to-bmad
description: Use when applying requirements-to-verification traceability to BMAD specs, memlogs, adversarial reviews, edge-case reviews, verification-gap reviews, or preservation checks.
---

# Adapting RVTF To BMAD

**REQUIRED BACKGROUND:** Use `tracing-requirements-to-verification`.

## Host Contract Snapshot

- Host repo/method: BMAD Method Epic/SPEC, Story, Build/build-auto, review,
  triage, and orchestrator lifecycles.
- Branch: `main`.
- Revision: `116491165d850e9d074554c6271f452363bb607a`.

This mapping is pinned to that exact host revision. Re-audit it before use if
BMAD Story, Build, review/triage, or orchestrator behavior changes.

## Principle

BMAD is strong at spec preservation and gap review. RVTF supplies the canonical Requirement, Acceptance Item, Journey, evidence, gap, and decision records that BMAD reviews preserve and challenge. BMAD keeps its Story, build, review, and memlog lifecycle.

## Shared RVTF Boundary

Use the required core Skill's schema, gate, and review-governance references for
detailed fields and algorithms; this adapter only maps host boundaries.

- Use `goal`, `milestone`, and `unit` only for containment. Use
  `delivery_groups` with `execution_batch`, `verification_batch`, or
  `review_batch` for execution, verification, and review grouping. A Build run,
  group, or Story Unit completion never auto-closes a parent Epic/release.
- Effective gates are the union of host-native mandatory gates and RVTF-required
  gates. Reused `evidence_claims[].validity.status: valid` never removes a
  fresh/full host gate or claims current tests pass; keep `host_gate_status` and
  `current_test_status_claim` separate.
- Distinguish worker self-check, verification, and formal review. Dimensions do
  not imply reviewer or batch count. Parent coverage remains
  `review_state: pending_at_parent` until an actual receipt exists. Preserve
  strict independence and required specialist or segregation-of-duties fan-out.
- Keep historical review subject revisions immutable. Use assessed
  `review_coverage_carry_forward`, delta review, or controlled reopen instead of
  rebinding a prior batch.
- The Goal Continuation Contract is declarative: use one host authority and
  record `continuation_mode: durable_host|artifact_only|advisory`, locator,
  remaining scopes, and actual
  `execution_action: continue|stop|await_owner|host_boundary`. RVTF never invokes
  another Build or Story and never overrides user/orchestrator control.
- BMAD `done`, `shipped`, `archived`, or `override` remains `host_status`; RVTF
  closure follows trace truth.

## Host Scope, Gate, And Review Mapping

- Map an Epic or SPEC scope to a Goal or Milestone according to its actual
  closure boundary. Map Story to Unit. A Build run is an execution record
  attached to that Story, not a new Build Unit. Story Acceptance Criteria remain
  the canonical Acceptance Items.
- Every Build/build-auto run's review and triage is host-native mandatory and
  cannot be skipped by Epic/Milestone parent coverage or evidence reuse.
- Map adversarial, edge-case, and verification-gap review to dimensions. Do not
  multiply them into batches unless actual host roles, specialist risk, strict
  independence, or segregation of duties requires fan-out.
- One build-auto invocation handles one Story/run. Story closure never closes an
  Epic/release; the orchestrator owns backlog order, next Story selection, and
  blocked routing.
- Derive continuation from the Build spec terminal status, deferred findings,
  and one orchestrator authority/reference. At the command boundary it is
  normally `artifact_only` or `advisory` with `execution_action: stop` or
  `host_boundary`; return control rather than scheduling the next Story.
- BMAD `done` changes `host_status` only and never promotes a parent RVTF scope
  to complete.

## Mapping

| BMAD area | RVTF addition |
| --- | --- |
| Spec kernel | Store capability tree, Requirement IDs, canonical Acceptance Items, Journey applicability, required Journeys and Steps, verification methods, validity decisions, constraints, non-goals, and review contract when formal review can affect closure. |
| Story | Treat a Story as a candidate Journey source, not an automatic Journey. Map Story acceptance criteria to canonical Acceptance Items and decide Journey applicability from the actual actor-goal path. |
| Build-auto Tasks & Acceptance | Attach the Build execution record to its Story Unit and map its work to Requirement, Acceptance Item, Journey, and Journey Step IDs. Use the I/O & Edge-Case Matrix to expose Item criteria and required alternative or recovery Steps without copying Item state. |
| UAT and edge-case execution | Record target-specific item evidence and, when the executed flow proves ordered Steps and expected outcome, explicit path evidence with covered Journey Step IDs. |
| Append-only memlog | Record Item, Requirement, and Journey status changes; item/path evidence; Journey applicability; review lifecycle; finding classifications; amendment decisions; and gaps as append-only events. |
| Review verification gap | Classify each gap against requirement ID, evidence quality, adoption, regression, verification method, or scope amendment. |
| Adversarial review | Attack unsupported `verified` claims, untraced extra scope, optional review findings that became work without approval, and incomplete review-batch coverage. |
| Edge-case hunter | Create missing acceptance criteria, candidate constraints, scope amendments, or gap entries for uncovered edge cases; late discoveries still need controlled closure-impact decisions. |
| Preservation validation | Check that later plans preserve canonical Item IDs/status, Journey/Step mappings, item/path evidence, gap targets, Requirement decisions, amendments, and review epoch decisions. |

## BMAD Review Add-On

Use this prompt in BMAD reviews:

```text
Review the RVTF trace matrix and gap ledger. Find Requirements or Acceptance
Items without evidence, evidence that does not prove its declared Item or
Journey target, Journeys whose ordered Steps or expected outcome are unproven,
untraced scope, review findings that were implemented without classification,
lost deferred gaps, status changes not supported by the memlog, review batches
that omit assigned dimensions, and remediation changes outside the frozen
finding set.
```

## Completion Rule

BMAD can challenge whether the story stayed intact. RVTF defines the rows and evidence BMAD should challenge.

Attach this mapping to the relevant Story or build task while preserving BMAD's
own grouping:

```yaml
requirement_ids: []
acceptance_item_ids: []
journey_ids: []
journey_step_ids: []
```

Story completion does not auto-verify its Acceptance Items or any candidate
Journey. UAT can support both evidence axes only when its records separately name
the Item criterion and the covered Step order/outcome claims.

When BMAD discovers a new edge case, do not treat it as automatic work. Record whether it is a required gap, candidate cross-cutting constraint, accepted amendment, optional enhancement, or rejected extra.

Freeze does not suppress edge-case discovery. It controls whether a late edge
case reopens current delivery, becomes an amendment, is deferred, or is rejected
outside the current closure decision.
