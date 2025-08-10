"""
routines to fetch securities data
"""
import pandas as pd
import yfinance as yf

def get_stock_history(ticker: str, start_date=None, days=None) -> pd.DataFrame:
    """
    Use yfinance to get historical stock data for a given ticker.

    Arguments:
        ticker -- An uppercase string representing the stock ticker symbol.

    Keyword Arguments:
        start_date -- The start date for the fetched data. The data will
         include dates from the start date through today. (default: {None})
        days -- The number of days (starting with today) to fetch data
         (default: {None})
         
        **Note**: You must specify either `start_date` or `days`, not both.

    Raises:
        ValueError: The function raises a ValueError if both `start_date`
            and `days` are provided.

    Returns:
        A pandas DataFrame containing the historical stock data.
    """
    # call with start_date or days, not both
    if start_date is not None and days is not None:
        raise ValueError("Specify either start_date or days, not both.")

    # initialize an empty DataFrame for the ticker data
    ticker_data: pd.DataFrame = pd.DataFrame()

    # use yfinance to get SPY data starting with the first date
    # in the balances and ending today
    yf_ticker = yf.Ticker(ticker)
    if start_date is not None:
        #end_date = dt.today().strftime('%Y-%m-%d')
        ticker_data: pd.DataFrame = yf_ticker.history(
                                                start=start_date,
                                                #end=end_date,
                                                auto_adjust=True
                                                )
    elif days is not None:
        ticker_data: pd.DataFrame = yf_ticker.history(
                                                period=f"{days}d",
                                                auto_adjust=True
                                                )
    ticker_data.reset_index(inplace=True)

    return ticker_data
