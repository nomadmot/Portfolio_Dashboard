"""
Provide start and end period selections
"""

# standard library imports
import logging
from datetime import date
from enum import Enum

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
            to_date: date|None = None) -> tuple[date, date]:
    """
    provide start and end dates for the given period selection

    Args:
        period (Periods): selected period
        from_date (date, optional): custom start date for 'Custom' period. Defaults to None.

    Returns:
        tuple(date, date): start and end dates for the selected period
    """
