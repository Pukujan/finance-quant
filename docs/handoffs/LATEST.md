# Handoff — A1 Nautilus published latency API ineligible

Date: 2026-08-25
Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #15
Assurance phase: A1

Required governance/state files were read before changes. Starting durable head `0caffcf8bcc164a282960c6bbf2cf6aeddce8378` was re-verified green across ordinary tests, legacy Phase-B, bootstrap assurance, runtime candidates, and the prior negative Nautilus callback-adapter evaluator before this slice began.

This slice evaluated the remaining obvious production-native timing path for pinned NautilusTrader `v1.230.0` / source commit `8160730c7c550480b0a439fb11086a4c4de15f0b`: submit the unchanged bar-1 MARKET/GTC intent through production `BacktestEngine` / `SimulatedExchange` with native insert latency, then use a strategy-clock alert at a session-known timestamp strictly before the next open so the command queue can settle without reading bar-2 payload. No custom fill model or private binding was permitted.

Exact pinned source exposes the inflight queue surface (`has_pending_commands`, `generate_inflight_command`, `process(...)`) and its generated public stub plus source unit test advertise `StaticLatencyModel` through `nautilus_trader.execution`. The exact published CPython 3.12 Linux wheel for `nautilus_trader==1.230.0` does not export that public symbol. Importing it raises `ImportError: cannot import name 'StaticLatencyModel' from 'nautilus_trader.execution'`.

Outcome-neutral evaluator run `32910563339` completed successfully and uploaded `a1-nautilus-native-latency-preopen-evaluation`. Its receipt records `mechanism_status: INELIGIBLE_PUBLISHED_API_UNAVAILABLE`, `semantic_conformance: NOT_EXECUTED`, `source_release_skew: true`, `runtime_disposition: PENDING`, and authority `NONE`. The unchanged next-open expectation remains quantity `5`, price `11`, time `2026-06-02T13:30:00Z`, source `bar-2`. This mechanism is not recorded as an FQ property failure because the production semantic probe was not executable through the pinned release's public API.

Two earlier workflow failures in this slice were integration-only and were fixed without weakening semantics: the first used a wrong source-marker name; the second directly exposed the published-wheel import failure. The evaluator now converts that release/API mismatch into explicit fail-closed ineligibility instead of bypassing the public package via `_libnautilus`.

A1 remains IN_PROGRESS. Nautilus retains the native-GTC `FQ-PROP-015` failure, callback-deferral `FQ-PROP-021` failure, and now this published-latency-API ineligibility receipt. LEAN's public two-bar production differential remains positive evidence only. Candidate dispositions remain PENDING; runtime selection remains NONE; authority remains NONE; autonomous paper/live execution remains disabled; sealed-holdout contents were not accessed.

## Next exact action

1. Require the exact durable-state head to pass tests, legacy phase-b, bootstrap-assurance, runtime-candidates, `a1-nautilus-adapter-evaluation`, and `a1-nautilus-preopen-evaluation`.
2. Preserve all three Nautilus receipts and do not use private bindings to manufacture a public production mechanism.
3. Establish whether any remaining public production-native Nautilus mechanism can realize the unchanged next-bar-open MARKET semantics without future event payload or custom fill logic; otherwise record candidate-path exhaustion explicitly.
4. Continue the remaining A1 hidden-acceptance, mutation, metamorphic, determinism/clean-environment, and chaos/fault gates. Do not advance to issue #16 until every conjunctive A1 gate passes and durable state explicitly permits promotion.

Append-only record: `docs/handoffs/2026-08-25-a1-nautilus-published-latency-api-ineligible.md`.
