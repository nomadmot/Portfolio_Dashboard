"""
functions to query market holidays
"""
# standard library imports
from datetime import date
import logging

# third-party imports
from duckdb import connect

# local application imports
from config import SETTINGS

# Initialize logging
logger = logging.getLogger(__name__)
logger.setLevel(SETTINGS.loglevel_application.to_logging_level())
# mark entry into the module
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

if __name__ == "__main__":
    # test the get_closed_count function
    # python -m utility.market_calendar
    closed_count = get_closed_count(date(2024, 12, 31), date(2025, 8, 1))
    print(f"Closed market holidays between 2024-12-31 and 2025-08-01: {closed_count}")
