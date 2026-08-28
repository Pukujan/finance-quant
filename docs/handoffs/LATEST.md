# Handoff — bounded Market State Fabric direction

Date: 2026-08-28
Branch: `main`
Active architecture proposal: #35
Product mode: local research + zero-money simulated paper only; no broker/live capital

## Current product state

The working workstation and fixed parallel research laboratory are already merged to `main` from PR #34.

Product merge commit: `9fb53a7974ada959b3ed3bd7d7efe135e6e98848`.

The fixed lab remains the benchmark/evaluation authority. Candidate code must not own canonical outcomes, PIT cuts, scoring, evaluation identity, router timing or paper-account truth.

Stable fixed-lab flow:

`publish immutable PIT components -> assemble fixed benchmark -> parallel exact-version arms -> same canonical realized outcome -> ExperimentLedger -> prior-resolved-only router -> isolated shadow paper`

## Architecture refinement now durable

The 2026-08-28 design discussion is captured in #35 rather than left in chat history.

North star:

`world data -> PIT evidence -> epistemic/market state -> exposure/retrieval -> forecast distributions -> portfolio allocation -> local paper -> realized outcome -> learning`

Key correction: forward paper is not a late deployment stage. Every executable surviving arm/policy should start accumulating prospective paper history as soon as it can make a valid decision.

The project is **not** a literal whole-world model. Implementation proceeds through bounded market spheres.

Initial sphere:

- AI + semiconductors;
- US + China + Taiwan;
- roughly 50–100 equities/ETFs;
- daily decisions initially;
- 1d / 5d / 20d horizons.

Architecture remains asset-class-neutral for later crypto/prediction-market adapters.

## New execution issues

- #35 — architecture proposal / north star / phase plan
- #36 — walking skeleton + typed Market IR/API contracts + AI-agent work graph + tiered CI
- #37 — bounded Market State Fabric: claims/evidence/epistemics/trends/exposures
- #38 — forecast-to-allocation portfolio engine + diversified forward paper
- #39 — reproducible Research Evidence Bundle + semantic provenance export

Existing lanes remain active and are extended rather than replaced:

- #27 fixed experiment flywheel/control plane
- #29 historical PIT data lanes
- #19 temporal KG + PIT-safe RAG
- #21 local models/ranking
- #18 continuous paper loop
- #17/#32 workstation UX/lineage

## What the Market State Fabric means

Do not store naked graph facts.

Preserve:

`SourceArtifact -> Observation -> Claim -> Evidence -> bitemporal EpistemicState -> MarketBeliefState -> Derived MarketState -> BenchmarkedKnowledge -> PredictiveKnowledge`

Keep factual reliability, attention/hype, economic materiality, exposure strength and predictive usefulness separate.

Use a stable core ontology plus versioned domain modules. Temporal economic relations retain valid/knowledge time, provenance, confidence and materiality. Graph traversal remains typed and bounded.

`TrendState` tracks level, robust percentile/z-score, multi-horizon velocity, acceleration, noise, trend shape, structural breaks, novelty, persistence, saturation/decay and cross-source confirmation rather than one generic sentiment/hype number.

## Data compression

Local-first pipeline:

`raw stream -> relevance -> dedup/story clusters -> claims/events/entities -> state deltas/checkpoints -> compact MarketState -> model matrices`

Target tiers:

- cold raw permitted evidence: compressed Parquet/ZSTD;
- canonical claims/events/entities/relations/provenance;
- MarketState checkpoints/deltas;
- PIT model-ready decision snapshots.

Do not predict once per incoming article. Use scheduled cuts and/or material state changes.

## Forecasting direction

Retrieval has two roles:

1. retrieve current relevant evidence;
2. retrieve prior resolved states/episodes similar to the present one.

Initial arms stay interpretable:

- price only;
- direct news/events;
- TrendState;
- compact MarketState;
- MarketState + bounded graph exposure;
- historical analog weighted-return baseline;
- LightGBM/XGBoost cross-sectional ranker.

Later temporal/neural models are conditional on evidence that simpler models/state representations justify them.

## Portfolio engine — do not stop at predictions

#38 owns the second half of the product.

The system must explicitly answer:

- where to invest;
- how much to invest;
- how much cash to keep;
- how to diversify by economic exposure;
- what to buy/sell/hold;
- when/where to rebalance under simulated liquidity/cost assumptions;
- when to abstain/no-trade.

`PortfolioIntent` is the typed handoff from forecasts to paper execution and includes target weights, trade deltas, target cash, expected return/risk/cost, turnover, binding constraints and provenance.

Initial allocation-policy arms:

1. equal-weight top-K;
2. edge/confidence weighted top-K with caps;
3. volatility-scaled/risk-budgeted;
4. mean-variance/robust convex allocation with turnover/cost penalties;
5. explicit cash/no-trade threshold.

Each uses identical upstream forecasts and gets its own historical OOS comparison + persistent isolated forward paper account. Forecast skill and allocation skill are scored separately.

## SWE / agent operating model

Use a modular monolith with process-isolated heavy workers, not microservices by default.

Permanent walking skeleton:

`SourceAdapter -> CanonicalObservation -> MarketState -> ForecastDistribution -> PortfolioIntent -> PaperFill -> CanonicalOutcome -> Score -> Workstation`

#36 freezes shared typed contracts and machine-readable work packets before the broad parallel candidate wave.

Every work packet declares dependencies, owned files/modules, typed inputs/outputs, forbidden authority, acceptance tests and required product proof.

Use stronger central reasoning/integration agents for temporal semantics, statistical leakage, shared architecture and hard debugging; fan bounded adapters/features/models/tests/UX out to parallel workers. Model routing should be empirical rather than a permanent Sol=Luna role assignment.

Verification is risk-targeted:

- lint/strict types/contracts for ordinary AI coding errors;
- focused TDD;
- property/invariant tests;
- metamorphic tests for PIT/reordering/dedup/retrieval invariance;
- targeted mutation tests for tiny research-invalidating bugs;
- deterministic replay;
- Lean/SMT only for concrete hard invariants where executable tests are insufficient;
- historical WFO + forward paper judge research value.

Correctness gates merges. Alpha/performance gates research promotion.

## Audit/reproducibility

#39 targets a sellable Research Evidence Bundle using immutable manifests/ledger plus RDF/JSON-LD, OWL 2, SHACL, PROV-O, deterministic hashes and RO-Crate-style packaging where useful.

The audit layer is not the hot runtime. Its purpose is to let an external party trace a result from exact inputs/state/model/portfolio intent through realized outcome and reproduce scoring where licensed data are available.

## Immediate next action

1. Implement/freeze #36 shared contracts, walking skeleton, MarketIR, PortfolioIntent, work-packet schema and CI tiers.
2. Resume #29 raw market/SEC/macro/news workers behind those contracts.
3. Build #37 AI+semiconductor state vertical slices.
4. Feed #19 KG/RAG + historical analog retrieval into experiment arms.
5. Run #21 conventional local model/ranking families.
6. Implement #38 allocation-policy competitors and start their forward paper accounts immediately.
7. Surface evidence/state/forecast/allocation/fills/results in #32/#17.
8. Add #39 audit export after useful experiment lineages exist.

Each phase must report correctness, data quality/coverage, signal metrics, portfolio/paper metrics and operational metrics.

## Important boundaries

- No live capital/broker authority.
- Software correctness is not predictive evidence.
- Negative OOS/forward-paper results stay in lineage.
- Do not inspect or optimize against the private sealed holdout without explicit authorization.
- Do not build distributed infrastructure unless actual local workload demonstrates the need.
- Do not let assurance/meta-systems become the product.
