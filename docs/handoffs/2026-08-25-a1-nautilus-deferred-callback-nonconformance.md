# Handoff — A1 Nautilus deferred-callback nonconformance

Date: 2026-08-25
Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #15
Assurance phase: A1

Required governance/state files were read before changes. Pre-adapter head `8deb8d7e6106dbaef2e12f28fa8687fc6ca280f9` was fully green across tests, legacy Phase-B, runtime-candidates, and bootstrap assurance.

Implementation commit `faafc0ce616d07d7d99fc623ba0ceddb20912406` added an outcome-neutral production evaluation for a thin NautilusTrader timing adapter. The existing bar-1 MARKET intent is buffered until the bar-2 strategy callback; the path still uses pinned NautilusTrader `v1.230.0` / commit `8160730c7c550480b0a439fb11086a4c4de15f0b`, production `BacktestEngine` / `SimulatedExchange`, native GTC matching, no custom fill model, and no future bar payload before submission.

Run `32907656115` completed successfully as an evaluator. Three independent runs were identical: quantity `5`, price `12.00`, time `2026-06-02T13:30:00Z`, source `bar-2`. The unchanged oracle requires price `11` at that same time/source. Evidence therefore records `semantic_conformance: FAIL` and `failed_property: FQ-PROP-021`. This supplements, rather than replaces, the earlier native-GTC `FQ-PROP-015` failure.

A1 remains IN_PROGRESS. Candidate dispositions remain PENDING. Authority remains NONE and all existing capital/holdout restrictions remain unchanged.

## Next exact action

1. Require the exact durable-state head to pass tests, legacy phase-b, bootstrap-assurance, runtime-candidates, and the Nautilus adapter-evaluation workflow.
2. Evaluate a production-native queue/latency mechanism only if its release boundary is derivable PIT-safely from contract-known/session information without future event payloads while preserving the MARKET intent and production matching; otherwise record it as ineligible.
3. Preserve both Nautilus negative receipts and continue the remaining A1 hidden-acceptance, mutation, metamorphic, determinism/clean-environment, and chaos/fault gates before final candidate disposition.
4. Do not advance to issue #16 while A1 remains incomplete.

Append-only record: `docs/handoffs/2026-08-25-a1-nautilus-deferred-callback-nonconformance.md`.
