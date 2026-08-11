'''
Test suite for utility.market_calendar module
'''
import pytest
from unittest.mock import patch, MagicMock
from datetime import date
import sys

# To prevent the database connection from initializing during imports, 
# we must mock 'duckdb.execute' before importing anything that uses it.
with patch('duckdb.execute') as mock_exec:
    mock_exec.return_value = MagicMock()
    from utility.market_calendar import (
        market_is_open,
        calculate_begin_date,
        calculate_end_date,
        count_trading_days,
    )

@pytest.fixture(autouse=True)
def mock_duckdb_sql():
    with patch('utility.market_calendar.sql') as mock_sql:
        # Default behavior for sql(): return a mock result that can be fetchone()'d
        mock_result = MagicMock()
        # By default, assume market is open (no entry in holidays table)
        mock_result.fetchone.return_value = None 
        mock_sql.return_value = mock_result
        yield mock_sql

def test_market_is_open(mock_duckdb_sql):
    # Test weekend (Saturday) - should return False without calling SQL
    assert market_is_open(date(2024, 1, 6)) is False
    # Test weekend (Sunday) - should return False without calling SQL
    assert market_is_open(date(2024, 1, 7)) is False
    
    # Test a known trading day (Tuesday) - SQL returns None -> Open
    mock_duckdb_sql.return_value.fetchone.return_value = None
    assert market_is_open(date(2024, 1, 2)) is True
    
    # Test a known holiday - SQL returns ('Closed',) -> Closed
    mock_duckdb_sql.return_value.fetchone.return_value = ('Closed',)
    assert market_is_open(date(2024, 1, 1)) is False

def test_count_trading_days(mock_duckdb_sql):
    # Mock market_is_open behavior for a specific range: 2024-01-01 to 2024-01-05
    # Jan 1: Closed, Jan 2-5: Open
    def side_effect(*args, **kwargs):
        # The actual call is result.fetchone(), which takes no args.
        # We need to know the date being checked, but fetchone() doesn't receive it.
        # Instead of side_effect on fetchone, we should mock market_is_open or 
        # use a stateful mock. For now, let's use a list of return values 
        # matching the expected call sequence.
        return next(results)

    results = iter([('Closed',), None, None, None, None])
    mock_duckdb_sql.return_value.fetchone.side_effect = results
    
    start = date(2024, 1, 1)
    end = date(2024, 1, 5)
    assert count_trading_days(start, end) == 4

def test_calculate_begin_date(mock_duckdb_sql):
    # Mock: Jan 1 Closed, others Open.
    # calculate_begin_date loops backwards from end_date (Jan 5).
    # Sequence: Jan 4, Jan 3, Jan 2...
    results = iter([None, None, None]) # All open for the first 3 days back
    mock_duckdb_sql.return_value.fetchone.side_effect = results

    end_date = date(2024, 1, 5)
    days = 3
    begin_date = calculate_begin_date(end_date, days)
    # 2024-01-05 (Fri), 04 (Thu), 03 (Wed) -> begin_date should be 2024-01-02
    # because the loop does:
    # 1. begin_date = Jan 4, is_open=True, count=1
    # 2. begin_date = Jan 3, is_open=True, count=2
    # 3. begin_date = Jan 2, is_open=True, count=3 -> loop ends
    assert begin_date == date(2024, 1, 2)


def test_calculate_end_date(mock_duckdb_sql):
    # Mock: Jan 1 Closed, others Open.
    # calculate_end_date loops forwards from begin_date (Jan 2).
    # Sequence: Jan 3, Jan 4, Jan 5...
    results = iter([None, None, None]) # All open for the first 3 days forward
    mock_duckdb_sql.return_value.fetchone.side_effect = results

    begin_date = date(2024, 1, 2)
    days = 3
    end_date = calculate_end_date(begin_date, days)
    # 2024-01-03 (Wed), 04 (Thu), 05 (Fri) -> end_date should be 2024-01-05
    assert end_date == date(2024, 1, 5)

def test_symmetry(mock_duckdb_sql):
    # Mock all days as open for simplicity in symmetry test
    mock_duckdb_sql.return_value.fetchone.return_value = None
    
    start_date = date(2024, 6, 3) # A Monday
    interval = 10
    end_calc = calculate_end_date(start_date, interval)
    begin_calc = calculate_begin_date(end_calc, interval)
    assert begin_calc == start_date
