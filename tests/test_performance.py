"""
Unit tests for core/performance.py

The performance routines are pure pandas/numpy, but importing them through the
``core`` package executes ``core/__init__.py``, which pulls in the database
connection. We therefore mock duckdb/utility/config before import, mirroring
tests/test_query_portfolio.py.

AI generated
"""
# import standard libraries
import os
import sys
from datetime import date
from unittest.mock import MagicMock

# 1. Fix Working Directory for relative paths in settings.py
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
os.chdir(root_dir)

# 2. Mock DATABASE_CONNECTION before importing any core/utility modules
mock_duckdb = MagicMock()
class MockDuckDBError(Exception):
    pass
mock_duckdb.Error = MockDuckDBError
sys.modules["duckdb"] = mock_duckdb

mock_db = MagicMock()
mock_db_module = MagicMock()
mock_db_module.DATABASE_CONNECTION = mock_db
sys.modules['utility.database'] = mock_db_module

# 3. Mock SETTINGS to avoid Pydantic ValidationError during import
mock_settings = MagicMock()
mock_settings.defaults = MagicMock()
mock_settings.defaults.max_time_machine_days = 180
mock_loglevel = MagicMock()
mock_loglevel.to_logging_level.return_value = 10 # logging.DEBUG
mock_settings.loglevel_application = mock_loglevel
mock_settings.loglevel_streamlit = mock_loglevel
mock_settings.loglevel_sqlalchemy = mock_loglevel

mock_settings_module = MagicMock()
mock_settings_module.SETTINGS = mock_settings
sys.modules['config.settings'] = mock_settings_module


# import 3rd party libraries
import numpy as np
import polars as pl
import pytest


# import local libraries
from core.performance import (
    simple_daily,
    simple_cumulative,
    twr_daily,
    twr_cumulative,
    xirr,
    mwr_series,
    mwr_cumulative,
)


# --- small helpers to build test series ---
def _series(values):
    """A plain RangeIndexed polars Series of floats."""
    return pl.Series([float(v) for v in values])


def _dated(values, start="2024-01-01", freq_days=1):
    """A date-valued polars Series of floats (MWR needs the dates for day counts)."""
    from datetime import datetime, timedelta
    base = datetime.strptime(start, "%Y-%m-%d")
    dates = [base + timedelta(days=freq_days * i) for i in range(len(values))]
    return pl.DataFrame({
        "date": pl.Series(dates, dtype=pl.Datetime),
        "value": pl.Series([float(v) for v in values], dtype=pl.Float64),
    })


def _dated_cash_flows(values, start="2024-01-01", freq_days=1):
    """A two-column dated cash-flow frame, the shape the page builds and passes to MWR."""
    from datetime import datetime, timedelta
    base = datetime.strptime(start, "%Y-%m-%d")
    dates = [base + timedelta(days=freq_days * i) for i in range(len(values))]
    return pl.DataFrame({
        "date": pl.Series(dates, dtype=pl.Datetime),
        "value": pl.Series([float(v) for v in values], dtype=pl.Float64),
    })


# ==============================================================================
# TEST SUITE FOR simple_* (must match the legacy inline math exactly)
# ==============================================================================
def test_simple_daily_matches_legacy():
    bal = _series([100, 110, 99])
    daily = simple_daily(bal)
    assert daily["value"].item(0) == 0.0
    assert daily["value"].item(1) == pytest.approx(0.10)
    assert daily["value"].item(2) == pytest.approx((99 - 110) / 110)


def test_simple_cumulative_matches_legacy():
    bal = _series([100, 110, 99])
    cum = simple_cumulative(bal)
    assert cum["value"].item(0) == 0.0
    assert cum["value"].item(1) == pytest.approx(0.10)
    assert cum["value"].item(2) == pytest.approx(-0.01)


# ==============================================================================
# TEST SUITE FOR twr_* (time-weighted, cash-flow adjusted)
# ==============================================================================
def test_twr_no_cash_flows_equals_simple():
    bal = _series([100, 110, 99])
    assert twr_daily(bal)["value"].to_list() == pytest.approx(
        simple_daily(bal)["value"].to_list())
    assert twr_cumulative(bal)["value"].to_list() == pytest.approx(
        simple_cumulative(bal)["value"].to_list())


def test_twr_deposit_day_is_zero_return():
    # a $60 deposit on day 2 with a flat market must not register as profit
    bal = _series([100, 160])
    cf = pl.Series([0.0, 60.0])
    assert twr_daily(bal, cf)["value"].item(1) == pytest.approx(0.0)
    assert twr_cumulative(bal, cf)["value"].item(1) == pytest.approx(0.0)
    # contrast: the naive simple method would call this a 60% gain
    assert simple_cumulative(bal)["value"].item(1) == pytest.approx(0.60)


def test_twr_deposit_with_market_gain():
    # market +5% and a $60 deposit -> only the 5% should be measured
    bal = _series([100, 165])
    cf = pl.Series([0.0, 60.0])
    assert twr_daily(bal, cf)["value"].item(1) == pytest.approx(0.05)
    assert twr_cumulative(bal, cf)["value"].item(1) == pytest.approx(0.05)


def test_twr_withdrawal_is_zero_return():
    # a $60 withdrawal on day 2 with a flat market (100 -> 40) is not a loss
    bal = _series([100, 40])
    cf = pl.Series([0.0, -60.0])
    assert twr_daily(bal, cf)["value"].item(1) == pytest.approx(0.0)
    assert twr_cumulative(bal, cf)["value"].item(1) == pytest.approx(0.0)


# ==============================================================================
# TEST SUITE FOR xirr (money-weighted / IRR solver)
# ==============================================================================
def test_xirr_simple_one_year():
    # 2023-01-01 -> 2024-01-01 is exactly 365 days, so +10% implies IRR = 10%
    flows = [(date(2023, 1, 1), -100000.0), (date(2024, 1, 1), +110000.0)]
    assert xirr(flows) == pytest.approx(0.10, abs=1e-4)


def test_xirr_deposit_is_zero_return():
    # fund 100k, deposit 60k the next day, flat market -> IRR ~ 0
    flows = [(date(2024, 1, 1), -100000.0),
             (date(2024, 1, 31), -60000.0),
             (date(2024, 1, 31), +160000.0)]
    assert xirr(flows) == pytest.approx(0.0, abs=1e-6)


def test_xirr_no_solution_same_sign():
    flows = [(date(2024, 1, 1), -100.0), (date(2024, 2, 1), -50.0)]
    assert xirr(flows) is None


def test_xirr_single_flow_is_none():
    assert xirr([(date(2024, 1, 1), -100.0)]) is None


# ==============================================================================
# TEST SUITE FOR mwr_series / mwr_cumulative
# ==============================================================================
def test_mwr_no_cash_flows_equals_simple_cumulative():
    # over a full year with no flows, cumulative MWR must equal simple cumulative
    bal = _dated([100.0, 110.0], start="2024-01-01", freq_days=365)
    cum = mwr_cumulative(bal)
    assert cum["value"].to_list() == pytest.approx(
        simple_cumulative(bal["value"])["value"].to_list(), abs=1e-6)


def test_mwr_series_shape_and_first_value():
    bal = _dated([100.0, 110.0, 99.0])
    s = mwr_series(bal)
    assert len(s) == len(bal)
    assert s["value"].item(0) == 0.0


def test_mwr_deposit_is_zero_return():
    # fund 100, deposit 60 the next day, flat market -> cumulative MWR ~ 0
    bal = _dated([100.0, 160.0])
    cf = pl.Series([0.0, 60.0])
    cum = mwr_cumulative(bal, cf)
    assert cum["value"].item(1) == pytest.approx(0.0, abs=1e-6)


def test_mwr_short_period_large_gain_is_finite():
    # a gain over a short span yields a large (but finite) annualized IRR
    bal = _dated([100.0, 110.0], start="2024-01-01", freq_days=2)  # +10% in 2 days
    s = mwr_series(bal)
    assert np.isfinite(s["value"].item(1))
    assert s["value"].item(1) > 1.0  # annualized well beyond 100%


def test_mwr_dated_deposit_is_netted():
    """
    Regression: the page passes cash flows as a *dated* two-column frame. A deposit
    that doubles the balance must be netted out of the money-weighted return, so the
    cumulative MWR reflects only the (flat) market, not the deposit. Before the fix
    the dated cash-flow branch dropped every flow and the MWR tracked the simple
    return (a phantom ~100% gain).
    """
    bal = _dated([100.0, 100.0, 200.0])             # flat, then a 100 deposit + flat
    cf = _dated_cash_flows([0.0, 0.0, 100.0])
    cum = mwr_cumulative(bal, cf)
    assert cum["value"].item(2) == pytest.approx(0.0, abs=1e-6)
    # the unadjusted simple return would call this a 100% gain
    assert simple_cumulative(bal["value"])["value"].item(2) == pytest.approx(1.0, abs=1e-9)


def test_mwr_dated_deposit_does_not_match_simple():
    """
    Regression: when a deposit is present, the money-weighted return must *diverge*
    from the simple return. The two are equal only when no external flow occurs.
    """
    bal = _dated([100.0, 160.0])
    cf = _dated_cash_flows([0.0, 60.0])             # a 60 deposit on day 2
    mwr = mwr_cumulative(bal, cf)["value"].item(1)
    simple = simple_cumulative(bal["value"])["value"].item(1)
    assert mwr == pytest.approx(0.0, abs=1e-6)     # flat market -> ~0, deposit excluded
    assert simple == pytest.approx(0.60, abs=1e-9)  # naive method sees the deposit
    assert abs(mwr - simple) > 0.1
