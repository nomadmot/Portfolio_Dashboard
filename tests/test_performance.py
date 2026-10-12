"""
Unit tests for core/performance.py

The performance routines are pure pandas/numpy, but importing them through the
``core`` package executes ``core/__init__.py``, which pulls in the database
connection. We therefore mock duckdb/utility/config before import, mirroring
tests/test_query_portfolio.py.
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
import pandas as pd
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
    """A plain RangeIndexed Series of floats."""
    return pd.Series([float(v) for v in values])


def _dated(values, start="2024-01-01", freq="D"):
    """A date-indexed Series of floats (MWR needs the dates for day counts)."""
    idx = pd.date_range(start=start, periods=len(values), freq=freq)
    return pd.Series([float(v) for v in values], index=idx)


# ==============================================================================
# TEST SUITE FOR simple_* (must match the legacy inline math exactly)
# ==============================================================================
def test_simple_daily_matches_legacy():
    bal = _series([100, 110, 99])
    daily = simple_daily(bal)
    assert daily.iloc[0] == 0.0
    assert daily.iloc[1] == pytest.approx(0.10)
    assert daily.iloc[2] == pytest.approx((99 - 110) / 110)


def test_simple_cumulative_matches_legacy():
    bal = _series([100, 110, 99])
    cum = simple_cumulative(bal)
    assert cum.iloc[0] == 0.0
    assert cum.iloc[1] == pytest.approx(0.10)
    assert cum.iloc[2] == pytest.approx(-0.01)


# ==============================================================================
# TEST SUITE FOR twr_* (time-weighted, cash-flow adjusted)
# ==============================================================================
def test_twr_no_cash_flows_equals_simple():
    bal = _series([100, 110, 99])
    assert twr_daily(bal).tolist() == pytest.approx(simple_daily(bal).tolist())
    assert twr_cumulative(bal).tolist() == pytest.approx(
        simple_cumulative(bal).tolist())


def test_twr_deposit_day_is_zero_return():
    # a $60 deposit on day 2 with a flat market must not register as profit
    bal = _series([100, 160])
    cf = pd.Series([0.0, 60.0])
    assert twr_daily(bal, cf).iloc[1] == pytest.approx(0.0)
    assert twr_cumulative(bal, cf).iloc[1] == pytest.approx(0.0)
    # contrast: the naive simple method would call this a 60% gain
    assert simple_cumulative(bal).iloc[1] == pytest.approx(0.60)


def test_twr_deposit_with_market_gain():
    # market +5% and a $60 deposit -> only the 5% should be measured
    bal = _series([100, 165])
    cf = pd.Series([0.0, 60.0])
    assert twr_daily(bal, cf).iloc[1] == pytest.approx(0.05)
    assert twr_cumulative(bal, cf).iloc[1] == pytest.approx(0.05)


def test_twr_withdrawal_is_zero_return():
    # a $60 withdrawal on day 2 with a flat market (100 -> 40) is not a loss
    bal = _series([100, 40])
    cf = pd.Series([0.0, -60.0])
    assert twr_daily(bal, cf).iloc[1] == pytest.approx(0.0)
    assert twr_cumulative(bal, cf).iloc[1] == pytest.approx(0.0)


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
    bal = _dated([100.0, 110.0], start="2024-01-01", freq="365D")
    cum = mwr_cumulative(bal)
    assert cum.tolist() == pytest.approx(
        simple_cumulative(bal).tolist(), abs=1e-6)


def test_mwr_series_shape_and_first_value():
    bal = _dated([100.0, 110.0, 99.0])
    s = mwr_series(bal)
    assert len(s) == len(bal)
    assert s.iloc[0] == 0.0


def test_mwr_deposit_is_zero_return():
    # fund 100, deposit 60 the next day, flat market -> cumulative MWR ~ 0
    bal = _dated([100.0, 160.0])
    cf = pd.Series([0.0, 60.0], index=bal.index)
    cum = mwr_cumulative(bal, cf)
    assert cum.iloc[1] == pytest.approx(0.0, abs=1e-6)


def test_mwr_short_period_large_gain_is_finite():
    # a gain over a short span yields a large (but finite) annualized IRR
    bal = _dated([100.0, 110.0], start="2024-01-01", freq="2D")  # +10% in 2 days
    s = mwr_series(bal)
    assert np.isfinite(s.iloc[1])
    assert s.iloc[1] > 1.0  # annualized well beyond 100%
