"""
Pure performance-calculation routines for the portfolio dashboard.

This module is intentionally free of any database or Streamlit dependencies so
that the return mathematics can be unit-tested in isolation. It provides three
ways to measure portfolio performance from a series of end-of-period values and
an optional series of net external cash flows:

* ``simple_*``   -- the naive total/daily percent change (no cash-flow adjustment).
* ``twr_*``      -- time-weighted returns, which chain-link daily returns after
                    netting out external cash flows.
* ``mwr_series`` / ``mwr_cumulative`` -- a running money-weighted return
                    (annualized IRR) computed for each day from the beginning of
                    the series.

A "cash flow" is a net external movement of money that should be excluded from
the measured return (e.g. deposits and withdrawals). Its sign follows the stored
transaction amount: positive adds to the balance, negative removes from it.
"""
# Import 3rd party libraries
import numpy as np
import pandas as pd


# --- Simple (naive) performance ---
def simple_daily(balances: pd.Series) -> pd.Series:
    """
    Day-over-day percent change for a balance series (first day = 0).

    Arguments:
        balances -- Series of end-of-period values, ascending.

    Returns:
        A Series of daily percent changes aligned to ``balances``.
    """
    daily = balances.pct_change(fill_method=None)
    daily.iloc[0] = 0.0
    return daily


def simple_cumulative(balances: pd.Series) -> pd.Series:
    """
    Cumulative percent change from the first value (first day = 0).

    Arguments:
        balances -- Series of end-of-period values, ascending.

    Returns:
        A Series of cumulative percent changes aligned to ``balances``.
    """
    initial = balances.iloc[0]
    return balances / initial - 1.0


# --- Time-weighted performance ---
def twr_daily(balances: pd.Series, cash_flows=None) -> pd.Series:
    """
    Time-weighted daily return, netting out external cash flows.

    The return for day t is ``(V_t - CF_t) / V_{t-1} - 1`` where ``CF_t`` is the
    net external cash flow on that date. With no cash flows this reduces exactly
    to the simple daily percent change.

    Arguments:
        balances -- Series of end-of-period values, ascending.
        cash_flows -- Series aligned to ``balances`` (or a scalar) of net
            external cash flows per date; None/0 means no cash flows.

    Returns:
        A Series of time-weighted daily returns aligned to ``balances``.
    """
    if cash_flows is None:
        cash_flows = 0.0
    adjusted = balances - cash_flows      # V_t - CF_t
    prev = balances.shift(1)              # V_{t-1}
    daily = adjusted / prev - 1.0
    daily.iloc[0] = 0.0
    return daily


def twr_cumulative(balances: pd.Series, cash_flows=None) -> pd.Series:
    """
    Time-weighted cumulative return (chain-linked daily returns).

    Arguments:
        balances -- Series of end-of-period values, ascending.
        cash_flows -- Series aligned to ``balances`` (or a scalar) of net
            external cash flows per date; None/0 means no cash flows.

    Returns:
        A Series of time-weighted cumulative returns aligned to ``balances``.
    """
    daily = twr_daily(balances, cash_flows)
    return (1.0 + daily).cumprod() - 1.0


# --- Money-weighted performance (IRR) ---
def xirr(flows, initial_guess: float = None):
    """
    Compute the annualized internal rate of return (XIRR) for dated cash flows
    using Newton-Raphson with a bisection fallback.

    Arguments:
        flows -- iterable of (date, amount) pairs. ``amount`` uses the investor
            wallet convention: negative = money invested/outflow, positive =
            money received/inflow. At least two flows are required and they must
            include both a positive and a negative amount.
        initial_guess -- optional starting rate for Newton's method (default 0.0).

    Returns:
        The annualized IRR as a float, or None if no solution is found.
    """
    flows = list(flows)
    if len(flows) < 2:
        return None

    amounts = np.array([float(amount) for _, amount in flows], dtype=float)
    # an IRR only exists when there are cash flows of both signs
    if (amounts > 0).all() or (amounts < 0).all():
        return None

    t0 = min(d for d, _ in flows)
    t = np.array([(d - t0).days / 365.0 for d, _ in flows], dtype=float)

    def npv(rate):
        return float(np.sum(amounts * (1.0 + rate) ** (-t)))

    def dnpv(rate):
        return float(np.sum(-amounts * t * (1.0 + rate) ** (-t - 1.0)))

    # establish a bracket [lo, hi] containing a sign change (root inside). The
    # annualized rate can be very large when the elapsed period is short, so the
    # upper bound is widened generously before giving up.
    lo = -0.999999
    hi = 10.0
    f_lo = npv(lo)
    f_hi = npv(hi)
    if f_lo * f_hi > 0:
        # widen the upper bound looking for a sign change
        bracketed = False
        while hi < 1e30:
            hi *= 2.0
            f_hi = npv(hi)
            if f_lo * f_hi <= 0:
                bracketed = True
                break
        if not bracketed:
            return None

    r = float(initial_guess) if initial_guess is not None else 0.0
    if not (lo < r < hi):
        r = (lo + hi) / 2.0

    for _ in range(200):
        f = npv(r)
        if abs(f) < 1e-8:
            return r
        df = dnpv(r)
        # Newton step; fall back to bisection when it leaves the bracket
        r_new = r - f / df if df != 0.0 else (lo + hi) / 2.0
        if not (lo < r_new < hi):
            r_new = (lo + hi) / 2.0
        # narrow the bracket using the sign at r_new
        f_new = npv(r_new)
        if f_lo * f_new <= 0:
            hi, f_hi = r_new, f_new
        else:
            lo, f_lo = r_new, f_new
        if abs(hi - lo) < 1e-9:
            return (hi + lo) / 2.0
        r = r_new

    return (lo + hi) / 2.0


def mwr_series(balances: pd.Series, cash_flows=None) -> pd.Series:
    """
    Running money-weighted return (annualized IRR) since the first date.

    For each day t the annualized IRR is solved over the flows
    ``[-V_0 @ t0, -CF_d @ d for each netted-out flow, +V_t @ t]``, warm-starting
    Newton's method from the previous day's IRR for speed. The index of
    ``balances`` must be date-like so that day counts can be computed.

    Arguments:
        balances -- Series of end-of-period values indexed by date, ascending.
        cash_flows -- Series aligned to ``balances`` (or a scalar) of net
            external cash flows per date; None/0 means no cash flows.

    Returns:
        A Series aligned to ``balances`` whose value at each date is the
        annualized IRR from the first date up to and including that date. The
        first element is 0.0.
    """
    n = len(balances)
    if cash_flows is None or not isinstance(cash_flows, pd.Series):
        cf_arr = np.full(n, float(cash_flows) if cash_flows is not None else 0.0)
    else:
        cf_arr = cash_flows.reindex(balances.index).fillna(0.0).to_numpy(dtype=float)

    values = balances.to_numpy(dtype=float)
    dates = list(balances.index)

    result = np.zeros(n, dtype=float)
    running_flows = [(dates[0], -values[0])]  # investor funds the start (outflow)
    prev_irr = None

    for i in range(1, n):
        if cf_arr[i] != 0.0:
            running_flows.append((dates[i], -cf_arr[i]))
        day_flows = running_flows + [(dates[i], values[i])]  # terminal value (inflow)
        irr = xirr(day_flows, initial_guess=prev_irr)
        if irr is None:
            result[i] = np.nan
        else:
            result[i] = irr
            prev_irr = irr

    return pd.Series(result, index=balances.index)


def mwr_cumulative(balances: pd.Series, cash_flows=None) -> pd.Series:
    """
    Running money-weighted CUMULATIVE (total, non-annualized) return since the
    first date, suitable for direct comparison with a time-weighted cumulative
    series on the same axis.

    Each day's annualized IRR is converted to a total return over the elapsed
    time: ``(1 + IRR_t) ** ((t - t0).days / 365) - 1``.

    Arguments:
        balances -- Series of end-of-period values indexed by date, ascending.
        cash_flows -- Series aligned to ``balances`` (or a scalar) of net
            external cash flows per date; None/0 means no cash flows.

    Returns:
        A Series aligned to ``balances`` of cumulative money-weighted returns.
    """
    irr = mwr_series(balances, cash_flows).to_numpy(dtype=float)
    t0 = balances.index[0]
    elapsed_days = np.array([(d - t0).days for d in balances.index], dtype=float) / 365.0
    total = (1.0 + irr) ** elapsed_days - 1.0
    return pd.Series(total, index=balances.index)
