from __future__ import annotations

import copy
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from itertools import permutations

import pytest

from finance_quant.execution.conformance import load_runtime_contract
from finance_quant.execution.reference import run_daily_reference


def _fixture() -> dict:
    return {
        "fixture_id": "daily-metamorphic-001",
        "initial_cash": "1000",
        "fee_per_unit": "0.10",
        "events": [
            {
                "event_id": "bar-1",
                "instrument_id": "TEST",
                "event_time": "2026-01-02T16:00:00Z",
                "known_at": "2026-01-02T16:00:00Z",
                "sequence": 1,
                "payload": {"open": "10", "close": "11", "liquidity": "100"},
            },
            {
                "event_id": "bar-2",
                "instrument_id": "TEST",
                "event_time": "2026-01-05T16:00:00Z",
                "known_at": "2026-01-05T16:00:00Z",
                "sequence": 2,
                "payload": {"open": "12", "close": "13", "liquidity": "3"},
            },
            {
                "event_id": "bar-3",
                "instrument_id": "TEST",
                "event_time": "2026-01-06T16:00:00Z",
                "known_at": "2026-01-06T16:00:00Z",
                "sequence": 3,
                "payload": {"open": "14", "close": "15", "liquidity": "100"},
            },
        ],
        "intents": [
            {
                "intent_id": "intent-1",
                "instrument_id": "TEST",
                "created_at": "2026-01-02T16:00:00Z",
                "side": "BUY",
                "quantity": "5",
                "order_type": "MARKET",
            }
        ],
    }


def _economic_projection(receipt: dict, *, strip_fill_time: bool = False) -> dict:
    fills = copy.deepcopy(receipt["fills"])
    if strip_fill_time:
        for fill in fills:
            fill.pop("event_time", None)
    return {
        "orders": receipt["orders"],
        "fills": fills,
        "cash_ledger": receipt["cash_ledger"],
        "positions": receipt["positions"],
        "rejections": receipt["rejections"],
        "cash": receipt["cash"],
        "equity": receipt["equity"],
        "nav": receipt["nav"],
    }


def _shift_timestamp(value: str, delta: timedelta) -> str:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00")) + delta
    assert parsed.tzinfo == timezone.utc
    return parsed.isoformat().replace("+00:00", "Z")


@pytest.mark.parametrize("order", list(permutations(range(3))))
def test_metamorphic_event_input_permutation_preserves_receipt(order: tuple[int, int, int]) -> None:
    contract = load_runtime_contract()
    base = _fixture()
    permuted = copy.deepcopy(base)
    permuted["events"] = [permuted["events"][index] for index in order]

    assert run_daily_reference(permuted, contract, seed=23) == run_daily_reference(base, contract, seed=23)


def test_metamorphic_uniform_time_shift_preserves_execution_economics() -> None:
    contract = load_runtime_contract()
    base = _fixture()
    shifted = copy.deepcopy(base)
    delta = timedelta(days=35)
    for event in shifted["events"]:
        event["event_time"] = _shift_timestamp(event["event_time"], delta)
        event["known_at"] = _shift_timestamp(event["known_at"], delta)
    for intent in shifted["intents"]:
        intent["created_at"] = _shift_timestamp(intent["created_at"], delta)

    base_receipt = run_daily_reference(base, contract, seed=23)
    shifted_receipt = run_daily_reference(shifted, contract, seed=23)

    assert _economic_projection(shifted_receipt, strip_fill_time=True) == _economic_projection(
        base_receipt, strip_fill_time=True
    )
    assert shifted_receipt["fills"][0]["event_time"] == _shift_timestamp(
        base_receipt["fills"][0]["event_time"], delta
    )


def test_metamorphic_future_known_decoy_cannot_change_execution_economics() -> None:
    contract = load_runtime_contract()
    base = _fixture()
    decoy = copy.deepcopy(base)
    decoy["events"].append(
        {
            "event_id": "future-known-decoy",
            "instrument_id": "TEST",
            "event_time": "2026-01-03T16:00:00Z",
            "known_at": "2026-02-03T16:00:00Z",
            "sequence": 99,
            "payload": {"open": "1", "close": "999", "liquidity": "100000"},
        }
    )

    assert _economic_projection(run_daily_reference(decoy, contract, seed=23)) == _economic_projection(
        run_daily_reference(base, contract, seed=23)
    )


def test_metamorphic_more_eligible_liquidity_cannot_reduce_fill_quantity() -> None:
    contract = load_runtime_contract()
    base = _fixture()
    liquid = copy.deepcopy(base)
    liquid["events"][1]["payload"]["liquidity"] = "100"

    partial = run_daily_reference(base, contract, seed=23)
    full = run_daily_reference(liquid, contract, seed=23)

    assert float(full["orders"][0]["filled_quantity"]) >= float(partial["orders"][0]["filled_quantity"])
    assert full["orders"][0]["state"] == "FILLED"


def test_metamorphic_increasing_non_negative_fees_cannot_improve_terminal_nav() -> None:
    contract = load_runtime_contract()
    base = _fixture()
    higher_fee = copy.deepcopy(base)
    higher_fee["fee_per_unit"] = "0.35"

    base_receipt = run_daily_reference(base, contract, seed=23)
    higher_fee_receipt = run_daily_reference(higher_fee, contract, seed=23)

    assert higher_fee_receipt["positions"] == base_receipt["positions"]
    assert [
        (fill["quantity"], fill["price"], fill["source_event_id"])
        for fill in higher_fee_receipt["fills"]
    ] == [
        (fill["quantity"], fill["price"], fill["source_event_id"])
        for fill in base_receipt["fills"]
    ]
    assert Decimal(higher_fee_receipt["nav"]) <= Decimal(base_receipt["nav"])


def test_metamorphic_equivalent_fill_split_preserves_terminal_quantity_and_cash() -> None:
    contract = load_runtime_contract()
    single = _fixture()
    single["intents"][0]["quantity"] = "3"

    split = copy.deepcopy(single)
    split["intents"] = [
        {
            **copy.deepcopy(single["intents"][0]),
            "intent_id": "intent-1a",
            "quantity": "1",
        },
        {
            **copy.deepcopy(single["intents"][0]),
            "intent_id": "intent-1b",
            "quantity": "2",
        },
    ]

    single_receipt = run_daily_reference(single, contract, seed=23)
    split_receipt = run_daily_reference(split, contract, seed=23)

    assert sum(Decimal(fill["quantity"]) for fill in split_receipt["fills"]) == sum(
        Decimal(fill["quantity"]) for fill in single_receipt["fills"]
    )
    assert split_receipt["positions"] == single_receipt["positions"]
    assert Decimal(split_receipt["cash"]) == Decimal(single_receipt["cash"])
    assert Decimal(split_receipt["nav"]) == Decimal(single_receipt["nav"])
