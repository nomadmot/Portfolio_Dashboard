"""
Unit tests for the portfolio models
"""
import datetime as dt
import models.portfolio as portfolio


#instantiate a Security object for testing
security = portfolio.Security(
    symbol="AAPL",
    name="Apple Inc.",
    security_type=portfolio.SecurityType.STOCK,
    associated_symbol="",
    # empty lists for trades, prices, and notes
    trades=[],
    prices=[],
    notes=[]
)
# Invoke the __repr__ method of the Security class
print(security)

#Instantiate an Account object for testing
account = portfolio.Account(
    id=1,
    name="Test Account",
    trades=[]
)
# Invoke the __repr__ method of the Account class
print(account)

#Instantiate a Trade object for testing
trade = portfolio.Trade(
    id=1,
    account_id=account.id,
    symbol="AAPL",
    trade_date=dt.date(year=2024, month=6, day=1),
    trade_type=portfolio.TradeType.BUY,
    quantity=10,
    price=150.00,
    fees=.01,
    account=account,
    securities=security
)
# Invoke the __repr__ method of the Trade class
print(trade)

#Instantiate a Price object for testing
price = portfolio.Price(
    symbol="AAPL",
    date=dt.date(year=2024, month=6, day=1),
    close_price=150.00,
    securities=security
)
# Invoke the __repr__ method of the Price class
print(price)

#Instantiate a Note object for testing
note = portfolio.Note(
    id=account.id,
    note_date=dt.datetime(year=2024, month=6, day=1),
    content="This is a test note for the security.",
    symbol="AAPL",
    securities=security
)
# Invoke the __repr__ method of the Note class
print(note)

# Instantiate a DailyBalance object for testing
daily_balance = portfolio.DailyBalance(
    date=dt.date(year=2024, month=6, day=1),
    account_id=account.id,
    balance=10000.00
)
# Invoke the __repr__ method of the DailyBalance class
print(daily_balance)
