#!/usr/bin/env python3
"""Validate the additive RVTF YAML examples and their semantic invariants."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

try:
    import yaml
except ModuleNotFoundError:
    print(
        "error: PyYAML is required by validate-schema-examples.py; install it "
        "for the interpreter selected by PYTHON_BIN (for example: "
        "\"$PYTHON_BIN\" -m pip install PyYAML).",
        file=sys.stderr,
    )
    raise SystemExit(2)


SUPPORTED_SCHEMA_VERSIONS = {"0.3.0", "0.4.0"}
SCOPE_KINDS = {"goal", "milestone", "unit"}
GROUP_KINDS = {"execution_batch", "verification_batch", "review_batch"}
TRACE_STATUSES = {"pending", "implemented", "verified", "deferred", "blocked", "rejected"}
CLOSURE_DISPOSITIONS = {
    "complete",
    "complete_with_deferred_gaps",
    "complete_with_residual_risk",
    "incomplete",
    "blocked",
    "invalid_requirements",
}
CLOSED_DISPOSITIONS = {
    "complete",
    "complete_with_deferred_gaps",
    "complete_with_residual_risk",
}
CLAIM_VALIDITY_STATUSES = {"valid", "stale", "invalidated", "unknown"}
CLAIM_TARGET_KINDS = {"acceptance_item", "journey"}
VERIFICATION_TIERS = {"worker", "batch", "milestone", "completion"}
REVIEW_CADENCES = {"unit", "batch", "milestone", "host_native"}
REVIEW_COMBINATION_POLICIES = {"combined_allowed", "separate_required", "host_native"}
CONTINUATION_MODES = {"durable_host", "artifact_only", "advisory"}
CONTINUATION_ACTIONS = {"continue", "stop", "await_owner", "host_boundary"}
STOP_BASES = {
    "goal_complete",
    "all_remaining_work_blocked",
    "owner_requested_stop",
    "host_runtime_boundary",
    "host_command_completed",
}
EXPECTED_ERROR_RE = re.compile(r"^# expected-error: ([a-z0-9][a-z0-9-]*)$")


@dataclass(frozen=True)
class Diagnostic:
    """One stable, sortable schema diagnostic."""

    code: str
    path: str
    message: str


def _diag(code: str, path: str, message: str) -> Diagnostic:
    return Diagnostic(code=code, path=path, message=message)


def _records(document: Mapping[str, Any], key: str) -> list[Mapping[str, Any]]:
    value = document.get(key, [])
    if not isinstance(value, list):
        return []
    return [record for record in value if isinstance(record, Mapping)]


def _index(records: Iterable[Mapping[str, Any]], key: str) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for record in records:
        value = record.get(key)
        if isinstance(value, str) and value:
            result.setdefault(value, record)
    return result


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item]


def _subject_revisions(record: Mapping[str, Any]) -> set[str]:
    revisions: set[str] = set()
    for subject in record.get("subject_refs", []):
        if isinstance(subject, Mapping):
            revision = subject.get("revision")
            if isinstance(revision, str) and revision:
                revisions.add(revision)
    return revisions


def _claim_validity_status(claim: Mapping[str, Any]) -> Any:
    validity = claim.get("validity")
    return validity.get("status") if isinstance(validity, Mapping) else None


def _trace_indexes(document: Mapping[str, Any]) -> tuple[set[str], set[str], set[str], set[str]]:
    requirement_ids: set[str] = set()
    item_ids: set[str] = set()
    journey_ids: set[str] = set()
    step_ids: set[str] = set()
    for requirement in _records(document, "requirements"):
        requirement_id = requirement.get("id")
        if isinstance(requirement_id, str):
            requirement_ids.add(requirement_id)
        for item in requirement.get("acceptance", []):
            if isinstance(item, Mapping) and isinstance(item.get("id"), str):
                item_ids.add(item["id"])
    for journey in _records(document, "journeys"):
        journey_id = journey.get("id")
        if isinstance(journey_id, str):
            journey_ids.add(journey_id)
        for step in journey.get("steps", []):
            if isinstance(step, Mapping) and isinstance(step.get("id"), str):
                step_ids.add(step["id"])
    return requirement_ids, item_ids, journey_ids, step_ids


def validate_document_shape(document: Any) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    if not isinstance(document, Mapping):
        return [_diag("document-not-mapping", "$", "the YAML document must be a mapping")]

    version = document.get("schema_version")
    if version not in SUPPORTED_SCHEMA_VERSIONS:
        diagnostics.append(
            _diag(
                "unsupported-schema-version",
                "schema_version",
                "schema_version must be exactly 0.3.0 or 0.4.0",
            )
        )

    list_fields = (
        "requirements",
        "journeys",
        "delivery_scopes",
        "delivery_groups",
        "evidence_artifacts",
        "evidence_claims",
        "evidence_validity_assessments",
        "review_epochs",
        "review_batches",
        "review_impact_assessments",
        "review_coverage_carry_forward",
        "host_gate_receipts",
        "review_findings",
        "scope_amendments",
        "gaps",
    )
    for field in list_fields:
        if field in document and not isinstance(document[field], list):
            diagnostics.append(_diag("invalid-collection", field, f"{field} must be a list"))
        elif isinstance(document.get(field), list):
            for index, value in enumerate(document[field]):
                if not isinstance(value, Mapping):
                    diagnostics.append(
                        _diag("invalid-record", f"{field}[{index}]", "record must be a mapping")
                    )

    for field in ("scope", "review_contract", "review_freeze", "verification_policy", "closure_packet"):
        if field in document and not isinstance(document[field], Mapping):
            diagnostics.append(_diag("invalid-object", field, f"{field} must be a mapping"))
    return diagnostics


def validate_unique_identifiers(document: Mapping[str, Any]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []

    def check(values: Iterable[tuple[Any, str]], missing_code: str, duplicate_code: str) -> None:
        seen: set[str] = set()
        for value, path in values:
            if not isinstance(value, str) or not value:
                diagnostics.append(_diag(missing_code, path, "a non-empty stable identifier is required"))
            elif value in seen:
                diagnostics.append(_diag(duplicate_code, path, f"duplicate identifier {value!r}"))
            else:
                seen.add(value)

    collections = (
        ("requirements", "id", "missing-requirement-id", "duplicate-requirement-id"),
        ("delivery_scopes", "scope_ref", "missing-scope-ref", "duplicate-scope-ref"),
        ("delivery_groups", "group_ref", "missing-group-ref", "duplicate-group-ref"),
        ("evidence_artifacts", "id", "missing-artifact-id", "duplicate-artifact-id"),
        ("evidence_claims", "id", "missing-claim-id", "duplicate-claim-id"),
        (
            "evidence_validity_assessments",
            "id",
            "missing-validity-assessment-id",
            "duplicate-validity-assessment-id",
        ),
        ("review_epochs", "id", "missing-review-epoch-id", "duplicate-review-epoch-id"),
        ("review_batches", "id", "missing-review-batch-id", "duplicate-review-batch-id"),
        (
            "review_impact_assessments",
            "id",
            "missing-review-impact-assessment-id",
            "duplicate-review-impact-assessment-id",
        ),
        (
            "review_coverage_carry_forward",
            "id",
            "missing-review-carry-forward-id",
            "duplicate-review-carry-forward-id",
        ),
        (
            "host_gate_receipts",
            "id",
            "missing-host-gate-receipt-id",
            "duplicate-host-gate-receipt-id",
        ),
        ("review_findings", "id", "missing-review-finding-id", "duplicate-review-finding-id"),
        ("scope_amendments", "id", "missing-scope-amendment-id", "duplicate-scope-amendment-id"),
        ("journeys", "id", "missing-journey-id", "duplicate-journey-id"),
    )
    for collection, key, missing, duplicate in collections:
        check(
            ((record.get(key), f"{collection}[{index}].{key}") for index, record in enumerate(_records(document, collection))),
            missing,
            duplicate,
        )

    items: list[tuple[Any, str]] = []
    for requirement_index, requirement in enumerate(_records(document, "requirements")):
        acceptance = requirement.get("acceptance", [])
        if isinstance(acceptance, list):
            for item_index, item in enumerate(acceptance):
                if isinstance(item, Mapping):
                    items.append((item.get("id"), f"requirements[{requirement_index}].acceptance[{item_index}].id"))
    check(items, "missing-acceptance-item-id", "duplicate-acceptance-item-id")

    steps: list[tuple[Any, str]] = []
    for journey_index, journey in enumerate(_records(document, "journeys")):
        journey_steps = journey.get("steps", [])
        if isinstance(journey_steps, list):
            for step_index, step in enumerate(journey_steps):
                if isinstance(step, Mapping):
                    steps.append((step.get("id"), f"journeys[{journey_index}].steps[{step_index}].id"))
    check(steps, "missing-journey-step-id", "duplicate-journey-step-id")

    contract = document.get("review_contract")
    if isinstance(contract, Mapping) and isinstance(contract.get("expected_batches"), list):
        check(
            (
                (batch.get("id"), f"review_contract.expected_batches[{index}].id")
                for index, batch in enumerate(contract["expected_batches"])
                if isinstance(batch, Mapping)
            ),
            "missing-expected-review-batch-id",
            "duplicate-expected-review-batch-id",
        )
    return diagnostics


def validate_delivery_scopes(document: Mapping[str, Any]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    scopes = _records(document, "delivery_scopes")
    scope_index = _index(scopes, "scope_ref")
    amendments = _index(_records(document, "scope_amendments"), "id")

    for index, scope in enumerate(scopes):
        scope_ref = scope.get("scope_ref")
        path = f"delivery_scopes[{index}]"
        if scope.get("scope_kind") not in SCOPE_KINDS:
            diagnostics.append(
                _diag("invalid-scope-kind", f"{path}.scope_kind", "scope_kind must be goal, milestone, or unit")
            )
        if scope.get("disposition") not in CLOSURE_DISPOSITIONS:
            diagnostics.append(
                _diag("invalid-scope-disposition", f"{path}.disposition", "scope disposition is not canonical")
            )
        if "required_for_parent" in scope and not isinstance(scope.get("required_for_parent"), bool):
            diagnostics.append(
                _diag("invalid-required-for-parent", f"{path}.required_for_parent", "required_for_parent must be boolean")
            )

        parent_ref = scope.get("parent_scope_ref")
        if parent_ref is not None and parent_ref not in scope_index:
            diagnostics.append(
                _diag(
                    "unknown-parent-scope",
                    f"{path}.parent_scope_ref",
                    f"parent scope {parent_ref!r} does not resolve",
                )
            )

        if "required_child_scope_refs" in scope:
            children = scope.get("required_child_scope_refs")
            if not isinstance(children, list):
                diagnostics.append(
                    _diag(
                        "invalid-required-child-inventory",
                        f"{path}.required_child_scope_refs",
                        "required_child_scope_refs must be a list",
                    )
                )
                continue
            if not isinstance(scope.get("required_child_inventory_revision"), str) or not scope.get(
                "required_child_inventory_revision"
            ):
                diagnostics.append(
                    _diag(
                        "missing-required-child-inventory-revision",
                        f"{path}.required_child_inventory_revision",
                        "authoritative child inventory requires a revision",
                    )
                )
            seen_children: set[str] = set()
            for child_index, child_ref in enumerate(children):
                child_path = f"{path}.required_child_scope_refs[{child_index}]"
                if child_ref in seen_children:
                    diagnostics.append(_diag("duplicate-required-child", child_path, f"duplicate child {child_ref!r}"))
                    continue
                if isinstance(child_ref, str):
                    seen_children.add(child_ref)
                child = scope_index.get(child_ref)
                if child is None:
                    diagnostics.append(_diag("unknown-required-child-scope", child_path, f"child {child_ref!r} does not resolve"))
                    continue
                if child.get("parent_scope_ref") != scope_ref:
                    diagnostics.append(
                        _diag(
                            "required-child-parent-mismatch",
                            child_path,
                            f"child {child_ref!r} does not point back to {scope_ref!r}",
                        )
                    )
                if child.get("required_for_parent") is not True:
                    diagnostics.append(
                        _diag(
                            "required-child-flag-mismatch",
                            child_path,
                            f"child {child_ref!r} is inventoried as required but required_for_parent is not true",
                        )
                    )
                if scope.get("disposition") in CLOSED_DISPOSITIONS and child.get("disposition") not in CLOSED_DISPOSITIONS:
                    diagnostics.append(
                        _diag(
                            "blocked-required-child-closes-parent",
                            child_path,
                            f"closed parent {scope_ref!r} has required child {child_ref!r} with disposition {child.get('disposition')!r}",
                        )
                    )

    for index, scope in enumerate(scopes):
        parent_ref = scope.get("parent_scope_ref")
        parent = scope_index.get(parent_ref)
        if parent is None:
            continue
        scope_ref = scope.get("scope_ref")
        inventory = parent.get("required_child_scope_refs")
        inventoried = isinstance(inventory, list) and scope_ref in inventory
        if scope.get("required_for_parent") is True and not inventoried:
            diagnostics.append(
                _diag(
                    "required-child-missing-from-inventory",
                    f"delivery_scopes[{index}].required_for_parent",
                    f"required child {scope_ref!r} is absent from parent {parent_ref!r} inventory",
                )
            )
        if scope.get("required_for_parent") is False and inventoried:
            diagnostics.append(
                _diag(
                    "optional-child-present-in-required-inventory",
                    f"delivery_scopes[{index}].required_for_parent",
                    f"optional child {scope_ref!r} appears in the required inventory",
                )
            )

        exclusion = scope.get("required_inventory_exclusion")
        if exclusion is None:
            continue
        exclusion_path = f"delivery_scopes[{index}].required_inventory_exclusion"
        if not isinstance(exclusion, Mapping):
            diagnostics.append(
                _diag(
                    "invalid-required-inventory-exclusion",
                    exclusion_path,
                    "required_inventory_exclusion must be a mapping",
                )
            )
            continue
        amendment = amendments.get(exclusion.get("amendment_ref"))
        if amendment is None or amendment.get("decision") != "accepted":
            diagnostics.append(
                _diag(
                    "required-child-removal-without-accepted-amendment",
                    f"{exclusion_path}.amendment_ref",
                    "claimed removal from required inventory must resolve an accepted scope amendment",
                )
            )
            continue
        inventory_revision = parent.get("required_child_inventory_revision")
        removal_matches = (
            scope.get("required_for_parent") is False
            and not inventoried
            and exclusion.get("inventory_revision") == inventory_revision
            and amendment.get("parent_scope_ref") == parent_ref
            and scope_ref in _string_list(amendment.get("removed_required_child_scope_refs"))
            and amendment.get("required_child_inventory_revision") == inventory_revision
        )
        if not removal_matches:
            diagnostics.append(
                _diag(
                    "required-child-removal-record-mismatch",
                    exclusion_path,
                    "removal claim, accepted amendment, requiredness, parent, child, and revised inventory must agree",
                )
            )

    # A scope has at most one parent, so each cycle is a functional-graph cycle.
    reported_cycles: set[frozenset[str]] = set()
    for start in sorted(scope_index):
        order: list[str] = []
        position: dict[str, int] = {}
        current: Any = start
        while current in scope_index and current not in position:
            position[current] = len(order)
            order.append(current)
            current = scope_index[current].get("parent_scope_ref")
        if current in position:
            cycle = frozenset(order[position[current] :])
            if cycle not in reported_cycles:
                reported_cycles.add(cycle)
                diagnostics.append(
                    _diag("cyclic-parent-scope", f"delivery_scopes[{min(cycle)}]", f"parent cycle contains {sorted(cycle)!r}")
                )

    groups = _records(document, "delivery_groups")
    for index, group in enumerate(groups):
        path = f"delivery_groups[{index}]"
        if group.get("group_kind") not in GROUP_KINDS:
            diagnostics.append(
                _diag(
                    "invalid-delivery-group-kind",
                    f"{path}.group_kind",
                    "group_kind must be execution_batch, verification_batch, or review_batch",
                )
            )
        members = group.get("member_scope_refs")
        if not isinstance(members, list):
            diagnostics.append(
                _diag("invalid-delivery-group-members", f"{path}.member_scope_refs", "member_scope_refs must be a list")
            )
            continue
        seen_members: set[str] = set()
        for member_index, member_ref in enumerate(members):
            member_path = f"{path}.member_scope_refs[{member_index}]"
            if member_ref in seen_members:
                diagnostics.append(_diag("duplicate-delivery-group-member", member_path, f"duplicate member {member_ref!r}"))
            elif member_ref not in scope_index:
                diagnostics.append(_diag("unknown-delivery-group-member", member_path, f"scope {member_ref!r} does not resolve"))
            elif isinstance(member_ref, str):
                seen_members.add(member_ref)
    return diagnostics


def _assessment_basis_is_explicit(basis: Any) -> bool:
    required = {
        "target_revision_before",
        "target_revision_after",
        "verifier_revision_before",
        "verifier_revision_after",
        "dependency_fingerprint_before",
        "dependency_fingerprint_after",
        "environment_compatibility",
        "freshness",
        "rationale",
    }
    return isinstance(basis, Mapping) and required.issubset(basis) and all(basis.get(key) not in (None, "") for key in required)


def _lite_reuse_basis_is_explicit(validity: Mapping[str, Any]) -> bool:
    basis = validity.get("reuse_basis")
    if isinstance(basis, Mapping):
        return all(basis.get(key) not in (None, "") for key in ("target", "verifier", "dependency", "environment", "freshness", "rationale"))
    rationale = validity.get("rationale")
    if isinstance(rationale, str):
        lowered = rationale.lower()
        return all(term in lowered for term in ("target", "verifier", "dependency", "environment", "freshness"))
    return False


def validate_evidence_registry(document: Mapping[str, Any]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    _, item_ids, journey_ids, _ = _trace_indexes(document)
    journey_steps = {
        journey.get("id"): {
            step.get("id")
            for step in journey.get("steps", [])
            if isinstance(step, Mapping) and isinstance(step.get("id"), str)
        }
        for journey in _records(document, "journeys")
        if isinstance(journey.get("id"), str)
    }
    artifacts = _index(_records(document, "evidence_artifacts"), "id")
    claims = _index(_records(document, "evidence_claims"), "id")
    assessments = _index(_records(document, "evidence_validity_assessments"), "id")
    policy = document.get("verification_policy") if isinstance(document.get("verification_policy"), Mapping) else {}
    policy_id = policy.get("id")
    mode = document.get("scope", {}).get("mode") if isinstance(document.get("scope"), Mapping) else None

    for requirement_index, requirement in enumerate(_records(document, "requirements")):
        acceptance = requirement.get("acceptance", [])
        if not isinstance(acceptance, list):
            diagnostics.append(
                _diag(
                    "invalid-acceptance-items",
                    f"requirements[{requirement_index}].acceptance",
                    "acceptance must be a list",
                )
            )
            continue
        for item_index, item in enumerate(acceptance):
            if not isinstance(item, Mapping):
                continue
            item_id = item.get("id")
            status = item.get("status")
            if status not in TRACE_STATUSES:
                diagnostics.append(
                    _diag(
                        "invalid-acceptance-item-status",
                        f"requirements[{requirement_index}].acceptance[{item_index}].status",
                        "Acceptance Item status is not canonical",
                    )
                )
            for evidence_index, evidence in enumerate(item.get("evidence", [])):
                if not isinstance(evidence, Mapping):
                    continue
                evidence_path = f"requirements[{requirement_index}].acceptance[{item_index}].evidence[{evidence_index}]"
                if "evidence_ref" in evidence:
                    claim = claims.get(evidence.get("evidence_ref"))
                    if claim is None:
                        diagnostics.append(
                            _diag("unknown-evidence-claim", f"{evidence_path}.evidence_ref", "evidence_ref does not resolve")
                        )
                    elif claim.get("target_kind") != "acceptance_item" or claim.get("target_ref") != item_id:
                        diagnostics.append(
                            _diag(
                                "evidence-claim-target-mismatch",
                                f"{evidence_path}.evidence_ref",
                                "Item evidence_ref must resolve to an Item-specific claim for this Item",
                            )
                        )
                    elif status == "verified" and _claim_validity_status(claim) != "valid":
                        diagnostics.append(
                            _diag(
                                "verified-item-uses-invalid-claim",
                                f"{evidence_path}.evidence_ref",
                                "a verified Item requires a currently valid target-specific claim",
                            )
                        )
                elif evidence.get("target") != item_id:
                    diagnostics.append(
                        _diag(
                            "inline-item-evidence-target-mismatch",
                            f"{evidence_path}.target",
                            "inline Item evidence must target its canonical Acceptance Item",
                        )
                    )

    for journey_index, journey in enumerate(_records(document, "journeys")):
        journey_id = journey.get("id")
        if journey.get("status") not in TRACE_STATUSES:
            diagnostics.append(
                _diag(
                    "invalid-journey-status",
                    f"journeys[{journey_index}].status",
                    "Journey status is not canonical",
                )
            )
        local_steps: set[str] = set()
        for step_index, step in enumerate(journey.get("steps", [])):
            if not isinstance(step, Mapping):
                continue
            step_id = step.get("id")
            if isinstance(step_id, str):
                local_steps.add(step_id)
            for item_ref_index, item_ref in enumerate(step.get("acceptance_item_ids", [])):
                if item_ref not in item_ids:
                    diagnostics.append(
                        _diag(
                            "unknown-step-acceptance-item",
                            f"journeys[{journey_index}].steps[{step_index}].acceptance_item_ids[{item_ref_index}]",
                            f"Acceptance Item {item_ref!r} does not resolve",
                        )
                    )
        for evidence_index, evidence in enumerate(journey.get("path_evidence", [])):
            if not isinstance(evidence, Mapping):
                continue
            evidence_path = f"journeys[{journey_index}].path_evidence[{evidence_index}]"
            if "evidence_ref" in evidence:
                claim = claims.get(evidence.get("evidence_ref"))
                if claim is None:
                    diagnostics.append(
                        _diag("unknown-evidence-claim", f"{evidence_path}.evidence_ref", "evidence_ref does not resolve")
                    )
                elif claim.get("target_kind") != "journey" or claim.get("target_ref") != journey_id:
                    diagnostics.append(
                        _diag(
                            "evidence-claim-target-mismatch",
                            f"{evidence_path}.evidence_ref",
                            "path evidence_ref must resolve to a Journey-specific claim for this Journey",
                        )
                    )
                elif journey.get("status") == "verified" and _claim_validity_status(claim) != "valid":
                    diagnostics.append(
                        _diag(
                            "verified-journey-uses-invalid-claim",
                            f"{evidence_path}.evidence_ref",
                            "a verified Journey requires a currently valid target-specific path claim",
                        )
                    )
            else:
                unknown_steps = set(_string_list(evidence.get("covers_steps"))) - local_steps
                if unknown_steps:
                    diagnostics.append(
                        _diag(
                            "inline-path-evidence-step-mismatch",
                            f"{evidence_path}.covers_steps",
                            f"inline path evidence references steps outside this Journey: {sorted(unknown_steps)!r}",
                        )
                    )

    for index, assessment in enumerate(_records(document, "evidence_validity_assessments")):
        if assessment.get("claim_ref") not in claims:
            diagnostics.append(
                _diag(
                    "unknown-validity-assessment-claim",
                    f"evidence_validity_assessments[{index}].claim_ref",
                    "assessment claim_ref does not resolve",
                )
            )

    for index, claim in enumerate(_records(document, "evidence_claims")):
        path = f"evidence_claims[{index}]"
        artifact = artifacts.get(claim.get("artifact_ref"))
        if artifact is None:
            diagnostics.append(_diag("unknown-claim-artifact", f"{path}.artifact_ref", "claim artifact_ref does not resolve"))
        target_kind = claim.get("target_kind")
        target_ref = claim.get("target_ref")
        if not isinstance(claim.get("proves"), str) or not claim.get("proves"):
            diagnostics.append(_diag("missing-claim-proof", f"{path}.proves", "claim must state what it proves"))
        if target_kind not in CLAIM_TARGET_KINDS:
            diagnostics.append(
                _diag("invalid-claim-target-kind", f"{path}.target_kind", "target_kind must be acceptance_item or journey")
            )
        elif target_kind == "acceptance_item" and target_ref not in item_ids:
            diagnostics.append(_diag("unknown-claim-target", f"{path}.target_ref", "Acceptance Item target does not resolve"))
        elif target_kind == "journey" and target_ref not in journey_ids:
            diagnostics.append(_diag("unknown-claim-target", f"{path}.target_ref", "Journey target does not resolve"))

        validity = claim.get("validity")
        if not isinstance(validity, Mapping):
            diagnostics.append(_diag("missing-claim-validity", f"{path}.validity", "claim validity is required"))
            continue
        status = validity.get("status")
        if status not in CLAIM_VALIDITY_STATUSES:
            diagnostics.append(
                _diag(
                    "invalid-claim-validity-status",
                    f"{path}.validity.status",
                    "evidence_claims[].validity.status must be valid, stale, invalidated, or unknown",
                )
            )
            continue
        if status == "valid" and artifact is not None and artifact.get("result") != "passed":
            diagnostics.append(
                _diag("valid-claim-from-failed-artifact", f"{path}.validity.status", "a valid claim requires a passed artifact")
            )
        if target_kind == "journey":
            covered_steps = set(_string_list(claim.get("covers_steps")))
            target_steps = journey_steps.get(target_ref, set())
            if not covered_steps or not covered_steps.issubset(target_steps) or not claim.get("proves_order") or not claim.get("proves_outcome"):
                diagnostics.append(
                    _diag(
                        "invalid-journey-evidence-claim",
                        path,
                        "Journey claims require target-local covered steps plus order and outcome proof",
                    )
                )
        if status != "valid" or artifact is None:
            continue

        checked_revision = validity.get("checked_against_revision")
        artifact_revision = artifact.get("subject_revision")
        if not isinstance(checked_revision, str) or not checked_revision:
            diagnostics.append(
                _diag(
                    "missing-claim-checked-revision",
                    f"{path}.validity.checked_against_revision",
                    "a valid claim requires checked_against_revision",
                )
            )
            continue
        if checked_revision == artifact_revision:
            continue

        assessment_ref = validity.get("assessment_ref")
        assessment = assessments.get(assessment_ref)
        if assessment is None:
            if mode == "lite" and _lite_reuse_basis_is_explicit(validity):
                continue
            code = "unsupported-lite-cross-revision-validity" if mode == "lite" else "missing-cross-revision-validity-assessment"
            diagnostics.append(
                _diag(
                    code,
                    f"{path}.validity",
                    "cross-revision valid reuse requires an assessment or an explicit lite comparison basis",
                )
            )
            continue

        if not _assessment_basis_is_explicit(assessment.get("basis")):
            diagnostics.append(
                _diag(
                    "opaque-cross-revision-validity-basis",
                    f"evidence_validity_assessments[{assessment_ref}].basis",
                    "cross-revision validity must compare target, verifier, dependency, environment, and freshness explicitly",
                )
            )
            continue

        mismatch = (
            assessment.get("claim_ref") != claim.get("id")
            or assessment.get("from_revision") != artifact_revision
            or assessment.get("checked_against_revision") != checked_revision
            or not assessment.get("assessor_ref")
            or not assessment.get("policy_ref")
            or assessment.get("decision") != "valid"
            or (policy_id and assessment.get("policy_ref") != policy_id)
        )
        if mismatch:
            diagnostics.append(
                _diag(
                    "cross-revision-validity-assessment-mismatch",
                    f"{path}.validity.assessment_ref",
                    "assessment must match the claim, from/to revisions, assessor, policy, and valid decision",
                )
            )

    return diagnostics


def validate_verification_policy(document: Mapping[str, Any]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    policy = document.get("verification_policy")
    if policy is None:
        return diagnostics
    if not isinstance(policy, Mapping):
        return diagnostics
    version = document.get("schema_version")
    mode = document.get("scope", {}).get("mode") if isinstance(document.get("scope"), Mapping) else None
    tiers = policy.get("tiers")
    if version == "0.4.0" and mode in {"standard", "strict"}:
        if not isinstance(tiers, Mapping) or not VERIFICATION_TIERS.issubset(tiers):
            diagnostics.append(
                _diag(
                    "incomplete-verification-policy-tiers",
                    "verification_policy.tiers",
                    "0.4 standard/strict policy must contain worker, batch, milestone, and completion tiers",
                )
            )
        else:
            for tier in sorted(VERIFICATION_TIERS):
                if not isinstance(tiers[tier], Mapping) or not _string_list(tiers[tier].get("command_refs")):
                    diagnostics.append(
                        _diag(
                            "empty-verification-policy-tier",
                            f"verification_policy.tiers.{tier}",
                            f"{tier} tier requires command_refs",
                        )
                    )
        if "host_native_required_gates" not in policy or not isinstance(policy.get("host_native_required_gates"), list):
            diagnostics.append(
                _diag(
                    "missing-host-native-gate-floor",
                    "verification_policy.host_native_required_gates",
                    "0.4 standard/strict policy must preserve host_native_required_gates",
                )
            )

    required_gates = {
        gate.get("gate_ref"): gate
        for gate in policy.get("host_native_required_gates", [])
        if isinstance(gate, Mapping) and isinstance(gate.get("gate_ref"), str)
    }
    receipts = _index(_records(document, "host_gate_receipts"), "id")
    for index, receipt in enumerate(_records(document, "host_gate_receipts")):
        if receipt.get("current_test_status_claim") == "passed" and receipt.get("status") != "passed":
            diagnostics.append(
                _diag(
                    "stale-current-test-status-claim",
                    f"host_gate_receipts[{index}].current_test_status_claim",
                    "current tests may be claimed passed only from a passed fresh host receipt",
                )
            )

    closure = document.get("closure_packet")
    if not isinstance(closure, Mapping):
        return diagnostics
    gate_status_records = closure.get("host_gate_status", [])
    if not isinstance(gate_status_records, list):
        diagnostics.append(
            _diag("invalid-host-gate-status", "closure_packet.host_gate_status", "host_gate_status must be a list")
        )
        return diagnostics
    gate_status = {
        record.get("gate_ref"): record
        for record in gate_status_records
        if isinstance(record, Mapping) and isinstance(record.get("gate_ref"), str)
    }
    if closure.get("disposition") in CLOSED_DISPOSITIONS:
        for gate_ref in sorted(required_gates):
            status = gate_status.get(gate_ref)
            if status is None or status.get("status") != "satisfied":
                diagnostics.append(
                    _diag(
                        "missing-required-host-gate-receipt",
                        "closure_packet.host_gate_status",
                        f"closed 0.4 packet must satisfy required host gate {gate_ref!r}",
                    )
                )

    for index, status in enumerate(gate_status_records):
        if not isinstance(status, Mapping) or status.get("status") != "satisfied":
            continue
        path = f"closure_packet.host_gate_status[{index}]"
        required = required_gates.get(status.get("gate_ref"))
        receipt = receipts.get(status.get("receipt_ref"))
        if receipt is None:
            diagnostics.append(_diag("unknown-host-gate-receipt", f"{path}.receipt_ref", "receipt_ref does not resolve"))
            continue
        if required is None:
            diagnostics.append(
                _diag("unsupported-host-gate-satisfaction", f"{path}.gate_ref", "satisfied gate is not in the effective host floor")
            )
            continue
        matches = (
            receipt.get("gate_ref") == status.get("gate_ref")
            and receipt.get("status") == "passed"
            and receipt.get("subject_revision") == status.get("subject_revision") == closure.get("subject_revision")
            and receipt.get("lifecycle_boundary") == required.get("lifecycle_boundary")
            and receipt.get("freshness") == required.get("freshness")
        )
        if not matches:
            diagnostics.append(
                _diag(
                    "host-gate-receipt-mismatch",
                    f"{path}.receipt_ref",
                    "satisfied host gate requires a passed receipt with matching gate, boundary, freshness, and revision",
                )
            )
    return diagnostics


def validate_review_governance(document: Mapping[str, Any]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    version = document.get("schema_version")
    mode = document.get("scope", {}).get("mode") if isinstance(document.get("scope"), Mapping) else None
    contract = document.get("review_contract")
    contract = contract if isinstance(contract, Mapping) else None
    scopes = _index(_records(document, "delivery_scopes"), "scope_ref")
    epochs = _index(_records(document, "review_epochs"), "id")
    batches = _index(_records(document, "review_batches"), "id")
    findings = _index(_records(document, "review_findings"), "id")
    assessments = _index(_records(document, "review_impact_assessments"), "id")
    carry_forwards = _index(_records(document, "review_coverage_carry_forward"), "id")

    if contract is not None and version == "0.4.0":
        if contract.get("cadence") not in REVIEW_CADENCES:
            diagnostics.append(
                _diag("invalid-review-cadence", "review_contract.cadence", "cadence must be unit, batch, milestone, or host_native")
            )
        if not isinstance(contract.get("child_scope_policy"), str) or not contract.get("child_scope_policy"):
            diagnostics.append(
                _diag("missing-review-child-policy", "review_contract.child_scope_policy", "new review contract requires child_scope_policy")
            )
        if not isinstance(contract.get("covered_child_scope_refs"), list):
            diagnostics.append(
                _diag(
                    "missing-covered-child-scope-refs",
                    "review_contract.covered_child_scope_refs",
                    "new review contract requires covered_child_scope_refs, which may be empty",
                )
            )
        if contract.get("batch_combination_policy") not in REVIEW_COMBINATION_POLICIES:
            diagnostics.append(
                _diag(
                    "invalid-review-batch-combination-policy",
                    "review_contract.batch_combination_policy",
                    "batch_combination_policy must be combined_allowed, separate_required, or host_native",
                )
            )
        if not isinstance(contract.get("host_native_required_batches"), list):
            diagnostics.append(
                _diag(
                    "missing-host-native-review-batches",
                    "review_contract.host_native_required_batches",
                    "new review contract must preserve host_native_required_batches",
                )
            )
        dimensions = contract.get("dimensions")
        baseline = dimensions.get("baseline") if isinstance(dimensions, Mapping) else None
        required_baseline = {"requirement-fidelity", "impact-and-ownership", "verification-and-closure"}
        if not isinstance(baseline, list) or not required_baseline.issubset(set(_string_list(baseline))):
            diagnostics.append(
                _diag(
                    "missing-baseline-review-dimensions",
                    "review_contract.dimensions.baseline",
                    "new review contract must retain all baseline dimensions",
                )
            )
        if mode == "strict" and contract.get("independence", {}).get("required") is not True:
            diagnostics.append(
                _diag(
                    "missing-strict-review-independence",
                    "review_contract.independence.required",
                    "strict review requires implementer-independent coverage",
                )
            )
        for index, child_ref in enumerate(_string_list(contract.get("covered_child_scope_refs"))):
            if scopes and child_ref not in scopes:
                diagnostics.append(
                    _diag(
                        "unknown-covered-child-scope",
                        f"review_contract.covered_child_scope_refs[{index}]",
                        f"covered child {child_ref!r} does not resolve",
                    )
                )

    for index, epoch in enumerate(_records(document, "review_epochs")):
        if contract is not None and epoch.get("contract") != contract.get("id"):
            diagnostics.append(
                _diag("unknown-review-contract", f"review_epochs[{index}].contract", "review epoch contract does not resolve")
            )
        prior_epoch = epoch.get("prior_epoch")
        if prior_epoch is not None and prior_epoch not in epochs:
            diagnostics.append(
                _diag("unknown-prior-review-epoch", f"review_epochs[{index}].prior_epoch", "prior_epoch does not resolve")
            )

    for index, batch in enumerate(_records(document, "review_batches")):
        epoch = epochs.get(batch.get("epoch"))
        if epoch is None:
            diagnostics.append(
                _diag("unknown-review-batch-epoch", f"review_batches[{index}].epoch", "review batch epoch does not resolve")
            )
            continue
        if _subject_revisions(batch) != _subject_revisions(epoch):
            diagnostics.append(
                _diag(
                    "review-batch-subject-revision-mismatch",
                    f"review_batches[{index}].subject_refs",
                    "review batch must remain bound to its epoch's actual subject revision",
                )
            )

    for index, finding in enumerate(_records(document, "review_findings")):
        epoch_ref = finding.get("epoch")
        batch_ref = finding.get("batch")
        if epoch_ref is not None and epoch_ref not in epochs:
            diagnostics.append(
                _diag("unknown-review-finding-epoch", f"review_findings[{index}].epoch", "finding epoch does not resolve")
            )
        if batch_ref is not None:
            batch = batches.get(batch_ref)
            if batch is None:
                diagnostics.append(
                    _diag("unknown-review-finding-batch", f"review_findings[{index}].batch", "finding batch does not resolve")
                )
            elif epoch_ref is not None and batch.get("epoch") != epoch_ref:
                diagnostics.append(
                    _diag(
                        "review-finding-epoch-batch-mismatch",
                        f"review_findings[{index}].batch",
                        "finding batch must belong to the declared epoch",
                    )
                )

    freeze = document.get("review_freeze")
    if isinstance(freeze, Mapping):
        freeze_epoch = epochs.get(freeze.get("epoch"))
        if freeze_epoch is None:
            diagnostics.append(_diag("unknown-review-freeze-epoch", "review_freeze.epoch", "freeze epoch does not resolve"))
        elif _subject_revisions(freeze) != _subject_revisions(freeze_epoch):
            diagnostics.append(
                _diag(
                    "review-freeze-subject-revision-mismatch",
                    "review_freeze.subject_refs",
                    "freeze must use the exact epoch subject revision",
                )
            )
        for batch_ref in _string_list(freeze.get("accepted_batches")):
            batch = batches.get(batch_ref)
            if batch is None or batch.get("epoch") != freeze.get("epoch"):
                diagnostics.append(
                    _diag(
                        "invalid-review-freeze-batch",
                        "review_freeze.accepted_batches",
                        f"accepted batch {batch_ref!r} must resolve in the freeze epoch",
                    )
                )
        for finding_ref in _string_list(freeze.get("frozen_findings")):
            if finding_ref not in findings:
                diagnostics.append(
                    _diag(
                        "unknown-frozen-review-finding",
                        "review_freeze.frozen_findings",
                        f"frozen finding {finding_ref!r} does not resolve",
                    )
                )

    for index, assessment in enumerate(_records(document, "review_impact_assessments")):
        if assessment.get("source_batch_ref") not in batches:
            diagnostics.append(
                _diag(
                    "unknown-review-impact-source-batch",
                    f"review_impact_assessments[{index}].source_batch_ref",
                    "impact assessment source batch does not resolve",
                )
            )

    for index, carry in enumerate(_records(document, "review_coverage_carry_forward")):
        path = f"review_coverage_carry_forward[{index}]"
        source = batches.get(carry.get("source_batch_ref"))
        if source is None:
            diagnostics.append(
                _diag("unknown-review-carry-forward-source-batch", f"{path}.source_batch_ref", "source batch does not resolve")
            )
            continue
        if carry.get("from_revision") not in _subject_revisions(source):
            diagnostics.append(
                _diag(
                    "review-carry-forward-source-revision-mismatch",
                    f"{path}.from_revision",
                    "from_revision must equal the immutable historical source-batch revision",
                )
            )
            continue
        impact = assessments.get(carry.get("impact_assessment_ref"))
        if impact is None:
            diagnostics.append(
                _diag(
                    "unknown-review-carry-forward-impact-assessment",
                    f"{path}.impact_assessment_ref",
                    "impact assessment does not resolve",
                )
            )
            continue
        unchanged = set(_string_list(carry.get("unchanged_dimensions")))
        impact_unchanged = set(_string_list(impact.get("unchanged_dimensions")))
        mismatch = (
            impact.get("source_batch_ref") != carry.get("source_batch_ref")
            or impact.get("from_revision") != carry.get("from_revision")
            or impact.get("to_revision") != carry.get("to_revision")
            or unchanged != impact_unchanged
            or impact.get("assessor_ref") != carry.get("assessor_ref")
            or impact.get("decision") != "accepted"
            or carry.get("decision") != "accepted"
            or not impact.get("rationale")
        )
        if mismatch:
            diagnostics.append(
                _diag(
                    "review-carry-forward-impact-mismatch",
                    path,
                    "carry-forward and accepted impact assessment must agree on source, revisions, dimensions, assessor, and decision",
                )
            )
            continue
        target_epoch = carry.get("target_epoch")
        if target_epoch is not None:
            target = epochs.get(target_epoch)
            if target is None:
                diagnostics.append(
                    _diag("unknown-review-carry-forward-target-epoch", f"{path}.target_epoch", "target_epoch does not resolve")
                )
            elif carry.get("to_revision") not in _subject_revisions(target):
                diagnostics.append(
                    _diag(
                        "review-carry-forward-target-revision-mismatch",
                        f"{path}.to_revision",
                        "to_revision must match the target epoch revision",
                    )
                )
        covered = {
            coverage.get("dimension")
            for coverage in source.get("dimension_coverage", [])
            if isinstance(coverage, Mapping) and coverage.get("status") == "covered"
        }
        if not unchanged.issubset(covered):
            diagnostics.append(
                _diag(
                    "review-carry-forward-uncovered-dimension",
                    f"{path}.unchanged_dimensions",
                    "carry-forward can preserve only dimensions actually covered by the source batch",
                )
            )

    if contract is not None and version == "0.4.0":
        actual_host_refs = {
            batch.get("host_batch_ref")
            for batch in batches.values()
            if isinstance(batch.get("host_batch_ref"), str)
        }
        for host_ref in _string_list(contract.get("host_native_required_batches")):
            if host_ref not in actual_host_refs:
                diagnostics.append(
                    _diag(
                        "missing-host-native-review-batch",
                        "review_contract.host_native_required_batches",
                        f"required host-native batch {host_ref!r} has no actual review receipt",
                    )
                )
        actual_host_kinds = {batch.get("host_kind") for batch in batches.values()}
        for index, expected in enumerate(contract.get("expected_batches", [])):
            if isinstance(expected, Mapping) and expected.get("host_kind") not in actual_host_kinds:
                diagnostics.append(
                    _diag(
                        "missing-expected-review-batch",
                        f"review_contract.expected_batches[{index}]",
                        f"expected host review kind {expected.get('host_kind')!r} has no actual batch",
                    )
                )

    for index, scope in enumerate(_records(document, "delivery_scopes")):
        review_state = scope.get("review_state")
        if review_state is None:
            continue
        if review_state not in {"pending_at_parent", "covered_at_parent", "not_required"}:
            diagnostics.append(
                _diag(
                    "invalid-child-review-state",
                    f"delivery_scopes[{index}].review_state",
                    "review_state must be pending_at_parent, covered_at_parent, or not_required",
                )
            )
        if review_state == "pending_at_parent" and (
            contract is None
            or contract.get("child_scope_policy") != "covered_at_parent"
            or scope.get("scope_ref") not in _string_list(contract.get("covered_child_scope_refs"))
            or contract.get("scope_ref") != scope.get("parent_scope_ref")
        ):
            diagnostics.append(
                _diag(
                    "uncontracted-parent-review-pending",
                    f"delivery_scopes[{index}].review_state",
                    "pending_at_parent requires explicit parent coverage for this child scope",
                )
            )
        if review_state == "pending_at_parent" and scope.get("disposition") in CLOSED_DISPOSITIONS:
            diagnostics.append(
                _diag(
                    "pending-parent-review-closes-scope",
                    f"delivery_scopes[{index}].disposition",
                    "review_state: pending_at_parent is future coverage, so the formally reviewed scope must remain incomplete",
                )
            )
        if review_state == "covered_at_parent" and (
            contract is None
            or contract.get("child_scope_policy") != "covered_at_parent"
            or scope.get("scope_ref") not in _string_list(contract.get("covered_child_scope_refs"))
            or contract.get("scope_ref") != scope.get("parent_scope_ref")
        ):
            diagnostics.append(
                _diag(
                    "uncontracted-parent-review-coverage",
                    f"delivery_scopes[{index}].review_state",
                    "covered_at_parent requires a parent contract that explicitly covers this child",
                )
            )
        if review_state == "covered_at_parent":
            scope_closure = document.get("closure_packet")
            parent_review_receipt = scope_closure.get("review_closure") if isinstance(scope_closure, Mapping) else None
            if (
                not isinstance(scope_closure, Mapping)
                or scope_closure.get("scope_ref") != scope.get("scope_ref")
                or not isinstance(parent_review_receipt, Mapping)
                or parent_review_receipt.get("status") != "closed"
            ):
                diagnostics.append(
                    _diag(
                        "missing-parent-review-closure-receipt",
                        f"delivery_scopes[{index}].review_state",
                        "covered_at_parent requires an actual closed parent review receipt for this child closure",
                    )
                )

    closure = document.get("closure_packet")
    review_closure = closure.get("review_closure") if isinstance(closure, Mapping) else None
    if not isinstance(review_closure, Mapping) or review_closure.get("status") != "closed":
        return diagnostics
    epoch = epochs.get(review_closure.get("epoch"))
    if epoch is None:
        diagnostics.append(_diag("unknown-review-closure-epoch", "closure_packet.review_closure.epoch", "review closure epoch does not resolve"))
        return diagnostics
    if epoch.get("status") != "closed" or _subject_revisions(epoch) != {
        subject.get("revision")
        for subject in review_closure.get("subject_refs", [])
        if isinstance(subject, Mapping) and isinstance(subject.get("revision"), str)
    } or (isinstance(closure, Mapping) and closure.get("subject_revision") not in _subject_revisions(epoch)):
        diagnostics.append(
            _diag(
                "review-closure-revision-mismatch",
                "closure_packet.review_closure.subject_refs",
                "closed review must use the exact closed epoch subject revision",
            )
        )

    covered_dimensions: set[str] = set()
    accepted_reviewers: list[Mapping[str, Any]] = []
    for batch_ref in _string_list(review_closure.get("accepted_batches")):
        batch = batches.get(batch_ref)
        if batch is None:
            diagnostics.append(
                _diag("unknown-accepted-review-batch", "closure_packet.review_closure.accepted_batches", f"batch {batch_ref!r} does not resolve")
            )
            continue
        if batch.get("epoch") != epoch.get("id"):
            diagnostics.append(
                _diag(
                    "accepted-review-batch-wrong-epoch",
                    "closure_packet.review_closure.accepted_batches",
                    f"batch {batch_ref!r} does not belong to the closure epoch",
                )
            )
        if batch.get("coverage_status") != "complete":
            diagnostics.append(
                _diag(
                    "accepted-review-batch-incomplete",
                    "closure_packet.review_closure.accepted_batches",
                    f"accepted batch {batch_ref!r} must have complete declared coverage",
                )
            )
        accepted_reviewers.append(batch.get("reviewer", {}))
        covered_dimensions.update(
            coverage.get("dimension")
            for coverage in batch.get("dimension_coverage", [])
            if isinstance(coverage, Mapping) and coverage.get("status") == "covered"
        )

    for carry_ref in _string_list(review_closure.get("accepted_carry_forward")):
        carry = carry_forwards.get(carry_ref)
        if carry is None:
            diagnostics.append(
                _diag(
                    "unknown-accepted-review-carry-forward",
                    "closure_packet.review_closure.accepted_carry_forward",
                    f"carry-forward {carry_ref!r} does not resolve",
                )
            )
            continue
        if carry.get("to_revision") not in _subject_revisions(epoch):
            diagnostics.append(
                _diag(
                    "accepted-review-carry-forward-wrong-revision",
                    "closure_packet.review_closure.accepted_carry_forward",
                    f"carry-forward {carry_ref!r} does not target the closure revision",
                )
            )
        covered_dimensions.update(_string_list(carry.get("unchanged_dimensions")))
        source = batches.get(carry.get("source_batch_ref"))
        if source is not None:
            accepted_reviewers.append(source.get("reviewer", {}))
            if source.get("coverage_status") != "complete":
                diagnostics.append(
                    _diag(
                        "review-carry-forward-source-incomplete",
                        "closure_packet.review_closure.accepted_carry_forward",
                        f"carry-forward {carry_ref!r} cannot reuse an incomplete source batch",
                    )
                )

    if contract is not None:
        dimensions = contract.get("dimensions", {})
        required_dimensions = set(_string_list(dimensions.get("baseline"))) | set(_string_list(dimensions.get("triggered")))
        if not required_dimensions.issubset(covered_dimensions):
            diagnostics.append(
                _diag(
                    "incomplete-review-closure-coverage",
                    "closure_packet.review_closure",
                    f"closed review lacks coverage for {sorted(required_dimensions - covered_dimensions)!r}",
                )
            )
        required_host_refs = set(_string_list(contract.get("host_native_required_batches")))
        accepted_host_refs = {
            batches[batch_ref].get("host_batch_ref")
            for batch_ref in _string_list(review_closure.get("accepted_batches"))
            if batch_ref in batches
        }
        if not required_host_refs.issubset(accepted_host_refs):
            diagnostics.append(
                _diag(
                    "host-native-review-batch-not-accepted",
                    "closure_packet.review_closure.accepted_batches",
                    "closed review must accept every required host-native batch",
                )
            )
        if contract.get("independence", {}).get("required") is True and any(
            reviewer.get("relationship_to_implementer") != "independent" for reviewer in accepted_reviewers
        ):
            diagnostics.append(
                _diag(
                    "review-closure-lacks-independence",
                    "closure_packet.review_closure",
                    "required independent review coverage cannot be self-approved",
                )
            )

    return diagnostics


def validate_closure_continuation(document: Mapping[str, Any]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    if document.get("schema_version") != "0.4.0":
        return diagnostics
    closure = document.get("closure_packet")
    if not isinstance(closure, Mapping):
        return diagnostics
    scopes = _index(_records(document, "delivery_scopes"), "scope_ref")
    scope_ref = closure.get("scope_ref")
    closed_scope = scopes.get(scope_ref)
    if scopes and closed_scope is None:
        diagnostics.append(_diag("unknown-closure-scope", "closure_packet.scope_ref", "closure scope_ref does not resolve"))
        return diagnostics
    if closure.get("disposition") not in CLOSURE_DISPOSITIONS:
        diagnostics.append(
            _diag("invalid-closure-disposition", "closure_packet.disposition", "closure disposition is not canonical")
        )
    if closed_scope is not None and closure.get("disposition") != closed_scope.get("disposition"):
        diagnostics.append(
            _diag(
                "closure-scope-disposition-mismatch",
                "closure_packet.disposition",
                "closure packet and delivery scope must preserve the same RVTF disposition",
            )
        )
    scope_kind = closed_scope.get("scope_kind") if closed_scope is not None else None
    if scope_kind is None and isinstance(scope_ref, str) and ":" in scope_ref:
        scope_kind = scope_ref.split(":", 1)[0]
    if scope_kind == "goal":
        return diagnostics

    continuation = closure.get("continuation")
    if not isinstance(continuation, Mapping):
        diagnostics.append(
            _diag(
                "missing-non-goal-continuation",
                "closure_packet.continuation",
                "new 0.4 non-goal closure packets require continuation",
            )
        )
        return diagnostics
    parent_ref = continuation.get("parent_scope_ref")
    parent = scopes.get(parent_ref)
    if not isinstance(parent_ref, str) or not parent_ref:
        diagnostics.append(
            _diag(
                "missing-continuation-parent",
                "closure_packet.continuation.parent_scope_ref",
                "non-Goal continuation requires a parent_scope_ref",
            )
        )
    if scopes and parent is None and isinstance(parent_ref, str) and parent_ref:
        diagnostics.append(
            _diag("unknown-continuation-parent", "closure_packet.continuation.parent_scope_ref", "continuation parent does not resolve")
        )
    if closed_scope is not None and closed_scope.get("parent_scope_ref") != parent_ref:
        diagnostics.append(
            _diag(
                "continuation-parent-mismatch",
                "closure_packet.continuation.parent_scope_ref",
                "continuation parent must match the closed scope parent",
            )
        )
    if parent is not None and continuation.get("parent_disposition") != parent.get("disposition"):
        diagnostics.append(
            _diag(
                "continuation-parent-disposition-mismatch",
                "closure_packet.continuation.parent_disposition",
                "continuation parent disposition must preserve current parent truth",
            )
        )
    if parent is None and continuation.get("parent_disposition") not in CLOSURE_DISPOSITIONS | {"unknown"}:
        diagnostics.append(
            _diag(
                "invalid-continuation-parent-disposition",
                "closure_packet.continuation.parent_disposition",
                "continuation requires the known parent disposition or unknown for detached advisory work",
            )
        )
    mode = continuation.get("continuation_mode")
    if mode not in CONTINUATION_MODES:
        diagnostics.append(
            _diag(
                "invalid-continuation-mode",
                "closure_packet.continuation.continuation_mode",
                "continuation_mode must be durable_host, artifact_only, or advisory",
            )
        )
    if mode in {"durable_host", "artifact_only"} and (
        not continuation.get("authority_ref") or not continuation.get("resume_locator")
    ):
        diagnostics.append(
            _diag(
                "missing-continuation-authority",
                "closure_packet.continuation",
                f"{mode} continuation requires authority_ref and resume_locator",
            )
        )
    if mode == "advisory" and not continuation.get("authority_ref"):
        diagnostics.append(
            _diag(
                "missing-advisory-authority",
                "closure_packet.continuation.authority_ref",
                "advisory continuation must identify the user or external orchestrator authority",
            )
        )
    remaining = continuation.get("remaining_scope_refs")
    if not isinstance(remaining, list):
        diagnostics.append(
            _diag(
                "invalid-continuation-remaining-scopes",
                "closure_packet.continuation.remaining_scope_refs",
                "remaining_scope_refs must be a list",
            )
        )
    else:
        for index, remaining_ref in enumerate(remaining):
            if scopes and remaining_ref not in scopes:
                diagnostics.append(
                    _diag(
                        "unknown-continuation-remaining-scope",
                        f"closure_packet.continuation.remaining_scope_refs[{index}]",
                        f"remaining scope {remaining_ref!r} does not resolve",
                    )
                )
            elif remaining_ref in scopes and scopes[remaining_ref].get("disposition") in CLOSED_DISPOSITIONS:
                diagnostics.append(
                    _diag(
                        "closed-scope-listed-as-remaining",
                        f"closure_packet.continuation.remaining_scope_refs[{index}]",
                        f"closed scope {remaining_ref!r} is not remaining work",
                    )
                )
    conditions = continuation.get("next_entry_conditions")
    if not isinstance(conditions, list) or (remaining and not _string_list(conditions)):
        diagnostics.append(
            _diag(
                "missing-continuation-entry-conditions",
                "closure_packet.continuation.next_entry_conditions",
                "remaining work requires concrete next entry conditions",
            )
        )
    action = continuation.get("execution_action")
    if action not in CONTINUATION_ACTIONS:
        diagnostics.append(
            _diag(
                "invalid-continuation-action",
                "closure_packet.continuation.execution_action",
                "execution_action must be continue, stop, await_owner, or host_boundary",
            )
        )
    stop_basis = continuation.get("stop_basis")
    if action in {"stop", "host_boundary"}:
        if stop_basis not in STOP_BASES:
            diagnostics.append(
                _diag(
                    "missing-continuation-stop-basis",
                    "closure_packet.continuation.stop_basis",
                    "actual stop or host boundary requires a canonical stop_basis",
                )
            )
    elif stop_basis is not None:
        diagnostics.append(
            _diag(
                "unexpected-continuation-stop-basis",
                "closure_packet.continuation.stop_basis",
                "stop_basis is allowed only for an actual stop or host boundary",
            )
        )
    return diagnostics


def validate_document(document: Any) -> list[Diagnostic]:
    """Run every focused validator and return deterministic diagnostics."""

    shape_diagnostics = validate_document_shape(document)
    if not isinstance(document, Mapping):
        return shape_diagnostics
    diagnostics = list(shape_diagnostics)
    diagnostics.extend(validate_unique_identifiers(document))
    diagnostics.extend(validate_delivery_scopes(document))
    diagnostics.extend(validate_evidence_registry(document))
    diagnostics.extend(validate_verification_policy(document))
    diagnostics.extend(validate_review_governance(document))
    diagnostics.extend(validate_closure_continuation(document))
    return sorted(set(diagnostics), key=lambda diagnostic: (diagnostic.path, diagnostic.code, diagnostic.message))


def load_document(path: Path) -> tuple[Any, list[Diagnostic]]:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")), []
    except (OSError, yaml.YAMLError) as error:
        return None, [_diag("yaml-load-error", str(path), str(error))]


def expected_error_code(path: Path) -> str | None:
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            match = EXPECTED_ERROR_RE.fullmatch(line)
            return match.group(1) if match else None
    except OSError:
        return None
    return None


def _format_diagnostics(diagnostics: Sequence[Diagnostic]) -> str:
    return ", ".join(f"{diagnostic.code}@{diagnostic.path}" for diagnostic in diagnostics) or "none"


def run_fixture_contract(root: Path) -> int:
    fixture_root = root / "scripts" / "fixtures" / "schema"
    positive_paths = sorted((fixture_root / "positive").glob("*.yaml"))
    negative_paths = sorted((fixture_root / "negative").glob("*.yaml"))
    if not positive_paths or not negative_paths:
        print(
            f"error: expected positive and negative YAML fixtures under {fixture_root}",
            file=sys.stderr,
        )
        return 2

    accepted = 0
    expected_rejected = 0
    failures = 0
    for path in positive_paths:
        document, load_diagnostics = load_document(path)
        diagnostics = load_diagnostics or validate_document(document)
        relative = path.relative_to(fixture_root)
        if diagnostics:
            failures += 1
            print(f"FAIL {relative}: expected accepted; diagnostics={_format_diagnostics(diagnostics)}")
        else:
            accepted += 1
            print(f"PASS {relative}: accepted")

    for path in negative_paths:
        expected = expected_error_code(path)
        document, load_diagnostics = load_document(path)
        diagnostics = load_diagnostics or validate_document(document)
        relative = path.relative_to(fixture_root)
        actual_codes = [diagnostic.code for diagnostic in diagnostics]
        if expected is not None and len(diagnostics) == 1 and actual_codes == [expected]:
            expected_rejected += 1
            print(f"PASS {relative}: rejected [{expected}]")
        else:
            failures += 1
            expectation = expected or "missing-valid-expected-error-comment"
            print(
                f"FAIL {relative}: expected exactly [{expectation}]; "
                f"diagnostics={_format_diagnostics(diagnostics)}"
            )

    print(
        "schema fixtures: "
        f"{accepted} accepted, {expected_rejected} expected rejected, {failures} failures"
    )
    return 0 if failures == 0 else 1


def main(argv: Sequence[str]) -> int:
    if argv:
        print("usage: validate-schema-examples.py", file=sys.stderr)
        return 2
    return run_fixture_contract(Path(__file__).resolve().parent.parent)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
