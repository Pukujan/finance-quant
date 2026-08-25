# Project boundary

`finance-quant` owns the quantitative research/trading laboratory's **policy, contracts, temporal truth, research semantics, evidence, risk/promotion authority, and operator experience**.

## Owned here

- point-in-time/bitemporal data semantics and dataset identity;
- restricted quant IR + temporal/static safety rules;
- research hypotheses, features, labels, walk-forward/split policy and evaluation contracts;
- temporal knowledge-graph semantics, retrieval/weighting policy and versioning;
- local learner contracts and authorized training-data provenance;
- portfolio intent, risk limits and promotion policy;
- execution/paper-session contracts, immutable receipts and conformance tests;
- hidden/sealed evaluation protocol and promotion evidence;
- typed backend API/authority gates;
- operator/research frontend UX (never execution/promotion authority);
- project orchestration, session continuity, issue/state/handoff contracts.

## Mature OSS / external implementation boundary

External systems may supply replaceable machinery behind our contracts:

- NautilusTrader and QuantConnect LEAN are execution/runtime candidates for issue #15; neither is currently selected by the replatform until the bakeoff passes.
- MLflow may store/display experiment and artifact metadata; it is not promotion truth.
- Qlib, LightGBM, scikit-learn, PyTorch and similar libraries may implement research/model lanes; they do not own PIT semantics or promotion.
- Parquet/databases/object stores may implement storage; `finance-quant` owns logical temporal/data contracts.
- FOSSIL may provide durable reviewed evidence/provenance references; it does not own trading, experiment, risk, promotion or high-volume market data.
- Cortex is not a required control-plane dependency. Any future adapter must remain optional/removable.

Adoption order is: upstream pinned dependency -> thin adapter -> constrained extension -> fork only as a documented last resort.

## Frontend authority boundary

New work is vertical-slice oriented (`backend/domain -> typed API/events -> evidence -> UI`). The UI can inspect state and request allowed operations, but it cannot directly mutate authoritative fills/account state, widen risk, promote candidates, open sealed holdouts, or authorize capital.

## Capital boundary

No project issue, CI pass, model/KG output, holdout result, UI action, agent instruction, or OSS runtime automatically grants live-capital authority. Live capital requires a separate explicit human authorization and bounded risk/capital policy.

## Current status

Master replatform: #12. Bootstrap: #13. Assurance contract: #14. Execution/runtime bakeoff: #15. Autonomous Trader v0: #16. Frontend shell/vertical-slice contract: #17.
