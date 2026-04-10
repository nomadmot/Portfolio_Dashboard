"""
This module defines enumerations for the portfolio management system
"""

# enumeration class for trade types
class TradeType:
    """
    Class representing the different types of trades that
    can be tracked in the portfolio management system.
    """
    BUY = "BUY"
    SELL = "SELL"
    TRANSFER = "TRAN"
    EXERCISE = "EXRC"
    EXPIRE = "EXPR"
    ASSIGN = "ASGN"

    Types = (BUY, SELL, TRANSFER, EXERCISE, EXPIRE, ASSIGN)

    @classmethod
    def is_valid(cls, value):
        """
        Validate the input value by verifying whether or not the value exists
        within the TradeType enumeration

        Arguments:
            value -- The input value to be validated

        Returns:
            True if the input is valid, otherwise false
        """
        return value in (cls.Types)

# enumeration class for security types
class SecurityType:
    """
    Class representing the different types of securities that
    can be tracked in the portfolio management system.
    """
    STOCK = 'S'
    BOND = 'B'
    ETF = 'E'
    MUTUAL_FUND = 'M'
    OPTION = 'O'

    Types = (STOCK, BOND, ETF, MUTUAL_FUND, OPTION)

    @classmethod
    def is_valid(cls, value):
        """
        Validate the input value by verifying whether or not the value exists
        within the SecurityType enumeration

        Arguments:
            value -- The input value to be validated

        Returns:
            True if the input is valid, otherwise false
        """
        return value in (cls.Types)
