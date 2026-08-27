"""Durable local virtual-account truth for A2 Autonomous Trader v0."""
from __future__ import annotations

import hashlib
import json
import sqlite3
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping

D = Decimal


class AccountInvariantError(ValueError):
    """Raised when an account transition would violate authoritative state invariants."""


def _decimal(value: object, *, field: str) -> Decimal:
    try:
        result = D(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise AccountInvariantError(f"{field} must be a decimal") from exc
    if not result.is_finite():
        raise AccountInvariantError(f"{field} must be finite")
    return result


def _text(value: Decimal) -> str:
    if value == 0:
        return "0"
    return format(value.normalize(), "f")


def _identifier(value: object, *, field: str) -> str:
    text = str(value)
    if not text:
        raise AccountInvariantError(f"{field} must be non-empty")
    return text


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class VirtualAccountStore:
    """Transactional SQLite account store with idempotent fill application.

    The store is intentionally finance-quant owned. Runtime adapters may propose normalized
    fills, but this store is the authoritative local paper account truth.
    """

    def __init__(self, path: str | Path, *, initial_cash: object | None = None) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._init_schema()
        row = self._conn.execute("SELECT cash FROM account_state WHERE singleton = 1").fetchone()
        if row is None:
            if initial_cash is None:
                raise AccountInvariantError("initial_cash is required for a new account store")
            cash = _decimal(initial_cash, field="initial_cash")
            with self._conn:
                self._conn.execute(
                    "INSERT INTO account_state(singleton, cash) VALUES(1, ?)",
                    (_text(cash),),
                )
        elif initial_cash is not None:
            requested = _text(_decimal(initial_cash, field="initial_cash"))
            if requested != str(row["cash"]):
                raise AccountInvariantError("initial_cash cannot reset an existing durable account")

    def _init_schema(self) -> None:
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS account_state (
                singleton INTEGER PRIMARY KEY CHECK(singleton = 1),
                cash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS positions (
                instrument_id TEXT PRIMARY KEY,
                quantity TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                intent_id TEXT NOT NULL UNIQUE,
                session_id TEXT NOT NULL,
                instrument_id TEXT NOT NULL,
                side TEXT NOT NULL CHECK(side IN ('BUY','SELL')),
                quantity TEXT NOT NULL,
                filled_quantity TEXT NOT NULL,
                state TEXT NOT NULL CHECK(state IN ('ACCEPTED','PARTIALLY_FILLED','FILLED','CANCELLED','REJECTED')),
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS fills (
                fill_id TEXT PRIMARY KEY,
                order_id TEXT NOT NULL REFERENCES orders(order_id),
                session_id TEXT NOT NULL,
                instrument_id TEXT NOT NULL,
                quantity TEXT NOT NULL,
                price TEXT NOT NULL,
                fee TEXT NOT NULL,
                event_time TEXT NOT NULL,
                source_event_id TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS cash_ledger (
                entry_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                kind TEXT NOT NULL,
                amount TEXT NOT NULL,
                fill_id TEXT NOT NULL UNIQUE REFERENCES fills(fill_id)
            );
            """
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "VirtualAccountStore":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def submit_order(
        self,
        *,
        order_id: object,
        intent_id: object,
        session_id: object,
        instrument_id: object,
        side: str,
        quantity: object,
        created_at: object,
    ) -> bool:
        order_id_s = _identifier(order_id, field="order_id")
        intent_id_s = _identifier(intent_id, field="intent_id")
        session_id_s = _identifier(session_id, field="session_id")
        instrument_id_s = _identifier(instrument_id, field="instrument_id")
        created_at_s = _identifier(created_at, field="created_at")
        side_s = str(side).upper()
        if side_s not in {"BUY", "SELL"}:
            raise AccountInvariantError("side must be BUY or SELL")
        quantity_d = _decimal(quantity, field="quantity")
        if quantity_d <= 0:
            raise AccountInvariantError("quantity must be positive")
        expected = {
            "order_id": order_id_s,
            "intent_id": intent_id_s,
            "session_id": session_id_s,
            "instrument_id": instrument_id_s,
            "side": side_s,
            "quantity": _text(quantity_d),
            "filled_quantity": "0",
            "state": "ACCEPTED",
            "created_at": created_at_s,
        }
        prior = self._conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id_s,)).fetchone()
        if prior is not None:
            if dict(prior) != expected:
                raise AccountInvariantError("conflicting duplicate order_id")
            return False
        intent_prior = self._conn.execute("SELECT order_id FROM orders WHERE intent_id = ?", (intent_id_s,)).fetchone()
        if intent_prior is not None:
            raise AccountInvariantError("intent_id already belongs to another order")
        with self._conn:
            self._conn.execute(
                """INSERT INTO orders(order_id,intent_id,session_id,instrument_id,side,quantity,filled_quantity,state,created_at)
                   VALUES(:order_id,:intent_id,:session_id,:instrument_id,:side,:quantity,:filled_quantity,:state,:created_at)""",
                expected,
            )
        return True

    def apply_fill(
        self,
        *,
        fill_id: object,
        order_id: object,
        session_id: object,
        instrument_id: object,
        quantity: object,
        price: object,
        fee: object,
        event_time: object,
        source_event_id: object,
    ) -> bool:
        fill_id_s = _identifier(fill_id, field="fill_id")
        order_id_s = _identifier(order_id, field="order_id")
        session_id_s = _identifier(session_id, field="session_id")
        instrument_id_s = _identifier(instrument_id, field="instrument_id")
        event_time_s = _identifier(event_time, field="event_time")
        source_event_id_s = _identifier(source_event_id, field="source_event_id")
        quantity_d = _decimal(quantity, field="quantity")
        price_d = _decimal(price, field="price")
        fee_d = _decimal(fee, field="fee")
        if quantity_d <= 0:
            raise AccountInvariantError("fill quantity must be positive")
        if price_d < 0:
            raise AccountInvariantError("fill price cannot be negative")
        if fee_d < 0:
            raise AccountInvariantError("fee cannot be negative")
        fill = {
            "fill_id": fill_id_s,
            "order_id": order_id_s,
            "session_id": session_id_s,
            "instrument_id": instrument_id_s,
            "quantity": _text(quantity_d),
            "price": _text(price_d),
            "fee": _text(fee_d),
            "event_time": event_time_s,
            "source_event_id": source_event_id_s,
        }
        prior = self._conn.execute("SELECT * FROM fills WHERE fill_id = ?", (fill_id_s,)).fetchone()
        if prior is not None:
            if dict(prior) != fill:
                raise AccountInvariantError("conflicting duplicate fill_id")
            return False

        order = self._conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id_s,)).fetchone()
        if order is None:
            raise AccountInvariantError("fill requires a preceding order")
        if order["state"] not in {"ACCEPTED", "PARTIALLY_FILLED"}:
            raise AccountInvariantError("order is not fill-eligible")
        if str(order["instrument_id"]) != instrument_id_s:
            raise AccountInvariantError("fill instrument does not match order")
        if str(order["session_id"]) != session_id_s:
            raise AccountInvariantError("fill session does not match order")

        order_qty = _decimal(order["quantity"], field="order.quantity")
        already = _decimal(order["filled_quantity"], field="order.filled_quantity")
        new_filled = already + quantity_d
        if new_filled > order_qty:
            raise AccountInvariantError("cumulative fill exceeds accepted order quantity")

        cash_row = self._conn.execute("SELECT cash FROM account_state WHERE singleton = 1").fetchone()
        if cash_row is None:
            raise AccountInvariantError("account state is missing")
        cash = _decimal(cash_row["cash"], field="cash")
        side = str(order["side"])
        gross = quantity_d * price_d
        cash_delta = -(gross + fee_d) if side == "BUY" else gross - fee_d
        next_cash = cash + cash_delta
        signed_quantity = quantity_d if side == "BUY" else -quantity_d
        position_row = self._conn.execute(
            "SELECT quantity FROM positions WHERE instrument_id = ?", (instrument_id_s,)
        ).fetchone()
        current_position = D("0") if position_row is None else _decimal(position_row["quantity"], field="position.quantity")
        next_position = current_position + signed_quantity
        next_state = "FILLED" if new_filled == order_qty else "PARTIALLY_FILLED"

        with self._conn:
            self._conn.execute(
                """INSERT INTO fills(fill_id,order_id,session_id,instrument_id,quantity,price,fee,event_time,source_event_id)
                   VALUES(:fill_id,:order_id,:session_id,:instrument_id,:quantity,:price,:fee,:event_time,:source_event_id)""",
                fill,
            )
            self._conn.execute("UPDATE account_state SET cash = ? WHERE singleton = 1", (_text(next_cash),))
            self._conn.execute(
                """INSERT INTO positions(instrument_id,quantity) VALUES(?,?)
                   ON CONFLICT(instrument_id) DO UPDATE SET quantity = excluded.quantity""",
                (instrument_id_s, _text(next_position)),
            )
            self._conn.execute(
                "UPDATE orders SET filled_quantity = ?, state = ? WHERE order_id = ?",
                (_text(new_filled), next_state, order_id_s),
            )
            self._conn.execute(
                "INSERT INTO cash_ledger(entry_id,session_id,kind,amount,fill_id) VALUES(?,?,?,?,?)",
                (f"cash:{fill_id_s}", session_id_s, "FILL", _text(cash_delta), fill_id_s),
            )
        return True

    def authoritative_state(self) -> dict[str, Any]:
        account = self._conn.execute("SELECT cash FROM account_state WHERE singleton = 1").fetchone()
        if account is None:
            raise AccountInvariantError("account state is missing")

        def rows(query: str) -> list[dict[str, Any]]:
            return [dict(row) for row in self._conn.execute(query).fetchall()]

        return {
            "cash": str(account["cash"]),
            "positions": rows("SELECT instrument_id,quantity FROM positions ORDER BY instrument_id"),
            "orders": rows(
                "SELECT order_id,intent_id,session_id,instrument_id,side,quantity,filled_quantity,state,created_at FROM orders ORDER BY order_id"
            ),
            "fills": rows(
                "SELECT fill_id,order_id,session_id,instrument_id,quantity,price,fee,event_time,source_event_id FROM fills ORDER BY fill_id"
            ),
            "cash_ledger": rows(
                "SELECT entry_id,session_id,kind,amount,fill_id FROM cash_ledger ORDER BY entry_id"
            ),
        }

    def state_hash(self) -> str:
        return canonical_hash(self.authoritative_state())

    def nav(self, marks: Mapping[str, object]) -> dict[str, str]:
        state = self.authoritative_state()
        cash = _decimal(state["cash"], field="cash")
        marked = D("0")
        for position in state["positions"]:
            quantity = _decimal(position["quantity"], field="position.quantity")
            if quantity == 0:
                continue
            instrument = str(position["instrument_id"])
            if instrument not in marks:
                raise AccountInvariantError(f"missing mark for non-zero position: {instrument}")
            mark = _decimal(marks[instrument], field=f"mark[{instrument}]")
            if mark < 0:
                raise AccountInvariantError("mark cannot be negative")
            marked += quantity * mark
        nav = cash + marked
        return {
            "cash": _text(cash),
            "marked_position_value": _text(marked),
            "nav": _text(nav),
        }
