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

Issue #15 must select the execution/runtime substrate by evidence, not preference. LEAN and NautilusTrader must be exercised through the same finance-quant contracts and normalized receipts. A1 is conjunctive: SDD/PDD, static/IR validation, unit/regression, property/state-machine testing, hidden acceptance, mutation testing, differential/metamorphic testing, repeated determinism, clean-environment validation, and chaos/fault injection must all pass before disposition or promotion.

The A1 SDD/PDD is `docs/plans/A1_EXECUTION_RUNTIME_CONFORMANCE.md`; the executable runtime contract is `contracts/execution/runtime-conformance-v1.json`. Stable properties `FQ-PROP-015` through `FQ-PROP-022` remain bound in the property catalog.

## LEAN production candidate status

The finance-quant LEAN slice directly exercises pinned LEAN commit `185c691b89f28bd68e48d53c02147415134975f0` through production `EquityFillModel.MarketOnOpenFill`, without brokerage credentials or the LEAN CLI, against `fixtures/execution/a1-lean-fill-probe-v1.json`. Candidate evidence remains `runtime_disposition: PENDING` and `authority: NONE`.

Exact-head runtime-candidates run `32884104244` completed **SUCCESSFULLY** on implementation head `aeb5cd4ab6f53a966bbc344e45afde1b2a552573`. Its `lean-production-fill-probe` job verified the candidate pin/license, built the production LEAN fill-model probe, ran three deterministic candidate probes, and uploaded A1 receipts. The semantic evidence is the contracted fill (`quantity=5`, `price=11`, `fill_time=2026-06-02T13:30:00Z`, source `bar-2`) with identical canonical candidate/reference receipt hashes across repeated runs.

This is a genuine LEAN production-slice pass, but it is **not** an A1 runtime disposition. NautilusTrader evidence and all remaining conjunctive A1 gates are still required.

## NautilusTrader production candidate status

The candidate is pinned to NautilusTrader release `v1.230.0`, upstream commit `8160730c7c550480b0a439fb11086a4c4de15f0b`, with LGPL-3.0-only source licensing recorded in `contracts/execution/nautilus-a1-candidate-pin-v1.json`. Credentials and the Nautilus CLI are not required for the intended A1 production backtest/matching probe.

Exact pinned-source analysis of `nautilus_trader/backtest/engine.pyx` establishes the production ordering needed by the unchanged A1 daily-bar contract: external bar data is first sent to `SimulatedExchange.process_bar` and only afterward delivered through the data engine to strategies; trade-bar matching processes the bar open first; an opening gap enables market filling; and matching iteration uses the bar `ts_init`. Therefore a market order submitted from the prior bar can be resting before the next bar's open is auctioned.

The runtime-candidate workflow now contains a fail-closed **source-production-matching preflight** which checks the exact upstream commit, license, these production source-path invariants, and emits a deterministic provenance receipt. This preflight is deliberately marked `production_probe_status: NOT_YET_EXECUTED`: it is not executable Nautilus fill evidence and cannot be used to select or disposition the runtime.

## Validation status

- Prior durable head `854773bc45614907e2c53c395a1f87b3cc3d8f85` is explicitly green: tests run `32888794288`, legacy phase-b run `32888794305`, bootstrap-assurance run `32888794317`, and A1 runtime-candidates run `32888794347` all completed successfully.
- Runtime-candidates run `32884104244`: **PASS** for the credential-free LEAN production fill probe and three-run canonical determinism.
- The previous handoff-format defect (`Next:` instead of required `Next exact action`) was repaired without changing runtime semantics, tests, properties, mutation thresholds, PIT invariants, or authority.
- The newly added Nautilus production-matching preflight still requires exact-head CI validation after this state update.

A1 remains **IN_PROGRESS**. Executable NautilusTrader production candidate evidence, hidden acceptance, mutation-threshold evidence, broader metamorphic coverage, complete candidate chaos/fault campaigns, and final conjunctive gate receipts remain outstanding. No primary runtime may be selected yet.

## Next exact action

1. Require exact-head tests/bootstrap-assurance/runtime-candidates to remain green with the pinned Nautilus source-production preflight; fix any real failure without weakening tests or invariants.
2. Implement the minimal credential-free **executable NautilusTrader production fill probe** against exactly the same public daily-bar decision/fill semantics and normalized comparison classes used by LEAN/reference. Do not substitute a custom/synthetic fill path for the production matching engine.
3. Run three canonical deterministic Nautilus probes and differential receipts, then continue the remaining A1 hidden, mutation, metamorphic, clean-environment, and chaos/fault evidence for both candidates.
4. Only after every conjunctive A1 gate passes may #15 record candidate dispositions and select a primary runtime.

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
