from sqlalchemy.orm import (
    Mapped, mapped_column, relationship, registry
)
from sqlalchemy import (
    create_engine, Integer, String, Float, Date, DateTime,
    ForeignKey, CheckConstraint, Text
)
import datetime as dt

mapper_registry = registry()

# enumeration class for trade types
class TradeType:
    BUY = "BUY"
    SELL = "SELL"
    TRANSFER = "TRAN"
    EXERCISE = "EXRC"
    EXPIRE = "EXPR"

    Types = (BUY, SELL, TRANSFER, EXERCISE, EXPIRE)

    @classmethod
    def is_valid(cls, value):
        return value in (cls.Types)
    
# enumeration class for security types
class SecurityType:
    STOCK = 'S'
    BOND = 'B'
    ETF = 'E'
    MUTUAL_FUND = 'M'
    OPTION = 'O'

    Types = (STOCK, BOND, ETF, MUTUAL_FUND, OPTION)

    @classmethod
    def is_valid(cls, value):
        return value in (cls.Types)

@mapper_registry.mapped_as_dataclass()
class Security:
    __tablename__ = 'securities'
    __table_args__ = (
        CheckConstraint(f"security_type IN {SecurityType.Types}", name="chk_security_type"),
    )

    symbol: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    security_type: Mapped[SecurityType] = mapped_column(String, nullable=False)
    # For options, this is the underlying stock symbol
    associated_symbol: Mapped[str] = mapped_column(String, nullable=True)

    trades: Mapped[list["Trade"]] = relationship("Trade", back_populates="securities")
    prices: Mapped[list["Price"]] = relationship("Price", back_populates="securities")
    notes: Mapped[list["Note"]] = relationship("Note", back_populates="securities")

    def __repr__(self):
        return f"<Security(symbol={self.symbol!r}, name={self.name!r}, security_type={self.security_type!r}, " \
               f"associated_symbol={self.associated_symbol!r})>"


@mapper_registry.mapped_as_dataclass()
class Account:
    __tablename__ = 'accounts'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)

    trades: Mapped[list["Trade"]] = relationship("Trade", back_populates="account")

    def __repr__(self):
        return f"<Account(id={self.id!r}, name={self.name!r})>"


@mapper_registry.mapped_as_dataclass()
class Trade:
    __tablename__ = 'trades'
    __table_args__ = (
        CheckConstraint(f"trade_type IN {TradeType.Types}", name="chk_trade_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey('accounts.id'))
    symbol: Mapped[str] = mapped_column(String, ForeignKey('securities.symbol'), nullable=False)
    trade_date: Mapped[Date] = mapped_column(Date, nullable=False)
    trade_type: Mapped[TradeType] = mapped_column(String, nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    fees: Mapped[float] = mapped_column(Float, nullable=False)

    account: Mapped["Account"] = relationship("Account", back_populates="trades")
    securities: Mapped["Security"] = relationship("Security", back_populates="trades")

    def __repr__(self):
        return (f"<Trade(id={self.id!r}, account_id={self.account_id!r}, symbol={self.symbol!r}, "
                f"trade_date={self.trade_date!r}, trade_type={self.trade_type!r}, "
                f"quantity={self.quantity!r}, price={self.price!r}, fees={self.fees!r})>")


@mapper_registry.mapped_as_dataclass()
class Price:
    __tablename__ = 'prices'

    symbol: Mapped[str] = mapped_column(String, ForeignKey('securities.symbol'), primary_key=True)
    date: Mapped[Date] = mapped_column(Date, primary_key=True)
    close_price: Mapped[float] = mapped_column(Float, nullable=False)

    securities: Mapped["Security"] = relationship("Security", back_populates="prices")

    def __repr__(self):
        return f"<Price(symbol={self.symbol!r}, date={self.date!r}, close_price={self.close_price!r})>"


@mapper_registry.mapped_as_dataclass()
class Note:
    __tablename__ = 'notes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    note_date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    symbol: Mapped[str] = mapped_column(String, ForeignKey('securities.symbol'), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    securities: Mapped["Security"] = relationship("Security", back_populates="notes")

    def __repr__(self):
        return (f"<kNote(id={self.id!r}, symbol={self.symbol!r}, "
                f"note_date={self.note_date!r}, content={self.content!r})>")


@mapper_registry.mapped_as_dataclass()
class DailyBalance:
    __tablename__ = 'daily_balances'

    date: Mapped[dt.date] = mapped_column(Date, primary_key=True)
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey('accounts.id'), primary_key=True)
    balance: Mapped[float] = mapped_column(Float, nullable=False)

    def __repr__(self):
        return f"<DailyBalance(date={self.date!r}, account_id={self.account_id!r}, balance={self.balance!r})>"
