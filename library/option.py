'''
classes and methods related to modeling equity options
'''
from enum import Enum
import datetime as dt
import yfinance as yf


# internal enumeration class to manage option type
class OptionType():
    '''
    enumeration used to manage option type for the Option class
    should be set to call or put, undefined is error condition
    '''
    CALL = "C"
    PUT = "P"

class Option():
    '''
    Represents an option
    '''
    # instance variables
    _ticker = None


    # instance properties
    @property
    def symbol(self) -> str:
        '''
        return the symbol of the the option
        '''
        return self._symbol
    @symbol.setter
    def symbol(self, symbol: str):
        '''
        set the symbol of the option
        '''
        self._symbol = symbol


    @property
    def underlying(self) -> str:
        '''
        return the symbol of the stock underlying the option
        '''
        return self._underlying
    @underlying.setter
    def underlying(self, underlying: str):
        '''
        set the symbol of the stock underlying the option
        '''
        self._underlying = underlying


    @property
    def strike_price(self) -> float:
        '''
        return the strike price of the option
        '''
        return self._strike_price
    @strike_price.setter
    def strike_price(self, strike_price: float):
        '''
        set the strike price of the option
        '''
        self._strike_price = strike_price


    @property
    def option_type(self) -> str:
        '''
        return the option type (put or call)
        '''
        return self._option_type
    @option_type.setter
    def option_type(self, option_type: str):
        '''
        set the option type (put or call)
        '''
        self._option_type = option_type


    @property
    def expiration_date(self) -> dt.date:
        '''
        return the strike price of the option
        '''
        return self._expiration_date
    @expiration_date.setter
    def expiration_date(self, expiration_date: dt.date):
        '''
        set the strike price of the option
        '''
        self._expiration_date = expiration_date


    # method to provide detail about class contents
    def __repr__(self):
        return str(self.__dict__)

    # factory method to create an Option object using seperate parameters
    @classmethod
    def create_from_parameters(cls,
        underlying: str,
        strike_price: float,
        option_type: str,
        # date must be in %Y/%m/%d (yyyy/mm/dd) format
        expiration_date: str) -> object:
        '''
        construct an Option object using parameters as seperate variables

        Arguments:
            underlying -- the symbol of the underlying equity
            strike_price -- the strike price of the option
            option_type -- the type (OptionTtype.call or OptionTtype.put)
                of the option
            expiration_date -- the expiration date of the option in
                "YYYY/MM/DD" format
        '''
        # create an empty Option class object
        opt = Option()
        # set the instance properties
        opt.underlying = underlying
        opt.expiration_date = dt.datetime.strptime(expiration_date,"%Y/%m/%d").date()
        opt.option_type = option_type
        opt.strike_price = strike_price
        # create a yfinance ticker object for this option
        opt._ticker = yf.Ticker(opt.get_yfinance_option_symbol())

        return opt

    # factory method to create an Option object from the Yahoo option symbol
    @classmethod
    def create_from_yfinance_symbol(cls, option_symbol: str) -> object:
        '''
        construct an Option object using the Yahoo symbol

        Arguments:
            option_symbol -- The Yahoo symbol for the option
        '''
        # create an empty Option class object
        opt = Option()
        # find the end of the underlying symbol
        i = 0
        while not option_symbol[i].isnumeric():
            i = i + 1
        # set the instance properties
        # the underlying symbol begins after the initial dash
        # and ends at the first numeric character
        opt.underlying = option_symbol[1:i]
        # expiration date is six characters after the underlying symbol
        expiration_date = option_symbol[i: i+6]
        i = i + 6
        opt.expiration_date = dt.datetime.strptime(expiration_date,"%y%m%d").date()
        # the next character in the symbol is the first character
        # of the option type
        option_type = option_symbol[i: i+1]
        i = i + 1
        if option_type == "C":
            opt.option_type = OptionType.CALL
        elif option_type == "P":
            opt.option_type = OptionType.PUT
        else:
            raise ValueError(f"Invalid option type: {option_type} in symbol {option_symbol}")
        # the next 5 characters of the symbol is the strike price
        opt.strike_price = float(option_symbol[i: i+5])
        # create a yfinance ticker object for this option
        opt._ticker = yf.Ticker(option_symbol)

        return opt
    

    # factory method to create an Option object from the Fidelity option symbol
    @classmethod
    def create_from_fidelity_symbol(cls, option_symbol: str) -> object:
        '''
        construct an Option object using the Yahoo symbol

        Arguments:
            option_symbol -- The Yahoo symbol for the option
        '''

        # create an empty Option class object
        opt = Option()

        # set the symbol property
        opt.symbol = option_symbol

        # find the end of the underlying symbol
        i = 0
        while not option_symbol[i].isnumeric():
            i += 1
        # set the instance properties
        opt.underlying = option_symbol[:i]
        # expiration date is six characters after the underlying symbol
        expiration_date = option_symbol[i: i+6]
        i += 6
        opt.expiration_date = dt.datetime.strptime(expiration_date,"%y%m%d").date()
        # the next character in the symbol is the first character
        # of the option type
        option_type = option_symbol[i: i+1]
        i += 1
        if option_type == "C":
            opt.option_type = OptionType.CALL
        elif option_type == "P":
            opt.option_type = OptionType.PUT
        else:
            raise ValueError(f"Invalid option type: {option_type} in symbol {option_symbol}")
        # the rest of the characters of the symbol is the strike price
        opt.strike_price = float(option_symbol[i:])
        # create a yfinance ticker object for this option
        opt._ticker = yf.Ticker(opt.get_yfinance_option_symbol())

        return opt


    # instance methods
    def get_yfinance_option_symbol(self) -> str:
        '''
        return the Yahoo option symbol based on the Option attributes
        '''
        # strike price is 8 integer digits with the last 3 set to zero
        strike_price = str(self.strike_price * 1000).zfill(8)

        # expiration date is 2-digit year followed by 2-digit month and day
        exp_date = f"{str(self.expiration_date.year)[2:]}"
        exp_date = f"{exp_date}{str(self.expiration_date.month).zfill(2)}"
        exp_date = f"{exp_date}{str(self.expiration_date.day).zfill(2)}"

        return f"-{self.underlying}{exp_date}{self.option_type}{strike_price}"

    def get_option_info(self) -> dict:
        '''
        return a dictionary containing current option info from Yahoo financial
        '''
        return self._ticker.get_info()

    def get_history(self) -> dict:
        '''
        return a dictionary containing history data from Yahoo financial
        '''
        return self._ticker.history("max")

    def get_maturity_days(self, from_date: str=None) -> int:
        '''
        return the number of days until maturity by subtracting the from_date
        from the option expiration date. if from_date isn't specified, todays
        date is used instead.
        '''
        if from_date is None:
            from_date = dt.date.today()
        else:
            # input from_date must be in %Y/%m/%d (yyyy/mm/dd) format
            from_date = dt.datetime.strptime(from_date,"%Y/%m/%d").date()

        # subtract from_date from the expiration date to get the
        # number of days until maturity
        return (self.expiration_date - from_date).days

if __name__ == "__main__":
    #test = Option.create_from_parameters( "AAPL", 250, OptionType.CALL, "2025/9/18")
    test = Option.create_from_yfinance_symbol("T250919P00016000")
    print(f"\nOption object:\n{test}")

    print(f"\nOption symbol: {test.get_yfinance_option_symbol()}")
    print("Yahoo data:")
    for key, value in test.get_option_info().items():
        print(f"{key}: {value}")
    print("\nYahoo history:")
    for key, value in test.get_history().items():
        print(f"{key}: {value}")

    print(f"\nDays until expiration: {test.get_maturity_days()}")
    print(f"Days from 2024/12/2: {test.get_maturity_days('2024/12/2')}")
