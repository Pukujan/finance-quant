"""Common checker/evaluator boundary for all proposal lanes."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from ..dsl.checker import TemporalError, check
from ..dsl.interpreter import evaluate
from ..orchestration.contracts import content_hash
from .random_lane import Proposal


@dataclass(frozen=True)
class ProposalEvaluation:
    proposal_hash: str
    lane_id: str
    valid: bool
    score: float | None
    violation_class: str | None
    trial_hash: str


def evaluate_proposal(proposal: Proposal, histories: Sequence[dict]) -> ProposalEvaluation:
    """Checker first; invalid proposals are visible trials, never silently dropped."""
    trial_hash = content_hash({"lane": proposal.lane_id, "proposal": proposal.expression_hash})
    try:
        check(proposal.expression)
        values = [evaluate(proposal.expression, history) for history in histories]
        score = sum(values) / len(values) if values else 0.0
        return ProposalEvaluation(proposal.expression_hash, proposal.lane_id, True, score, None, trial_hash)
    except (TemporalError, ValueError, KeyError, ZeroDivisionError) as exc:
        return ProposalEvaluation(proposal.expression_hash, proposal.lane_id, False, None,
                                  type(exc).__name__, trial_hash)
