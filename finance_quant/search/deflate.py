"""Multiple-testing deflation for search lanes. Proposal-only: never promotion."""
from __future__ import annotations


def benjamini_hochberg(pvalues: list[float], alpha: float = 0.05) -> list[bool]:
    """Return a mask of discoveries at FDR alpha. Empty input -> empty mask."""
    n = len(pvalues)
    if n == 0:
        return []
    order = sorted(range(n), key=lambda i: pvalues[i])
    cutoff = -1
    for rank, i in enumerate(order, 1):
        if pvalues[i] <= alpha * rank / n:
            cutoff = rank
    accepted = [False] * n
    for rank, i in enumerate(order, 1):
        if rank <= cutoff:
            accepted[i] = True
    return accepted


def spearman_p_approx(abs_ic: float, n: int) -> float:
    """Rough two-sided p-value for Spearman-like |IC| with sample size n.
    Conservative placeholder until a stats library is a declared dependency.
    """
    if n < 3:
        return 1.0
    t = abs_ic * ((n - 2) / max(1e-12, 1 - abs_ic * abs_ic)) ** 0.5
    # crude: larger |t| -> smaller p; saturates at 1 and ~0
    return max(1e-6, min(1.0, 1.0 / (1.0 + t * t)))
