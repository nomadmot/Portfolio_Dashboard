"""
Provide start and end period selections
"""

# standard library imports
from datetime import date, timedelta

# local application imports
from . import get_logger, market_is_open, Periods

# initialize logging
_logger = get_logger(__name__)
_logger.debug("In module %s", __name__)

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
    _logger.debug("In function _calculate_begin_date with end_date=%s, market_days=%s",
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
    _logger.debug("Exiting function _calculate_begin_date with begin_date=%s", begin_date)
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
    _logger.debug("In function get_period_dates with period=%s, from_date=%s, to_date=%s",
                 period, from_date, to_date)

    # check input values
    if period is None:
        _logger.debug("nothing to do")
        return (None, None)

    # provide default dates
    if from_date is None:
        from_date = date.today()
    if to_date is None:
        to_date = date.today()

    match period:
        case Periods.NONE:
            begin_date = from_date
            end_date = to_date

        case Periods.D30:
            end_date = from_date
            begin_date = _calculate_begin_date(end_date=end_date, market_days=30)

        case Periods.D50:
            end_date = from_date
            begin_date = _calculate_begin_date(end_date=end_date, market_days=50)

        case Periods.D90:
            end_date = from_date
            begin_date = _calculate_begin_date(end_date=end_date, market_days=90)

        case Periods.YTD:
            begin_date = from_date.replace(month=1, day=1)
            end_date = to_date

        case Periods.YR1:
            begin_date = from_date.replace(year=date.today().year - 1)
            end_date = to_date

        case Periods.ALL:
            begin_date = date(year=1960, month=1, day=1)  # earliest possible date
            end_date = to_date

        case Periods.CUS:
            begin_date = from_date
            end_date = to_date

        case _:
            # raise an error if the period is not recognized
            raise ValueError(f"Invalid period: {period}")

    # log exit from the function
    _logger.debug("Exiting function get_period_dates with begin_date=%s, end_date=%s",
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
        _logger.warning("Period %s is not found, returning D30", period)
        ret = Periods.D30

    return ret
