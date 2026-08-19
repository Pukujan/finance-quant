# Sealed Acceptance Interface

Issue #9's exact cases and labels live only in private `Pukujan/finance-quant-holdout`.
The public project records only `SealRecord` commitments and `SafeAcceptanceReceipt`
aggregates, implemented in `finance_quant.acceptance.seal`.

Clean-runner requirements:

1. Mount one sealed case set read-only, the candidate artifact read-only, and the
   reference interpreter image.
2. Carry no provider, brokerage, MLflow, GitHub, or general network credentials.
3. Validate the case Merkle root and labels hash against the public `SealRecord` before
   executing any candidate.
4. Emit exactly one safe aggregate receipt through the one-shot result writer.
5. Enforce use counters: `SEAL-A` max two per epoch; `SEAL-B` exactly one.

The current host's coarse `gh` PAT can read private repositories; it is not a valid
clean runner identity. Use a fine-grained credential excluding the holdout repository,
or a separate IAM-scoped object store identity, before real cases are populated.
