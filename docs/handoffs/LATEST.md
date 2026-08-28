# Handoff — adaptive modular quantitative portfolio engine

Date: 2026-08-28
Branch: `main`
Active architecture issue: #35 (pending latest framing reconciliation)
Product mode: local research + zero-money simulated paper only; no broker/live capital

## Full continuation package

**Read this first:**

`docs/handoffs/SESSION_2026-08-28_ADAPTIVE_QUANT_ENGINE.md`

That file is the detailed continuation package for the long 2026-08-28 design session. It captures the repo state, empirical results, architecture evolution, MarketState/epistemic/trend concepts, portfolio engine, OSS/data choices, market-reality/overfitting discussion, agent/SWE operating model, adversarial failure matrix, success/kill criteria and exact next-session bootstrap prompt.

## Latest conceptual correction

The product center is now:

> **adaptive modular multi-strategy quantitative portfolio engine**

Canonical loop:

`heterogeneous signal providers -> model/meta weights -> forecast distributions/ranks -> portfolio allocation -> local zero-money paper -> realized outcomes -> weight/version evolution`

Important consequence:

**MarketState, temporal KG/RAG, news/epistemics, vendor pre-quantized feeds, fundamentals/macro, momentum, breakout, volatility and analog retrieval are signal-provider families. None is architecturally privileged.**

The engine must be able to learn that any sophisticated provider deserves zero weight.

#35/#36 were originally written before this final clarification and may over-center MarketState. The next session should reconcile those issues before implementing the contract freeze literally.

## Existing fixed substrate remains unchanged

The working workstation and fixed parallel lab are already on `main`.

`finance_quant.lab` remains the authority for:

- PIT benchmark/snapshot truth;
- canonical realized outcomes;
- evaluation identity;
- scoring;
- prior-resolved-only routing semantics;
- isolated persistent paper-account truth.

Candidate providers/models/strategy/meta/portfolio policies do not own the answer key.

Existing AAPL empirical baseline remains:

- 1,988 WFO predictions;
- price-only direction: 53.3702%;
- price + current small SEC feature set: 51.8612%;
- delta: -1.5091pp.

The current small SEC feature set hurt the price baseline. This remains useful negative evidence, not a KG success claim.

Existing local paper proof remains signal -> persistence -> next-open simulated fill -> mark, not profitability evidence.

## Immediate next session

Read in order:

1. `AGENTS.md`
2. `docs/CURRENT_STATE.md`
3. `docs/handoffs/SESSION_2026-08-28_ADAPTIVE_QUANT_ENGINE.md`
4. #35
5. #36
6. this file
7. #27 and relevant candidate issues/contracts/tests.

Then:

1. reconcile #35/#36 so the adaptive multi-strategy engine is clearly the parent and MarketState is optional;
2. freeze the smallest shared `SignalProvider`/signal artifact, strategy/meta weight, forecast and `PortfolioIntent` contracts;
3. make the permanent walking skeleton work with a simple price/momentum/breakout/volatility strategy **without** KG/news;
4. resume parallel raw-data, MarketState, KG/RAG, model and portfolio-policy workers behind those contracts;
5. put every executable credible strategy/policy into local forward paper immediately.

## Exact bootstrap prompt for a new chat

> Continue `Pukujan/finance-quant` from durable repo state, not from assumptions. Read `AGENTS.md`, `docs/CURRENT_STATE.md`, and `docs/handoffs/SESSION_2026-08-28_ADAPTIVE_QUANT_ENGINE.md`, then issues #35 and #36 and `docs/handoffs/LATEST.md`. The latest conceptual correction is that the product is an **adaptive modular multi-strategy quantitative portfolio engine**: heterogeneous signal providers -> model/meta weights -> forecast distributions/ranks -> portfolio allocation -> local zero-money paper -> realized outcomes -> weight/version evolution. Market State/KG/RAG/news/vendor feeds are optional signal providers, not the product itself. First reconcile #35/#36/CURRENT_STATE against that correction and tell me exactly what durable issue/contracts need changing; then implement the smallest correct contract/walking-skeleton correction rather than doing more architecture discussion. Preserve fixed `finance_quant.lab` PIT/outcome/scoring/account semantics, keep live capital out of scope, do not inspect the sealed holdout, and make every executable strategy enter forward paper as soon as valid.

## Hard boundaries

- no broker/live-capital authority;
- no sealed-holdout inspection without explicit authorization;
- negative research results remain durable;
- correctness gates software merges; investment metrics gate research promotion;
- preserve trial genealogy to defend against AI-powered strategy-selection overfitting;
- do not let assurance/orchestration infrastructure become the product;
- do not build distributed infrastructure until real local workload requires it.
