# Spike #3 — Quant DSL/IR + temporal-effect checker + reference interpreter

Issue: Pukujan/finance-quant#3
Status: **DECIDED 2026-08-19** — ADOPT two-tier IR + temporal-effect checker + reference interpreter; REJECT Turing-complete DSL and no-DSL. Decision recorded on issue #3 under owner auto-delegation (owner-reversible).
Serves invariants: I1 (PIT correctness — *statically*), I5 (search proposes, never promotes),
I6 (risk veto mechanical), I2 (reproducibility via IR as artifact)

---

## 1. Why a DSL at all — the strongest argument and the strongest objection

**For:** Every alternative enforcement point for I1/I6 is runtime detective work.
If strategies are arbitrary Python (Qlib-style) or C# (LEAN-style), then "does this
feature peek?" is answered by *testing* (spike #9) and code review — both incomplete.
A restricted expression IR makes the temporal question **decidable**: every node's
knowledge-time bound is computed by the type/effect system, and a violation is a
compile error, not a caught-in-backtest surprise. Also: search lanes (#7 — GP, AlphaGen,
RD-Agent, LLMs) all emit *expressions or programs*; a common IR is the only sane choke
point to quarantine their output (I5). AlphaGen literally emits expression trees
(verified: `alphagen` `Expression` API) — an IR target already exists in the ecosystem.

**Against:** DSL gravity. A bad DSL becomes the project's main maintenance burden and
researchers route around it (back to raw Python) within a month. Qlib survived with
convention + its expression engine (`$close`, `Ref()`, `Mean()` — already a proto-DSL).
Prior art of failure: countless internal quant DSLs that died of scope creep.

**Synthesis (recommended direction):** do **not** build a general strategy language.
Build a **two-tier IR**:

- **Tier 1 — Expression IR (build this).** Numeric expression trees over PIT data:
  scalars, cross-sectional ops, rolling/window ops. This is where leakage lives.
  Static temporal-effect checker assigns each node a `kt`-requirement bound and rejects
  anything whose bound exceeds the evaluation instant. ~85% of alpha-search output is
  expressible here (formulaic alphas, feature sets).
- **Tier 2 — Orchestration manifest (build this thin).** Declarative YAML/JSON describing
  universe, schedule, signal→weight mapping, order intent, risk-limit bindings. Not
  Turing-complete. Compiles to a Qlib config or a LEAN algorithm stub.
- **Tier 0 — Escape hatch (explicit, logged, quarantined).** Arbitrary code allowed only
  behind a `TRUSTED_CODE` gate (human-reviewed, hash-pinned, excluded from search lanes).
  This concedes honestly what the DSL will never express, instead of pretending.

## 2. Temporal-effect checker — the core asset

Type system sketch (each expression node gets effect `E = (kt_bound, vt_bound)`):

```
const(x)                 : E = (-∞, -∞)            -- needs nothing
field(sym, name)         : E = (t, t)              -- PIT read at evaluation instant
Ref(e, n) / lag          : kt_bound(E) - n bars
Mean/Std/Corr(e, w)      : vt window [t-w, t], kt_bound(E) ≤ t … enforced per node
Rank/XS-op(e)            : universe AS OF (t,t) injected — checker requires universe node
Fundamental(f, lag_decl) : kt_bound = publication_time(f) — CHECKER VERIFIES lag_decl ≥ declared source lag, cannot just trust researcher
future_absorb()          : NOT IN THE GRAMMAR (no negative lookback operator exists)
```

Key design rule: **there is no operator that moves kt forward.** Leakage is then
unrepresentable, not merely detectable. The checker also emits a per-expression
`kt_bound` certificate consumed by the data loader (it knows exactly which knowledge-time
to query — this doubles as the interface to spike #2's `as_of` API) and by the sealed
holdout harness (#9).

Checker must also flag II-adjacent sins: division without declared denominator guard,
universe-dependent ops without universe node, non-deterministic functions (`random()`
without seeded entropy node — serves I2).

## 3. Reference interpreter

A single-file, dependency-light, *obviously-correct* interpreter over the expression IR,
running against the gold fixture from spike #2. Its purposes:

1. **Semantics oracle** for the bake-off in #9 (adversarial cases assert interpreter
   behavior == production engine behavior on poisoned data).
2. **Compile target validator**: Qlib expression-engine output and (later) any compiled
   path must match the reference interpreter to tolerance on the fixture corpus.
3. Sealed-holdout evaluator (#9): holdout scoring runs the *reference* implementation,
   so a fast-path bug in the production engine cannot manufacture holdout alpha.

Deliberately slow. ~300–600 lines of Python. If it grows past ~1k lines, the IR is too fat.

## 4. Vertical-slice impact

- Phase B boring baselines B1–B5 are written **in Tier-1 IR or Tier-2 manifest** — proving
  the boring path needs no escape hatch. If B1 (e.g. SMA cross) can't be expressed, the IR
  design is wrong; that's a cheap, early falsification test.
- `compile(IR) -> qlib_expr` adapter is the Qlib boundary touchpoint (spike #4).
- Manifest emits LEAN algorithm stubs (spike #5) — same strategy, two executions, diff
  becomes an acceptance check.

## 5. Options

| Option | Leakage story | Cost | Risk |
|---|---|---|---|
| A. Two-tier IR + checker + reference interpreter (recommended) | static, certified | ~2–4 weeks to useful | scope creep — mitigated by Tier ban-list |
| B. Qlib expression engine + runtime audits only | runtime detective | ~0 new | leaks found late; search output unquarantined (fails I5 spirit) |
| C. Full strategy DSL (Turing-complete, like a mini Haskell) | strongest | months | dies of complexity; REJECT |
| D. No DSL, everything Python + LLM review | weakest | ~0 | I1 unenforced; REJECT |

## 6. Evidence gaps before decision

- Expressiveness probe: take Qlib's Alpha158 (158 features, verified exists as
  `qlib.contrib.data.handler`) and check what fraction is Tier-1 expressible. If <70%,
  rethink grammar before adopting.
- Prior-art pass on the operator set: WorldQuant Alpha101 + Qlib's op list as coverage tests.
- Decide IR serialization (JSON vs S-expr vs protobuf) — trivial but must be one.

## 6a. V0 implementation evidence (2026-08-19)

Committed in `51b26c1`: JSON-serializable Tier-1 IR (`Const`, PIT `Field`,
`Fundamental`, unary/binary, historical `Lag`, `Rolling`, `CrossSection`); a temporal
checker that rejects negative lag and under-declared publication lag; and a
dependency-light reference interpreter. Every accepted expression emits a
`max_lookahead_days == 0` witness (first executable `FQ-PROP-001` coverage).
`30cadf0` proves B1's PIT -> checked IR -> interpreter -> artifact-hash path.
Alpha158's >=70% coverage probe remains outstanding; no claim is made yet.

## 7. Recommendation

**ADOPT option A with a hard scope fence:** Tier-1 expression IR + temporal-effect checker
+ reference interpreter + thin orchestration manifest. Explicit **REJECT** of a
Turing-complete DSL (option C). Success criterion written into the decision: "B1–B5 and
≥70% of Alpha158 expressible without Tier 0; reference interpreter ≤1k LOC."
Link the checker's temporal properties to spike #8 (formal partition) as prime
**selective-proof candidates**.
