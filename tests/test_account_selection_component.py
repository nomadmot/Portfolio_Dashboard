"""
Unit tests for utility/account_selection_component.py
Note: This test file assumes the same mocked 'duckdb', 'utility.database',
    and 'config.settings' modules as test_query_portfolio.py so that the
    real settings and database files are never touched.
"""
# import standard libraries
from unittest.mock import MagicMock
import os
import sys
from uuid import uuid4

# 1. Fix Working Directory for relative paths in settings.py
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
os.chdir(root_dir)

# Remember the original module table entries so they can be restored below;
# other test files (e.g. test_config) must not see the mocks installed next.
#
# KNOWN PRE-EXISTING BUG: this file snapshots the module table at COLLECTION
# time (top of module) but only restores it at the bottom of the module body
# below. If another test module in the same pytest session has ALREADY imported
# the real 'duckdb'/'config'/'config.settings'/'utility.database' modules
# (e.g. test_config.py importing the real config.settings), those real modules
# are replaced here by the mocks and restored there, which is fine; BUT if this
# file is collected/imported AFTER the real modules are already cached in
# sys.modules, the restore loop unconditionally writes back the ORIGINAL
# (possibly-None) values, which can drop the real modules from sys.modules
# mid-session and cause confusing import errors in later test files.
# Correct fix: only restore an entry if this file actually replaced it
# (i.e. only write back / pop if the current sys.modules value is the mock
# installed above, not something else). Do not change test behavior when
# working on this file.
_original_modules = {
    name: sys.modules.get(name)
    for name in ("duckdb", "config", "config.settings", "utility.database")
}

# 2. Mock duckdb before importing any core/utility modules
mock_duckdb = MagicMock()
class MockDuckDBError(Exception):
    pass
mock_duckdb.Error = MockDuckDBError
sys.modules["duckdb"] = mock_duckdb

# 3. Mock the database module so no connection is created
mock_db = MagicMock()
mock_db_module = MagicMock()
mock_db_module.DATABASE_CONNECTION = mock_db
sys.modules['utility.database'] = mock_db_module

# 4. Mock SETTINGS to avoid loading the real configuration files
mock_settings = MagicMock()
mock_settings.defaults = MagicMock()
mock_settings.defaults.max_time_machine_days = 180

mock_loglevel = MagicMock()
mock_loglevel.to_logging_level.return_value = 10 # logging.DEBUG
mock_settings.loglevel_application = mock_loglevel
mock_settings.loglevel_streamlit = mock_loglevel

mock_settings_module = MagicMock()
mock_settings_module.SETTINGS = mock_settings
sys.modules['config.settings'] = mock_settings_module


# import 3rd party libraries
import pytest
from streamlit.testing.v1 import AppTest

# import local libraries
from schemas.portfolio import Account
from utility.account_selection_component import (
    AccountSelectionComponent,
    get_account_selection_component,
)
from utility.autoupdate_multiselect_component import (
    AutoUpdateMultiselectComponent,
    get_aumc_instance,
)

# Restore the original module table entries now that the local imports
# have completed; the imported module objects remain cached and usable.
# (See KNOWN PRE-EXISTING BUG note above about the _original_modules
# snapshot/restore pattern in this file.)
for _name, _original in _original_modules.items():
    if _original is None:
        sys.modules.pop(_name, None)
    else:
        sys.modules[_name] = _original


def _run_script(options: list[Account], allow_multiple: bool) -> AppTest:
    """
    Run an AppTest script that creates, renders, and reports the selection
    of a uniquely-keyed AccountSelectionComponent.
    """
    key = f"test_{uuid4()}"
    options_literal = ", ".join(
        f"Account(account_id={a.account_id}, account_name={a.account_name!r})"
        for a in options
    )
    script = f"""
import streamlit as st
from schemas.portfolio import Account
from utility.account_selection_component import get_account_selection_component
selector = get_account_selection_component(
    "{key}", "Account:", [{options_literal}], allow_multiple={allow_multiple})
selector.render()
st.text(str(selector.selected))
"""
    app_test = AppTest.from_string(script)
    app_test.run()
    return app_test


def _reported(app_test: AppTest):
    """Return the reported selection (the text element written after render)."""
    return app_test.main.children[1].value


# ==============================================================================
# TEST SUITE FOR DEFAULT SELECTION
# ==============================================================================
def test_single_select_defaults_to_account_one():
    """Account 1 is selected by default when present (even out of order)."""
    app_test = _run_script(
        [Account(account_id=2, account_name="Beta"),
         Account(account_id=1, account_name="Alpha")],
        allow_multiple=False,
    )
    assert app_test.selectbox[0].value == "Alpha"
    assert _reported(app_test) == '1'

def test_single_select_defaults_to_first_option_without_account_one():
    """The first option is selected when account 1 does not exist."""
    app_test = _run_script(
        [Account(account_id=2, account_name="Beta"),
         Account(account_id=3, account_name="Gamma")],
        allow_multiple=False,
    )
    assert app_test.selectbox[0].value == "Beta"
    assert _reported(app_test) == '2'

def test_multi_select_defaults_to_account_one():
    """Account 1 is the only default selection in multi-select mode."""
    app_test = _run_script(
        [Account(account_id=1, account_name="Alpha"),
         Account(account_id=2, account_name="Beta")],
        allow_multiple=True,
    )
    assert app_test.multiselect[0].value == ["Alpha"]
    assert _reported(app_test) == '[1]'

def test_empty_options_report_no_selection():
    """An empty options list yields None (single) or [] (multi)."""
    single = AccountSelectionComponent("empty_single", "Account:", [])
    assert single.selected is None
    multi = AccountSelectionComponent("empty_multi", "Account(s):", [],
                                      allow_multiple=True)
    assert multi.selected == []


# ==============================================================================
# TEST SUITE FOR SELECTION CHANGES
# ==============================================================================
def test_single_select_change_updates_selected():
    """Changing the selectbox updates the reported account ID."""
    app_test = _run_script(
        [Account(account_id=1, account_name="Alpha"),
         Account(account_id=2, account_name="Beta")],
        allow_multiple=False,
    )
    app_test.selectbox[0].set_value("Beta")
    app_test.run()
    assert app_test.selectbox[0].value == "Beta"
    assert _reported(app_test) == '2'

def test_multi_select_change_updates_selected():
    """Changing the multiselect updates the reported account IDs."""
    app_test = _run_script(
        [Account(account_id=1, account_name="Alpha"),
         Account(account_id=2, account_name="Beta"),
         Account(account_id=3, account_name="Gamma")],
        allow_multiple=True,
    )
    app_test.multiselect[0].set_value(["Beta", "Gamma"])
    app_test.run()
    assert app_test.multiselect[0].value == ["Beta", "Gamma"]
    assert _reported(app_test) == '[2, 3]'

def test_selection_persists_across_runs():
    """The selection survives a rerun without user interaction."""
    app_test = _run_script(
        [Account(account_id=1, account_name="Alpha"),
         Account(account_id=2, account_name="Beta")],
        allow_multiple=False,
    )
    app_test.selectbox[0].set_value("Beta")
    app_test.run()
    assert _reported(app_test) == '2'
    app_test.run()
    assert _reported(app_test) == '2'


# ==============================================================================
# TEST SUITE FOR DISPLAY LABELS
# ==============================================================================
def test_duplicate_names_are_disambiguated():
    """Duplicate account names are displayed with their ID appended."""
    app_test = _run_script(
        [Account(account_id=1, account_name="Dup"),
         Account(account_id=2, account_name="Dup"),
         Account(account_id=3, account_name="Solo")],
        allow_multiple=False,
    )
    assert app_test.selectbox[0].options == ["Dup (1)", "Dup (2)", "Solo"]
    app_test.selectbox[0].set_value("Dup (2)")
    app_test.run()
    assert _reported(app_test) == '2'

def test_allow_multiple_property_reflects_configuration():
    """The allow_multiple property reports the configured mode."""
    assert AccountSelectionComponent("k1", "Account:", []).allow_multiple is False
    assert AccountSelectionComponent("k2", "Account(s):", [],
                                     allow_multiple=True).allow_multiple is True


# ==============================================================================
# TEST SUITE FOR THE FACTORY
# ==============================================================================
def test_factory_returns_existing_instance_for_same_key():
    """The factory returns the same instance for a repeated key."""
    options = [Account(account_id=1, account_name="Alpha")]
    first = get_account_selection_component("shared_key", "Account:", options)
    second = get_account_selection_component("other_key_label_unused", "Account:",
                                             options)
    assert first is get_account_selection_component("shared_key", "Account:", options)
    assert first is not second


# ==============================================================================
# TEST SUITE FOR AutoUpdateMultiselectComponent
# ==============================================================================
def test_set_options_replaces_options_and_prunes_selection():
    """
    set_options replaces the options list, drops any selected values that are
    no longer available, and re-renders the widget so that the stale selection
    is no longer reported.
    """
    app_test = AppTest.from_string("""
import streamlit as st
from utility.autoupdate_multiselect_component import get_aumc_instance
component = get_aumc_instance(
    "smoke_set_options", "Select Symbol(s):", ["AAPL", "GOOGL", "MSFT"],
    accept_new_options=False, placeholder="Select symbols...",)
component.selected = ["AAPL", "MSFT"]
component.set_options(["GOOGL", "IBM"])
st.text(str(component._options))
""")
    app_test.run()
    # the replacement options were rendered, and the stale selection pruned
    assert app_test.multiselect[0].options == ["GOOGL", "IBM"]
    assert app_test.multiselect[0].value == []
    assert app_test.main.children[1].value == "['GOOGL', 'IBM']"

def test_set_options_preserves_still_available_selections():
    """Selections that remain in the new options list are kept in the widget."""
    app_test = AppTest.from_string("""
import streamlit as st
from utility.autoupdate_multiselect_component import get_aumc_instance
component = get_aumc_instance(
    "smoke_set_options_keep", "Select Symbol(s):", ["AAPL", "GOOGL"],
    accept_new_options=False, placeholder="Select symbols...",)
component.selected = ["AAPL", "GOOGL"]
component.set_options(["AAPL", "GOOGL", "MSFT"])
st.text(str(component.selected))
""")
    app_test.run()
    assert app_test.multiselect[0].options == ["AAPL", "GOOGL", "MSFT"]
    assert app_test.multiselect[0].value == ["AAPL", "GOOGL"]
    assert app_test.main.children[1].value == "['AAPL', 'GOOGL']"

def test_set_options_deduplicates_and_sorts():
    """The new options list is deduplicated and kept sorted."""
    component = AutoUpdateMultiselectComponent(
        "set_options_sort", "Select Symbol(s):", ["ZZZ"])
    component.selected = []

    component.set_options(["MSFT", "AAPL", "MSFT"])

    assert component._options == ["AAPL", "MSFT"]

def test_set_options_selection_persists_across_runs():
    """
    A selection survives a rerun after the options have been replaced.
    AppTest does not re-register widget values after a second run, so the
    persistence is verified through the component instance instead.
    """
    app_test = AppTest.from_string("""
import streamlit as st
from utility.autoupdate_multiselect_component import get_aumc_instance
component = get_aumc_instance(
    "smoke_set_options_persist", "Select Symbol(s):", ["AAPL", "GOOGL"],
    accept_new_options=False, placeholder="Select symbols...",)
if "done" not in st.session_state:
    component.selected = ["GOOGL"]
    component.set_options(["GOOGL", "MSFT"])
    st.session_state["done"] = True
st.text(str(component.selected))
""")
    app_test.run()
    assert app_test.multiselect[0].value == ["GOOGL"]
    assert app_test.multiselect[0].options == ["GOOGL", "MSFT"]

    from utility.autoupdate_multiselect_component import _COMPONENT_INSTANCES
    component = _COMPONENT_INSTANCES["smoke_set_options_persist"]
    assert component.selected == ["GOOGL"]

    # rerun without user interaction; the selection must persist
    app_test.run()
    assert component.selected == ["GOOGL"]
