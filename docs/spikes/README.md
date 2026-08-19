# Phase A spike evidence memos

Status: **DRAFT — evidence packs only.** Per issue #1, every spike ends in an explicit
`ADOPT | CONSTRAIN | REJECT | DEFER` decision recorded **by the project owner** in the
GitHub issue. These memos assemble bounded evidence, options, and a recommendation to
make that decision cheap. Nothing here authorizes locking the vertical slice.

| Memo | Issue | Question |
|---|---|---|
| [02-pit-data-temporal-storage.md](02-pit-data-temporal-storage.md) | #2 | What is the PIT market-data authority and which temporal storage carries it? |
| [03-quant-dsl-ir.md](03-quant-dsl-ir.md) | #3 | Do we build a strategy DSL/IR with a static temporal-effect checker? |
| [04-qlib-mlflow-boundary.md](04-qlib-mlflow-boundary.md) | #4 | Where exactly is the Qlib/MLflow experiment boundary drawn? |
| [05-lean-execution-bridge.md](05-lean-execution-bridge.md) | #5 | How do we bridge to LEAN and contract fill/slippage/order semantics? |
| [06-fossil-ontology-graph-features.md](06-fossil-ontology-graph-features.md) | #6 | What is the FOSSIL lineage ontology and the PIT-safe graph-feature boundary? |
| [07-research-search-bakeoff.md](07-research-search-bakeoff.md) | #7 | Which alpha-search lanes (human/random/GP/AlphaGen/RD-Agent/LLM) earn a seat? |
| [08-formal-methods-partition.md](08-formal-methods-partition.md) | #8 | What gets properties vs PBT vs TLA+ vs selective Lean proof? |
| [09-sealed-holdout-adversarial.md](09-sealed-holdout-adversarial.md) | #9 | How is the sealed holdout sealed, and how does adversarial acceptance run? |
| [10-native-orchestration.md](10-native-orchestration.md) | #10 | Native campaign orchestration: WorkOrders, attempts, local backend, fan-out/fan-in |

Conventions used in all memos:

- **Invariant refs** (`I1`–`I8`) point at the eight central project invariants in issue #1.
- **Vertical-slice impact** = the minimum interface this decision must export to Phase B.
- **Bake-off scorecards** are qualitative first passes, to be replaced by measured runs
  where the memo says so. Scores: `++` strong, `+` adequate, `0` weak, `-` disqualifying risk.
- Facts verified live on 2026-08-19 are tagged `(verified)`; design judgments are not facts.
