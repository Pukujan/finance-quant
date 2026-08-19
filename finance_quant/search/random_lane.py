"""Deterministic RANDOM proposal lane, the permanent bake-off floor."""
from __future__ import annotations

import random
from dataclasses import dataclass

from ..dsl.ir import Binary, Const, Field, Lag, Rolling, Unary
from ..orchestration.contracts import content_hash


@dataclass(frozen=True)
class Proposal:
    lane_id: str
    seed: int
    expression: object
    expression_hash: str
    authority: str = "propose_only"


def propose(seed: int, count: int = 10) -> list[Proposal]:
    rng = random.Random(seed)
    fields = ("close", "volume", "open", "high", "low")
    out = []
    for _ in range(count):
        field = Field(rng.choice(fields))
        if rng.random() < 0.5:
            expr = Rolling(rng.choice(("mean", "std", "sum")), field, rng.randint(2, 10))
        else:
            expr = Binary(rng.choice(("add", "sub", "mul")), field,
                          Lag(Field(rng.choice(fields)), rng.randint(1, 5)))
        out.append(Proposal("random-v0", seed, expr, content_hash(str(expr))))
    return out
