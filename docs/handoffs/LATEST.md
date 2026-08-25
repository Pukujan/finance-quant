# Handoff — A1 Nautilus executable production nonconformance

Date: 2026-08-25  
Branch: `bootstrap/oss-autonomous-trader-replatform`  
Active issue: #15  
Assurance phase: A1  
Project status: `A1_LEAN_DIFFERENTIAL_SLICE`

The required A1 governance/state inputs were re-read before modification: `AGENTS.md`, `docs/CURRENT_STATE.md`, issue #15, `docs/handoffs/LATEST.md`, and `contracts/assurance/capability-assurance-v1.json`. The prior exact head `35e3b57d21687e2e040324ce9d48abec50512b6c` was verified fully green across tests, legacy phase-b, bootstrap assurance, and runtime candidates before executable Nautilus work began.

This run added a credential-free executable NautilusTrader `v1.230.0` probe against exact upstream commit `8160730c7c550480b0a439fb11086a4c4de15f0b`. The probe uses production `BacktestEngine` / `SimulatedExchange`, the unchanged public two-bar A1 fixture, a native market order, and no custom fill model. The first harness error—single-currency CASH venue incompatibility with the synthetic currency pair—was corrected by using Nautilus multi-currency CASH mode without changing any execution oracle or fixture semantics.

The corrected native-GTC production execution produced a substantive deterministic mismatch: quantity `5` filled at `10.00` at `2026-06-01T20:00:00Z` from `bar-1`, while the A1 contract requires the earliest eligible next-bar fill at `11.00` at `2026-06-02T13:30:00Z` from `bar-2`. This violates critical `FQ-PROP-015`; the oracle was not changed to accept it.

A production-native `AT_THE_OPEN` attempt did not fill. Exact pinned `nautilus_trader/backtest/engine.pyx` explains why: `_process_market_order` explicitly rejects `AT_THE_OPEN` and `AT_THE_CLOSE` time-in-force as not currently supported. This eliminates the obvious market-on-open translation without relying on newer documentation or a synthetic execution path.

The candidate workflow was then hardened so this semantic mismatch is recorded as candidate evidence rather than confused with a broken harness. Runtime-candidates run `32905724960` completed successfully: LEAN again conformed through its exact pinned production `MarketOnOpenFill` path, while Nautilus ran three identical native-GTC production probes and emitted `semantic_conformance: FAIL`, `failed_property: FQ-PROP-015`, with final `runtime_disposition: PENDING`. Workflow success means the evaluation operated correctly; it does not waive the Nautilus mismatch.

A1 remains **IN_PROGRESS**. Trading authority remains **NONE**. Autonomous paper trading and live capital remain **DISABLED**. Sealed-holdout exact cases/labels were not accessed.

## Next exact action

1. Require exact-head tests, legacy phase-b, bootstrap-assurance, and runtime-candidates to be green after this durable-state commit; repair only genuine implementation/state defects without weakening tests or invariants.
2. Before assigning Nautilus a final `REFERENCE_ONLY` or `REJECT` disposition, evaluate only PIT-safe thin-adapter mechanisms that still use production matching and are permitted by the A1 SDD/PDD to eliminate same-bar submission. Do not use custom fill models, future bar values, or semantic waivers. If none conforms, preserve the deterministic `FQ-PROP-015` failure.
3. Continue A1 hidden acceptance, mutation, metamorphic, determinism/clean-environment, and chaos/fault evidence for runtime paths still eligible under the contract.
4. Do not select a primary runtime, start #16, grant paper authority, enable live capital, or access sealed holdout contents until every required A1 gate is green and durable state explicitly permits promotion.

Append-only record: `docs/handoffs/2026-08-25-a1-nautilus-executable-nonconformance.md`.
