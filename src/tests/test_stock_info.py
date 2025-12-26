"""
Tests for the stock_info module
"""

from core import (
    get_security_info,
    get_basic_quote,
)

symbol = "AAPL"
print(get_security_info(symbol))
print(get_basic_quote(symbol))
