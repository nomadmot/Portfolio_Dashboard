import datetime as dt
from schemas import SecurityType, TradeType
from schemas.portfolio import Account, DailyBalance, Note, Security, Trade
def test_security_creation():
    security = Security(
        symbol="AAPL",
        name="Apple Inc.",
        security_type=SecurityType.STOCK,
        associated_symbol=""
    )
    assert security.symbol == "AAPL"
    assert security.name == "Apple Inc."
def test_account_creation():
    account = Account(
        account_id=1,
        account_name="Test Account"
    )
    assert account.account_id == 1
    assert account.account_name == "Test Account"
def test_trade_creation():
    trade = Trade(
        account_id=1,
        symbol="AAPL",
        trade_date=dt.date(year=2024, month=6, day=1),
        trade_type=TradeType.BUY,
        quantity=10,
        price=150.00,
        fees=0.75
    )
    assert trade.account_id == 1
    assert trade.symbol == "AAPL"
def test_note_creation():
    note = Note(
        symbol="AAPL",
        note_date=dt.datetime(year=2024, month=6, day=1),
        content="This is a test note for the security."
    )
    assert note.symbol == "AAPL"
    assert note.content == "This is a test note for the security."
def test_daily_balance_creation():
    daily_balance = DailyBalance(
        date=dt.date(year=2024, month=6, day=1),
        account_id=1,
        balance=10000.00
    )
    assert daily_balance.date == dt.date(year=2024, month=6, day=1)
    assert daily_balance.balance == 10000.00
