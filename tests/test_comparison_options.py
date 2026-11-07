"""
Unit tests for the "Compare:" selectbox helpers in utility/comparison_options.py.

The helpers are pure functions with no database or Streamlit dependencies, so
they can be imported and tested in isolation (mirroring the mock setup used by
the other test files for the modules they transitively pull in).
"""
# import standard libraries
import os
import sys
from unittest.mock import MagicMock

# 1. Fix Working Directory for relative paths in settings.py
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
os.chdir(root_dir)

# 2. Remember the original module table entries so they can be restored below
_original_modules = {
    name: sys.modules.get(name)
    for name in ("duckdb", "config", "config.settings", "utility.database")
}

# 3. Mock duckdb before importing any core/utility modules
mock_duckdb = MagicMock()
class MockDuckDBError(Exception):
    pass
mock_duckdb.Error = MockDuckDBError
sys.modules["duckdb"] = mock_duckdb

# 4. Mock the database module so no connection is created
mock_db = MagicMock()
mock_db_module = MagicMock()
mock_db_module.DATABASE_CONNECTION = mock_db
sys.modules['utility.database'] = mock_db_module

# 5. Mock SETTINGS to avoid loading the real configuration files
mock_settings = MagicMock()
mock_settings.defaults = MagicMock()
mock_settings.defaults.max_time_machine_days = 180
mock_loglevel = MagicMock()
mock_loglevel.to_logging_level.return_value = 10  # logging.DEBUG
mock_settings.loglevel_application = mock_loglevel
mock_settings.loglevel_streamlit = mock_loglevel

mock_settings_module = MagicMock()
mock_settings_module.SETTINGS = mock_settings
sys.modules['config.settings'] = mock_settings_module


# import 3rd party libraries
import pytest

# import local libraries
from schemas.portfolio import Account
from utility.comparison_options import (
    EMP_DASH,
    COMPARISON_PREFIX,
    disambiguated_name,
    comparison_options,
    is_account_option,
    account_name_from_option,
    account_id_for_option,
)

# Restore the original module table entries now that the local imports have
# completed; the imported module objects remain cached and usable.
for _name, _original in _original_modules.items():
    if _original is None:
        sys.modules.pop(_name, None)
    else:
        sys.modules[_name] = _original


# ==============================================================================
# TEST SUITE FOR is_account_option / account_name_from_option
# ==============================================================================
def test_is_account_option_true_for_prefixed():
    assert is_account_option(f"{COMPARISON_PREFIX}Roth IRA") is True
    assert is_account_option(f"{EMP_DASH} X") is True


def test_is_account_option_false_for_ticker():
    assert is_account_option("SPY") is False
    assert is_account_option("QQQ") is False


def test_is_account_option_false_for_bare_em_dash():
    # a label that is exactly the em-dash (no trailing space) is not an account
    assert is_account_option(EMP_DASH) is False
    assert is_account_option("") is False


def test_account_name_from_option_returns_name():
    assert account_name_from_option(f"{COMPARISON_PREFIX}Roth IRA") == "Roth IRA"


def test_account_name_from_option_none_for_ticker():
    assert account_name_from_option("SPY") is None


# ==============================================================================
# TEST SUITE FOR disambiguated_name
# ==============================================================================
def test_disambiguated_name_unique_name_has_no_suffix():
    accounts = [Account(account_id=1, account_name="Alpha")]
    assert disambiguated_name(accounts[0], accounts) == "Alpha"


def test_disambiguated_name_duplicate_name_gets_id_suffix():
    accounts = [
        Account(account_id=1, account_name="Dup"),
        Account(account_id=2, account_name="Dup"),
        Account(account_id=3, account_name="Solo"),
    ]
    by_id = {a.account_id: a for a in accounts}
    assert disambiguated_name(by_id[1], accounts) == "Dup (1)"
    assert disambiguated_name(by_id[2], accounts) == "Dup (2)"
    assert disambiguated_name(by_id[3], accounts) == "Solo"


# ==============================================================================
# TEST SUITE FOR comparison_options
# ==============================================================================
def test_comparison_options_tickers_first_then_accounts():
    accounts = [
        Account(account_id=1, account_name="Alpha"),
        Account(account_id=2, account_name="Beta"),
    ]
    options = comparison_options(["SPY"], accounts)
    assert options == ["SPY", f"{COMPARISON_PREFIX}Alpha", f"{COMPARISON_PREFIX}Beta"]


def test_comparison_options_account_named_like_ticker_is_disambiguated():
    # an account literally named "SPY" is prefixed with the em-dash, so it can
    # never be mistaken for the SPY ticker in the selectbox
    accounts = [Account(account_id=9, account_name="SPY")]
    options = comparison_options(["SPY"], accounts)
    assert options == ["SPY", f"{COMPARISON_PREFIX}SPY"]


# ==============================================================================
# TEST SUITE FOR account_id_for_option
# ==============================================================================
def test_account_id_for_option_resolves_unique_name():
    accounts = [
        Account(account_id=1, account_name="Alpha"),
        Account(account_id=2, account_name="Beta"),
    ]
    assert account_id_for_option(f"{COMPARISON_PREFIX}Beta", accounts) == 2
    assert account_id_for_option(f"{COMPARISON_PREFIX}Alpha", accounts) == 1


def test_account_id_for_option_none_for_ticker():
    accounts = [Account(account_id=1, account_name="Alpha")]
    assert account_id_for_option("SPY", accounts) is None


def test_account_id_for_option_resolves_duplicate_by_id():
    accounts = [
        Account(account_id=1, account_name="Dup"),
        Account(account_id=2, account_name="Dup"),
    ]
    assert account_id_for_option(f"{COMPARISON_PREFIX}Dup (1)", accounts) == 1
    assert account_id_for_option(f"{COMPARISON_PREFIX}Dup (2)", accounts) == 2


def test_account_id_for_option_unknown_label_is_none():
    accounts = [Account(account_id=1, account_name="Alpha")]
    assert account_id_for_option(f"{COMPARISON_PREFIX}DoesNotExist", accounts) is None
