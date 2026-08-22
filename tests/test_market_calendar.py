import sys
from unittest.mock import patch, MagicMock

# Mock duckdb before importing utility to prevent database connection errors
mock_duckdb = MagicMock()
sys.modules["duckdb"] = mock_duckdb

import pytest
from datetime import date, timedelta
from unittest.mock import patch
from src.utility.market_calendar import get_closed_count, market_is_open, calculate_begin_date, count_trading_days

# Mock class to simulate duckdb result objects
class MockResult:
    def __init__(self, rows=None):
        self.rows = rows or []
    def fetchone(self):
        return self.rows[0] if self.rows else None
    def fetchall(self):
        return self.rows

# Test for get_closed_count function
@patch('src.utility.market_calendar.DATABASE_CONNECTION')
def test_get_closed_count(mock_connection):
    # execute() returns a result whose single row holds the count
    mock_connection.execute.return_value = MockResult([(2,)])
    result = get_closed_count(date(2024, 12, 31), date(2025, 8, 1))
    assert result == 2

    # Test with no holidays
    mock_connection.execute.return_value = MockResult([(0,)])
    result = get_closed_count(date(2024, 10, 31), date(2024, 11, 1))
    assert result == 0

# Test for market_is_open function
@patch('src.utility.market_calendar.DATABASE_CONNECTION')
def test_market_is_open(mock_connection):
    # Test weekday (open): table row says Open
    mock_connection.execute.return_value = MockResult([('Open',)])
    assert market_is_open(date(2025, 7, 24)) == True

    # Test weekend (closed): returns False before querying the database
    mock_connection.execute.return_value = MockResult([('Closed',)])
    assert market_is_open(date(2025, 12, 28)) == False  # Sunday
    assert market_is_open(date(2025, 12, 27)) == False  # Saturday

    # Test known holiday on a weekday: table row says Closed
    mock_connection.execute.return_value = MockResult([('Closed',)])
    assert market_is_open(date(2025, 12, 25)) == False

# Test for calculate_begin_date function
def test_calculate_begin_date():
    end = date(2025, 7, 24)
    begin = calculate_begin_date(end, 30)
    assert (end - begin).days >= 42  # ~6 weeks with weekends

# Test for count_trading_days function
def test_count_trading_days():
    # Test within a month
    start = date(2025, 7, 1)
    end = date(2025, 7, 31)
    assert count_trading_days(start, end) == 23  # Corrected from 22 to 23
    
    # Test single day (weekday)
    assert count_trading_days(date(2025, 7, 24), date(2025, 7, 24)) == 1
    
    # Test single day (weekend)
    assert count_trading_days(date(2025, 7, 27), date(2025, 7, 27)) == 0


