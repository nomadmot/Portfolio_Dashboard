"""
Provide start and end period selections
"""

# standard library imports
import logging
from datetime import date
from enum import Enum

# local application imports
from config import SETTINGS

# Initialize logging
logger = logging.getLogger(__name__)
logger.setLevel(SETTINGS.loglevel_application.to_logging_level())
# mark entry into the module
logger.debug("In module %s", __name__)

class Periods(Enum):
    """
    Enumeration class for time period selections.
    """
    D30 = "30 Days"
    D50 = "50 Days"
    D90 = "90 Days"
    YTD = "YTD"
    YR1 = "1 Year"
    ALL = "All"
    CUS = "Custom"

    @classmethod
    def get_periods(cls):
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


def get_period_dates(
            period: Periods,
            from_date: date|None = None,
            to_date: date|None = None) -> tuple[date|None, date|None]:
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

    match period:
        case Periods.D30:
            raise NotImplementedError("D30 period not implemented yet")

        case Periods.D50:
            raise NotImplementedError("D50 period not implemented yet")

        case Periods.D90:
            raise NotImplementedError("D90 period not implemented yet")

        case Periods.YTD:
            begin_date = date.today().replace(month=1, day=1)
            end_date = date.today()

        case Periods.YR1:
            begin_date = date.today().replace(year=date.today().year - 1)
            end_date = date.today()

        case Periods.ALL:
            begin_date = None
            end_date = date.today()

        case Periods.CUS:
            begin_date = from_date
            end_date = to_date

    # log exit from the function
    logger.debug("Exiting function get_period_dates with begin_date=%s, end_date=%s",
                 begin_date, end_date)
    return (begin_date, end_date)
