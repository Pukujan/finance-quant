# A1 LEAN production candidate probe — append-only handoff

Date: 2026-08-25  
Branch: `bootstrap/oss-autonomous-trader-replatform`  
Active issue: #15  
Assurance phase: A1

## Scope

This session remained entirely inside A1 execution/runtime conformance. It did not select a runtime, start #16, enable paper/live capital authority, or access sealed-holdout exact cases/labels.

## Evidence discovered

Branch head `24976efc7587f83175e24442f281b9a4b7b577b3` contained a new credential-free LEAN production fill-model probe pinned to LEAN source commit `185c691b89f28bd68e48d53c02147415134975f0`.

The candidate workflow `32875746733` verified the exact source pin/license and successfully built the production probe, but failed in `Run three deterministic candidate probes`. On the same implementation head, tests `32875746688` and Phase-B `32875746634` passed.

## Defect and fix

Pinned upstream `EquityFillModel.MarketOnOpenFill` treats `Order.Time` as UTC, and LEAN's own `EquityFillModel` tests convert a New York-local submission instant to UTC before constructing `MarketOnOpenOrder`. The initial finance-quant probe constructed `MarketOnOpenOrder` with the local wall-clock `DateTime` directly.

Commit `6e21bc0fc51f29124ada8eef7c925be88d3975fc` fixes the harness by converting the decision instant to UTC before creating the order. It also records LEAN's fill message for diagnostics. No expected price/time, differential comparison, PIT rule, or authority rule was loosened.

Commit `57758d7d8ab81c1e6445ec42ec970c2b1c788d91` makes the candidate workflow preserve stdout/stderr artifacts even on failure. It still requires a zero probe exit status before normalization and still requires `assert_normalized_receipts_conform` plus three-run raw/evidence equivalence.

## Validation state at handoff

Fresh exact-head A1 runtime-candidates run `32876861792` for implementation head `57758d7d8ab81c1e6445ec42ec970c2b1c788d91` was still in progress when durable documentation was written. Other ordinary workflows were also re-running. No post-fix conformance pass is claimed here.

A1 remains `IN_PROGRESS`; required hidden acceptance, mutation, metamorphic, deterministic/clean-environment, and chaos/fault evidence is not yet complete, and NautilusTrader candidate evidence is still outstanding.

## Resume

Recheck exact implementation head `57758d7d8ab81c1e6445ec42ec970c2b1c788d91`. If `32876861792` fails, inspect the preserved `a1-lean-production-fill-probe` artifact and correct the harness/runtime integration without weakening any oracle or invariant. If it passes, record the three-run equivalence receipt and proceed only to a thin credential-free NautilusTrader candidate for the same daily-bar subset. Do not widen either runtime or assign a disposition until all conjunctive A1 gates pass.
