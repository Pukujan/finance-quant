"""Prepare deterministic A2 strategy/risk evidence and a single-intent execution fixture."""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping

from finance_quant.risk.veto import PortfolioState, RiskLimits
from finance_quant.trader.risk import gate_portfolio_intent
from finance_quant.trader.strategy import BaselineStrategyConfig, StrategyInvariantError, generate_baseline_decision


def _canonical_events(events: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    for raw in events:
        event = dict(raw)
        event_id = str(event.get("event_id", ""))
        if not event_id:
            raise ValueError("controlled fixture event_id must be non-empty")
        prior = seen.get(event_id)
        if prior is not None and prior != event:
            raise ValueError(f"ambiguous duplicate event_id: {event_id}")
        seen[event_id] = event
    return sorted(
        seen.values(),
        key=lambda event: (str(event["event_time"]), int(event["sequence"]), str(event["event_id"])),
    )


def prepare_controlled_fixture(spec: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    events = _canonical_events(list(spec.get("events", [])))
    config = BaselineStrategyConfig(**dict(spec.get("strategy_config", {})))
    decision = generate_baseline_decision(
        events,
        session_id=str(spec["session_id"]),
        instrument_id=str(spec["instrument_id"]),
        decision_time=str(spec["decision_time"]),
        config=config,
    )
    if decision.status != "INTENT" or decision.intent is None:
        raise ValueError("controlled A2 fixture must deterministically produce one intent")
    state = PortfolioState(**dict(spec.get("risk_state", {})))
    limits = RiskLimits(**dict(spec.get("risk_limits", {})))
    gated = gate_portfolio_intent(state, decision.intent, limits)
    if gated.decision.status != "APPROVED" or gated.approved_intent is None:
        raise ValueError("controlled A2 fixture must pass the mechanical risk gate")

    fixture = {
        "fixture_id": str(spec["fixture_id"]),
        "initial_cash": str(spec["initial_cash"]),
        "fee_per_unit": str(spec.get("fee_per_unit", "0")),
        "events": events,
        "intents": [gated.approved_intent.execution_intent()],
    }
    evidence = {
        "schema_version": "1.0.0",
        "issue": 16,
        "phase": "A2",
        "session_id": str(spec["session_id"]),
        "strategy_id": decision.strategy_id,
        "strategy_spec_hash": decision.strategy_spec_hash,
        "strategy_hash": decision.strategy_hash,
        "strategy_status": decision.status,
        "strategy_source_event_ids": list(decision.source_event_ids),
        "risk_hash": gated.risk_hash,
        "risk_decision": asdict(gated.decision),
        "approved_intent": gated.approved_intent.execution_intent(),
        "authority": "NONE",
    }
    return fixture, evidence


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--fixture-out", type=Path, required=True)
    parser.add_argument("--evidence-out", type=Path, required=True)
    args = parser.parse_args(argv)
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    fixture, evidence = prepare_controlled_fixture(spec)
    args.fixture_out.parent.mkdir(parents=True, exist_ok=True)
    args.evidence_out.parent.mkdir(parents=True, exist_ok=True)
    args.fixture_out.write_text(json.dumps(fixture, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.evidence_out.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
