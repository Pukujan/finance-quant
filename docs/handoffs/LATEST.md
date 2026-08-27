# Handoff — OSS product architecture reassessment before A2 HITL

Date: 2026-08-27
Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #16
Assurance phase: A2
Authority: trading `NONE`; unattended paper disabled; live capital disabled

A2 public implementation/assurance and genuine one-shot hidden acceptance are complete for frozen public evaluation SHA `1ecc470cd6e0e23bf1d439f51e4e2c39674f02c4` / candidate artifact SHA-256 `446fdc1a0c87db3a6a2ab4e94fab3d7e9f8fd389cc41676be12c3803b1f2d093`. The remaining formal A2 gate is `HITL_PROMOTION`.

**Do not request or grant HITL yet.** The owner clarified that the intended product is a visible local autonomous quant workstation with configurable starting paper capital, real historical/ongoing PIT data, temporal knowledge/RAG, local model training, paper execution, and a proper operator dashboard. The current A2 kernel proves the lower trading/account/replay substrate but does not yet provide that whole product.

A detailed OSS product-level scan is now the active next step. Verified candidates include:

- `AI4Finance-Foundation/FinRL-Trading` (FinRL-X): unified market data, ML/DRL strategies, backtesting, Alpaca paper/live execution, risk/P&L and deployment workflow; candidate larger trading/research substrate.
- `Open-Papertrade/Open-Papertrade`: Django + Next.js full-stack paper trading on live quotes, charts/backtests, SEC filing RAG with citations/refusal, local LLM support; strongest candidate/reference for visible product UX and RAG, with AGPL licensing implications.
- `Open-Finance-Lab/AgenticTrading`: agent dashboard, backtests/paper simulations, positions/trades/reasoning, FastAPI/frontend, broker infrastructure and FinAgent orchestration; shipping paper backend still requires caution because repo identifies it as a stub in the current v2 execution layout.
- `microsoft/qlib` + `microsoft/RD-Agent`: strongest current research/factor/model automation candidates; Qlib includes full ML pipeline, PIT DB support, online serving and trading/research infrastructure, while RD-Agent(Q) automates factor/model co-optimization.
- OpenBB and FinGPT remain follow-up candidates for broad data/research and financial RAG components.

Finance-quant already contains valuable reusable assets that should not be discarded casually: strict `vt/kt` bitemporal PIT semantics/store, Polygon ingestion, Qlib compiler boundary, temporal-KG boundary design, validated LEAN execution, authoritative SQLite account/replay, sealed acceptance, mutation/chaos testing and authority/promotion controls.

## Next exact action

Perform an explicit OSS architecture bakeoff and produce a layer-by-layer **KEEP / REPLACE / ADAPT / DELETE** matrix for data/PIT, research/model training, KG/RAG, execution/paper account, frontend/operator UX and local deployment. Evaluate licensing, maintenance, Windows/local operation, security/credentials, provenance/PIT correctness and conformance-test cost. Then update the roadmap before implementing the pivot.

Until that decision is durable:

- keep trading authority `NONE`;
- keep unattended paper disabled;
- keep live capital disabled;
- do not consume another A2 hidden seal use;
- do not throw away validated evidence;
- do not continue custom frontend/model work merely because it was on the old sequence.

Detailed append-only handoff: `docs/handoffs/2026-08-27-oss-product-architecture-reassessment.md`.
