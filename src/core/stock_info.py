"""
Use YFinance to get current stock info
"""
import yfinance as yf

def get_basic_quote(symbol: str) -> dict:
    """
    Get basic stock quote information for a given symbol
    :param symbol: Stock symbol
    :return: Dictionary with basic stock information
    """
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
        return basic_quote
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return {}
