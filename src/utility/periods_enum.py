"""
Provide start and end period selections
"""

# standard library imports
from enum import Enum

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
