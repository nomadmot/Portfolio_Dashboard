"""
functions to query market holidays
"""
# standard library imports
from datetime import date

# third-party imports
from duckdb import connect

# local application imports
from config import SETTINGS
from utility import get_logger

# mark entry into the module
logger = get_logger(__name__)
logger.debug("In module %s", __name__)

# connect to the duckdb database
DUCKDB = connect(SETTINGS.duck_database)
logger.info("Connected to duckdb database at %s", SETTINGS.duck_database)

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
    query = (
        "SELECT COUNT(*) AS holiday_count "
        "FROM market_holidays "
        "WHERE Status = 'Closed' "
        "AND Date >= ? "
        "AND Date <= ?;"
        )
    # execute the query
    result = DUCKDB.execute(query, (start_date, end_date)).fetchone()
    logger.debug("Query executed, result: %s", result)

    # extract the count from the result
    if result is not None:
        result = result[0]
    else:
        raise LookupError("Could not retrieve closed market holiday count")

    # return the result
    logger.debug("Exiting function get_closed_count with result=%s", result)
    return result

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
    query = (
        "SELECT Status "
        "FROM market_holidays "
        "WHERE Date = ?;"
        )
    # execute the query
    result = DUCKDB.execute(query, (check_date,)).fetchone()
    logger.debug("Query executed, result: %s", result)

    # determine if market is open
    if result is None:
        # no entry means market is open
        is_open = True
    else:
        status = result[0]
        is_open = status != 'Closed'

    logger.debug("Exiting function market_is_open with is_open=%s", is_open)
    return is_open

if __name__ == "__main__":
    # test the get_closed_count function
    # python -m utility.market_calendar
    closed_count = get_closed_count(date(2024, 12, 31), date(2025, 8, 1))
    print(f"Closed market holidays between 2024-12-31 and 2025-08-01: {closed_count}")
