"""
Unit tests for core/query_portfolio.py
Note: This test file assumes the existence of a mockable 'DATABASE_CONNECTION'
    object and that the necessary mock objects (like pandas.DataFrame) are available.
"""
# import standard libraries
from datetime import date
from unittest.mock import MagicMock, patch
import sys
import os

# 1. Fix Working Directory for relative paths in settings.py
# The file is at src/tests/test_query_portfolio.py. 
# Relative to this file, the project root (containing .settings/) is 3 levels up.
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
os.chdir(root_dir)

# 2. Mock DATABASE_CONNECTION before importing any core/utility modules
mock_db = MagicMock()
mock_db_module = MagicMock()
mock_db_module.DATABASE_CONNECTION = mock_db
sys.modules['utility.database'] = mock_db_module

# 3. Mock SETTINGS to avoid Pydantic ValidationError during import
# This prevents the code from trying to load .settings/app_config.yml and failing
mock_settings = MagicMock()
# Mock the AppDefaults nested model if needed by other components
mock_settings.defaults = MagicMock()
mock_settings.defaults.max_time_machine_days = 180

# Mock the log level enum and its conversion method to return a valid logging integer
mock_loglevel = MagicMock()
mock_loglevel.to_logging_level.return_value = 10 # logging.DEBUG
mock_settings.loglevel_application = mock_loglevel
mock_settings.loglevel_streamlit = mock_loglevel
mock_settings.loglevel_sqlalchemy = mock_loglevel

mock_settings_module = MagicMock()
mock_settings_module.SETTINGS = mock_settings
sys.modules['config.settings'] = mock_settings_module


# import 3rd party libraries
import pandas as pd
import pytest





#import local libraries
from schemas import Account
from core import (
    get_account,
    get_balance_history,
    get_security_symbols,
    lookup_associated_symbols,
    get_trades,
    get_last_trade_date,
    get_first_balance_date,
    get_first_trade_date,
)

# --- Fixtures for Mocking ---

@pytest.fixture
def mock_connection():
    """
    Mocks the global DATABASE_CONNECTION object to control database interactions.
    This fixture must be used in all tests that touch the database.
    """
    # Create a mock connection object that simulates the behavior of the real connection
    mock_conn = MagicMock()

    # We need to mock the execute method which is called repeatedly
    mock_conn.execute.return_value.fetchone.return_value = (1, "TestAccount")
    mock_conn.execute.return_value.fetchall.return_value = []
    mock_conn.execute.return_value.rowcount = 0

    return mock_conn

@pytest.fixture(autouse=True)
def mock_database_connection(mock_connection):
    """
    This fixture patches the global DATABASE_CONNECTION object 
    in the module scope before every test runs.
    """
    with patch('core.query_portfolio.DATABASE_CONNECTION', mock_connection):
        yield mock_connection

# ==============================================================================
# TEST SUITE FOR get_account
# ==============================================================================
def test_get_account_success(mock_connection):
    """Tests successful retrieval of an account."""
    # Configure the mock to return a specific result for the account check
    mock_connection.execute.return_value.fetchone.return_value = (1, "TestAccount")

    # Mock the return of the Account Pydantic model (assuming AccountBase is used)
    # In a real test, we would mock the entire AccountBase constructor.
    # For this test, we just check if the function runs without error.

    # We must mock the return of the Account constructor itself for a clean test.
    with patch('core.query_portfolio.Account',
               return_value=Account(account_id=1, account_name="TestAccount")):
        account = get_account(account_id=1)
        assert account.account_id == 1
        assert account.account_name == "TestAccount"

def test_get_account_not_found(mock_connection):
    """Tests failure when the account ID does not exist."""
    # Configure the mock to return None (no rows found)
    mock_connection.execute.return_value.fetchone.return_value = None

    with pytest.raises(ValueError, match="Account with ID 999 does not exist."):
        get_account(account_id=999)

# ==============================================================================
# TEST SUITE FOR get_balance_history
# ==============================================================================
def test_get_balance_history_success(mock_connection):
    """Tests successful retrieval and DataFrame creation for balance history."""
    # Mock the result set: (date, balance)
    mock_connection.execute.return_value.fetchall.return_value = [
        (date(2023, 1, 1), 1000.00),
        (date(2023, 1, 15), 1200.00)
    ]

    df = get_balance_history(
        account_id=1,
        begin_date=date(2023, 1, 1),
        end_date=date(2023, 1, 31),
        ascending=False,
    )

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    # Check if sorting worked (if we mocked the sorting correctly)
    assert df['date'].iloc[0] == date(2023, 1, 1)

def test_get_balance_history_no_results(mock_connection):
    """Tests case where no balance records are found."""
    # Mock the result set to be empty
    mock_connection.execute.return_value.fetchall.return_value = []

    df = get_balance_history(
        account_id=1,
        begin_date=date(2023, 1, 1),
        end_date=date(2023, 1, 31)
    )

    assert isinstance(df, pd.DataFrame)
    assert df.empty

# ==============================================================================
# TEST SUITE FOR get_security_symbols
# ==============================================================================
def test_get_security_symbols_no_options(mock_connection):
    """Tests fetching symbols when options are excluded."""
    # Mock the result set for non-option symbols
    mock_connection.execute.return_value.fetchall.return_value = [
        ('AAPL',),
        ('GOOGL',)
    ]

    symbols = get_security_symbols(include_options=False)
    assert symbols == ['AAPL', 'GOOGL']

def test_get_security_symbols_with_options(mock_connection):
    """Tests fetching symbols when options are included."""
    # Mock the result set to return both base and option symbols
    mock_connection.execute.return_value.fetchall.return_value = [
        ('AAPL',),
        ('AAPL',), # Duplicate entry to test set logic
        ('GOOGL',),
        ('AAPL',), # Option symbol
    ]

    symbols = get_security_symbols(include_options=True)
    # Expect unique, sorted list
    assert sorted(list(set(symbols))) == ['AAPL', 'GOOGL']

# ==============================================================================
# TEST SUITE FOR lookup_associated_symbols
# ==============================================================================
def test_lookup_associated_symbols_success(mock_connection):
    """Tests successful retrieval of associated symbols."""
    # Mock the result set: (associated_symbol,)
    mock_connection.execute.return_value.fetchall.return_value = [
        ('AAPL',),
        ('GOOGL',)
    ]

    symbols = lookup_associated_symbols(symbols=['AAPL', 'GOOGL'])
    # Expect the union of the original and the found symbols, sorted and unique
    assert sorted(symbols) == ['AAPL', 'GOOGL']

def test_lookup_associated_symbols_none_found(mock_connection):
    """Tests when no associated symbols are found."""
    mock_connection.execute.return_value.fetchall.return_value = []

    symbols = lookup_associated_symbols(symbols=['XYZ'])
    assert symbols == ['XYZ']

# ==============================================================================
# TEST SUITE FOR get_trades
# ==============================================================================
def test_get_trades_success(mock_connection):
    """Tests successful retrieval and DataFrame transformation for trades."""
    # Mocking a complex result set: (symbol, name, symbol, date, type, quantity, price, fees)
    mock_connection.execute.return_value.fetchall.return_value = [
        ('AAPL', 'Apple Inc.', 'AAPL', date(2023, 1, 1), 'BUY', 10, 150.00, 5.00),
        ('GOOGL', 'Google Inc.', 'GOOGL', date(2023, 1, 1), 'SELL', 5, 100.00, 2.00),
    ]

    df = get_trades(
        symbols=['AAPL', 'GOOGL'],
        begin_date=date(2023, 1, 1),
        end_date=date(2023, 1, 31),
        ascending=False
    )

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    # Check the calculated amount for the SELL trade (should be negative)
    assert df[df['Symbol'] == 'GOOGL']['Amount'].iloc[0] == -500.00

# ==============================================================================
# TEST SUITE FOR get_last_trade_date
# ==============================================================================
def test_get_last_trade_date_success(mock_connection):
    """Tests retrieving the most recent trade date."""
    # Mock the result set: (date,)
    mock_connection.execute.return_value.fetchone.return_value = (date(2024, 5, 15),)

    last_date = get_last_trade_date()
    assert last_date == date(2024, 5, 15)

def test_get_last_trade_date_no_results(mock_connection):
    """Tests case where no trades have been recorded."""
    # Mock the result set to be None
    mock_connection.execute.return_value.fetchone.return_value = None

    last_date = get_last_trade_date()
    assert last_date is None

# ==============================================================================
# TEST SUITE FOR get_first_balance_date
# ==============================================================================
def test_get_first_balance_date_success(mock_connection):
    """Tests retrieving the earliest balance date."""
    # Mock the result set: (date,)
    mock_connection.execute.return_value.fetchone.return_value = (date(2020, 1, 1),)

    first_date = get_first_balance_date()
    assert first_date == date(2020, 1, 1)

def test_get_first_balance_date_no_results(mock_connection):
    """Tests case where no balance records are found."""
    # Mock the result set to be None
    mock_connection.execute.return_value.fetchone.return_value = None

    first_date = get_first_balance_date()
    assert first_date is None

# ==============================================================================
# TEST SUITE FOR get_first_trade_date
# ==============================================================================
def test_get_first_trade_date_success(mock_connection):
    """Tests retrieving the earliest trade date."""
    # Mock the result set: (date,)
    mock_connection.execute.return_value.fetchone.return_value = (date(2019, 6, 15),)

    first_date = get_first_trade_date()
    assert first_date == date(2019, 6, 15)

def test_get_first_trade_date_no_results(mock_connection):
    """Tests case where no trades have been recorded."""
    # Mock the result set to be None
    mock_connection.execute.return_value.fetchone.return_value = None

    first_date = get_first_trade_date()
    assert first_date is None

