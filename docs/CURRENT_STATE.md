# Current project state

<!-- MACHINE-STATE: architecture=OSS_FIRST_AUTONOMOUS_TRADER_REPLATFORM status=A1_LEAN_DIFFERENTIAL_SLICE assurance=A1 active_issue=15 -->

## Active direction

The active master plan is GitHub issue **#12 — OSS-first autonomous trader + visual research console**. Current work is **#15 — NautilusTrader vs LEAN execution/runtime conformance bakeoff**, governed by assurance phase **A1** in issue #14 and `contracts/assurance/capability-assurance-v1.json`.

The old Phase-B execution plan (#11) remains **PARKED** and preserved as a legacy oracle. Do not treat it as active sequencing authority.

## Current capability and authority

- Project status: **A1_LEAN_DIFFERENTIAL_SLICE**
- Bootstrap machine status: **BOOTSTRAP_COMPLETE**
- Assurance phase: **A1 — OSS execution/runtime bakeoff**
- Trading authority: **NONE**
- Autonomous paper trading: **DISABLED**
- Live capital: **DISABLED**
- Sealed holdout: isolated; ordinary agents may not inspect exact cases/labels

## A1 objective and mandatory gates

Issue #15 must select the execution/runtime substrate by evidence, not preference. LEAN and NautilusTrader must be exercised through the same finance-quant contracts and normalized receipts. A1 is conjunctive: SDD/PDD, static/IR validation, unit/regression, property/state-machine testing, hidden acceptance, mutation testing, differential/metamorphic testing, repeated determinism, clean-environment validation, and chaos/fault injection must all pass before final candidate dispositions or promotion.

The A1 SDD/PDD is `docs/plans/A1_EXECUTION_RUNTIME_CONFORMANCE.md`; the executable runtime contract is `contracts/execution/runtime-conformance-v1.json`. Stable properties `FQ-PROP-015` through `FQ-PROP-022` remain bound in the property catalog.

## LEAN production candidate status

The finance-quant LEAN slice directly exercises pinned LEAN commit `185c691b89f28bd68e48d53c02147415134975f0` through production `EquityFillModel.MarketOnOpenFill`, without brokerage credentials or the LEAN CLI, against `fixtures/execution/a1-lean-fill-probe-v1.json`. Candidate evidence remains `runtime_disposition: PENDING` and `authority: NONE`.

Runtime-candidates run `32905724960` again completed the LEAN production job successfully on implementation head `9cdd7cdc9cd4d43bea7ac6f7b9589d9f2d14c0c0`. It built the exact pinned source and reproduced the contracted three-run fill (`quantity=5`, `price=11`, `fill_time=2026-06-02T13:30:00Z`, source `bar-2`). This remains production-slice evidence, not a final runtime disposition.

## NautilusTrader production candidate status

NautilusTrader remains pinned to release `v1.230.0`, exact upstream commit `8160730c7c550480b0a439fb11086a4c4de15f0b`, LGPL-3.0-only, with no credentials or Nautilus CLI required and authority NONE.

The executable production probe now reaches the pinned `BacktestEngine` / `SimulatedExchange` matching path using the same public two-bar fixture and unchanged finance-quant market intent. With native GTC market semantics, an intent submitted from bar 1 is filled immediately on bar 1 at `10.00` and `2026-06-01T20:00:00Z`, rather than at the next eligible bar open `11.00` at `2026-06-02T13:30:00Z`. This violates critical property `FQ-PROP-015`; the oracle was not weakened or normalized to accept the candidate behavior.

The remaining obvious production-native market-on-open semantic is also unavailable in the pinned version: exact `nautilus_trader/backtest/engine.pyx` rejects `AT_THE_OPEN` and `AT_THE_CLOSE` time-in-force as “not currently supported.” An attempted `AT_THE_OPEN` probe therefore produced no fill, confirming that switching time-in-force is not a conforming workaround.

Runtime-candidates run `32905724960` now treats this as candidate-evaluation evidence rather than a broken test: it verifies the exact pin/source facts, runs the native GTC production probe three times, requires identical same-bar observations, writes `semantic_conformance: FAIL` / `failed_property: FQ-PROP-015`, and leaves `runtime_disposition: PENDING`. The workflow itself is green because it correctly detects and records the candidate’s deterministic semantic failure; green workflow status does **not** mean Nautilus conforms.

The A1 specification permits candidate-specific same-bar defaults to be disabled or normalized away, but any such adapter must remain PIT-safe and must still use production matching. No adapter workaround has yet been accepted. Final `REFERENCE_ONLY` or `REJECT` disposition is therefore deferred until the A1 gate process reaches the candidate-disposition gate.

## Validation status

- Prior durable head `35e3b57d21687e2e040324ce9d48abec50512b6c` was fully green across tests, legacy phase-b, bootstrap assurance, and runtime candidates before executable Nautilus work began.
- Runtime-candidates run `32905724960`: **PASS as an evaluation workflow** on implementation head `9cdd7cdc9cd4d43bea7ac6f7b9589d9f2d14c0c0`; LEAN production conformance passed and Nautilus deterministic production nonconformance was correctly detected and recorded.
- Earlier Nautilus execution run `32905286137` produced the decisive native-GTC observation: `5 @ 10.00` on `bar-1`. Run `32905508650` then verified that `AT_THE_OPEN` does not produce a conforming fill; exact pinned source explains this by explicitly rejecting that TIF.
- Ordinary tests, legacy phase-b, and bootstrap-assurance for implementation head `9cdd7cdc9cd4d43bea7ac6f7b9589d9f2d14c0c0` were still running when this durable state was written. The documentation/state commit itself must also be validated before the baseline can be called fully green.

A1 remains **IN_PROGRESS**. Hidden acceptance, mutation-threshold evidence, broader metamorphic coverage, complete clean-environment/determinism evidence for the surviving conforming path, chaos/fault campaigns, and final candidate dispositions remain outstanding. No primary runtime may be selected yet.

## Next exact action

1. Require exact-head tests, legacy phase-b, bootstrap-assurance, and runtime-candidates to finish green after this durable-state update; fix any genuine failure without weakening an invariant.
2. Before finalizing Nautilus as `REFERENCE_ONLY` or `REJECT`, evaluate only production-matching, PIT-safe thin-adapter mechanisms permitted by the A1 SDD/PDD for eliminating same-bar submission. Do not use a custom fill model, future bar values, hidden cases, or semantic waivers. If no such mechanism satisfies the unchanged public differential, retain the deterministic `FQ-PROP-015` failure as the candidate result.
3. Continue the remaining conjunctive A1 hidden-acceptance, mutation, metamorphic, determinism/clean-environment, and chaos/fault gates for the runtime path(s) still eligible under the contract, while preserving Nautilus negative evidence.
4. Only after every required A1 gate is green may #15 assign final candidate dispositions and select a primary runtime.

Do not start #16, enable autonomous paper authority, enable live capital, or inspect sealed-holdout exact cases/labels while A1 remains incomplete.

## Required read order for a fresh session

1. `AGENTS.md`
2. this file
3. GitHub issue #12 and active issue #15
4. `docs/handoffs/LATEST.md`
5. `contracts/assurance/capability-assurance-v1.json`
6. `docs/plans/A1_EXECUTION_RUNTIME_CONFORMANCE.md`
7. `contracts/execution/runtime-conformance-v1.json`
8. relevant execution adapter/probe/workflow files and tests
