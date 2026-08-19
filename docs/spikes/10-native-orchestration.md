# Spike #10 — Native research orchestration: WorkOrders, attempts, local backend, fan-out/fan-in

Issue: Pukujan/finance-quant#10
Status: **DECIDED 2026-08-19** — ADOPT V0 as implemented (working code on main with 19 property tests + exit demo); DEFER non-local backends; Cortex V5 REJECTED as dependency. Decision recorded on issue #10 under owner auto-delegation (owner-reversible).
Serves invariants: I2 (reproducibility), I7 (failures visible), I5/I6 (authority walls),
I3 via sealed-capability separation (invariant 10), Phase C case #15 (retry/resume
duplicate authority). Consumes: #2 snapshot IDs, #3 factor hashes, #4 run ledger,
#5 LEAN replay jobs, #9 capability separation.

---

## 1. Reading of the issue (what is actually being decided)

The issue already fixes most architecture: `Campaign -> deterministic expansion ->
WorkOrders -> bounded local workers -> ResultReceipts -> deterministic fan-in`, local
subprocess backend only, no Ray/GHA/cluster/cloud/agent runtimes in V0, Cortex V5
explicitly a non-dependency. So this spike's real decision surface is narrower than the
other eight:

1. **Ratify or amend the contracts** (WorkOrder / ResultReceipt field lists).
2. **Pin the semantics that make the 12 invariants true by construction**, not by
   testing luck: the attempt state machine, the idempotency rule, the fan-in rule.
3. Decide the **persistence substrate** for attempt lifecycle (the one thing the issue
   leaves open and the one thing that determines half the invariants).
4. Produce the adversarial/property-test catalog mapping onto #8's partition.

## 2. The one genuinely open design choice: where attempt truth lives

Invariants 1-5 (attempt exists before compute; terminal outcome for every allocation;
failures can't vanish; retry idempotency; duplicate receipts can't fork authority) are
all statements about a **write-ahead attempt log** with exactly-once semantics at the
authority boundary. Options:

| Option | Invariants 1-5 fit | Cost | Notes |
|---|---|---|---|
| A. SQLite WAL attempt ledger (single writer, file in repo-adjacent data dir) | ++ (transactions give 1,2,4,5 almost for free; a UNIQUE(attempt_id) + state machine table kills duplicate receipts by construction) | near zero (stdlib) | **Recommended.** Boring, inspectable, backupable, zero services. Concurrency ceiling is one writer — fine: scheduler is single-process by design. |
| B. Append-only JSONL event log + derived state views | + | low | Event-sourcing purist choice; every invariant needs hand-rolled folds; easier to get subtly wrong (compaction, partial writes). Good as the *audit* export of option A. |
| C. MLflow tracking server as attempt store | 0 | medium | **Boundary violation** per the issue's own invariant 12: MLflow owns run truth, not attempt lifecycle. Also latency/typing mismatch. REJECT. |
| D. In-memory + checkpoint files | - | lowest | Fails invariant 1/3 across scheduler crashes — the exact moment they matter. REJECT. |

**Recommendation A**, with a JSONL mirror (B) emitted transactionally as the portable
audit/FOSSIL-ingestible artifact. Two keys pin the semantics:

- `attempt_id = blake2b(canonical(WorkOrder))` — content-addressed, so "retrying an
  identical WorkOrder" and "allocating it" are the same database event (invariant 4,
  idempotency, becomes *structural* — a retry is an INSERT-OR-IGNORE, not a judgment call).
  Distinct retries of a *failed* attempt carry `attempt_id + retry_seq` — lineage without
  authority forking (invariant 5): only the receipt that wins
  `INSERT ... WHERE NOT EXISTS (authoritative_result for work_order_hash)` counts;
  later duplicates are stored but flagged `superseded_duplicate`, never deleted (I7).
- fan-in compares against the **expansion manifest hash + expected attempt_id set**
  (issue's own rule) — a campaign/fold is `COMPLETE` only when every expected attempt_id
  has a terminal row. No successful-worker-count shortcuts (invariant 7).

## 3. Attempt state machine (draft v0.1 — the artifact the issue asks for)

```
ISSUED ---------------> QUEUED ------------> RUNNING -----------> COMPLETED
  |                      |  |                  | |---> REJECTED (pre-flight: hash/capability check)
  |                      |  |                  | |---> FAILED    (worker-reported error)
  |                      |  |                  | |---> CRASHED   (supervisor-detected death/timeout)
  |                      |  \--> CANCELLED (pre-start cancellation)
  |                      \--> CANCELLED
  \--(never QUEUED; e.g. manifest superseded)--> CANCELLED

Rules: ISSUED row is written BEFORE any process spawn (invariant 1).
Terminal states are exactly {COMPLETED, REJECTED, FAILED, CANCELLED, CRASHED} (inv. 2).
No outgoing transitions from terminal states except: FAILED/CRASHED --retry--> new row
(same work_order_hash, retry_seq+1) — never an in-place resurrection.
RUNNING older than timeout without heartbeat -> supervisor writes CRASHED itself
(workers cannot write their own terminal state; they *emit* receipts, the supervisor
*commits* them — this is what makes invariant 3 hold: a dead worker's row was already
there before it died).
```

## 4. Amendments proposed to the contract field lists (owner to ratify/reject)

WorkOrder — the issue's list is strong; propose adding:
- `work_order_hash` (the content address from sec. 2; makes "attempt_id exists before
  compute" trivially auditable — attempt_id IS work_order_hash in V0),
- `manifest_hash` (which expansion produced it; enables partial-campaign reasoning),
- `heartbeat_deadline` + `wall_timeout_seconds` (crash detection contract, not config),
- `egress_class` (none | litellm_only | vendor_data_only) — declares network surface;
  the sealed-holdout capability (invariant 10) then composes as
  `authority_class=sealed_scoring AND egress_class=none`, which is cheap to test.

ResultReceipt — propose adding:
- `work_order_hash` + `retry_seq` (join key; receipts without a pre-existing attempt row
  are REJECTED by the supervisor — malformed-receipt test),
- `envelope_hash` (hash of the receipt itself, signed by the supervisor at commit, not
  by the worker — workers are untrusted; a worker signature would sign into its own
  authority),
- `environment_capture_ref` (the issue's "deterministic environment/config capture"
  needs a hash field to hang on: lockfile hash + container/venv id + seedEcho),
- explicit `artifact_manifest` (list of {path_ref, sha256, bytes}) rather than freeform
  output refs — determinism checks (#5 double-run diff) consume this directly.

## 5. Authority matrix sketch (invariant 8/9/10 enforcement)

| Capability class | Can issue WorkOrders of type | Can write attempt ledger | Can write ExperimentLedger | Can touch promotion/risk state |
|---|---|---|---|---|
| `research_worker` (default) | nothing (workers never issue) | no — emits receipts to supervisor only | via facade annotations on its own receipt | **no** (structural: API not present in worker sandbox env) |
| `sealed_scoring_worker` | nothing | no | sealed result row (one-shot token, #9) | no |
| `scheduler_core` | all task types in V0 list | yes (sole writer) | fan-in aggregates | no |
| `promotion_service` (post-slice) | none | no | no | yes — #9 review path only |

The V0 simplification that makes this affordable: **a worker is a subprocess whose
environment contains no client for the ledger, the promotion API, or sealed storage** —
capability by *absence of handle*, verified by the property tests below, not by policy
days. (#6's same trick: sandbox = no network beyond declared egress.)

## 6. Fan-out cases for V0 (from the issue's product, made concrete)

`factor_set × model × fold × cost_scenario × execution_replay` — with the connector rule
that execution-replay attempts depend on prediction artifacts (not all products are
independent): expansion manifest = DAG, hashable, auditable, attempt count known
pre-flight. Deterministic ordering rule: manifest emits attempts in lexicographic
`(factor_hash, model_config_hash, fold_id, cost_policy_version, replay_id)` order;
fan-in sorts by attempt_id — completion order cannot leak into output (invariant 6),
and the aggregation test is literally "shuffle receipt arrival -> same output hash."

## 7. Property/stateful test catalog (issue's list, operationalized; slots into #8 as
this module's T1/T2 tier)

| Test | Generator / method | Property |
|---|---|---|
| retry idempotency | Hypothesis: random crash points | final ledger has exactly one authoritative result per work_order_hash |
| duplicate receipts | replay same receipt 1-5x | extras stored as superseded_duplicate; aggregates unchanged |
| out-of-order completion | shuffle receipt arrival order | deterministic aggregate hash invariant |
| crash before/after artifact write | kill -9 at fuzzed offsets | no terminal COMPLETED without full artifact_manifest; CRASHED row present |
| cancellation mid-exec | cancel at fuzzed times | CANCELLED terminal; no orphan process (assert via process table) |
| partial campaign fan-in | drop 10-90% of attempts | status never reports COMPLETE; partial aggregates carry `partial=true`, excluded from promotion evidence (inv. 7) |
| malformed receipt | arbitrary/mutated JSON | rejected at supervisor; attempt unaffected |
| deterministic expansion | same campaign spec, 100 runs | identical manifest hash + attempt_id set |
| authority boundary | worker attempts ledger/promotion calls | ImportError/absence — static env assertion + dynamic attempt logged as security event |
| scheduler crash mid-campaign | kill scheduler, restart | resume discovers state solely from ledger; no attempt silently lost (inv. 3 under the worst actor) |

No TLA+ for V0 core (matches the issue's gate). The promotion/holdout/capability
concurrency semantics, if modeled, live in #8's single `PromotionLadder.tla`; the
attempt machine above is small enough that its T1 stateful suite is sufficient.

## 8. Local backend contract (V0, draft)

- pool of N worker slots (N = min(cpu-1, ram/headroom)); a slot = one subprocess,
  cwd = fresh temp dir, env = allowlist, rlimits set, stdout/stderr -> bounded ring
  buffer (cap 1 MiB, overflow -> FAILED with `output_overflow` class);
- supervisor polls heartbeat file; timeout -> kill tree -> CRASHED (never trust worker
  exit code alone: exit 0 without a committed receipt parse = FAILED);
- cancellation = SIGTERM, 10s grace, SIGKILL; cancellation of a QUEUED row is a ledger
  transition only;
- no shared FS between workers except read-only artifact store; worker writes go to its
  own staging dir -> supervisor moves verified artifacts into the store (this is what
  kills "hidden shared mutable state" structurally rather than by review).

## 9. Vertical-slice impact

- The B1/B2-style exit campaign in the issue maps 1:1 onto Phase B steps 2-5; this
  module is therefore **on the slice's critical path** (unlike most of #7). Roughly:
  contracts + SQLite ledger + local backend + property suite v1 ~ the first real code
  in this repo, and it forces #2's `dataset_snapshot_id`, #3's `factor_hash`, and #4's
  run-record demands to become concrete — good forcing function, in the right order.
- Nothing here needs Qlib/LEAN integrated yet: task_type `feature_eval` over the gold
  fixture with a stub evaluator proves invariants 1-11 before real physics arrives.

## 10. Evidence gaps before decision

- None blocking: this is a build-verify spike, not an explore spike. The only true
  externals are (a) confirm Python-version floor with #4's Qlib constraint
  (py3.8-3.12 upstream; modern pick: 3.11/3.12), (b) owner's taste on SQLite path
  layout/backups, (c) whether `attempt_id == work_order_hash` is accepted (I recommend
  yes; it removes a whole class of mapping bugs for free).

## 11. Recommendation

**ADOPT** the V0 architecture and code boundary as stated in the issue, with:
SQLite-WAL attempt ledger + JSONL audit mirror (sec. 2), content-addressed
work_order_hash/attempt_id (sec. 2), the state machine of sec. 3 verbatim, contract
field amendments of sec. 4, capability-by-absence authority model (sec. 5), manifest-
based fan-in only (sec. 6), and the test catalog of sec. 7 as the definition of done.
**DEFER** all non-local backends behind the proven-need adapter gate already stated in
the issue. Cortex V5: **REJECT as dependency**, as the issue requires.
