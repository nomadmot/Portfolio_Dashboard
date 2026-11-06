"""
Helpers for the "Compare:" selectbox on the Performance Summary page.

The comparison target is either a ticker symbol (a stock, e.g. SPY) or another
portfolio account. Account options are visually distinguished from ticker symbols
by a leading em-dash + space, so an account named (e.g.) "SPY" can never be
mistaken for the SPY ticker. Duplicate account names are disambiguated with their
ID (mirroring ``AccountSelectionComponent``).

This module is intentionally free of any database or Streamlit dependencies so
that the option-building / resolution logic can be unit-tested in isolation.
"""
# Import standard libraries
from typing import List

# Import local modules
from schemas import Account
from . import get_logger

# mark entry into the module
_logger = get_logger(__name__)
_logger.debug("In module %s", __name__)

# An em-dash (the "emphasis dash") followed by a space marks an account option,
# so it can never be confused with a (plain) ticker symbol in the selectbox.
EMP_DASH = "\u2014"
COMPARISON_PREFIX = EMP_DASH + " "


def disambiguated_name(account: Account, accounts: List[Account]) -> str:
    """
    The display name for an account, with its ID appended when the name is shared
    by more than one account (mirrors ``AccountSelectionComponent``'s
    disambiguation).
    """
    name = account.account_name
    if sum(1 for a in accounts if a.account_name == name) > 1:
        return f"{name} ({account.account_id})"
    return name


def comparison_options(symbols: List[str], accounts: List[Account]) -> List[str]:
    """
    Build the "Compare:" selectbox options: the ticker symbols first, followed by
    every account, each prefixed with the em-dash marker and shown with its
    disambiguated name.
    """
    return [
        *symbols,
        *[f"{COMPARISON_PREFIX}{disambiguated_name(a, accounts)}"
          for a in accounts],
    ]


def is_account_option(label: str) -> bool:
    """True if the given option label represents an account (em-dash prefixed)."""
    return label.startswith(COMPARISON_PREFIX)


def account_name_from_option(label: str) -> str | None:
    """
    Return the display name (with any ID suffix) for an account option, or None
    if the label is a ticker symbol (i.e. has no em-dash prefix).
    """
    return label[len(COMPARISON_PREFIX):] if is_account_option(label) else None


def account_id_for_option(label: str, accounts: List[Account]) -> int | None:
    """
    Resolve an account option label to its account ID, or None for a ticker
    option. Matches on the disambiguated display name.
    """
    if not is_account_option(label):
        return None
    name = account_name_from_option(label)
    for a in accounts:
        if disambiguated_name(a, accounts) == name:
            return a.account_id
    return None
