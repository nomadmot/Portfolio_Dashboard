"""
Use YFinance to get current stock info
"""
# Third Party Imports
import yfinance as yf

# Local Application Imports
import config

# Set up logging
logger = config.LOGGER

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
