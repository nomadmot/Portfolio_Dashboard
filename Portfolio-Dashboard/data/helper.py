"""
Contains helper classes and functions for data access
"""
from enum import Enum

class Periods(Enum):
    """
    Enumeration for time period selections
    """
    D30 = "30 days"
    D50 = "50 days"
    D90 = "90 days"
    YTD = "ytd"
    YR1 = "1 yr"

    PERIODS = [D30, D50, D90, YTD, YR1]

    @classmethod
    def get_display_periods(cls) -> list:
        """
        provide a list of display values for period selection

        Returns:
            list of display values for period selection
        """
        return cls.PERIODS.value
