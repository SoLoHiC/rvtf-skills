---
name: adapting-rvtf-to-bmad
description: Use when applying requirements-to-verification traceability to BMAD specs, memlogs, adversarial reviews, edge-case reviews, verification-gap reviews, or preservation checks.
---

# Adapting RVTF To BMAD

**REQUIRED BACKGROUND:** Use `tracing-requirements-to-verification`.

## Principle

BMAD is strong at spec preservation and gap review. RVTF supplies the canonical requirement rows that BMAD reviews preserve and challenge.

## Mapping

| BMAD area | RVTF addition |
| --- | --- |
| Spec kernel | Store capability tree, requirement IDs, acceptance criteria, verification methods, validity decisions, constraints, non-goals, and review contract when formal review can affect closure. |
| Append-only memlog | Record requirement status changes, evidence additions, review applicability, batch coverage, freeze, remediation, reopen, finding classifications, amendment decisions, and gap decisions as append-only events. |
| Review verification gap | Classify each gap against requirement ID, evidence quality, adoption, regression, verification method, or scope amendment. |
| Adversarial review | Attack unsupported `verified` claims, untraced extra scope, optional review findings that became work without approval, and incomplete review-batch coverage. |
| Edge-case hunter | Create missing acceptance criteria, candidate constraints, scope amendments, or gap entries for uncovered edge cases; late discoveries still need controlled closure-impact decisions. |
| Preservation validation | Check that later plans preserve prior requirement decisions, amendment decisions, review epoch decisions, and gap ledger entries. |

## BMAD Review Add-On

Use this prompt in BMAD reviews:

```text
Review the RVTF trace matrix and gap ledger. Find requirements without evidence,
evidence that does not prove the stated acceptance criterion, untraced scope,
review findings that were implemented without classification, lost deferred gaps,
status changes not supported by the memlog, review batches that omit assigned
dimensions, and remediation changes outside the frozen finding set.
```

## Completion Rule

BMAD can challenge whether the story stayed intact. RVTF defines the rows and evidence BMAD should challenge.

When BMAD discovers a new edge case, do not treat it as automatic work. Record whether it is a required gap, candidate cross-cutting constraint, accepted amendment, optional enhancement, or rejected extra.

Freeze does not suppress edge-case discovery. It controls whether a late edge
case reopens current delivery, becomes an amendment, is deferred, or is rejected
outside the current closure decision.
