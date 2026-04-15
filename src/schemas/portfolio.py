"""
This module defines Pydantic data models for the portfolio management system
"""

# standard imports
import datetime as dt
from typing import Optional

# 3rd party imports
from pydantic import BaseModel, Field, field_validator

# local imports
from . import TradeType, SecurityType

# --- Security Schema ---
class Security(BaseModel):
    """
    Pydantic model representing a stock, option, EFT, or other investment asset

    Raises: Value error if the security_type field is invalid
    """
    symbol: str = Field(..., description="Unique stock ticker symbol.")
    name: str
    security_type: str = Field(..., description="Must be a valid SecurityType.")
    associated_symbol: Optional[str] = Field(None, description="Underlying symbol for options.")

    @field_validator('security_type')
    @classmethod
    def validate_security_type(cls, v):
        """
        Validate the input security type against the SecurityType enumeration

        Arguments:
            v -- the input value

        Raises:
            ValueError: The input value failed verification

        Returns:
            The input Value
        """
        if not SecurityType.is_valid(v):
            raise ValueError(f"Invalid security type: {v}. Must be one of {SecurityType.Types}")
        return v

# --- Account Schema ---
class Account(BaseModel):
    """
    Pydantic model representing a cross-reference directory of account IDs and the account name
    """
    account_id: int
    account_name: str

# --- Trade Schema ---
class Trade(BaseModel):
    """
    Pydantic model representing a stock transaction

    Raises: Value error if the security_type field is invalid
    """
    account_id: int
    symbol: str
    trade_date: dt.date
    trade_type: str = Field(..., description="Must be a valid TradeType.")
    quantity: float
    price: float
    fees: float

    @field_validator('trade_type')
    @classmethod
    def validate_trade_type(cls, v):
        """
        Validate the input security type against the TradeType enumeration

        Arguments:
            v -- the input value

        Raises:
            ValueError: The input value failed verification

        Returns:
            The input Value
        """
        if not TradeType.is_valid(v):
            raise ValueError(f"Invalid trade type: {v}. Must be one of {TradeType.Types}")
        return v

# --- Note Schema ---
class Note(BaseModel):
    """
    Pydantic model representing a text note aplicable to a specific date and stock symbol
    """
    symbol: str
    note_date: dt.datetime
    content: str

# --- DailyBalance Schema ---
class DailyBalance(BaseModel):
    """
    Pydantic model representing the ending balance on the given date for the given account
    """
    date: dt.date
    account_id: int
    balance: float
