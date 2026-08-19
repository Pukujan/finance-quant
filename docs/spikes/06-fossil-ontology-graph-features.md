# Spike #6 — FOSSIL quant ontology/lineage + PIT-safe graph-feature boundary

Issue: Pukujan/finance-quant#6
Status: **DECIDED 2026-08-19** — ADOPT ontology + five graph-feature boundary rules, delivered as a dedicated FOSSIL pack with narrow mounts (per fossil-core#176 pack laws); CONSTRAIN Phase B to static graph fixtures; DEFER graph DB. Decision recorded on issue #6 under owner auto-delegation (owner-reversible).
Serves invariants: I2 (reproducibility), I7 (failed trials visible), I1 (PIT correctness
of *derived* graph features), plus the master issue's authority boundary (FOSSIL is not
the numerical hot path)

---

## 1. Two separable deliverables, one spike

**D6.1 — Ontology/lineage:** the vocabulary by which quant facts (datasets, runs,
models, decisions, evidence) get durable, reviewable identity in FOSSIL.
**D6.2 — Graph-feature boundary:** the rule set that lets graph-derived features
(e.g., correlation graphs, sector/supply-chain edges) exist without manufacturing
history or leaking future edges.

They share one spike because both are about *where derived knowledge lives and what
clocks it obeys*.

## 2. D6.1 — Quant ontology into FOSSIL (cold path, non-numeric)

FOSSIL's stated role (master issue): reviewed evidence, decisions, assumptions,
provenance, experiment/result references — *not* the time-series hot path. That is the
right split; MLflow/PIT store own hot artifacts, FOSSIL owns their *meaning and
review trail*.

Draft ontology (PROV-O-shaped, kept small on purpose — ontology bloat kills adoption):

**Entities** (`prov:Entity`)
- `fq:DataSnapshot` — {manifest_hash, namespaces, vt_range, kt_bound} (from #2)
- `fq:RunRecord` — mirrors #4's record, by reference not by payload (FOSSIL stores the
  hash + review metadata; MLflow stores the payload)
- `fq:ModelArtifact`, `fq:FeatureIR` (hash + grammar version from #3)
- `fq:BacktestReceipt` (from #5) and `fq:EvaluationReport`

**Activities** (`prov:Activity`)
- `fq:ExperimentRun`, `fq:SearchTrial` (lane-tagged, ties to #7), `fq:AdversarialCase`
  (ties to #9), `fq:PromotionReview`, `fq:DataIngest`

**Agents** (`prov:Agent`)
- `fq:HumanRole` (owner/reviewer), `fq:AgentLane` (random/GP/AlphaGen/RD-Agent/LLM
  from #7), `fq:PipelineService`

**Relations** (the interesting part)
- `wasDerivedFrom` — snapshot -> run -> model -> receipt -> review
- `wasGeneratedBy` / `used` — standard PROV
- `fq:supersedes` — restatement lineage: revision N+1 supersedes N; N remains queryable
  forever (I7 for *data*, mirrors memo #2's no-delete rule)
- `fq:decidedBy` — every promotion/holdout decision links to exactly one
  `fq:PromotionReview` with `ADOPT|CONSTRAIN|REJECT|DEFER` outcome + evidence links
- `fq:knownAt` — **the crucial one**: every FOSSIL-asserted fact about market reality
  carries the same kt discipline as the PIT store, so evidence graphs obey I1 too
  (an assumption recorded in June must not be readable as if known in March)

Review-write rule: writes into FOSSIL from pipelines happen only through signed
"evidence commits" referencing run_record hashes (#4). Agents can propose (open a
review), only the owner role merges. This is I5 applied to institutional memory.

## 3. D6.2 — PIT-safe graph features

The failure modes this boundary exists to block (all in Phase C's adversarial list):
- an edge created from a *later-announced* relationship (supplier link disclosed in a
  10-K filed 2 months after quarter end);
- graph statistics recomputed globally at t_end and back-attributed to all earlier t
  (classic "the projection state manufactures history");
- survivorship: graph built over today's constituents;
- embedding models trained on full-horizon graphs then queried as of t.

**Boundary rules (proposed contract):**
1. Graph is a **bitemporal edge store**: `edge(src, dst, kind, vt_interval, kt_interval)`
   — same model as memo #2, just a different namespace (`graph_edge`).
2. Feature computation at evaluation instant `t` runs on the graph snapshot
   `G(t_vt, t_kt)` only. Node/edge sets are `AS OF`-filtered *before* any projection or
   aggregation. No global recompute + backfill. Ever.
3. Any learned artifact over graphs (embeddings, GNN weights) is a **versioned model
   artifact** with its own run_record (#4): a GNN trained with data up to kt is a
   function `f_kt`; serving it at evaluation instant t requires `kt <= t`, enforced by
   the run-record query, enforced harder by the Tier-1 checker if features are IR nodes
   (`graph_feature(name, model_run_id)` gets `kt_bound = that run's dataset kt_bound`).
4. Graph-feature outputs land back in the PIT store as ordinary `namespace: graph_feature`
   records with their own vt/kt — after that they are *just data* and all I1 machinery
   applies uniformly. Derived caches are fine; manufactured authority is not (master-issue
   authority boundary, verbatim intent).
5. FOSSIL holds graph-feature *definitions* and *review trail*; numeric values live in
   the PIT store. No exceptions; this keeps FOSSIL out of the hot path.

## 4. Options scored

| Option | I2 lineage | I1 graph safety | Complexity | Verdict lean |
|---|---|---|---|---|
| A. Bitemporal edge store in PIT infra + FOSSIL definitions/reviews (recommended) | ++ | ++ | medium | **recommended** |
| B. Dedicated graph DB (Neo4j etc.) as feature source | + | 0 (as-of filtering is app-level discipline; one sloppy query leaks) | high | DEFER until a measured need exists |
| C. Precooked static graph snapshots per period | 0 | + (safe if discipline holds) | low | acceptable as Phase B fixture shortcut, explicitly labeled derived cache |
| D. No graph features at all | ++ | ++ | 0 | viable scoping choice for the vertical slice; the *boundary rules* are still needed before #7 lanes discover graph alphas |

## 5. Spike verification tasks

1. Encode 5 representative lineage stories (incl. one restatement + one failed run) as
   FOSSIL evidence commits; confirm a reviewer can reconstruct "who knew what when,
   decided what, on which data" from FOSSIL alone in under 10 clicks.
2. Poison drill: construct an edge announced late; show the as-of query at t excludes it
   and the leakage test (#9 harness) flags any feature built without the filter.
3. Fixture: tiny static graph (option C) to unblock Phase B without building the full
   edge store first.

## 6. Vertical-slice impact

- Phase B step 6 ("FOSSIL reviewed result/decision references") needs: the ontology
  above (v0.1), the evidence-commit writer, and one wired-in link from each B1-B5 run
  record to a FOSSIL review. Graph features themselves can be *DEFERRED past the slice*
  (option D+C fixture) without reducing the slice's evidential value.

## 7. Evidence gaps before decision

- ~~Requires seeing fossil-core#176~~ **Done (2026-08-19).** Findings imported:
  FOSSIL's assurance layer is property-first with a machine-readable catalog, pack
  authority laws (`write_targets ⊆ read_mounts`, "authority cannot widen itself") are
  among its Lean-first kernels, and promotion/lifecycle semantics freeze under #111.
  Consequence for this spike: finance-quant lineage evidence should live in a
  **dedicated FOSSIL pack** with narrow read/write mounts (agents mount read-only at
  most; the owner review path holds write) — the ontology in sec. 2 becomes that
  pack's vocabulary rather than free-floating graph writes. No machinery duplication
  needed; we register entities/relations, FOSSIL enforces authority.
- Owner taste call: how much FOSSIL ceremony is tolerable per experiment. Ontology
  above is minimal on purpose; going smaller is possible (`RunRecord + decidedBy` only),
  going bigger is a smell.

## 8. Recommendation

**ADOPT** the ontology skeleton (sec. 2) and graph-feature boundary rules (sec. 3).
**CONSTRAIN** Phase B to static-graph fixtures; full bitemporal edge store lands right
after the slice (it is sql-shaped work on already-chosen infra from #2, not research).
**DEFER** any dedicated graph database to a measured-revisit after bake-off. Write the
five boundary rules verbatim into the issue decision.
