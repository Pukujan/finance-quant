# Handoff — adaptive modular quantitative portfolio engine

Date: 2026-08-28
Branch: `main`
Active architecture issue: #35 (pending latest framing reconciliation)
Product mode: local research + zero-money simulated paper only; no broker/live capital

## Luna execution progress — market lane

The first candidate lane is now implemented locally in `finance_quant/lanes/market.py`.
It keeps raw OHLCV separate from timestamped split/dividend events, selects the
latest visible source revision at an explicit knowledge cut, and makes
split-adjusted reconstruction an explicit derived view. Existing user research
files under `data/knowledge_graph/` and `docs/spikes/` were preserved.

Real AAPL Yahoo chart data was fetched for `2023-01-01` through `2025-12-31`:

- 752 raw bars;
- 12 corporate-action events;
- raw artifact: `fa36ec25957cc5c6d699d2c568b50afc086bd014e6f241793dff35d2c7522c60`;
- timestamped-action artifact: `81beccaab4f4d406072b61b09928381a020fe4f57ff8dc6d5d134e0693ab9c00`.

The bounded development experiment rebuilt the raw artifact with an explicitly
named session-close knowledge-clock upper-bound assumption because the Yahoo
response does not provide complete historical first-publication timestamps:

- experiment output: `experiments/luna/market-aapl-dev-2023-2025/`;
- market artifact: `01ebec7b449cbd65ff7966136758c0a839e0a7eade6669f084fef1ca0cefc751`;
- 751 next-session canonical outcomes;
- evaluation hash: `b3d531720440ea71dfbfcc4db9b378c9dca266f29e9c92c8b9cb71f29875504c`;
- raw intraday-return arm directional accuracy: **50.5992%**.

This is a lane/public-development result, not evidence of profitability or
historical first-known correctness. The assumption and source limitation stay
attached to the artifact metadata and must be replaced by a source with proper
historical availability clocks before multi-lane claims.

## Additional Luna lane progress

The SEC/document lane is implemented in `finance_quant/lanes/sec.py` and has
been run against real public AAPL data for the same range:

- 12 filings and 966 structured CompanyFacts rows;
- filing artifact: `4992c0e673e6a69361c274170f8bd3cd4c7b725fda97bcffc980f55392325b37`;
- facts artifact: `e0c26c5e9a48c04b2d832ee4f1f2e0248d559f22d385d3645c20771ae95cbe80`;
- amendment count in this slice: 0;
- acceptance-time integration probe evaluation hash:
  `32eaa081fbd52a713cb51b1816c2443df39e03ab3bafba235d7a9a12e401f308`;
- 730 canonical outcomes; market-only and SEC-presence probe both scored
  **50.5479%** directional accuracy.

The macro vintage lane is implemented in `finance_quant/lanes/macro.py` and
published a CPIAUCSL current-vintage development artifact:

- artifact: `507b7f5fb7b3c54cc82b6d9b00d5797b67062cdbfe43f19aa04d43049dda7519`.

The artifact is explicitly marked current-vintage/conservative-ingest because
the public FRED graph endpoint does not expose the full ALFRED release archive.
The parser and visibility logic support pinned ALFRED CSV vintages when those
files are supplied.

The PIT-safe RAG lane is implemented in `finance_quant/lanes/rag.py` and has a
derived artifact from the SEC filing artifact:

- artifact: `d018c34466bbeafff83273b9225d1d85c9962ce5848b2dbd16103fe015cda50a`;
- parent: SEC filing artifact `4992c0e673e6a69361c274170f8bd3cd4c7b725fda97bcffc980f55392325b37`.

The temporal industrial-KG lane (`finance_quant/lanes/kg.py`) and local model
executors (`finance_quant/lanes/models.py`) are implemented and covered by
bounded traversal, PIT exclusion, provenance, and frozen-context tests.

The first bounded market/SEC/RAG/model-family matrix also completed:

- output: `experiments/luna/first-multilane-matrix-aapl/`;
- 5 arms and 730 shared canonical outcomes;
- evaluation hash: `809e9e91053211f1d4a809128a65513bf434c6f8fdf0c55cb420c0a106d7a650`;
- market raw, SEC-presence, and RAG-presence probes: **50.5479%** directional accuracy;
- logistic arm: **50.5479%**;
- threshold-tree arm: **54.1096%**.

The tree result is exploratory only: one symbol, one development period, and
the session-close clock assumption. It is not OOS evidence, a profitability
claim, or a promotion signal.

The model/router/shadow worker added an integration proof in
`tests/test_model_router_shadow_integration.py`: multiple local model arms
produce predictions from frozen contexts, the fixed router sees only resolved
prior OOS scores, and the selected arm advances an isolated restartable
zero-money shadow account idempotently. No fixed lab authority was changed.

The contextual-router experiment is recorded under
`experiments/luna/contextual-router-aapl/`:

- input evaluation hash: `809e9e91053211f1d4a809128a65513bf434c6f8fdf0c55cb420c0a106d7a650`;
- 730 routes, with 730 distinct shared canonical outcome IDs;
- selected `market-tree` 486 times and `market-sec-presence` 244 times;
- directional accuracy: **52.0548%**;
- compounded strategy net return: **0.1630** under the existing development
  cost convention.

This is a negative model-selection result relative to the standalone tree arm
on the same single-symbol development slice. It writes no paper state and is
not a promotion signal.

The news/event lane (`finance_quant/lanes/news.py`) is implemented with
publication/first-seen clocks, story-key syndication dedup, and bundle payloads.
A bounded GDELT replay is now pinned for public development:

- AAPL/AMZN/MSFT article metadata, 2023-01-01 through 2025-12-31: **2,270** records;
- replay SHA-256: `542560f6134cf4a869e125674dad15c65afaee76a38216ef7eb7f53c422ee685`;
- component artifact: `727188f0b7e6455206890ab484cf41eaeddb32730da48b6ce4ae497c30bfdd8f`;
- English-language filter and GDELT first-seen clocks are recorded in the source manifest.

This pull returned no distinct publication timestamps, so publication is
conservatively equal to first-seen for all 2,270 records. The environment
required an explicit HTTP endpoint fallback; the replay is content-pinned but
the source transport is not authenticated. It is therefore a public
development artifact, not a private/sealed scorer input.

A real public SEC regulatory-event artifact remains available separately:

- AAPL 8-K/8-K/A/6-K/6-K/A events, 2023-01-01 through 2025-12-31: 25 events;
- artifact: `d1f50afdfa884d4f26b1b7d7e6deb2623a797af1c67dd843301024edc231caa9`;
- exact acceptance clocks preserved.

`finance_quant/lanes/replay.py` now provides content-hashed JSONL replay input
validation for future pinned news and industrial-KG sources.

## Parallel Luna wave — public integration result

The seven candidate workstreams were run in parallel and integrated against the
fixed lab. The completed public artifacts and bounded experiments are retained
under `experiments/luna/`:

- pinned news/event replay: `03e52872be60d65a8186b522cf9c78f9a2fc60e0c4c6fcf15b28fc44d914b505`;
- pinned GDELT article replay: `727188f0b7e6455206890ab484cf41eaeddb32730da48b6ce4ae497c30bfdd8f`, with compact summary index `f04abd1eb257b610bac7c94889c228bd4c68c50aaff55aa588c94774923d4929`;
- ALFRED CPI vintage replay: `3f2f4ab1c4a68578b1814fc9f5dee648fe8f41006ee205e91a2102e2981b6e35`, 68 observations across three vintage cuts;
- Wikidata industrial relation snapshot: `353fe8d79c970a0be67e9d4b44619a896febe5465de69ec163b9ad624aead420`, 322 relations, with bounded traversal verified;
- multi-symbol market/SEC/events/RAG/model matrix: 2,197 shared outcomes for AAPL/MSFT/AMZN, evaluation hash `a01ad41ac0e83c34fd59b0a289be28ba935684a2067c748416acf8fa96e34a9e`;
- macro-integrated matrix: 1,503 shared outcomes and eight bounded arms, evaluation hash `f46f8be889b3f6e66fa22d8c2b12c03f84b2f96d3fe66eb9d55fd632bdf7a3d0`;
- fundamentals/news-index matrix: 1,503 shared outcomes and 15 bounded arms, evaluation hash `5feebfaa3f9a469d90080fbd5174efb2b455a4475313437f6a44f8b21788faf7`;
- chronological public OOS/regime summary: per-symbol 80/20 split with 440 aggregate OOS scores; summary hashes are recorded in `experiments/luna/multisymbol-oos-regime/manifest.json`;
- extended 2020–2025 public market/SEC run: 4,149 shared outcomes, evaluation
  hash `0912e4e64c02dfd13da68a56cdf2c9a20fdea3ac60caacd4fbb2596978d388ba`,
  with 831 independent chronological OOS decisions summarized under
  `experiments/luna/multisymbol-public-oos-regime-2020-2025/`;
- training-only entity-threshold control: per-symbol thresholds fit on the
  first 80% of that benchmark and evaluated on the same 831 OOS decisions;
  output `experiments/luna/trained-entity-tree-2020-2025/`, OOS summary
  `experiments/luna/trained-entity-tree-oos-regime-2020-2025/`;
- contextual router run: 2,197 decisions, evaluation hash `a01ad41ac0e83c34fd59b0a289be28ba935684a2067c748416acf8fa96e34a9e`, 52.6627% directional accuracy, and no unresolved-score access.

The integration probes intentionally keep the information-lane contribution
neutral; they prove PIT availability and arm wiring, not predictive value. The
tree arm is retained as exploratory only. The Wikidata snapshot has a truthful
2026-08-28 retrieval cut and is therefore not backdated into the 2023–2025
score. The GDELT replay is currently metadata-only and has no distinct
publication clock, so no GDELT predictive claim is made. Full repository
regression after the current public wave is `968 passed, 24 skipped`.

The current 2023–2025 AAPL/MSFT/AMZN US-equity slice is an engineering-first
public fixture, not a final market-scope decision. The open question covering
longer history, survivorship-aware equities, crypto, FX, prediction markets,
and asset-specific objective/cost semantics is recorded in
`docs/plans/OPEN_SCOPE_QUESTIONS.md` as `Q-SCOPE-001`.

The 2020–2025 extension broadens the public development check but does not
turn the session-close market clock into a source-native historical clock. Its
tree-vs-raw OOS result remains exploratory and is not a promotion signal.
The training-only per-symbol tree matched the fixed tree on OOS accuracy, so
the fixed absolute threshold `150` remains an unresolved control choice rather
than a validated universal model rule.
The calendar-year/cost-stress diagnostic is retained at
`experiments/luna/trained-entity-tree-calendar-cost-2020-2025/`; it shows
47.41% accuracy in 2022 and severe degradation as costs rise, so the apparent
development result is not promotion-grade.

## Historical workstation paper replay — frozen public inputs

The existing workstation model was replayed over 2018–2025 for AAPL, MSFT,
and AMZN using strict walk-forward ridge predictions and isolated durable local
virtual accounts. The corrected frozen run is at
`experiments/luna/workstation-paper-replay-2018-2025-frozen-v2/`; the original
frozen public inputs are at
`experiments/luna/workstation-paper-replay-2018-2025-frozen/inputs/`.

Each symbol has 2,011 daily bars and 1,824 predictions. Execution is a next-
session open target rebalance, marked at the next-session close, with 95%
allocation and 2 bps slippage. Per-account starting cash was $100,000:

| Symbol | Baseline final NAV | SEC-informed final NAV |
| --- | ---: | ---: |
| AAPL | $372,486.44 (+272.4864%) | $204,288.14 (+104.2881%) |
| MSFT | $404,867.88 (+304.8679%) | $251,546.30 (+151.5463%) |
| AMZN | $87,714.15 (−12.2858%) | $168,199.60 (+68.1996%) |

The independent repeat matched all prediction metrics, fills, NAVs, and
account state hashes. This is marked zero-money historical simulation, not
broker paper or live performance. It does not establish SEC-informed model
superiority: that arm loses to baseline on AAPL/MSFT and wins on AMZN. The
input clock caveat remains: adjusted Yahoo bars lack source-native historical
knowledge timestamps, and SEC facts use filed date as the knowledge cut.

The v2 replay persists a run fingerprint, atomically commits each order+fill,
and writes an atomic per-session checkpoint. Restarting the completed v2 run
produced identical state hashes without duplicate effects. Frozen cost
sensitivity across the three separate accounts produced aggregate marked
totals of **$951,632.84 at 0 bps**, **$865,068.47 at 2 bps**,
**$750,119.78 at 5 bps**, and **$592,973.35 at 10 bps** for baseline,
versus **$675,630.91**, **$624,034.03**, **$553,544.34**, and
**$453,524.03** for SEC-informed.

The replay harness is `scripts/run_workstation_paper_replay.py`, SHA-256
`2637a2f91f2405a5ad8772eda9ceb05b5ab7e94db2348cde6573a3008e8553a4`.

## Merge state
## Full continuation package

**Read this first:**

`docs/handoffs/SESSION_2026-08-28_ADAPTIVE_QUANT_ENGINE.md`

Current `main` handoff/documentation head: `12d63b8cbffc09cb41db9c341c0ae0329a913f4a`.

The merge was built directly on the previous `main` rather than merging the long-lived bootstrap branch. Obsolete A1/A2 assurance workflows/contracts, hidden-acceptance machinery, formal/TLA promotion material, and old assurance handoffs were deliberately excluded. Dirty integration PR #33 is closed and unmerged.
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

## Public Luna implementation result — 2026-08-28

The first non-probe fundamentals arm is now wired into the fixed lab. It
consumes only the frozen, acceptance-clocked SEC CompanyFacts artifact
`49082e11942dfadb56bdf27866a20f06b884d3c84a9842c0c4101f6828070de9` and emits
a bounded direction from the latest comparable revenue periods. Focused tests
and the full public regression are green: **968 passed, 24 skipped**.

The public development matrix used 1,503 shared outcomes, 13 explicit arms,
and the ALFRED CPI vintage artifact
`3f2f4ab1c4a68578b1814fc9f5dee648fe8f41006ee205e91a2102e2981b6e35`:

- evaluation hash: `43dfa010b5b5506699ace88614996f1181d4160dff9720973644daaa3f793ef5`;
- batch hash: `1bea1647e531d704d7d8863fc0844cad17b1bbf76655dd11cbded78f70453dd9`;
- `market-fundamentals`: **54.2249%** directional accuracy, MAE **0.011777**;
- raw price and macro/event/RAG presence probes: **50.0998%** directional accuracy;
- existing threshold-tree probe: **53.8257%** directional accuracy.

The CPI-momentum development arm was neutral for all 1,503 decisions because
the available ALFRED bundle has only three conservative year-end vintage cuts;
it produced no nonzero predictions and is not treated as evidence of macro
value. The 80/20 per-symbol OOS summary for fundamentals was **53.7954%** over
303 decisions versus **51.4851%** for raw price.

The fundamentals-plus-macro and fundamentals-plus-information arms matched
the fundamentals arm because those lanes are currently validated presence
inputs, not predictive features. These are public exploratory results only;
they do not establish hidden-holdout performance, causal value, or live
profitability.

## Who does what now
`finance_quant.lab` remains the authority for:

- PIT benchmark/snapshot truth;
- canonical realized outcomes;
- evaluation identity;
- scoring;
- prior-resolved-only routing semantics;
- isolated persistent paper-account truth.

Candidate providers/models/strategy/meta/portfolio policies do not own the answer key.

Existing AAPL empirical baseline remains:

The decision-tree choice remains explicitly unresolved. See
`docs/plans/OPEN_MODEL_QUESTIONS.md` (`Q-MODEL-001`) for the rationale,
current threshold-artifact risk, and resolution requirements. The tree remains
an exploratory control and is not a promotion decision.

## Next exact implementation wave

The initial seven-worker candidate wave is complete. Continue with source
hardening and OOS experiments:

1. run a clean walk-forward/OOS ablation for the new fundamentals arm across additional symbols and regimes;
2. replace development upper-bound clocks with source-native historical clocks where available;
3. replace the development-only GDELT fallback with an authenticated pinned
   historical news replay that has native publication/first-seen timestamps;
4. obtain dated industrial supplier/customer/competitor evidence before adding KG arms to historical scoring;
5. compare stronger local model families and contextual prior-OOS-only routing;
6. implement predictive macro/news/KG transforms only after their clocks and replay tests are independently green.
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
