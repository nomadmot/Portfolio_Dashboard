"""
Provide start and end period selections
"""

# standard library imports
import logging
from datetime import date, timedelta
from enum import Enum

# local application imports
from config import ENVIRONMENT
from utility import market_is_open

# Initialize logging
logger = logging.getLogger(__name__)
logger.setLevel(ENVIRONMENT.loglevel_application.to_logging_level())
# mark entry into the module
logger.debug("In module %s", __name__)

class Periods(Enum):
    """
    Enumeration class for time period selections.
    """
    NONE = "-Select Period-"
    D30 = "30 Days"
    D50 = "50 Days"
    D90 = "90 Days"
    YTD = "YTD"
    YR1 = "1 Year"
    ALL = "All"
    CUS = "Custom"

    @classmethod
    def get_periods(cls)-> list:
        """
        Provide a list of Period enum members
        """
        return [item[1] for item in cls.__members__.items()]

    @classmethod
    def get_label(cls, item)-> str:
        """
        provide a label for the period selection dropdown

        Returns:
            label for the period selection dropdown
        """
        return item.value

def _calculate_begin_date(end_date: date, market_days: int) -> date:
    """
    calculate the begin date given an end date and number of market days

    Args:
        end_date (date): end date
        market_days (int): number of market days

    Returns:
        date: calculated begin date
    """
    # log entry into the function
    logger.debug("In function _calculate_begin_date with end_date=%s, market_days=%s",
                 end_date, market_days)

    count = 0
    one_day = timedelta(days=1)
    begin_date = end_date
    # loop backwards from end_date to find the begin date
    while count < market_days:
        begin_date = begin_date - one_day
        if market_is_open(begin_date):
            count += 1

    # log exit from the function
    logger.debug("Exiting function _calculate_begin_date with begin_date=%s", begin_date)
    return begin_date

def get_period_dates(
            period: Periods,
            from_date: date|None = None,
            to_date: date|None = None
            ) -> tuple[date, date]:
    """
    provide start and end dates for the given period selection

    Args:
        period (Periods): selected period
        from_date (date, optional): custom start date for 'Custom' period. Defaults to None.

    Returns:
        tuple(date, date): start and end dates for the selected period
    """
    # log entry into the function
    logger.debug("In function get_period_dates with period=%s, from_date=%s, to_date=%s",
                 period, from_date, to_date)

    # check input values
    if period is None:
        logger.debug("nothing to do")
        return (None, None)
    # provide default dates
    if from_date is None:
        from_date = date.today()
    if to_date is None:
        to_date = date.today()

    match period:
        case Periods.NONE:
            begin_date = date.today()
            end_date = date.today()

        case Periods.D30:
            end_date = date.today()
            begin_date = _calculate_begin_date(end_date=end_date, market_days=30)

        case Periods.D50:
            end_date = date.today()
            begin_date = _calculate_begin_date(end_date=end_date, market_days=50)

        case Periods.D90:
            end_date = date.today()
            begin_date = _calculate_begin_date(end_date=end_date, market_days=90)

        case Periods.YTD:
            begin_date = date.today().replace(month=1, day=1)
            end_date = date.today()

        case Periods.YR1:
            begin_date = date.today().replace(year=date.today().year - 1)
            end_date = date.today()

        case Periods.ALL:
            begin_date = date(year=1960, month=1, day=1)  # earliest possible date
            end_date = date.today()

        case Periods.CUS:
            begin_date = from_date
            end_date = to_date

        case _:
            # raise an error if the period is not recognized
            raise ValueError(f"Invalid period: {period}")

    # log exit from the function
    logger.debug("Exiting function get_period_dates with begin_date=%s, end_date=%s",
                 begin_date, end_date)
    return (begin_date, end_date)


def get_period(period: str) -> Periods:
    """
    Given an input string, (i.e. 'D90'), return the correspond Periods enum member

    Arguments:
        period -- A string corresponding to the requested Periods enum member (i.e. 'D90')

    Returns:
        The Periods enum member corresponding to the input string. If the member is not found,
        a warning message is logged in the default Periods.D30 is returned.
    """
    try:
        ret = Periods[period]
    except KeyError:
        logger.warning("Period %s is not found, returning D30", period)
        ret = Periods.D30

    return ret
