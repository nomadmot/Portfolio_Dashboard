"""
routines to fetch securities data
"""
# Standard imports
from enum import Enum
from datetime import timedelta

# 3rd party imports
import pandas as pd
import yfinance as yf

# Local imports
from . import get_logger

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
        ticker_data: pd.DataFrame = yf_ticker.history(
                                                period=period.value,
                                                auto_adjust=True
                                                )
    ticker_data.reset_index(inplace=True)

    return ticker_data
