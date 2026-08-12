"""
routines to fetch securities data
"""
# Standard imports
from enum import Enum
from datetime import timedelta
from typing import List

# 3rd party imports
import pandas as pd
import yfinance as yf
import duckdb

# Local imports
from . import get_logger, DATABASE_CONNECTION
from schemas import Security

# mark entry into the module
_logger = get_logger(__name__)
_logger.debug("In module %s", __name__)

class YfPeriods(Enum):
    """
    Enumeration for time period selections
    """
    D1 = "1d"
    D5 = "5d"
    M1 = "1mo"
    M3 = "3mo"
    M6 = "6mo"
    YTD = "ytd"
    YR1 = "1y"

    PERIODS = [D1, D5, M1, M3, M6, YTD, YR1]

    @classmethod
    def get_display_periods(cls) -> list:
        """
        provide a list of display values for period selection

        Returns:
            list of display values for period selection
        """
        return cls.PERIODS.value

def get_stock_history(ticker: str,
                       start_date=None,
                       end_date=None,
                       period=None) -> pd.DataFrame:
    """
    Use yfinance to get historical stock data for a given ticker.

    Arguments:
        ticker -- An uppercase string representing the stock ticker symbol.

    Keyword Arguments:
        start_date -- The start date for the fetched data. The data will
         include dates from the start date through today. (default: {None})

        end_date -- The end date for the fetched data. If specified, the data
         will include dates up to and including the end date. (default: {None})

        period -- The time period to fetch data (use YfPeriods enum)
         (default: {None})
         
        **Note**: You must specify either `start_date` or `period`, not both.

    Raises:
        ValueError: The function raises a ValueError if both `start_date`
            and `period` are provided.
    Returns:
        A pandas DataFrame containing the historical stock data.
    """
    # call with start_date or days, not both
    if start_date is not None and period is not None:
        raise ValueError("Specify either start_date or period, not both.")

    # initialize an empty DataFrame for the ticker data
    ticker_data: pd.DataFrame = pd.DataFrame()

    # use yfinance to get SPY data starting with the first date
    # in the balances and ending today
    yf_ticker = yf.Ticker(ticker)
    if start_date is not None:
        if end_date is not None:
            # add one day to the end date to include the end date in the results
            ticker_data: pd.DataFrame = yf_ticker.history(
                                         start=start_date,
                                         end=end_date + timedelta(days=1),
                                         auto_adjust=True
                                         )
        else:
            ticker_data: pd.DataFrame = yf_ticker.history(
                                         start=start_date,
                                         auto_adjust=True
                                         )
    elif period is not None:
        period_val = period.value if hasattr(period, 'value') else period
        ticker_data: pd.DataFrame = yf_ticker.history(
                                              period=period_val,
                                              auto_adjust=True
                                              )
    ticker_data.reset_index(inplace=True)

    return ticker_data

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

