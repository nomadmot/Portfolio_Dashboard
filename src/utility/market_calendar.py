"""
functions to query market holidays
"""
# standard library imports
from datetime import date

# third-party imports
from duckdb import sql

# local application imports
from config import SETTINGS
from utility import get_logger

# mark entry into the module
logger = get_logger(__name__)
logger.debug("In module %s", __name__)

# resolve duckdb filename
_MARKET_HOLIDAYS = f"{SETTINGS.duck_puddle}market_holidays.parquet"
logger.info("Using duckdb file at %s", _MARKET_HOLIDAYS)

def get_closed_count(start_date: date, end_date: date) -> int|None:
    """
    get the count of closed market holidays between start_date and end_date

    :param start_date: starting date (date)
    :param end_date: ending date (date)
    :return: count of closed market holidays (int)
    """
    logger.debug("In function get_closed_count with start_date=%s, end_date=%s",
               start_date, end_date)

    # SQL query to get the count of closed market holidays
    result = sql(
        f"SELECT COUNT(*) AS holiday_count "
        f"FROM '{_MARKET_HOLIDAYS}' "
        f"WHERE Status = 'Closed' "
        f"AND Date >= '{start_date}' "
        f"AND Date <= '{end_date}';"
        )
    logger.debug("Query executed, result: %s", result)

    # extract the count from the result
    holiday_count = result.fetchone()
    if holiday_count is None:
        raise LookupError("Could not retrieve closed market holiday count")
    else:
        holiday_count = holiday_count[0]

    # return the result
    logger.debug("Exiting function get_closed_count with result=%s", holiday_count)
    return holiday_count

def market_is_open(check_date: date) -> bool:
    """
    check if the market is open on the given date

    :param check_date: date to check (date)
    :return: True if market is open, False if closed (bool)
    """
    logger.debug("In function market_is_open with check_date=%s", check_date)

    # check to see if the date is on a weekend
    if check_date.weekday() >= 5:
        logger.debug("Date %s is on a weekend, market is closed", check_date)
        return False

    # SQL query to check if the date is a market holiday
    result = sql(
        f"SELECT Status "
        f"FROM '{_MARKET_HOLIDAYS}' "
        f"WHERE Date = '{check_date}';"
        )
    logger.debug("Query executed, result: %s", result)

    # determine if market is open
    market_status = result.fetchone()
    if market_status is None:
        # no entry means market is open
        return_status = True
    else:
        status = market_status[0]
        return_status = status != 'Closed'

    logger.debug("Exiting function market_is_open with is_open=%s", return_status)
    return return_status

if __name__ == "__main__":
    # test the get_closed_count function
    # RUN: python -m utility.market_calendar
    closed_count = get_closed_count(date(2024, 12, 31), date(2025, 8, 1))
    print(f"Closed market holidays between 2024-12-31 and 2025-08-01: {closed_count}")
    closed_count = get_closed_count(date(2024, 10, 31), date(2024, 11, 1))
    print(f"Closed market holidays between 2024-10-31 and 2024-11-01: {closed_count}")
    closed_count = get_closed_count(date(2024, 11, 1), date(2024, 11, 1))
    print(f"Closed market holidays between 2024-11-01 and 2024-10-31: {closed_count}")
    test_date=date(2025,12,25)
    is_open = market_is_open(test_date)
    print(f"Market is open on {test_date}: {is_open}")
    test_date=date(2025,7,24)
    is_open = market_is_open(test_date)
    print(f"Market is open on {test_date}: {is_open}")
