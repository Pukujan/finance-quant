from __future__ import annotations

import inspect

from finance_quant.trader.evidence import ReplayableAccountStore
from finance_quant.trader.operator import build_operator_events, build_operator_snapshot, render_operator_html
import finance_quant.trader.operator as operator_module


def test_fq_prop_029_operator_surface_is_read_only_and_non_authoritative(tmp_path):
    authority = {"trading": "NONE", "paper_trading_enabled": False, "live_capital_enabled": False}
    with ReplayableAccountStore(tmp_path / "account.db", initial_cash="1000") as store:
        before = store.state_hash()
        snapshot = build_operator_snapshot(store, authority)
        assert store.state_hash() == before
        assert snapshot["mode"] == "READ_ONLY_OPERATOR_EVIDENCE"
        assert snapshot["commands"] == []
        assert snapshot["authority"] == authority
        assert build_operator_events(store) == []
        html = render_operator_html(snapshot)
        assert "read-only evidence" in html
        assert "No execution, promotion, brokerage, or capital command" in html

    source = inspect.getsource(operator_module)
    for forbidden in ("submit_order(", "apply_fill(", "commit_lean_session(", "assert_unattended_paper_authorized("):
        assert forbidden not in source
