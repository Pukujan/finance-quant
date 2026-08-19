# Search Bake-Off V0

The deterministic `random-v0` lane is the permanent floor. It emits only Tier-1 IR
proposals with `authority=propose_only`; no lane API can promote or mutate risk state.
Its seed and expression hash are suitable for `ExperimentLedger.agent_origin` and
candidate lineage. GP, AlphaGen, RD-Agent, and frontier-LLM adapters must target the
same `Proposal` contract and common evaluator before comparison.
