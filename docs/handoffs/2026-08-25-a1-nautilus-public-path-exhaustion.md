# A1 Nautilus public production path exhaustion

Date: 2026-08-25
Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #15
Assurance phase: A1

## Scope

Required governance/state files were read before any mutation. Starting durable head `97f0d19b1486662ca5a23aa9a902559a1c9acf22` was verified green across tests, legacy Phase-B, bootstrap assurance, runtime candidates, callback-adapter evaluation, and pre-open/latency evaluation before this slice began.

This slice answers the remaining bounded question for pinned NautilusTrader `v1.230.0` / source commit `8160730c7c550480b0a439fb11086a4c4de15f0b`: whether any public production-native mechanism remains that can realize the unchanged A1 next-bar-open MARKET/GTC semantics without future event payload, custom fill logic, private bindings, or changed order intent.

## Existing executable evidence

The unchanged public oracle requires BUY quantity `5`, price `11`, fill time `2026-06-02T13:30:00Z`, source `bar-2`.

- Native GTC production matching fills the bar-1 decision on bar 1 and is retained as a deterministic `FQ-PROP-015` failure.
- `AT_THE_OPEN` / `AT_THE_CLOSE` time-in-force is rejected by the pinned engine and is not an eligible replacement for the unchanged GTC intent.
- PIT-safe callback deferral preserves the already-created bar-1 MARKET intent but submits it from the bar-2 strategy callback. Run `32907656115` is deterministic across three executions and fills quantity `5` at price `12.00`, time `2026-06-02T13:30:00Z`, source `bar-2`; this remains a `FQ-PROP-021` failure because the oracle requires open `11`.
- Native insert latency plus a session-derived pre-open clock point is not publicly executable from the exact published CPython 3.12 Linux `nautilus_trader==1.230.0` wheel because `nautilus_trader.execution` does not export the source-advertised `StaticLatencyModel`. Run `32910563339` records `INELIGIBLE_PUBLISHED_API_UNAVAILABLE` and does not bypass the release through `_libnautilus`.

## Remaining session-clock analysis

The exact pinned `BacktestEngine` event loop advances strategy/exchange clocks to the next data timestamp before routing the next market-data item. Timer callbacks are therefore processed first; pending commands/events are drained; then exchanges are settled before the next data event is routed to the engine/strategies.

That ordering eliminates the last public no-latency session-clock variant. A pre-open timer submission settles before bar 2 reaches the exchange, so it cannot use bar-2 open as a legitimate new market state. A submission delayed until bar 2 is delivered to the strategy is the already-tested callback-deferral path and fills the bar at `12`, not the required open `11`. Holding the command across the pre-open settlement boundary requires native command latency, whose public release surface is ineligible as documented above.

No additional public production-native path remains under the unchanged comparison boundary. Private `_libnautilus` bindings, future bar payload, custom fill models, synthetic open prices, transformed order types/TIF, or any other semantic normalization that manufactures price `11` are explicitly outside the eligible A1 adapter boundary.

## Durable conclusion

For pinned NautilusTrader `v1.230.0`, the **public production-native mechanism search is exhausted for the unchanged next-bar-open MARKET/GTC contract**.

This is path-exhaustion evidence, not a premature final candidate disposition. `runtime_disposition` remains `PENDING` until all required A1 gates are green. LEAN's conforming public two-bar production probe remains positive evidence only; primary runtime selection remains `NONE / PENDING`.

No oracle, property, mutation threshold, PIT invariant, authority boundary, or test was weakened. Trading authority remains `NONE`; autonomous paper/live execution remains disabled; sealed-holdout contents were not accessed.

## Validation baseline

Starting head `97f0d19b1486662ca5a23aa9a902559a1c9acf22` is verified green at:

- tests `32910761679`
- legacy phase-b `32910761680`
- bootstrap-assurance `32910761746`, including contracts, formal TLA, full-validation, and fresh-environment
- runtime-candidates `32910761691`
- `a1-nautilus-adapter-evaluation` `32910761695`
- `a1-nautilus-preopen-evaluation` `32910761698`

## Next exact action

Require this documentation head to complete the same exact-head validation set. Then preserve all Nautilus negative/ineligible/path-exhaustion evidence and continue only the still-outstanding A1 hidden-acceptance, mutation, metamorphic, repeated-determinism, clean-environment, and chaos/fault gates. Final candidate dispositions and runtime selection remain prohibited until every conjunctive A1 gate passes. Do not begin issue #16 before durable state explicitly permits promotion.
