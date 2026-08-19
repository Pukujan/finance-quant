# Spike #7 — Automated research-search bake-off: human vs random/GP/AlphaGen/RD-Agent/frontier models

Issue: Pukujan/finance-quant#7
Status: DRAFT EVIDENCE PACK — owner decision pending
Serves invariants: I5 (search proposes, never promotes), I2 (reproducible trials),
I7 (all trials visible), I8 (no capability jump without the ladder)

---

## 1. Verified state of the world (2026-08-19)

- **AlphaGen** (ICT-FinD-Lab/alphagen, formerly RL-MLDM; KDD 2023): RL (maskable PPO)
  over formulaic alpha expression trees; ships **gplearn (GP) and DSO baselines in-repo**,
  an `alphagen_llm` module (LLM-as-generator + iterative routines), and `alphagen_qlib`
  data adapters; pools export human-readable JSON; `AlphaCalculator` interface verified
  (IC/RankIC/mutual-IC/pool-IC contract). Extension paper HARLA (LLM-assisted) published
  Frontiers of Computer Science 2026.
- **RD-Agent** (microsoft/RD-Agent): `fin_factor` / `fin_model` / `fin_quant` scenarios
  (verified CLI), iterative hypothesis->code->feedback loop, claims ~2x ARR vs benchmark
  factor libraries under $10/run (paper: arXiv 2505.15155, NeurIPS 2025); LiteLLM-native
  (matches our transport), Linux+Docker only, Qlib is its quant backend.
- **Qlib** hosts both as consumers (verified RD-Agent tie-in on the Qlib front page).
- **gplearn** alone is the GP yardstick; trivially runnable.
- **Random search** over the Tier-1 IR grammar (#3) is the disgrace-check baseline
  every learned lane must beat, or the lane is theatre.
- **Frontier LLM lane**: direct proposal of IR expressions by a strong model via LiteLLM,
  seeded with the grammar + a few examples (alphagen_llm shows the pattern).

## 2. Bake-off design (the deliverable)

Lanes (each = a proposal engine, nothing more — I5):
`HUMAN` (owner, small budget), `RANDOM`, `GP` (gplearn), `ALPHAGEN-RL`,
`ALPHAGEN-LLM`, `RD-AGENT(fin_factor)`, `LLM-DIRECT`.

**Arena:** fixture extract from #2 + Alpha158-style operators; single target (e.g.
5-day forward rank IC, cost-aware variant for the second rung). **Same data extract,
same target, same evaluation harness (reference interpreter, #3), same trial budget.**

Two budget-normalizations, both reported:
- **Compute-normalized**: N proposals per lane, N chosen so GPU lanes and CPU lanes
  all finish within the same wall-window (record actuals).
- **Dollar-normalized**: LLM lanes log LiteLLM cost; RD-Agent's <$10 claim gets tested
  on *our* arena, not theirs.

**Deflation controls (what makes this bake-off credible vs the literature's):**
1. Evaluation harness reports **full-trial distributions**, not best-of (I7): median
   quintile performance, not the max. Alpha mining papers report pooled best-of;
   decision-grade evidence needs the distribution.
2. **Deflated significance**: multiple-testing-aware thresholds (deflated Sharpe /
   BH-style control across *all* trials of *all* lanes combined — lanes do not get
   private multiplicity budgets).
3. **Diversity/novelty measure**: mutual-IC matrix per lane output vs a reference
   factor book (Alpha158); a lane that rediscovers known factors efficiently is worth
   less than one that finds orthogonal ones — measure both efficiency and orthogonality.
4. **Leakage audit on samples**: the temporal checker (#3) processes every proposal;
   any proposal needing kt > t is rejected *as invalid syntax*, logged as a lane
   violation (LLM lanes will produce these; the rate itself is evidence).
5. Every trial -> ExperimentLedger with `agent_origin` (#4 contract). No lane may
   promote; promotion is exclusively the #9 sealed path (I5, I8).

## 3. Decision rubric (what ADOPT means per lane)

A lane is ADOPTED if, on our arena: (a) it beats RANDOM by a pre-registered margin
(which is embarrassingly rare in honest settings), (b) its cost per *orthogonal,
checker-clean, deflated-significant* factor is competitive with HUMAN, and (c) its
violation rate is manageable. Otherwise CONSTRAIN (toy-only) or REJECT.

Scorecard to fill with the run (blank = to be measured):

| Lane | Orthogonal yield | $/valid factor | Violation rate | Ops burden | Lean |
|---|---|---|---|---|---|
| HUMAN | (baseline) | (baseline) | ~0 | n/a | reference |
| RANDOM | must-lose floor | high | ~0 | none | keep forever as floor |
| GP (gplearn) | ? | ? | ~0 | low | probable CONSTRAIN-adopt |
| ALPHAGEN-RL | ? | ? | ~0 (grammar-constrained) | medium (GPU, qlib adapter) | ? |
| ALPHAGEN-LLM | ? | ? | ? | low | ? |
| RD-AGENT(fin_factor) | ? | ? | ? | **high: Linux+Docker+full loop** | ? |
| LLM-DIRECT | ? | ? | ? (expected worst) | trivial | ? |

## 4. Costs & ops reality (pre-measured, from docs)

- RD-Agent: heaviest to operationalize (Linux-only, Docker-in-Docker style runs, env
  files per LLM, embedding model required). But it is the only lane that does
  *full-loop* research (hypothesis -> code -> metrics -> memory) rather than expression
  sampling. If any lane justifies its ops, it's this one — which is exactly what the
  bake-off exists to test, not assume.
- AlphaGen-RL: needs GPU time + qlib-format data; `alphagen_qlib` adapter exists but
  upstream itself swapped data sources (baostock) due to Qlib data trust concerns
  (verified in its README) — another vote for "Qlib data is a consumer, not authority."
- GP/random/LLM-direct: all cheap.

## 5. Option set for the actual decision

- **ADOPT** lanes that clear the rubric — as *proposal engines* with fixed, pinned
  versions and logged seeds.
- **CONSTRAIN** promising-but-hungry lanes (likely RD-Agent) to: weekly-batch cadence,
  fixed budget cap, sandboxed Docker (no network beyond LiteLLM), outputs only via IR.
- **REJECT** any lane whose value doesn't survive deflation or whose violations show
  it cannot respect the grammar.
- Standing rule for the issue's decision text: *a lane's authority is permanently
  "propose"; no score, however good, grants promotion — promotion lives only in #9.*

## 6. Vertical-slice impact

- Phase B does not depend on any AI lane (master issue: "no automated alpha search is
  allowed to become the first validation path"). Slice needs from this spike **only**:
  the IR-grammar random sampler (doubles as fuzz input for #3's checker) and the
  `agent_origin` plumbing in the ledger. Everything else is Phase C+ scope.
- This is good news: the highest-risk spike is also the most deferrable.

## 7. Evidence gaps before decision

- The bake-off run itself (design above is executable as soon as #2 fixture + #3
  checker exist).
- GPU availability/quotas for ALPHAGEN-RL on the intended box.
- Pre-register the rubric's margins *before* running (owner decision: pick numbers
  now, e.g. "beat RANDOM median by >= 0.01 rank IC at same budget" — my placeholder).

## 8. Recommendation

**ADOPT the bake-off protocol (sec. 2-3) as written**, with RANDOM and GP lanes built
first (cheap, they exercise the whole harness before expensive lanes touch it).
**CONSTRAIN** RD-Agent to the sandboxed weekly-batch profile pending its measured
yield. **DEFER** AlphaGen-RL until GPU budget is confirmed. Write "proposal-only
authority, forever" into the decision text verbatim.
