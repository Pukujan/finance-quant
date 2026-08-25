# Handoff — A1 Nautilus production-matching preflight pinned

Date: 2026-08-25  
Branch: `bootstrap/oss-autonomous-trader-replatform`  
Active issue: #15  
Assurance phase: A1  
Project status: `A1_LEAN_DIFFERENTIAL_SLICE`

The repaired baseline at head `854773bc45614907e2c53c395a1f87b3cc3d8f85` is now explicitly verified green: tests run `32888794288`, legacy phase-b run `32888794305`, bootstrap-assurance run `32888794317`, and runtime-candidates run `32888794347` all completed successfully. The prior LEAN production fill evidence therefore remains on a clean baseline.

NautilusTrader is now pinned for the corresponding A1 slice at release `v1.230.0`, exact upstream commit `8160730c7c550480b0a439fb11086a4c4de15f0b`, with LGPL-3.0-only licensing and authority NONE recorded in `contracts/execution/nautilus-a1-candidate-pin-v1.json`.

Exact pinned-source analysis of production `nautilus_trader/backtest/engine.pyx` resolved the previously open bar-ordering question. `BacktestEngine` sends an external `Bar` to `SimulatedExchange.process_bar` before delivering it through the data engine to strategies. The production trade-bar path processes the open first, enables market filling across an opening gap, and calls matching iteration at the bar `ts_init`. Thus a market order emitted after the prior bar can be resting when the next bar open is auctioned, which is structurally compatible with the unchanged A1 next-open contract.

The A1 runtime-candidate workflow now adds a credential-free, fail-closed Nautilus **source-production-matching preflight**. It checks the exact checkout SHA, license, candidate pin, and the production source-path invariants above, then uploads a deterministic provenance receipt. The receipt explicitly says `production_probe_status: NOT_YET_EXECUTED`; this source preflight is not executable fill evidence and is not a runtime disposition.

A1 remains **IN_PROGRESS**. Trading authority remains **NONE**. Autonomous paper trading and live capital remain **DISABLED**. Sealed-holdout exact cases/labels were not accessed.

## Next exact action

1. Require exact-head tests/bootstrap-assurance/runtime-candidates to remain green with the Nautilus pinned-source preflight; fix any genuine failure without weakening tests or invariants.
2. Implement the minimal credential-free executable NautilusTrader production fill probe against exactly the same public daily-bar decision/fill semantics and normalized comparison classes used by LEAN/reference. Do not replace production matching with a custom or synthetic fill model merely to satisfy the oracle.
3. Run three canonical deterministic Nautilus executions and normalized differential receipts, then continue the remaining A1 hidden, mutation, metamorphic, clean-environment, and chaos/fault gates for both candidates.
4. Only after every conjunctive A1 gate passes may #15 record candidate dispositions and select a primary runtime. Do not start #16.

Append-only record: `docs/handoffs/2026-08-25-a1-nautilus-production-matching-preflight.md`.
