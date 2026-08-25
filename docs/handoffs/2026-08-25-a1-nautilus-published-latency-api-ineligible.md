# A1 Nautilus published latency API ineligible

Date: 2026-08-25
Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #15
Assurance phase: A1

## Scope

Required governance/state files were read before any mutation. Starting durable head `0caffcf8bcc164a282960c6bbf2cf6aeddce8378` was re-verified green across ordinary tests, legacy Phase-B, bootstrap assurance, runtime candidates, and the prior negative Nautilus callback-adapter evaluator.

This slice tested whether pinned NautilusTrader `v1.230.0` / source commit `8160730c7c550480b0a439fb11086a4c4de15f0b` exposes a public production-native timing mechanism capable of settling the unchanged bar-1 MARKET/GTC intent before the next session open without reading bar-2 payload. The proposed path was native insert latency plus a strategy-clock alert at a session-known pre-open timestamp. Production `BacktestEngine` / `SimulatedExchange` matching remained mandatory; no custom fill model and no private binding were allowed.

## Evidence

Pinned source exposes the native inflight queue surface (`has_pending_commands`, `generate_inflight_command`, `process(...)`) and the Rust/Python binding source for `StaticLatencyModel`. The generated public stub includes `StaticLatencyModel`, and the pinned source unit test imports it from `nautilus_trader.execution`.

The exact published CPython 3.12 Linux wheel installed by `python -m pip install nautilus_trader==1.230.0` does not expose that public symbol. The import fails with `ImportError: cannot import name 'StaticLatencyModel' from 'nautilus_trader.execution'`.

Outcome-neutral evaluator run `32910563339` completed successfully. Artifact `a1-nautilus-native-latency-preopen-evaluation` records:

- `mechanism_status: INELIGIBLE_PUBLISHED_API_UNAVAILABLE`
- `semantic_conformance: NOT_EXECUTED`
- `source_release_skew: true`
- `runtime_disposition: PENDING`
- `authority: NONE`
- unchanged expected fill: quantity `5`, price `11`, time `2026-06-02T13:30:00Z`, source `bar-2`

The semantic probe is deliberately **not** labeled as an FQ property failure because the pinned release's public API cannot execute the mechanism. The workflow also deliberately does not reach into `_libnautilus` to bypass the published API.

Two earlier failures in this slice were integration-only. The first preflight used a non-existent source-marker name and was repaired to match the exact pinned queue symbols. The second was the public `StaticLatencyModel` import failure itself; the evaluator was then changed to retain that as explicit fail-closed ineligibility rather than crash or fabricate a pass. No oracle, invariant, property, authority boundary, or test threshold was weakened.

## Durable disposition

A1 remains **IN_PROGRESS**. Runtime selection remains **NONE / PENDING**. Trading authority remains **NONE**. Autonomous paper/live execution remains disabled. Sealed-holdout contents were not accessed.

Nautilus now has three distinct durable receipts: native-GTC `FQ-PROP-015` nonconformance, PIT-safe callback-deferral `FQ-PROP-021` nonconformance, and published-native-latency API ineligibility due to source/release skew. LEAN's public two-bar production differential remains positive evidence only, not a final runtime selection.

## Next exact action

Require the final durable-state head to complete its exact-head validation cycle. Preserve all existing negative/ineligible Nautilus evidence. Determine whether any remaining public production-native Nautilus path can meet the unchanged next-bar-open MARKET contract without future payload or custom fill logic; if none exists, record candidate-path exhaustion explicitly. Continue the remaining conjunctive A1 hidden-acceptance, mutation, metamorphic, determinism/clean-environment, and chaos/fault gates. Do not advance to issue #16 unless every A1 gate is green and durable state explicitly permits promotion.
