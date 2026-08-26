# Handoff — A1 Nautilus public production path exhaustion

Date: 2026-08-25
Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #15
Assurance phase: A1

Required governance/state files were read before changes. Starting durable head `97f0d19b1486662ca5a23aa9a902559a1c9acf22` was verified green across all six required baseline workflows: tests `32910761679`, legacy Phase-B `32910761680`, bootstrap assurance `32910761746`, runtime candidates `32910761691`, callback-adapter evaluation `32910761695`, and pre-open/latency evaluation `32910761698`. Bootstrap contracts, formal TLA, full validation, and fresh-environment jobs all succeeded.

This slice completed the remaining bounded source-level Nautilus timing analysis for pinned `v1.230.0` / commit `8160730c7c550480b0a439fb11086a4c4de15f0b` under the unchanged A1 next-bar-open MARKET/GTC contract. Existing executable evidence remains unchanged: native GTC is a deterministic `FQ-PROP-015` failure; PIT-safe bar-2 callback deferral fills `5 @ 12.00` at `2026-06-02T13:30:00Z` rather than the required open `11`, a `FQ-PROP-021` failure; and native insert latency is ineligible because the exact published wheel does not expose the advertised public `StaticLatencyModel` symbol.

The pinned `BacktestEngine` event loop closes the remaining session-clock loophole. Before routing each next data item it advances timers, drains pending commands/events, and settles exchanges. Therefore a session-known pre-open timer submission with no latency is settled against prior market state before bar 2 is routed. Waiting until the bar-2 strategy callback is already executable negative evidence and observes/fills the bar at its close. Native latency would be the production-native mechanism for delaying command settlement across that boundary, but the pinned published wheel's public API does not provide it. No private `_libnautilus` binding, future bar payload, custom fill model, or order-semantic transformation was used.

Accordingly, public production-native Nautilus paths are now recorded as exhausted for this specific unchanged next-open differential. This is not yet a final runtime disposition: Nautilus remains `PENDING`, LEAN remains positive evidence only, and A1 remains `IN_PROGRESS` until all conjunctive assurance gates are complete.

Trading authority remains `NONE`; autonomous paper/live execution remains disabled; sealed-holdout contents were not accessed.

## Next exact action

1. Require the path-exhaustion documentation head to pass tests, legacy phase-b, bootstrap-assurance, runtime-candidates, `a1-nautilus-adapter-evaluation`, and `a1-nautilus-preopen-evaluation`.
2. Preserve all Nautilus negative/ineligible/path-exhaustion evidence and do not manufacture conformity through private bindings, future payload, custom fill logic, or changed order semantics.
3. Implement/run the remaining A1 hidden-acceptance, mutation, metamorphic, repeated-determinism, clean-environment, and chaos/fault gates for still-eligible runtime paths, without exposing hidden cases or weakening thresholds.
4. Only after every A1 gate is green may issue #15 assign final candidate dispositions, select a primary runtime, and explicitly permit promotion. Do not advance to issue #16 before that point.

Append-only record: `docs/handoffs/2026-08-25-a1-nautilus-public-path-exhaustion.md`.
