"""Multiple-testing deflation for search lanes. Proposal-only: never promotion."""
from __future__ import annotations

import warnings

try:
    from scipy.stats import t as _student_t
except ImportError:  # pragma: no cover - depends on the runtime environment
    _student_t = None


_fallback_warned = False


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
    """Approximate the two-sided Spearman rank-correlation p-value.

    The usual large-sample approximation transforms the correlation to a
    t-statistic with ``n - 2`` degrees of freedom.  SciPy is optional so the
    search package remains usable in minimal environments; without it, the
    historical placeholder is retained and a warning is emitted.
    """
    global _fallback_warned

    if n < 3:
        return 1.0
    rho = min(1.0, max(0.0, abs(abs_ic)))
    denominator = 1.0 - rho * rho
    t_stat = float("inf") if denominator == 0.0 else rho * ((n - 2) / denominator) ** 0.5

    if _student_t is None:
        if not _fallback_warned:
            warnings.warn(
                "SciPy is unavailable; using the legacy Spearman p-value fallback.",
                RuntimeWarning,
                stacklevel=2,
            )
            _fallback_warned = True
        return max(1e-6, min(1.0, 1.0 / (1.0 + t_stat * t_stat)))

    return max(0.0, min(1.0, 2.0 * float(_student_t.sf(t_stat, n - 2))))
