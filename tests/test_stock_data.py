import sys
from unittest.mock import patch, MagicMock
import pandas as pd

# Mock duckdb before importing utility to prevent database connection errors
mock_duckdb = MagicMock()
sys.modules["duckdb"] = mock_duckdb

# Mock the database module entirely before any other imports
mock_db_module = MagicMock()
sys.modules["src.utility.database"] = mock_db_module
# Ensure the connection object exists on the mocked module
mock_db_module.DATABASE_CONNECTION = MagicMock()

import pytest
from datetime import date, timedelta
from unittest.mock import patch
from src.utility.stock_data import get_stock_history, get_security_info, get_basic_quote

# Mock class to simulate duckdb result objects
class MockResult:
    def __init__(self, rows=None):
        self.rows = rows or []
    def fetchone(self):
        return self.rows[0] if self.rows else None
    def fetchall(self):
        return self.rows

@patch('yfinance.Ticker')
def test_get_stock_history(mock_ticker):
    # Mock yfinance history return
    mock_instance = mock_ticker.return_value
    # Return a real DataFrame to avoid issues with MagicMock spec
    mock_instance.history.return_value = pd.DataFrame()
    
    result = get_stock_history("AAPL", period="1d")
    assert result is not None
    mock_instance.history.assert_called()

@patch('src.utility.DATABASE_CONNECTION')
def test_get_security_info(mock_db):
    # Mock database result: (symbol, name, security_type, associated_symbol)
    mock_db.execute.return_value.fetchone.return_value = ("AAPL", "Apple Inc.", "Stock", "AAPL")
    
    result = get_security_info("AAPL")
    assert result.symbol == "AAPL"
    assert result.name == "Apple Inc."
    assert result.security_type == "Stock"
    assert result.associated_symbol == "AAPL"

@patch('yfinance.Ticker')
def test_get_basic_quote(mock_ticker):
    # Mock yfinance info dictionary
    mock_instance = mock_ticker.return_value
    # Use a real dict for info to ensure .get() returns actual values
    mock_instance.info.return_value = {
        "shortName": "Apple Inc.",
        "currentPrice": 150.0,
        "previousClose": 148.0,
        "open": 149.0,
        "dayHigh": 151.0,
        "dayLow": 147.0,
        "volume": 1000000,
        "marketCap": 2000000000000,
    }
    
    result = get_basic_quote("AAPL")
    assert result["symbol"] == "AAPL"
    assert result["currentPrice"] == 150.0
    assert result["shortName"] == "Apple Inc."

@patch('yfinance.Ticker')
def test_get_basic_quote_adjustment(mock_ticker):
    # Test adjustment when currentPrice is 0.0
    mock_instance = mock_ticker.return_value
    mock_instance.info.return_value = {
        "shortName": "Apple Inc.",
        "currentPrice": 0.0,
        "previousClose": 148.0,
    }
    
    result = get_basic_quote("AAPL")
    assert result["currentPrice"] == 148.0
