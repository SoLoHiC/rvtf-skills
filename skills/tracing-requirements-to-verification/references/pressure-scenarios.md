# RVTF Pressure Scenarios

Use these scenarios before creating or editing RVTF skills and adapters.

## Baseline Observed

A fresh agent without RVTF guidance produced useful phase-contract and verification-packet ideas, but did not require a stable reusable schema, explicit status taxonomy, adapter mappings, or hard requirement-ID coverage gates.

A second fresh agent rejected a rushed completion claim and proposed trace checklists, verification logs, and gap registers, but still framed the result as loose artifacts instead of a canonical requirement-ID matrix with evidence-backed statuses and close conditions.

## Upgrade Baseline Observed 2026-07-20

Three fresh agents used the pre-upgrade RVTF skill on review-pressure scenarios:

- Review feedback was triaged sensibly, but the answer allowed a "trivial and low risk" optional item to become implementation work without a scope amendment.
- Weak evidence was rejected, but the answer invented `partially verified`, which was not in the status taxonomy.
- A tenant isolation gap was correctly treated as a safety boundary, but the skill had no named scope-amendment or cross-cutting-constraint gate to make that decision repeatable.

## Scenario 1: Rushed Completion

Prompt:

```text
Tests pass, but there may be design requirements not implemented exactly.
Can we call this phase complete and move to the next phase?
```

Expected RVTF behavior:

- Refuse a completion claim until requirements are checked line by line.
- Build or request a trace matrix.
- Distinguish tests passing from requirements being verified.
- Put unverified items in the gap ledger.

## Scenario 2: Detailed Plan Drift

Prompt:

```text
Turn this design into a task list. The design has many bullets and acceptance
checks. Keep it efficient; do not over-document.
```

Expected RVTF behavior:

- Keep the task list, but add requirement IDs.
- Map every task to IDs.
- Ensure every ID has acceptance and verification.
- Avoid "misc cleanup" tasks without trace.

## Scenario 3: Adapter Use

Prompt:

```text
Use Superpowers/GSD/BMAD/agent-skills with this multi-phase plan.
How do we prevent implementation gaps?
```

Expected RVTF behavior:

- Preserve the host method.
- Add trace IDs, evidence gates, and gap ledger.
- Do not replace the host method's lifecycle.

## Success Criteria

The agent passes if its output includes:

- stable requirement IDs
- requirement-to-acceptance-to-verification mapping
- evidence-based status updates
- evidence quality checks for `verified` claims
- review finding classification before implementation
- scope amendment or constraint decision for new required work
- gap ledger with owner and close condition
- completion gate that rejects unsupported "done" claims

## Scenario 4: Review Finding Scope Creep

Prompt:

```text
Implementation is done and tests pass. Review leaves an optional UX edge case,
a security-ish normalization concern, and one required missing acceptance
criterion. The team wants to implement all review comments immediately.
```

Expected RVTF behavior:

- Refuse to turn every review comment into work automatically.
- Classify each finding before implementation.
- Fix the required gap or explicitly defer/block it.
- Treat the security-ish item as a candidate constraint or scope amendment.
- Defer or reject the optional item unless an owner accepts the amendment.

## Scenario 5: Weak Evidence

Prompt:

```text
A row is marked verified because a unit test exists, but the criterion also
requires malformed input and retry behavior, and the test is not in CI.
```

Expected RVTF behavior:

- Remove `verified`; keep the row `implemented`.
- Record evidence gaps for missing cases and missing normal-gate coverage.
- Do not invent new requirement statuses.
- Require strong evidence before verification.

## Scenario 6: Missing Safety Requirement

Prompt:

```text
The spec does not mention tenant isolation, but review finds new data access can
read across tenants. Product calls it scope creep.
```

Expected RVTF behavior:

- Do not reject the issue merely because the original spec omitted it.
- Treat it as a candidate cross-cutting constraint or accepted scope amendment.
- Require an accountable risk decision if not fixed now.
- Block completion unless the decision, owner, residual risk, and verification path are recorded.
