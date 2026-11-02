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

All public functions accept polars objects (``pl.Series`` / one-column
``pl.DataFrame``) and return a one-column ``pl.DataFrame``. For the MWR
routines the balance series must be a two-column DataFrame of
``["date" (pl.Datetime), "value"]`` so that day counts can be computed for the
IRR solver; the same shape is accepted (optionally) for ``cash_flows``.

AI-Generated
note: The IRR solver is adapted from the public-domain implementation
"""
# Import 3rd party libraries
import numpy as np
import polars as pl


# --- input normalization ---
def _to_numpy(obj) -> np.ndarray:
    """Extract a numpy float array from a polars Series / one-column DataFrame."""
    if obj is None:
        return np.zeros(0, dtype=float)
    if isinstance(obj, pl.DataFrame):
        # take the last column as the value column (a two-column frame's
        # leading date column is ignored by the value-based routines)
        obj = obj.to_series(-1)
    if not isinstance(obj, pl.Series):
        return np.asarray(obj, dtype=float)
    return np.asarray(obj.to_list(), dtype=float)


def _split(obj):
    """
    Split an input into ``(dates, values)``.

    ``dates`` is ``None`` unless the input is a two-column DataFrame whose first
    column is a date/datetime column.
    """
    if isinstance(obj, pl.DataFrame):
        cols = obj.columns
        if len(cols) >= 2:
            first = obj[cols[0]].dtype
            if first in (pl.Datetime, pl.Date):
                return obj[cols[0]].to_list(), _to_numpy(obj[cols[1]])
            # first column is not a date; treat last column as values
            return None, _to_numpy(obj[cols[-1]])
        return None, _to_numpy(obj.to_series(0))
    return None, _to_numpy(obj)


# --- Simple (naive) performance ---
def simple_daily(balances: pl.Series | pl.DataFrame) -> pl.DataFrame:
    """
    Day-over-day percent change for a balance series (first day = 0).

    Arguments:
        balances -- polars Series (or one-column DataFrame) of end-of-period
            values, ascending.

    Returns:
        A one-column polars DataFrame of daily percent changes aligned to
        ``balances``.
    """
    bal = _to_numpy(balances)
    n = len(bal)
    if n == 0:
        return pl.DataFrame({"value": np.zeros(0, dtype=float)})
    daily = np.zeros(n, dtype=float)
    for i in range(1, n):
        daily[i] = (bal[i] - bal[i - 1]) / bal[i - 1] if bal[i - 1] != 0 else np.nan
    daily[0] = 0.0
    return pl.DataFrame({"value": daily})


def simple_cumulative(balances: pl.Series | pl.DataFrame) -> pl.DataFrame:
    """
    Cumulative percent change from the first value (first day = 0).

    Arguments:
        balances -- polars Series (or one-column DataFrame) of end-of-period
            values, ascending.

    Returns:
        A one-column polars DataFrame of cumulative percent changes aligned to
        ``balances``.
    """
    bal = _to_numpy(balances)
    if len(bal) == 0 or bal[0] == 0:
        return pl.DataFrame({"value": np.zeros(len(bal), dtype=float)})
    result = bal / bal[0] - 1.0
    return pl.DataFrame({"value": result})


# --- Time-weighted performance ---
def twr_daily(balances: pl.Series | pl.DataFrame,
              cash_flows: pl.Series | pl.DataFrame | float | None = None
              ) -> pl.DataFrame:
    """
    Time-weighted daily return, netting out external cash flows.

    The return for day t is ``(V_t - CF_t) / V_{t-1} - 1`` where ``CF_t`` is the
    net external cash flow on that date. With no cash flows this reduces exactly
    to the simple daily percent change.

    Arguments:
        balances -- polars Series (or one-column DataFrame) of end-of-period
            values, ascending.
        cash_flows -- polars Series aligned to ``balances`` (or a scalar) of
            net external cash flows per date; None/0 means no cash flows.

    Returns:
        A one-column polars DataFrame of time-weighted daily returns aligned to
        ``balances``.
    """
    bal = _to_numpy(balances)
    n = len(bal)
    if isinstance(cash_flows, (int, float)):
        cf = np.full(n, float(cash_flows), dtype=float)
    else:
        cf = _to_numpy(cash_flows)
        if len(cf) != n:
            cf = np.zeros(n, dtype=float)
    if n == 0:
        return pl.DataFrame({"value": np.zeros(0, dtype=float)})
    adjusted = bal - cf            # V_t - CF_t
    daily = np.full(n, np.nan, dtype=float)
    daily[0] = 0.0
    for i in range(1, n):
        prev = bal[i - 1]
        daily[i] = (adjusted[i] / prev - 1.0) if prev != 0 else np.nan
    return pl.DataFrame({"value": daily})


def twr_cumulative(balances: pl.Series | pl.DataFrame,
                   cash_flows: pl.Series | pl.DataFrame | float | None = None
                   ) -> pl.DataFrame:
    """
    Time-weighted cumulative return (chain-linked daily returns).

    Arguments:
        balances -- polars Series (or one-column DataFrame) of end-of-period
            values, ascending.
        cash_flows -- polars Series aligned to ``balances`` (or a scalar) of
            net external cash flows per date; None/0 means no cash flows.

    Returns:
        A one-column polars DataFrame of time-weighted cumulative returns
        aligned to ``balances``.
    """
    daily = np.asarray(twr_daily(balances, cash_flows)["value"].to_list(), dtype=float)
    result = np.cumprod(1.0 + daily) - 1.0
    return pl.DataFrame({"value": result})


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
        df = dnpv(r)
        # Newton step; fall back to bisection when it leaves the bracket
        r_new = r - npv(r) / df if df != 0.0 else (lo + hi) / 2.0
        if not (lo < r_new < hi):
            r_new = (lo + hi) / 2.0
        # converge on the *rate* (a dimensionless number), not on NPV which is
        # in dollar units and can be non-zero even at the exact root
        if abs(r_new - r) < 1e-12:
            return r_new
        # narrow the bracket using the sign at r_new
        f_lo = npv(lo)
        f_new = npv(r_new)
        if f_lo * f_new <= 0:
            hi = r_new
        else:
            lo = r_new
        if abs(hi - lo) < 1e-12:
            return (hi + lo) / 2.0
        r = r_new

    return (lo + hi) / 2.0


def mwr_series(balances: pl.Series | pl.DataFrame,
                cash_flows: pl.Series | pl.DataFrame | float | None = None
                ) -> pl.DataFrame:
    """
    Running money-weighted return (annualized IRR) since the first date.

    For each day t the annualized IRR is solved over the flows
    ``[-V_0 @ t0, -CF_d @ d for each netted-out flow, +V_t @ t]``, warm-starting
    Newton's method from the previous day's IRR for speed. Each ``CF_d`` is a net
    external cash flow supplied via ``cash_flows`` (e.g. a deposit, withdrawal,
    dividend, or fee) that should be excluded from the measured return. With no
    external flows this reduces to the plain day-over-day value change.

    Arguments:
        balances -- a two-column DataFrame of ``["date" (pl.Datetime),
            "value"]`` (ascending), or a one-column value series paired with
            dates via ``cash_flows``.
        cash_flows -- a two-column DataFrame of ``["date", "value"]`` of net
            external cash flows, or a scalar; None/0 means no cash flows.

    Returns:
        A one-column polars DataFrame aligned to ``balances`` whose value at each
        date is the annualized IRR from the first date up to and including that
        date. The first element is 0.0.
    """
    dates, values = _split(balances)
    n = len(values)

    # Build a per-balance-date array of net external cash flows. A cash flow is
    # attributed to the first balance day on/after its own date so a flow dated
    # off-calendar still nets out of the correct period.
    cf_values = np.zeros(n, dtype=float)
    if cash_flows is not None:
        cf_dates, cf_amounts = _split(cash_flows)
        if cf_dates is None:
            # a scalar or one-column series of flows aligned to the balance dates
            if isinstance(cash_flows, (int, float)):
                cf_values = np.full(n, float(cash_flows), dtype=float)
            elif cf_amounts is not None and len(cf_amounts) == n:
                cf_values = cf_amounts
        else:
            for d, amount in zip(cf_dates, cf_amounts):
                for i, bdate in enumerate(dates):
                    if bdate >= d:
                        cf_values[i] += float(amount)
                        break
    result = np.zeros(n, dtype=float)
    running_flows = [(dates[0], -values[0])]  # investor funds the start (outflow)
    prev_irr = None

    for i in range(1, n):
        if cf_values[i] != 0.0:
            running_flows.append((dates[i], -cf_values[i]))
        day_flows = running_flows + [(dates[i], values[i])]  # terminal value (inflow)
        irr = xirr(day_flows, initial_guess=prev_irr)
        if irr is None:
            result[i] = np.nan
        else:
            result[i] = irr
            prev_irr = irr

    return pl.DataFrame({"value": result})


def mwr_cumulative(balances: pl.Series | pl.DataFrame,
                   cash_flows: pl.Series | pl.DataFrame | float | None = None
                   ) -> pl.DataFrame:
    """
    Running money-weighted CUMULATIVE (total, non-annualized) return since the
    first date, suitable for direct comparison with a time-weighted cumulative
    series on the same axis.

    The daily money-weighted returns from ``mwr_series`` are chained:
    ``(1 + r_t)`` is cumulated and 1 is subtracted, exactly mirroring how
    ``twr_cumulative`` chains its daily returns.

    Arguments:
        balances -- a two-column DataFrame of ``["date" (pl.Datetime),
            "value"]`` (ascending), or a one-column value series.
        cash_flows -- a two-column DataFrame of ``["date", "value"]`` of net
            external cash flows, or a scalar; None/0 means no cash flows.

    Returns:
        A one-column polars DataFrame aligned to ``balances`` of cumulative
        money-weighted returns.
    """
    dates, _ = _split(balances)
    irr = np.asarray(mwr_series(balances, cash_flows)["value"].to_list(), dtype=float)
    # each element of ``irr`` is the annualized IRR over the window from the
    # first date up to and including that date. Convert each to a *total* return
    # over the elapsed time since the first date; the last element is the
    # cumulative money-weighted return for the period.
    t0 = dates[0]
    elapsed = np.array([(d - t0).days for d in dates], dtype=float) / 365.0
    with np.errstate(invalid="ignore", over="ignore"):
        total = (1.0 + irr) ** elapsed - 1.0
    total = np.where((1.0 + irr) < 0.0, np.nan, total)
    return pl.DataFrame({"value": total})
