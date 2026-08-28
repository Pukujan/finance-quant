# Current project state

<!-- MACHINE-STATE: architecture=ADAPTIVE_MODULAR_QUANT_PORTFOLIO_ENGINE status=CONTRACT_RECONCILIATION_BEFORE_PARALLEL_BUILD active_issue=35 -->

## Latest durable continuation package

Read `docs/handoffs/SESSION_2026-08-28_ADAPTIVE_QUANT_ENGINE.md` before resuming architecture/implementation work. It captures the full 2026-08-28 design session and the newest correction that occurred after #35/#36 were initially written.

## Active product direction

The product is now best framed as a **local adaptive modular multi-strategy quantitative portfolio engine**:

`heterogeneous signals -> model/meta weights -> forecast distributions/ranks -> portfolio allocation -> local zero-money paper -> realized outcomes -> weight/version evolution`

At decision time `T`, every participating signal/model may use only information legitimately knowable at `T`. The engine combines independent versioned strategy/signal providers, decides how much trust each deserves under the current context, converts forecasts into explicit target allocations/trades/cash, executes only local simulated paper, and updates future strategy credibility from subsequently realized outcomes.

**MarketState, temporal KG/RAG, news/epistemics and vendor pre-quantized feeds are optional signal-provider families, not the product itself.** Price/momentum/breakout/volatility/fundamental/macro strategies must fit the same engine without requiring MarketState.

Forward paper is a continuous benchmark, not a later deployment stage. Every executable credible strategy/policy should begin accumulating prospective paper history as soon as it can produce a valid decision.

Live capital remains out of scope.

## Immediate architecture reconciliation

Architecture proposal #35 and foundation issue #36 were written before the final strategy-centric clarification and may over-center the Market State Fabric.

Before broad implementation, the next session must reconcile #35/#36 around the parent structure:

```text
Adaptive Quantitative Portfolio Engine
    ├── Signal Provider Framework
    │     ├── price / momentum / breakout / volatility
    │     ├── fundamentals / macro
    │     ├── vendor quantified data
    │     ├── MarketState / epistemics / trends
    │     ├── KG / RAG / exposure / analog retrieval
    │     └── future signal families
    ├── Forecast / Model Expert Framework
    ├── MetaWeight / Context Router
    ├── Portfolio Policy Framework
    ├── Execution / Persistent Paper Accounts
    └── Outcome / Learning / Versioning
```

Do not silently make `MarketState` a mandatory universal input in the walking skeleton. A simple technical strategy must traverse the same permanent engine.

Likely shared contracts to settle in #36 include:

- `SignalProvider` / immutable `SignalArtifact` or `SignalVector`;
- `ForecastDistribution`;
- `StrategySpec`;
- meta/router weight state;
- `PortfolioIntent`;
- paper execution/fill objects;
- `CanonicalOutcome`;
- immutable artifact/version identity.

This should be a short contract correction, not a new assurance program.

## Fixed laboratory remains authoritative

The working workstation and fixed experiment laboratory are already merged to `main`.

`finance_quant.lab` continues to own canonical historical snapshots/outcomes, PIT cuts, scoring, evaluation identity, router timing and simulated-account truth. Candidate components may propose signals, state, retrieval, forecasts, strategy/meta weights and portfolio policies; they do not own the answer key.

Stable fixed-lab flow:

`publish immutable components -> assemble PIT benchmark -> run exact-version arms -> join same canonical outcome -> score -> ExperimentLedger -> prior-resolved-only routing -> isolated paper accounts`

Existing lab correctness semantics, component/evaluation hashes, mutation probes and paper-account invariants remain in force. Do not redesign them inside candidate lanes unless a concrete integration bug requires a centrally coordinated change.

## Existing empirical baseline retained

The workstation remains runnable:

`python -m finance_quant workstation --ticker AAPL --start 2018-01-01 --capital 100000`

Existing real AAPL/SEC workflow produced 1,988 walk-forward predictions:

- price-only directional accuracy: **53.3702%**;
- price + current small SEC-fundamental set: **51.8612%**;
- delta: **-1.5091 percentage points**.

The current tiny SEC structured feature set hurt the baseline. Do not claim KG predictive value from it.

Existing zero-money paper proof remains:

- 2026-08-26 signal persisted;
- 2026-08-27 simulated next-open fill: BUY 305 AAPL @ 310.61209779052734;
- marked NAV about $101,210.21 from $100,000.

That proves signal -> persistent state -> simulated execution -> mark, not profitability.

The current adjusted Yahoo historical lane is not strict raw PIT truth because later corporate actions can retroactively restate adjusted history. #29 should supply raw OHLCV + separately timestamped corporate actions.

## Strategy/meta-engine direction

The important object is not one permanent strategy but a versioned strategy specification combining:

- signal/provider versions + signal weights;
- model/expert versions + model weights;
- horizon/context/regime weighting;
- portfolio policy and risk parameters;
- execution/cost/rebalance assumptions.

Weights may initially be static controls, then evolve through inspectable prior-resolved-only methods such as exponentially weighted experts, rolling optimization, Bayesian/model averaging or contextual routers.

The system must preserve complete trial/version genealogy so AI-generated strategy search does not become automated backtest overfitting.

Do not optimize only directional accuracy or raw return. Evaluate forecast skill and portfolio skill separately, and decompose market/factor exposure from genuine selection/timing value where feasible.

## Portfolio engine direction

#38 owns forecast-to-allocation behavior.

The system must answer:

- where to invest;
- how much to invest;
- how much cash to hold;
- how to diversify by real economic/factor/theme exposure;
- what to buy/sell/hold;
- whether switching is worth transaction costs;
- when to rebalance;
- when to abstain/no-trade;
- how liquidity/correlation/risk constraints change raw forecast conviction.

`PortfolioIntent` is the immutable handoff from forecasts/meta-strategy to paper execution and records target weights, trade deltas, cash target, expected return/risk/cost, turnover, binding constraints and provenance.

Initial competing policy families remain:

1. equal-weight top-K;
2. edge/confidence-weighted top-K with caps;
3. volatility-scaled/risk-budgeted;
4. mean-variance/robust convex allocation with turnover/cost penalties;
5. explicit cash/no-trade threshold.

Each policy should receive identical upstream forecasts/cost assumptions and accumulate its own persistent forward paper history.

## Market State / epistemic provider direction

#37 remains a candidate signal-provider family, not the parent engine.

Useful layered representation:

`SourceArtifact -> Observation -> Claim/Proposition -> Evidence -> bitemporal EpistemicState -> MarketBeliefState -> Derived MarketState -> BenchmarkedKnowledge -> PredictiveKnowledge`

Factual reliability, market attention, economic materiality, exposure/transmission confidence and predictive usefulness remain separate.

`TrendState` should retain level, robust percentile/z-score, multi-horizon velocity, acceleration, noise, trend shape, structural-break probability, novelty, persistence, saturation/decay and cross-source confirmation rather than one generic hype score.

The ontology remains a stable core + versioned domain modules. Graph relations retain valid/knowledge time, provenance, confidence/materiality, and graph expansion stays typed/bounded.

## Raw vs pre-quantized data

The engine must support both custom extraction and already structured/quantized providers.

Potential data/source families include:

- raw market OHLCV/corporate actions;
- SEC filing text/XBRL;
- ALFRED/FRED macro vintages;
- GDELT/open event data;
- GitHub/Hugging Face activity for relevant technical/adoption signals;
- optional commercial RavenPack/LSEG MarketPsych/LSEG MRN/FactSet-Alexandria style feeds;
- social attention sources where licensing/coverage is appropriate.

Vendor scores are optional signal adapters, not hard dependencies. We do not need to recreate every professional extraction system before testing useful strategies.

## Local architecture / OSS direction

Use a modular monolith with process-isolated heavy workers, not microservices by default.

Own unique semantics; reuse commodity machinery:

- fixed `finance_quant.lab` / ExperimentLedger;
- existing paper account substrate;
- retained LEAN execution/backtest integration where useful;
- Parquet/ZSTD + DuckDB + Polars for local historical analytics;
- one retrieval engine initially (OpenSearch or lighter Qdrant where appropriate);
- LightGBM/XGBoost + transparent linear/ranking baselines;
- Qlib only where it materially accelerates research;
- local LLM runtime for extraction/classification where justified;
- RDFLib/pySHACL/OWL/PROV/RO-Crate-style export for #39 after useful lineages exist;
- no Kafka/Kubernetes/distributed lakehouse before actual workload demands them.

## SWE / multi-agent execution

Use typed shared contracts and durable work packets as synchronization boundaries for AI coding agents.

Every work packet should declare issue/dependencies, owned files/modules, typed inputs/outputs, forbidden authority, focused acceptance tests and required product proof/experiment/paper artifact.

Use stronger reasoning/integration agents for temporal semantics, statistical leakage, architecture, hard debugging and adversarial review; parallelize bounded adapters, signal providers, model executors, tests and UX. Agent/model routing should eventually be empirical rather than permanent Sol=Luna role assignment.

There is no direct Luna connector in the current ChatGPT environment; Luna must be launched externally.

## Verification strategy

Tests protect the product; assurance is not the roadmap.

Risk-targeted stack:

- lint/format + strict typing/import rules;
- typed contracts/schema round-trips;
- focused TDD/integration tests;
- property/invariant tests for universal semantics;
- metamorphic tests for PIT/reordering/dedup/retrieval invariance;
- targeted mutation probes for tiny bugs that could create fake alpha/account corruption;
- deterministic replay for experiment identity;
- Lean/SMT only for concrete hard invariants not credibly covered by executable tests;
- historical WFO + forward paper judge investment usefulness.

Correctness gates software merging. Noisy alpha metrics gate research promotion.

## Major adversarial risk

AI coding makes strategy generation cheap and therefore increases the danger of **automated strategy-selection overfitting**.

Do not implement `generate thousands -> choose best historical Sharpe -> declare winner`.

Preserve every attempted strategy/version and the number/search process that produced it. Use strict walk-forward chronology, appropriate untouched evaluation, multiple-testing/backtest-overfitting discipline and prospective paper evidence.

The engine must be allowed to conclude that sophisticated providers have zero useful weight.

## Active durable issues

- #12 — master workstation/product
- #27 — fixed versioned/full-information research lab
- #29 — historical PIT data lanes
- #19 — temporal KG + PIT-safe RAG
- #21 — local model research/training
- #18 — continuous local paper refresh
- #17/#32 — workstation/lineage UX
- #35 — architecture proposal; **must be reconciled with latest adaptive-engine correction**
- #36 — walking skeleton/API contracts/agent work graph; **must generalize beyond mandatory MarketState**
- #37 — Market State/epistemics/trends/exposures signal-provider family
- #38 — portfolio allocation + diversified forward paper
- #39 — reproducible Research Evidence Bundle

## Next exact action

1. Read `docs/handoffs/SESSION_2026-08-28_ADAPTIVE_QUANT_ENGINE.md`.
2. Reconcile #35/#36 and this current state so the adaptive multi-strategy engine is clearly the parent concept and MarketState is optional.
3. Freeze the smallest correct signal/strategy/meta/forecast/portfolio contracts and walking skeleton.
4. Prove the skeleton with a simple price/momentum/breakout/volatility vertical slice that does not require KG/news.
5. Resume #29/#37/#19/#21/#38 workers in parallel behind those contracts.
6. Put every executable credible strategy/policy into local forward paper immediately.
7. Surface signal weights, meta weights, forecasts, target allocation, fills, realized outcomes and version evolution in the workstation.
8. Add #39 audit/export only after useful lineages exist.

## Success criterion

The project succeeds as an investment system if the local adaptive engine can produce reproducible, PIT-correct strategies whose signal/model/policy weighting demonstrates stable incremental usefulness under strict walk-forward research and continues to produce useful cost/risk-adjusted behavior in immutable prospective paper portfolios.

It is not a requirement that MarketState/KG/RAG survive. It is a requirement that the engine objectively learn which components deserve weight.

## Required read order for a fresh session

1. `AGENTS.md`
2. this file
3. `docs/handoffs/SESSION_2026-08-28_ADAPTIVE_QUANT_ENGINE.md`
4. #35
5. #36
6. `docs/handoffs/LATEST.md`
7. #27 + fixed lab contracts/tests
8. relevant candidate issue (#29, #37/#19, #21, #38, #32/#17, #39)
9. `finance_quant/lab/`, `tests/test_lab_*.py`, mutation probes
10. `finance_quant/workstation/` and its product tests
11. older assurance material only when relevant to a concrete product bug
