# Current project state

<!-- MACHINE-STATE: architecture=TEMPORAL_MARKET_STATE_FABRIC_PLUS_FIXED_LAB status=CONTRACT_FREEZE_BEFORE_PARALLEL_BUILD active_issue=35 -->

## Active product direction

The working workstation and fixed experiment laboratory remain on `main`. The architecture has now been refined in durable proposal #35.

North star:

`world data -> PIT evidence -> epistemic/market state -> exposure/retrieval -> forecast distributions -> portfolio allocation -> local zero-money paper -> realized outcome -> learning`

At decision time `T`, the system must use only information legitimately knowable at `T`, derive a compact economically relevant state, rank the best/worst available investments, decide how much to hold/buy/sell/diversify/cash, persist an inspectable simulated portfolio decision, and learn from subsequent realized outcomes.

Forward paper is a continuous benchmark, not a later phase. Every executable surviving arm should begin accumulating prospective paper history as soon as it can make a valid decision.

Live capital remains out of scope.

## Scope control

Do not build a literal whole-world model.

The implementation unit is a **bounded market sphere**: a controlled investment universe plus the smallest economically relevant information frontier around it.

Initial empirical sphere from #35/#37:

- AI + semiconductors;
- US + China + Taiwan;
- roughly 50–100 equities/ETFs initially;
- daily decisions initially;
- 1d / 5d / 20d research horizons;
- interfaces remain asset-class-neutral for later crypto/prediction-market adapters.

Second-domain generalization should use something materially different, such as SaaS, without rewriting the core engine.

## Architecture

Use a **modular monolith with process-isolated heavy workers**, not microservices by default.

Three planes:

1. product/runtime — evidence -> state -> forecast -> portfolio -> paper -> workstation;
2. research/evaluation — fixed PIT benchmark -> arms -> canonical outcomes -> scores -> lineage -> forward paper;
3. agent-control — specs/contracts -> work packets -> agents -> CI -> merge -> handoff.

The agent-control plane exists to accelerate the product; it is not the product roadmap.

Permanent walking skeleton:

`SourceAdapter -> CanonicalObservation -> MarketState -> ForecastDistribution -> PortfolioIntent -> PaperFill -> CanonicalOutcome -> Score -> Workstation`

Every new capability should enter as a vertical slice through that spine.

## Fixed laboratory remains authoritative

`finance_quant.lab` continues to own canonical historical snapshots/outcomes, PIT cuts, scoring, evaluation identity, router timing and simulated-account truth. Candidate components may propose knowledge, state, retrieval, forecasts and portfolio policies; they do not own the answer key.

Stable flow:

`publish immutable components -> assemble PIT benchmark -> run exact-version arms -> join same canonical outcome -> score -> ExperimentLedger -> prior-resolved-only routing -> isolated paper accounts`

Existing fixed-lab semantics, component hashes, evaluation hashes, mutation probes and paper-account invariants remain in force. Proposal #35 extends the candidate/product layers rather than replacing these semantics.

## New durable architecture issues

- #35 — Temporal Market State Fabric + portfolio-intelligence proposal
- #36 — walking skeleton, typed Market IR/API contracts, AI-agent work graph and tiered CI
- #37 — bounded epistemic/trend Market State Fabric
- #38 — forecast-to-allocation portfolio engine + diversified forward paper
- #39 — reproducible Research Evidence Bundle + semantic provenance export

Existing execution lanes remain active:

- #27 fixed versioned knowledge/full-information experiment flywheel
- #29 historical PIT data lanes
- #19 temporal KG + PIT-safe RAG
- #21 local model research/training
- #18 continuous local paper refresh
- #17/#32 workstation/lineage UX

## Epistemic/state direction

Do not store naked graph facts. Preserve distinct layers:

`SourceArtifact -> Observation -> Claim/Proposition -> Evidence -> bitemporal EpistemicState -> MarketBeliefState -> Derived MarketState -> BenchmarkedKnowledge -> PredictiveKnowledge`

Factual confidence, market attention, economic materiality, exposure strength and predictive usefulness stay separate.

The ontology has a stable core plus versioned domain modules. The temporal graph carries valid/knowledge time, source/provenance, confidence and materiality. Graph traversal remains typed and bounded.

`TrendState` should retain level, robust percentile/z-score, multi-horizon velocity, acceleration, noise, dominant trend shape, structural-break probability, novelty, persistence, saturation/decay and cross-source confirmation instead of one generic hype score.

## Data/compression direction

Local-first data lifecycle:

`raw stream -> relevance filter -> dedup/story clusters -> claims/events/entities -> state deltas/checkpoints -> compact MarketState -> model matrices`

Target storage tiers:

- bronze/cold raw permitted evidence: compressed Parquet/ZSTD;
- silver canonical claims/events/entities/relations/provenance;
- gold MarketState checkpoints + deltas;
- platinum PIT model-ready decision snapshots.

Do not predict once per article. Predict at scheduled cuts and/or material state changes.

## Forecast/model direction

Retrieval is first-class but not a replacement for forecasting:

1. evidence retrieval — what matters at `T`;
2. historical analog retrieval — which prior resolved states resemble the current one.

Initial model comparisons should remain simple and interpretable:

- price-only;
- price + direct news/events;
- price + TrendState;
- price + compact MarketState;
- price + MarketState + bounded graph exposure;
- historical-analog weighted-return baseline;
- LightGBM/XGBoost cross-sectional ranker;
- later temporal/neural models only if data volume justifies them.

Prefer calibrated predictive distributions and cross-sectional ranking over pretending exact point-return forecasts are certain.

## Portfolio engine direction

#38 owns the second half of the product.

The system must answer:

- where to invest;
- how much to invest;
- how much cash to hold;
- how to diversify by real economic exposure;
- what to buy/sell/hold;
- where/when to trade under simulated liquidity/cost assumptions;
- when to abstain;
- how/when to rebalance.

`PortfolioIntent` is the immutable contract from forecasts to paper execution and records target weights, trade deltas, target cash, expected return/risk/cost, turnover, constraints and provenance.

Initial allocation-policy arms:

1. equal-weight top-K;
2. edge/confidence-weighted top-K with caps;
3. volatility-scaled/risk-budgeted;
4. mean-variance/robust convex allocation with turnover/cost penalties;
5. explicit cash/no-trade threshold policy.

Each policy receives identical upstream forecasts/cost assumptions and gets historical OOS metrics plus its own persistent forward paper account. Forecast quality and allocation quality are scored separately.

## SWE / multi-agent execution

#36 must be completed enough to freeze shared contracts before the broad parallel build.

Every agent work packet should declare issue/dependencies, owned modules, typed inputs/outputs, forbidden authority, focused acceptance tests and required product proof/experiment arm.

Use capability-based routing: stronger reasoning/integration agents for temporal semantics, statistical leakage, shared architecture and hard debugging; parallel workers for bounded adapters, feature lanes, model executors, tests and UX. Track agent performance by task class and merge/regression outcomes rather than hard-coding permanent roles.

Verification is risk-tiered:

- lint/format + strict typing/import rules;
- contract/schema round-trips;
- focused TDD;
- property/invariant tests;
- metamorphic tests for PIT/reordering/dedup/retrieval invariance;
- targeted mutation tests where tiny bugs could create fake alpha/account corruption;
- deterministic replay;
- Lean/SMT only for concrete hard invariants not credibly covered by executable tests;
- historical WFO + forward paper judge investment usefulness.

Correctness gates software merges. Alpha/performance gates research promotion.

## Reproducibility/audit direction

#39 targets a sellable `Research Evidence Bundle` using existing immutable manifests/ledger plus standards-based export where useful: RDF/JSON-LD, OWL 2, SHACL, PROV-O, deterministic hashes and RO-Crate-style packaging.

Goal: an external party can trace a result from exact inputs/state/model/portfolio decision through realized outcome and recompute scores where licensed inputs are available.

## Existing empirical baseline retained

The current workstation remains runnable:

`python -m finance_quant workstation --ticker AAPL --start 2018-01-01 --capital 100000`

Existing real AAPL/SEC workflow produced 1,988 walk-forward predictions:

- price-only directional accuracy: 53.3702%;
- price + current small SEC-fundamental set: 51.8612%;
- delta: -1.5091 percentage points.

The tiny fundamental set hurt the simple baseline. Do not claim KG predictive value from it.

Existing zero-money paper proof remains a signal -> persistent decision -> next-open simulated fill -> marked account proof, not profitability evidence.

## Immediate execution order

1. Freeze #36 walking-skeleton/API/MarketIR/PortfolioIntent/work-packet contracts and tiered CI.
2. In parallel, resume #29 raw market/SEC/macro/news PIT lanes behind those contracts.
3. Build #37 AI+semiconductor evidence/epistemic/trend MarketState vertical slices.
4. Feed #19 bounded KG/RAG and historical-analog retrieval into state/forecast arms.
5. Run #21 local ranker/model families against identical PIT states/outcomes.
6. Implement #38 competing allocation policies and start their forward paper accounts immediately.
7. Surface state, evidence, forecasts, target allocation, fills and comparative performance in #32/#17 workstation UX.
8. Add #39 audit/export once useful experiment lineages exist; do not put semantic-export tooling on the hot path prematurely.

Every phase reports five categories: correctness, data quality/coverage, signal metrics, portfolio/paper metrics and operational metrics.

## Success criterion

The project succeeds as an investment research system only if richer state provides stable **incremental leakage-free out-of-sample information** over simpler baselines and the resulting portfolio policies continue to add useful cost-adjusted value in immutable forward paper trading with controlled risk.

Negative lanes/models/policies remain durable results and can be removed from the active path rather than defended with added complexity.

## Required read order for a fresh implementation session

1. `AGENTS.md`
2. this file
3. #35
4. #36
5. `docs/handoffs/LATEST.md`
6. #27 + existing fixed lab contracts/tests
7. relevant implementation issue: #29, #37/#19, #21, #38, #32/#17 or #39
8. `finance_quant/lab/`, `tests/test_lab_*.py`, `scripts/run_lab_mutation_probes.py`
9. `finance_quant/workstation/` and `tests/test_workstation_product.py`
10. older assurance material only when relevant to a concrete product bug
