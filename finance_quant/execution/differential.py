"""A1 field-class differential comparison for normalized execution receipts."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Mapping

from .conformance import validate_receipt, validate_runtime_contract


class DifferentialConformanceError(AssertionError):
    """Raised when a candidate differs outside the explicit A1 comparison policy."""


@dataclass(frozen=True)
class Difference:
    path: str
    reference: Any
    candidate: Any
    field_class: str


# Runtime identity and the self-hash necessarily differ across implementations. They are
# explicitly outside the semantic comparison projection; candidate-native metadata must
# not be smuggled into any other normalized field.
PERMITTED_TOP_LEVEL_DIFFERENCES = {
    "runtime": "candidate implementation identity",
    "runtime_version": "candidate implementation pin",
    "receipt_hash": "self-hash includes runtime identity metadata",
}

_EXACT_TOP_LEVEL = (
    "contract_version",
    "fixture_id",
    "seed",
    "status",
    "orders",
    "fills",
    "cash_ledger",
    "positions",
    "corporate_actions",
    "rejections",
    "faults",
    "input_hash",
    "replay_lineage",
)

_NUMERIC_TOP_LEVEL = (
    "cash",
    "equity",
    "nav",
    "realized_pnl",
    "unrealized_pnl",
)


def _decimal(value: Any, path: str) -> Decimal:
    try:
        return Decimal(str(value))
    except Exception as exc:  # pragma: no cover - defensive fail-closed conversion
        raise DifferentialConformanceError(f"{path} is not a declared decimal field") from exc


def compare_normalized_receipts(
    reference: Mapping[str, Any],
    candidate: Mapping[str, Any],
    contract: Mapping[str, Any],
    *,
    decimal_tolerance: Decimal | str = Decimal("0"),
) -> list[Difference]:
    """Return semantic differences between two normalized A1 receipts.

    Unlisted fields are not silently ignored: both receipts are first validated against the
    runtime contract, then every normalized top-level field is either compared explicitly or
    appears in ``PERMITTED_TOP_LEVEL_DIFFERENCES``. The initial shared daily-bar subset uses
    zero numeric tolerance unless a caller explicitly supplies a contract-justified value.
    """
    validate_runtime_contract(contract)
    validate_receipt(reference, contract)
    validate_receipt(candidate, contract)
    tolerance = _decimal(decimal_tolerance, "decimal_tolerance")
    if tolerance < 0:
        raise DifferentialConformanceError("decimal_tolerance must be non-negative")

    expected_fields = set(contract["receipt"]["required_top_level"])
    classified = set(_EXACT_TOP_LEVEL) | set(_NUMERIC_TOP_LEVEL) | set(PERMITTED_TOP_LEVEL_DIFFERENCES)
    unclassified = expected_fields - classified
    if unclassified:
        raise DifferentialConformanceError(
            f"required receipt fields lack a comparison class: {sorted(unclassified)}"
        )

    differences: list[Difference] = []
    for field in _EXACT_TOP_LEVEL:
        if reference[field] != candidate[field]:
            differences.append(Difference(f"$.{field}", reference[field], candidate[field], "exact"))

    for field in _NUMERIC_TOP_LEVEL:
        left = _decimal(reference[field], f"$.{field}")
        right = _decimal(candidate[field], f"$.{field}")
        if abs(left - right) > tolerance:
            differences.append(
                Difference(f"$.{field}", str(left), str(right), "tolerance_bounded")
            )
    return differences


def assert_normalized_receipts_conform(
    reference: Mapping[str, Any],
    candidate: Mapping[str, Any],
    contract: Mapping[str, Any],
    *,
    decimal_tolerance: Decimal | str = Decimal("0"),
) -> None:
    differences = compare_normalized_receipts(
        reference,
        candidate,
        contract,
        decimal_tolerance=decimal_tolerance,
    )
    if differences:
        rendered = "; ".join(
            f"{item.path} [{item.field_class}] reference={item.reference!r} candidate={item.candidate!r}"
            for item in differences
        )
        raise DifferentialConformanceError(rendered)
