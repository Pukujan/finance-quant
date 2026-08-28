# 2026-08-28 — Luna-ready experiment executioner

Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #27

The fixed versioned parallel research laboratory is ready for candidate implementation agents.

See `docs/handoffs/LATEST.md` for the full current interface and commands.

Frozen execution direction:

`publish immutable PIT components -> assemble fixed historical benchmark -> expand exact/bounded arms -> parallel predictions -> same canonical realized outcome -> ExperimentLedger -> prior-OOS-only router -> isolated shadow paper`

Latest green code run: GitHub Actions `33173989475`, code SHA `4ce8be50ecdc453d0ece0db440bf2b93f693063b`.

Validation:

- 23 lab tests passed;
- 9/9 targeted source mutations killed;
- public CLI smoke passed;
- existing workstation 4/4 regression passed;
- artifact `lab-smoke-result`, ID 9686784711, ZIP SHA256 `a0bdbcc9c2708c82dee482408387aff3a5248c7c2843022cb53f7a9bd5826354`.

Candidate workers should now target #29, #19 and #21. They should adapt to `finance_quant.lab` interfaces rather than changing benchmark/outcome semantics inside their own lane.

Private/sealed holdout contents were not inspected or rerun.
