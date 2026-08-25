# A1 Nautilus executable production nonconformance

Date: 2026-08-25  
Branch: `bootstrap/oss-autonomous-trader-replatform`  
Issue: #15  
Assurance phase: A1

## What changed

Added `tools/nautilus_a1_probe/probe.py` and extended `.github/workflows/a1-runtime-candidates.yml` so pinned NautilusTrader `v1.230.0` / commit `8160730c7c550480b0a439fb11086a4c4de15f0b` is executed credential-free through production `BacktestEngine` / `SimulatedExchange` using the unchanged public A1 two-bar fixture.

The initial executable harness failed because a synthetic currency pair cannot be added to a single-currency CASH venue. The harness was corrected to Nautilus multi-currency CASH mode (`base_currency=None`). No fixture, oracle, PIT boundary, property, fee, liquidity, or authority rule changed.

## Production evidence

With native GTC market semantics, the decision-bar intent deterministically filled on `bar-1`:

- quantity: `5`
- price: `10.00`
- fill time: `2026-06-01T20:00:00Z`
- source event: `bar-1`

The unchanged A1 reference/LEAN contract requires the earliest eligible next-bar fill:

- quantity: `5`
- price: `11.00`
- fill time: `2026-06-02T13:30:00Z`
- source event: `bar-2`

Therefore the native Nautilus execution violates critical `FQ-PROP-015`.

A second probe attempted the production-native `AT_THE_OPEN` time-in-force. It produced no fill. Exact pinned source confirms `_process_market_order` rejects both `AT_THE_OPEN` and `AT_THE_CLOSE` as “not currently supported,” so the obvious market-on-open translation is unavailable in this version.

The candidate workflow now treats this as a deterministic negative candidate result. Runtime-candidates run `32905724960` passed as an evaluation workflow: the LEAN production job remained conformant, while the Nautilus job reproduced the same-bar result across three executions and emitted `production-nonconformance.json` with `semantic_conformance: FAIL` and `failed_property: FQ-PROP-015`. `runtime_disposition` remains `PENDING`; no final candidate disposition has been assigned.

## Authority and assurance

A1 remains **IN_PROGRESS**. Trading authority is **NONE**. Autonomous paper trading is **DISABLED**. Live capital is **DISABLED**. Sealed-holdout exact cases/labels were not accessed.

## Next exact action

Require exact-head ordinary and assurance CI to be green after the durable-state update. Then test only PIT-safe, thin adapter mechanisms explicitly allowed by the A1 SDD/PDD that still route fills through Nautilus production matching. Do not use a custom fill model, inspect future bar values, weaken the next-open oracle, or reinterpret workflow success as candidate conformance. If no compliant adapter eliminates same-bar execution, preserve this evidence for the final `REFERENCE_ONLY`/`REJECT` decision and continue the remaining conjunctive A1 gates for eligible runtime paths.
