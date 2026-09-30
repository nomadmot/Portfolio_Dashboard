import datetime as dt

import pytest

from schemas import SecurityType, TradeType
from schemas.portfolio import Security, Trade


def test_trade_type_new_values_are_valid():
    new_values = [
        TradeType.DEPOSIT,
        TradeType.WITHDRAWAL,
        TradeType.DIVIDEND,
        TradeType.INTEREST,
        TradeType.FEE,
        TradeType.TAX,
        TradeType.SPLIT,
        TradeType.JOURNAL,
    ]
    for value in new_values:
        assert value in TradeType.Types
        assert TradeType.is_valid(value)


def test_security_type_cash_is_valid():
    assert SecurityType.CASH in SecurityType.Types
    assert SecurityType.is_valid(SecurityType.CASH)


def test_trade_with_new_type_constructs():
    trade = Trade(
        account_id=1,
        symbol="$CASH",
        trade_date=dt.date(2026, 8, 17),
        trade_type=TradeType.DEPOSIT,
        quantity=1,
        price=60000.00,
        fees=0.00,
    )
    assert trade.trade_type == TradeType.DEPOSIT


def test_security_with_cash_type_constructs():
    security = Security(
        symbol="$CASH",
        name="Cash",
        security_type=SecurityType.CASH,
    )
    assert security.security_type == SecurityType.CASH


def test_trade_rejects_invalid_type():
    with pytest.raises(ValueError):
        Trade(
            account_id=1,
            symbol="AAPL",
            trade_date=dt.date(2024, 6, 1),
            trade_type="BOGUS",
            quantity=1,
            price=100.00,
            fees=0.00,
        )


def test_security_rejects_invalid_type():
    with pytest.raises(ValueError):
        Security(
            symbol="AAPL",
            name="Apple Inc.",
            security_type="X",
        )
