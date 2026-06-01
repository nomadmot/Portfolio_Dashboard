"""
Use YFinance to get current stock info
"""

# Standard imports
from typing import List
from datetime import date

# 3rd party imports
import yfinance as yf
import duckdb
# from sqlalchemy import select
# from sqlalchemy.orm import Session

# Local imports
from schemas import Security
from . import get_logger, DATABASE_CONNECTION # Updated import

# Initialize logger for this module
_logger = get_logger(__name__)
_logger.debug("In module %s", __name__)

def get_security_info(symbol: str) -> Security:
    """
    Get security information for a given symbol using the database.
    :param symbol: Stock symbol
    :return: Security dataclass instance
    """
    # 1. Transaction/Read Context: Use the connection object for a read operation.
    try:
        # 2. SQL Query: Select the security details directly.
        select_sql = """
        SELECT * FROM securities WHERE symbol = ? LIMIT 1;
        """
        # Execute the query using the connection object
        result = DATABASE_CONNECTION.execute(select_sql, (symbol,)).fetchone()

        if not result:
            raise ValueError(f"Security with symbol {symbol} does not exist.")

        # 3. Mapping: Manually map the raw tuple result back into the Security Pydantic model.
        # This replaces the ORM object return.
        return Security(
            symbol=result[0],
            name=result[1],
            security_type=result[2],
            associated_symbol=result[3]
        )
    except duckdb.Error as e:
        _logger.error("DuckDB Error retrieving security:", exc_info=True)
        raise RuntimeError(f"Database error during security retrieval: {e}") from e
    except ValueError as e:
        # Re-raise specific business logic errors
        raise e


def get_basic_quote(symbol: str) -> dict:
    """
    Get basic stock quote information for a given symbol using yfinance.
    :param symbol: Stock symbol
    :return: Dictionary with basic stock information
    """
    _logger.debug("In get_basic_quote, symbol=%s", symbol)
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        basic_quote = {
            "symbol": symbol,
            "shortName": info.get("shortName", ""),
            "currentPrice": info.get("currentPrice", 0.0),
            "previousClose": info.get("previousClose", 0.0),
            "open": info.get("open", 0.0),
            "dayHigh": info.get("dayHigh", 0.0),
            "dayLow": info.get("dayLow", 0.0),
            "volume": info.get("volume", 0),
            "marketCap": info.get("marketCap", 0),
        }
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return {}

    # Adjust data as necessary
    if basic_quote["currentPrice"] == 0.0:
        basic_quote["currentPrice"] = basic_quote["previousClose"]
        _logger.debug("Adjusted basic_quote: %s", basic_quote)
    return basic_quote
