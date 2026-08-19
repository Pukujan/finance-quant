from hypothesis import given, settings, strategies as st

from finance_quant.risk.veto import OrderIntent, PortfolioState, RiskLimits, RiskVeto, veto


@settings(max_examples=80)
@given(
    gross=st.floats(min_value=0, max_value=2, allow_nan=False, allow_infinity=False),
    net=st.floats(min_value=-1, max_value=1, allow_nan=False, allow_infinity=False),
    loss=st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False),
    notional=st.floats(min_value=0.01, max_value=2, allow_nan=False, allow_infinity=False),
    side=st.sampled_from(["buy", "sell"]),
)
def test_veto_never_allows_limit_breach(gross, net, loss, notional, side):
    limits = RiskLimits()
    state = PortfolioState(gross, net, loss)
    intent = OrderIntent(notional, side)
    signed = notional if side == "buy" else -notional
    would_breach = (
        gross + abs(notional) > limits.max_gross + 1e-12
        or abs(net + signed) > limits.max_net + 1e-12
        or loss > limits.max_loss + 1e-12
    )
    if would_breach:
        try:
            veto(state, intent, limits)
            assert False, "veto must raise on a limit breach"
        except RiskVeto:
            pass
    else:
        veto(state, intent, limits)
