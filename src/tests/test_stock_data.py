"""
this module contains a script to test the stock data retrieval
and processing functions
"""

from core import YfPeriods, get_stock_history

# retrieve stock history for 'AAPL' for the last month
aapl_data = get_stock_history('AAPL', period=YfPeriods.M1)
print(aapl_data)


# retrieve stock history for 'AAPL' for the period
# from 1992-01-01 to 1992-06-01
aapl_data = get_stock_history('AAPL',
                              start_date='1992-01-01',
                              end_date='1992-06-01',
                              )
print(aapl_data)
