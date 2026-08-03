---
name: adapting-rvtf-to-bmad
description: Use when applying requirements-to-verification traceability to BMAD specs, memlogs, adversarial reviews, edge-case reviews, verification-gap reviews, or preservation checks.
---

# Adapting RVTF To BMAD

**REQUIRED BACKGROUND:** Use `tracing-requirements-to-verification`.

## Principle

BMAD is strong at spec preservation and gap review. RVTF supplies the canonical Requirement, Acceptance Item, Journey, evidence, gap, and decision records that BMAD reviews preserve and challenge. BMAD keeps its Story, build, review, and memlog lifecycle.

## Mapping

| BMAD area | RVTF addition |
| --- | --- |
| Spec kernel | Store capability tree, Requirement IDs, canonical Acceptance Items, Journey applicability, required Journeys and Steps, verification methods, validity decisions, constraints, non-goals, and review contract when formal review can affect closure. |
| Story | Treat a Story as a candidate Journey source, not an automatic Journey. Map Story acceptance criteria to canonical Acceptance Items and decide Journey applicability from the actual actor-goal path. |
| Build-auto Tasks & Acceptance | Map host tasks to Requirement, Acceptance Item, Journey, and Journey Step IDs. Use the I/O & Edge-Case Matrix to expose Item criteria and required alternative or recovery Steps without copying Item state. |
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
