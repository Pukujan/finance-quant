# finance-quant

OSS-backed quantitative research, validation, governance, promotion, and autonomous paper-trading laboratory.

The active execution plan is GitHub issue #12. Project policy, architecture, assurance obligations, and capability promotion are durable project state; external frameworks are replaceable implementations behind `finance-quant` contracts.

<!-- BEGIN GENERATED PROJECT STATUS -->
## Project status (generated)

- Architecture: `OSS_FIRST_AUTONOMOUS_TRADER_REPLATFORM`
- Status: **BOOTSTRAP_IN_PROGRESS**
- Active epic / issue: **#12 / #13**
- Assurance phase: **A0 — Bootstrap governance and assurance**
- Current capability: **BOOTSTRAP_ONLY**
- Trading authority: **NONE**
- Paper trading enabled: **false**
- Live capital enabled: **false**
- Frontend authority: **OPERATOR_ONLY**
- Legacy Phase B: **PARKED** (evidence preserved)
- Next planned issue after bootstrap: **#15**

Machine source: `contracts/project/project-state.json`; assurance source: `contracts/assurance/capability-assurance-v1.json`.
<!-- END GENERATED PROJECT STATUS -->

## Replatform direction

New capabilities are built as vertical slices:

`domain/backend -> typed API/events -> evidence/observability -> thin operator/research UI -> end-to-end validation`

The frontend is an operator/research surface, never trading or promotion authority. The first autonomous trader will be a deliberately simple unattended local paper trader after the NautilusTrader-vs-LEAN runtime bakeoff. Knowledge graph and local learning capabilities are later controlled upgrades to an already-running autonomous paper system.

Read `AGENTS.md`, `docs/CURRENT_STATE.md`, issue #12/#13/#14, and `docs/handoffs/LATEST.md` before starting material work.

## Preserved Phase-B V0 evidence

The prior V0 is preserved as validated legacy plumbing/oracles, not the active project sequencing plan:

- Bitemporal PIT store (SQLite + JSONL+manifest) with restatement/delist/split fixture
- Tier-1 IR, temporal checker, reference interpreter, Qlib compiler
- Native orchestration (WorkOrders, attempts, local backend, deterministic fan-in)
- Append-only ExperimentLedger + MLflow-compatible export + fresh-env rerun receipt
- B1–B5 boring baselines (SMA, walk-forward, momentum, cross-sectional rank, buy-and-hold)
- Proposal-only RANDOM/GP search lanes (no promotion authority)
- Sealed-holdout commitment interface (cases stay off-repo)
- Mechanical risk veto, same-bar fill contract, promotion-ladder conformance
- Property catalog with executable oracle references and hidden-acceptance flags
- TLA+ PromotionLadder model plus executable TLC smoke integration
- Mutation-hardened sealed acceptance and adapter tests
- Optional TimescaleDB/XTDB/ArcticDB PIT adapters
- Generated LEAN algorithm skeleton and execution-contract tests
- Smoke, determinism, cost-stress, fresh-environment, and clean-runner drills

Legacy Phase-B issue #11 is parked and preserved; it does not override the new replatform sequence.

## Assurance

Capability assurance is defined in issue #14 and `contracts/assurance/capability-assurance-v1.json`. Depending on phase, required gates include SDD/PDD, static/IR checks, unit/regression, property/stateful, hidden acceptance, mutation thresholds, differential/metamorphic testing, repeated determinism, clean environment, chaos/fault injection, soak, TLA+, selective SMT/Lean4 obligations, and HITL promotion.

Required gates are conjunctive. A good aggregate score does not compensate for a failed critical invariant.

## Unified CLI

All existing entrypoints remain available via `python -m finance_quant <command>` while the replatform proceeds:

| Command | Target script |
|---|---|
| `docker-drill` | `scripts/run_docker_clean_runner_drill.py` — Docker clean-runner verification |
| `cost-stress` | `scripts/run_cost_stress_report.py` — nominal vs 2x-slippage cost comparison |
| `mvfi` | `scripts/run_phase_b_mvfi.py` — minimum viable Polygon ingest |
| `fresh-env-drill` | `scripts/run_fresh_environment_drill.py` — temp venv + pytest + verify |
| `help` | List available commands |
| `verify` | `scripts/verify.py` — pytest + smoke |
| `benchmark` | `scripts/run_phase_b_benchmark.py` — full Phase B benchmark |
| `freeze` | `scripts/freeze_fixture.py` — freeze/verify PIT fixture |
| `drill` | `scripts/run_phase_b_determinism_drill.py` — determinism check |
| `pit-bakeoff` | `scripts/run_pit_bakeoff.py` |
| `b1-b5` | `scripts/run_b1_b5_campaign.py` |
| `search-batch` | `scripts/run_search_batch.py` |
| `smoke` | `scripts/smoke.py` |
| `alpha158` | `scripts/alpha158_coverage.py` |
| `scorecard` | `scripts/run_search_scorecard.py` |
| `rank-ic` | `scripts/run_rank_ic_report.py` |
| `b2-scheduler` | `scripts/run_b2_via_scheduler.py` |
| `seal-mini` | `scripts/write_seal_mini_a.py` |
| `two-stage` | `scripts/run_two_stage.py` |
| `generate-lean` | `scripts/generate_lean.py` |
| `trial-gate` | `scripts/trial_gate.py` |

## Verify

```text
python -m venv .venv
.venv\Scripts\pip install -r requirements-dev.txt
.venv\Scripts\python -m pytest tests
```

Bootstrap-specific checks:

```text
python scripts/validate_bootstrap_contracts.py
python scripts/generate_project_status.py --check
python -m pytest tests/test_bootstrap_contracts.py tests/test_property_catalog.py -q
```

Useful existing scripts:

- `scripts/run_pit_bakeoff.py` — Q1–Q8 PIT harness
- `scripts/run_b1_b5_campaign.py` — boring baseline campaign
- `scripts/run_search_batch.py` — RANDOM+GP trials into the ledger
- `scripts/run_b2_via_scheduler.py` — B2 folds as native WorkOrders
- `scripts/run_search_scorecard.py` — RANDOM vs GP rank-IC scorecard (propose-only)
- `scripts/run_rank_ic_report.py` — B1–B5 walk-forward rank IC
- `scripts/run_two_stage.py` — feature_eval then LEAN replay
- `scripts/smoke.py` — pytest + bake-off + campaign + scorecard
- `scripts/run_docker_clean_runner_drill.py` — Docker clean-runner verification (optional)
- `scripts/run_cost_stress_report.py` — compare nominal vs 2x slippage cost stress
- `scripts/run_phase_b_benchmark.py` — full preserved Phase-B benchmark
- `scripts/run_phase_b_determinism_drill.py` — run benchmark N times and compare receipt hashes
- `scripts/run_fresh_environment_drill.py` — temp venv install + pytest + verify
- `scripts/generate_phase_b_holdout.py` — generate synthetic holdout + Merkle root
- `scripts/write_phase_b_seal.py` — write public seal commitment for the holdout
- `python -m finance_quant help` — list packaged command entrypoints
