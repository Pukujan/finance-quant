# A1 Nautilus production-matching preflight

Date: 2026-08-25  
Branch: `bootstrap/oss-autonomous-trader-replatform`  
Active issue: #15  
Assurance phase: A1

## Baseline verification

Before making this change, exact head `854773bc45614907e2c53c395a1f87b3cc3d8f85` was verified green across all currently triggered baseline workflows: tests `32888794288`, legacy phase-b `32888794305`, bootstrap-assurance `32888794317`, and A1 runtime-candidates `32888794347` all completed successfully.

## Nautilus exact-version finding

NautilusTrader release `v1.230.0` resolves to upstream commit `8160730c7c550480b0a439fb11086a4c4de15f0b`. Exact pinned production source in `nautilus_trader/backtest/engine.pyx` shows:

- external `Bar` data is processed by the simulated exchange before `self._data_engine.process(data)` delivers the bar to strategies;
- the trade-bar path calls `_process_trade_bar_open` before high/low/close processing;
- an opening gap sets `_fill_at_market = True`;
- matching iteration at the open uses `tick.ts_init`, derived from the bar `ts_init`.

These are the production semantics required for a prior-bar market order to be resting before the next daily bar open is auctioned. This resolves the structural compatibility question without weakening or altering the finance-quant A1 oracle.

## Durable changes

- Added `contracts/execution/nautilus-a1-candidate-pin-v1.json` with exact source pin, release, license, credential-free/CLI-free mode, runtime disposition PENDING, and authority NONE.
- Extended `.github/workflows/a1-runtime-candidates.yml` with a separate fail-closed `nautilus-production-matching-preflight` job. It checks the exact upstream checkout and production source-path invariants and uploads a deterministic provenance receipt.
- The preflight receipt explicitly records `production_probe_status: NOT_YET_EXECUTED`. Source inspection is not executable production-fill evidence and cannot select or disposition the candidate.
- Updated `docs/CURRENT_STATE.md` and `docs/handoffs/LATEST.md` to record the green baseline, exact Nautilus finding, and next permitted action.

No test, property, PIT rule, oracle, acceptance threshold, mutation threshold, authority rule, or sealed-holdout boundary was weakened or bypassed.

A1 remains **IN_PROGRESS**. Trading authority remains **NONE**; autonomous paper trading and live capital remain **DISABLED**; sealed-holdout exact cases/labels were not accessed.

## Next exact action

1. Require exact-head tests/bootstrap-assurance/runtime-candidates to remain green with the Nautilus pinned-source preflight; fix any genuine failure without weakening tests or invariants.
2. Implement the minimal credential-free executable NautilusTrader production fill probe against exactly the same public daily-bar decision/fill semantics and normalized comparison classes used by LEAN/reference. Do not substitute a custom/synthetic fill path for production matching.
3. Run three canonical deterministic Nautilus executions and normalized differential receipts, then continue the remaining conjunctive A1 hidden, mutation, metamorphic, clean-environment, and chaos/fault gates.
4. Do not start #16 or promote A1 until every required gate has passed and durable state explicitly permits promotion.
