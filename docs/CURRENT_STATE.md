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
- `finance_quant/execution/lean_a1.py` normalizes credential-free LEAN evidence for only the shared daily-bar subset, replaces candidate-native order/fill/ledger IDs with deterministic finance-quant semantic identities, and rejects same-bar, future-known, ambiguous-lineage, unsupported-status, and unsupported-ledger semantics;
- `finance_quant/execution/differential.py` classifies every required normalized receipt field as exact, tolerance-bounded, or explicitly permitted top-level runtime metadata and fails closed if a new required field has no comparison class;
- `tools/lean_a1_probe/` now exercises the pinned production LEAN `EquityFillModel.MarketOnOpenFill` directly, without brokerage credentials or the LEAN CLI, against `fixtures/execution/a1-lean-fill-probe-v1.json`;
- `scripts/run_lean_a1_fill_probe.py` derives candidate accounting from the actual LEAN fill, normalizes it, compares it to the independent reference receipt with `assert_normalized_receipts_conform`, and leaves runtime disposition `PENDING`;
- `tests/test_lean_a1_fill_probe.py` covers the pin/authority boundary, synthetic normalization/conformance, candidate-fill-derived accounting, and wrong execution-instant rejection;
- `.github/workflows/a1-runtime-candidates.yml` checks the exact LEAN source pin/license, builds the production fill-model probe, executes three independent candidate probes, requires byte-equivalent raw/evidence outputs, and preserves raw diagnostics even on failure.

This slice is candidate evidence only. It does **not** select LEAN, grant paper/live trading authority, or satisfy the remaining A1 gates by itself.

## Validation status for current A1 work

The first thin LEAN adapter head `c3c4ca1cb411c6b3700505044e30f85f424efb61` passed tests `32872417271`, Phase-B `32872417669`, and bootstrap-assurance `32872417964`.

The subsequent field-class differential implementation head `9e91ff07b97c82b45be38ab70b913743920c3a40` had Phase-B `32873391446` **PASS** and observed bootstrap-assurance fresh-environment/contracts/full-regression/smoke/TLA steps **PASS** before documentation began.

The first credential-free production LEAN probe head `24976efc7587f83175e24442f281b9a4b7b577b3` produced:

- tests `32875746688`: **PASS**;
- Phase-B `32875746634`: **PASS**;
- A1 runtime-candidates `32875746733`: **FAIL** specifically in `Run three deterministic candidate probes`; pin/license verification and the production LEAN probe build passed.

Investigation against pinned LEAN commit `185c691b89f28bd68e48d53c02147415134975f0` found a harness contract defect: LEAN `Order.Time` is UTC and its own `EquityFillModel` tests convert the local submission instant to UTC before constructing `MarketOnOpenOrder`, while the first finance-quant probe passed a New York-local wall-clock `DateTime` directly. Commit `6e21bc0fc51f29124ada8eef7c925be88d3975fc` corrects the order timestamp to UTC without changing execution semantics or the differential oracle. Commit `57758d7d8ab81c1e6445ec42ec970c2b1c788d91` preserves raw stdout/stderr artifacts on candidate failure while still failing closed on any nonzero probe status.

On exact implementation head `57758d7d8ab81c1e6445ec42ec970c2b1c788d91`, A1 runtime-candidates run `32876861792` was still **IN_PROGRESS** when this durable state was written. Exact-head Phase-B and the other ordinary workflows were also still running/rechecking after the fix. Do not record candidate conformance success until those exact runs complete successfully.

Local clone/test execution remains unavailable in this automation environment because direct `github.com` resolution is unavailable; GitHub Actions is the executable validation source for the production LEAN probe.

A1 remains **IN_PROGRESS**. NautilusTrader candidate evidence, hidden acceptance, mutation threshold evidence, broader metamorphic coverage, candidate fault/chaos campaigns, and complete gate receipts remain outstanding. No primary runtime may be selected yet.

## Next exact action

1. Recheck GitHub Actions for exact implementation head `57758d7d8ab81c1e6445ec42ec970c2b1c788d91`. If A1 runtime-candidates fails, inspect the preserved `a1-lean-production-fill-probe` diagnostics and fix the production probe without weakening `assert_normalized_receipts_conform`, deterministic reruns, or authority/PIT invariants.
2. If the exact LEAN candidate run passes, record its three-run raw/evidence equivalence and exact workflow receipt; then add the corresponding thin **NautilusTrader** adapter and credential-free candidate evidence for exactly the same public daily-bar subset and comparison classes before widening either runtime.
3. Continue the remaining required A1 hidden, mutation, metamorphic, deterministic/clean-environment, and chaos/fault evidence for both candidates.
4. Only after every conjunctive A1 gate passes may #15 record candidate dispositions and name a primary runtime.

Do not start Autonomous Trader v0 (#16), enable autonomous paper authority, enable live capital, or inspect sealed-holdout exact cases/labels while A1 remains incomplete.

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
10. `tools/lean_a1_probe/Program.cs`, `scripts/run_lean_a1_fill_probe.py`, `tests/test_lean_a1_fill_probe.py`, and `.github/workflows/a1-runtime-candidates.yml`
11. relevant execution/IR/property specs and tests
