"""Minimal deterministic GP-compatible proposal lane.

This is an expression-tree mutation baseline, not a claim to replace gplearn.
It targets the same proposal-only contract as random-v0 and is dependency-free.
"""
from __future__ import annotations

import random

from .random_lane import Proposal
from ..dsl.ir import Binary, Field, Lag, Rolling
from ..orchestration.contracts import content_hash


def evolve(seed: int, generations: int = 3, population: int = 12) -> list[Proposal]:
    rng = random.Random(seed)
    fields = ("close", "volume", "open", "high", "low")
    pool = [Rolling("mean", Field(rng.choice(fields)), rng.randint(2, 10)) for _ in range(population)]
    for _ in range(generations):
        next_pool = []
        for expr in pool:
            if rng.random() < .5:
                child = Binary("sub", expr, Lag(Field(rng.choice(fields)), rng.randint(1, 5)))
            else:
                child = Rolling("std", expr, rng.randint(2, 8))
            next_pool.append(child)
        pool = next_pool
    return [Proposal("gp-v0", seed, expr, content_hash(str(expr))) for expr in pool]
