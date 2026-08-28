"""Persistent zero-money shadow accounts for research arms."""
from __future__ import annotations

from decimal import Decimal, ROUND_FLOOR
from pathlib import Path
from typing import Mapping

from finance_quant.trader.account import VirtualAccountStore

from .core import LabError, content_hash

D = Decimal


class ShadowPaperLab:
    """One durable VirtualAccountStore per arm; no broker/live-capital path."""

    def __init__(self, state_dir: str | Path, *, initial_cash: float = 100_000.0) -> None:
        self.root = Path(state_dir) / "paper"
        self.root.mkdir(parents=True, exist_ok=True)
        self.initial_cash = D(str(initial_cash))
        if self.initial_cash <= 0:
            raise LabError("initial_cash must be positive")

    def _path(self, arm_id: str) -> Path:
        if not arm_id:
            raise LabError("arm_id cannot be empty")
        safe = content_hash({"arm_id": arm_id})[:24]
        return self.root / f"{safe}.sqlite"

    def _open(self, arm_id: str) -> VirtualAccountStore:
        path = self._path(arm_id)
        if path.exists():
            return VirtualAccountStore(path)
        return VirtualAccountStore(path, initial_cash=self.initial_cash)

    @staticmethod
    def _position(state: Mapping[str, object], instrument: str) -> D:
        for row in state.get("positions", []):
            if str(row["instrument_id"]) == instrument:
                return D(str(row["quantity"]))
        return D("0")

    @staticmethod
    def _marks(
        state: Mapping[str, object],
        instrument: str,
        execution_price: D,
        marks: Mapping[str, float] | None,
    ) -> dict[str, D]:
        resolved = {str(key): D(str(value)) for key, value in (marks or {}).items()}
        resolved[instrument] = execution_price
        for row in state.get("positions", []):
            name = str(row["instrument_id"])
            quantity = D(str(row["quantity"]))
            if quantity != 0 and name not in resolved:
                raise LabError(f"missing mark for existing shadow position: {name}")
        return resolved

    def advance(
        self,
        *,
        arm_id: str,
        instrument: str,
        decision_time: str,
        execution_time: str,
        predicted_return: float,
        execution_price: float,
        target_allocation: float = 0.95,
        fee_bps: float = 0.0,
        marks: Mapping[str, float] | None = None,
    ) -> dict:
        """Execute a long/cash arm at a supplied simulated execution price.

        Identities are keyed to the arm/decision/execution tuple. Rerunning the
        same transition is idempotent; conflicting recomputation raises in the
        underlying account store instead of silently double trading.
        """
        price = D(str(execution_price))
        allocation = D(str(target_allocation))
        fees = D(str(fee_bps))
        if price <= 0:
            raise LabError("execution_price must be positive")
        if allocation < 0 or allocation > 1:
            raise LabError("target_allocation must be between 0 and 1")
        if fees < 0:
            raise LabError("fee_bps cannot be negative")

        store = self._open(arm_id)
        try:
            state = store.authoritative_state()
            current = self._position(state, instrument)
            current_marks = self._marks(state, instrument, price, marks)
            nav = D(store.nav(current_marks)["nav"])
            target = D("0")
            if predicted_return > 0:
                target = (nav * allocation / price).to_integral_value(rounding=ROUND_FLOOR)
            delta = target - current
            transition_key = {
                "arm_id": arm_id,
                "instrument": instrument,
                "decision_time": decision_time,
                "execution_time": execution_time,
            }
            if delta != 0:
                order_id = "shadow-order:" + content_hash(transition_key)
                intent_id = "shadow-intent:" + content_hash(transition_key)
                fill_id = "shadow-fill:" + content_hash(transition_key)
                session_id = "shadow-session:" + content_hash({"arm_id": arm_id, "execution_time": execution_time})
                side = "BUY" if delta > 0 else "SELL"
                quantity = abs(delta)
                fee = quantity * price * fees / D("10000")
                store.submit_order(
                    order_id=order_id,
                    intent_id=intent_id,
                    session_id=session_id,
                    instrument_id=instrument,
                    side=side,
                    quantity=quantity,
                    created_at=execution_time,
                )
                store.apply_fill(
                    fill_id=fill_id,
                    order_id=order_id,
                    session_id=session_id,
                    instrument_id=instrument,
                    quantity=quantity,
                    price=price,
                    fee=fee,
                    event_time=execution_time,
                    source_event_id="shadow-source:" + content_hash(transition_key),
                )
            final_state = store.authoritative_state()
            final_marks = self._marks(final_state, instrument, price, marks)
            return {
                "arm_id": arm_id,
                "instrument": instrument,
                "position": str(self._position(final_state, instrument)),
                "executed": delta != 0,
                "state": final_state,
                "nav": store.nav(final_marks),
            }
        finally:
            store.close()

    def snapshot(self, arm_id: str, marks: Mapping[str, float]) -> dict:
        store = self._open(arm_id)
        try:
            return {"state": store.authoritative_state(), "nav": store.nav(marks)}
        finally:
            store.close()
