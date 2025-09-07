"""
Enumeration class for time period selections.
"""
from enum import Enum

class Periods(Enum):
    """
    Enumeration for time period selections
    """
    D30 = "30 Days"
    D50 = "50 Days"
    D90 = "90 Days"
    YTD = "YTD"
    YR1 = "1 Year"
    ALL = "All"

    PERIODS = [D30, D50, D90, YTD, YR1, ALL]

    @classmethod
    def get_display_periods(cls) -> list:
        """
        provide a list of display values for period selection

        Returns:
            list of display values for period selection
        """
        return cls.PERIODS.value
