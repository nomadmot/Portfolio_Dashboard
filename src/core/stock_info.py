"""
Use YFinance to get current stock info
"""
# Standard Library Imports
import logging

# Third Party Imports
import yfinance as yf
from sqlalchemy import select
from sqlalchemy.orm import Session

# Local Application Imports
import models.settings as settings
from models.portfolio import Security

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(settings.LogLevelApplication)

def get_security_info(symbol: str) -> Security:
    """
    Get security information for a given symbol

    :param symbol: Stock symbol

    :return: Security dataclass instance
    """
    logger.debug("In get_security_info, symbol=%s", symbol)
    # generate a sqlalchemy select statement to retrieve the security
    with Session(settings.DatabaseEngine) as session:
        result = session.execute(
            select(Security).where(Security.symbol == symbol)
            ).first()

    # check if the result is None, which means the security does not exist
    if not result:
        raise ValueError(f"Security with symbol {symbol} does not exist.")
    else:
        security = result[0]
        logger.debug("Found security: %s", security)

    # return the Security object
    return security

def get_basic_quote(symbol: str) -> dict:
    """
    Get basic stock quote information for a given symbol

    :param symbol: Stock symbol

    :return: Dictionary with basic stock information
    """
    logger.debug("" \
    "In get_basic_quote, symbol=%s", symbol)
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

    logger.debug("Yfinance returned: %s", basic_quote)
    #adjust data as neccessary
    if basic_quote["currentPrice"] == 0.0:
        basic_quote["currentPrice"] = basic_quote["previousClose"]
    logger.debug("Adjusted basic_quote: %s", basic_quote)

    return basic_quote
