# Handoff — A1 LEAN production probe normalization/determinism

Date: 2026-08-25  
Branch: `bootstrap/oss-autonomous-trader-replatform`  
Active issue: #15  
Assurance phase: A1  
Project status: `A1_LEAN_DIFFERENTIAL_SLICE`

The LEAN production candidate harness advanced without changing the A1 oracle or authority boundary. Run `32876861792` exposed a standalone map-file-provider dependency in `Symbol.Create`; commit `30936a2d6381ea4fa7a5f7a20c5d4ed07959dfcd` now constructs the equity SID directly with mapping disabled for this public fill-only probe. Run `32883152940` then proved the production `EquityFillModel.MarketOnOpenFill` itself succeeded, but LEAN wrote a TRACE line before its JSON result. Commits `0c3a30523388334fc2161635531de38efafad259` and `625059cf04e400531b535cd8495d5a2329b2b070` added strict log-tolerant extraction: exactly one expected LEAN result object is required; zero/multiple matches fail closed, with targeted tests.

On head `625059cf04e400531b535cd8495d5a2329b2b070`, runtime-candidates run `32883830248` generated three successful semantic evidence receipts with identical candidate hash `8b216968a95ad42fcc308d182d8420a63590a0841b26e04d5874b17fdca9d1cc`, identical reference hash `a99fe8251b79ccfad3df44a067f2964af6655d15f054eb32d200378f53532555`, and the contracted fill (`5 @ 11`, `2026-06-02T13:30:00Z`, source `bar-2`). The workflow failed only because raw stdout TRACE timestamps differ across runs. Commit `aeb5cd4ab6f53a966bbc344e45afde1b2a552573` preserves raw diagnostics but compares canonical extracted probe JSON plus normalized evidence for three-run determinism.

Exact-head runtime-candidates run `32884104244` and exact-head tests/Phase-B/bootstrap-assurance workflows were still running when this handoff was written. A1 remains **IN_PROGRESS**; do not claim LEAN candidate workflow success until those runs are green. NautilusTrader candidate evidence and the remaining hidden/mutation/metamorphic/clean-environment/chaos gates are still required before any runtime disposition.

Trading authority remains **NONE**. Autonomous paper trading and live capital remain **DISABLED**. Sealed-holdout exact cases/labels were not accessed.

Next: recheck `32884104244` and exact-head assurance workflows; after a genuine LEAN pass, proceed only within #15 to equivalent credential-free NautilusTrader evidence for the same public daily-bar subset, then complete every conjunctive A1 gate before promotion.

Append-only record: `docs/handoffs/2026-08-25-a1-lean-probe-normalization-determinism.md`.
