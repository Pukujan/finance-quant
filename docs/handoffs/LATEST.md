# Handoff — A1 public matrix green; hidden acceptance blocked on authorized runner

Date: 2026-08-26
Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #15
Assurance phase: A1

Required governance/state sources were re-read before changes. Property impact remains **STRENGTHEN** only: candidate pins, execution semantics, PIT rules, permitted differences, runtime dispositions, trading authority, and sealed-holdout restrictions were not changed.

Exact durable head `4739392b15319bb209d657294834fed4cfb02d29` completed the full eight-workflow public validation matrix successfully: tests `32926469922`, legacy Phase-B `32926469919`, bootstrap-assurance `32926469897`, runtime-candidates `32926469900`, Nautilus callback evaluator `32926469912`, Nautilus pre-open evaluator `32926469910`, `a1-assurance` `32926469899`, and LEAN clean-determinism `32926469909`.

This establishes a fully green public A1 baseline for the current slice. LEAN production differential, mutation, metamorphic, deterministic clean-runner, and chaos/fault evidence remain preserved. Nautilus retains its native same-bar `FQ-PROP-015` failure, deferred-callback `FQ-PROP-021` failure, published latency-API ineligibility, and public production-native path-exhaustion record. Candidate dispositions remain `PENDING` because A1 gates are conjunctive.

The remaining substantive blocker is genuine `HIDDEN_ACCEPTANCE`. `docs/acceptance/SEALED_INTERFACE.md` explicitly requires an authorized external clean runner that can execute the private sealed corpus without exposing cases/labels and emit only an aggregate `SafeAcceptanceReceipt` bound to the public `SealRecord`. Public CI and the ordinary repository GitHub identity are not valid clean-runner identities. `.github/workflows/a1-hidden-acceptance.yml` is only the aggregate receipt-ingress verifier and cannot itself satisfy hidden acceptance.

No attempt was made to inspect, search, checkout, print, or infer private holdout cases or labels. No fabricated receipt was created. Trading authority remains `NONE`; autonomous paper/live execution remains disabled; runtime selection remains `NONE / PENDING`.

## Next exact action

1. Use the authorized external clean runner defined by `docs/acceptance/SEALED_INTERFACE.md` to evaluate the exact candidate artifact against the sealed A1 corpus and emit only the public `SealRecord` plus aggregate `SafeAcceptanceReceipt`.
2. Submit that aggregate evidence through `.github/workflows/a1-hidden-acceptance.yml` and require `finance_quant.acceptance.a1_hidden` to verify it fail-closed.
3. If the aggregate hidden result fails, preserve the failure receipt and fix only public defects consistent with the unchanged A1 contract; do not inspect or optimize against hidden cases.
4. Only after hidden acceptance passes and all public gates remain green may issue #15 assign final candidate dispositions, select the primary runtime, update machine-readable state, and explicitly permit promotion. Do not begin issue #16 beforehand.

Append-only record: `docs/handoffs/2026-08-26-a1-public-matrix-green-hidden-blocked.md`.
