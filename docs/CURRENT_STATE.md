# Current project state

<!-- MACHINE-STATE: architecture=OSS_FIRST_AUTONOMOUS_TRADER_REPLATFORM status=A1_LEAN_DIFFERENTIAL_SLICE assurance=A1 active_issue=15 -->

## Active direction

The active master plan is GitHub issue **#12 — OSS-first autonomous trader + visual research console**.

Bootstrap issue **#13** is complete. Current work is **#15 — NautilusTrader vs LEAN execution/runtime conformance bakeoff**, governed by assurance phase **A1** in issue #14 and `contracts/assurance/capability-assurance-v1.json`.

The old Phase-B execution plan (#11) remains **PARKED**. Its PIT, IR, property catalog, sealed holdout, mutation-hardening, deterministic rerun, reference-interpreter, TLA+, LEAN/Qlib, and evidence assets remain preserved as legacy baselines/oracles. Do not treat #11 as active sequencing authority.

## Current capability

- Project status: **A1_LEAN_DIFFERENTIAL_SLICE**
- Bootstrap machine status: **BOOTSTRAP_COMPLETE**
- Assurance phase: **A1 — OSS execution/runtime bakeoff**
- Trading authority: **NONE**
- Autonomous paper trading: **DISABLED**
- Live capital: **DISABLED**
- Frontend: roadmap/vertical-slice policy only; **OPERATOR_ONLY** authority
- Sealed holdout: remains isolated; ordinary agents may not inspect exact cases/labels

## A0 bootstrap evidence

A0 completed after the bootstrap branch passed the full validation stack on 2026-08-25. The validated implementation head was `b01e9be2c6dd9eb27a1189dc5454f0e7a61db2ef` before the semantic state-transition commit.

Authoritative successful workflow runs for that validated implementation head:

- tests: run `32850720334` — full pytest + smoke: **PASS**;
- Phase-B legacy oracle: run `32850720245` — benchmark + three-run determinism + `verify --phase-b`: **PASS**;
- bootstrap assurance: run `32850720179` — contracts/docs/property oracles + pinned non-skippable TLA/TLC + full Windows validation + fresh isolated environment: **PASS**.

A0 validation uncovered and fixed real defects rather than weakening gates: legacy TLA syntax/protocol holes, fresh-venv package installation, cross-platform README generated-block checking, temp-directory B1–B5 artifact references, and LEAN custom-data absolute-path nondeterminism.

## Active A1 objective

Issue #15 must select the execution/runtime substrate by evidence, not preference. NautilusTrader and LEAN must be exercised through the same finance-quant execution contracts and normalized receipts.

A1 requires, at minimum, SDD/PDD, static/IR validation, unit/regression, property/state-machine testing, hidden acceptance, mutation testing, differential and metamorphic testing, repeated determinism, clean-environment validation, and chaos/fault injection.

The A1 SDD/PDD is defined in `docs/plans/A1_EXECUTION_RUNTIME_CONFORMANCE.md` and `contracts/execution/runtime-conformance-v1.json`. Stable properties `FQ-PROP-015` through `FQ-PROP-022` are bound into the global property catalog.

The executable finance-quant-owned oracle/candidate slice now includes:

- `finance_quant/execution/conformance.py` fail-closes on A1 authority/contract drift and validates/canonicalizes normalized receipts;
- `finance_quant/execution/reference.py` is a deliberately tiny independent daily-bar semantic oracle, not a production runtime;
- `finance_quant/execution/lean_a1.py` is the first thin candidate adapter. It normalizes already-produced, credential-free LEAN evidence for only the shared daily-bar subset, replaces candidate-native order/fill/ledger IDs with deterministic finance-quant semantic identities, and rejects same-bar, future-known, ambiguous-lineage, unsupported-status, and unsupported-ledger semantics;
- `finance_quant/execution/differential.py` classifies every required normalized receipt field as exact, tolerance-bounded, or explicitly permitted top-level runtime metadata and fails closed if a new required field has no comparison class;
- `tests/test_execution_conformance.py` and `tests/test_execution_reference.py` cover the contract/reference invariants;
- `tests/test_execution_lean_a1.py` covers LEAN normalization and fail-closed adapter behavior;
- `tests/test_execution_differential.py` proves the public shared-subset reference/LEAN fixtures converge semantically and detects exact/numeric drift.

This slice does **not** run a production LEAN engine, select LEAN or NautilusTrader, or grant paper/live trading authority. Candidate runtime execution evidence remains required before disposition.

## Validation status for current A1 work

The first thin LEAN adapter head `c3c4ca1cb411c6b3700505044e30f85f424efb61` passed all three GitHub workflows:

- tests run `32872417271`: **PASS**, including `python -m pytest tests -q` with **916 passed, 25 skipped**, plus `python scripts/smoke.py`;
- Phase-B legacy oracle run `32872417669`: **PASS**;
- bootstrap-assurance run `32872417964`: **PASS**, including contracts/status/property checks, fresh-environment full pytest+verify, full regression+smoke+three-run legacy determinism, and non-skipped TLA/TLC.

The subsequent field-class differential implementation head is `9e91ff07b97c82b45be38ab70b913743920c3a40`. On that exact implementation head, bootstrap-assurance fresh-environment, contract/property checks, full regression, smoke, and TLA/TLC have passed, and Phase-B run `32873391446` passed. Tests run `32873391360` and bootstrap-assurance run `32873391294` were still finishing wrapper/legacy steps when durable documentation began; recheck exact final branch-head CI after these documentation commits before widening scope.

Local clone/test execution remains unavailable because this automation environment cannot resolve `github.com`; GitHub Actions are the executable validation source for this session.

A1 remains **IN_PROGRESS**. Actual candidate-runtime execution evidence, NautilusTrader adapter/evidence, hidden acceptance, mutation threshold evidence, broader metamorphic coverage, candidate repeated determinism, and chaos/fault campaigns remain outstanding. No primary runtime may be selected yet.

## Next exact action

1. Verify GitHub Actions on the exact current branch head and fix any regression without weakening tests or invariants.
2. Add executable credential-free **LEAN candidate-run evidence** for the same public daily-bar subset and feed its normalized receipt through `assert_normalized_receipts_conform`; do not treat the historical Phase-B subprocess stub as candidate proof.
3. Add the corresponding thin NautilusTrader adapter for exactly the same subset and comparison classes before widening either candidate.
4. Continue hidden, mutation, metamorphic, repeated determinism, clean-environment, and chaos evidence for both candidates before any runtime disposition.

Do not select a primary runtime until all A1 required gates pass. Do **not** start Autonomous Trader v0 (#16) until #15 has explicit runtime dispositions and every required A1 gate passes.

## Required read order for a fresh session

1. `AGENTS.md`
2. this file
3. GitHub issue #12 and active issue #15
4. `docs/handoffs/LATEST.md`
5. `contracts/assurance/capability-assurance-v1.json`
6. `docs/plans/A1_EXECUTION_RUNTIME_CONFORMANCE.md`
7. `contracts/execution/runtime-conformance-v1.json`
8. `contracts/properties/finance-quant-properties-v1.json`
9. `finance_quant/execution/conformance.py`, `reference.py`, `lean_a1.py`, and `differential.py`
10. relevant execution/IR/property specs and tests
