"""
This module contains functions to access and manipulate daily balance data.
"""
# Import necessary libraries
from datetime import date
from sqlalchemy import select
from pandas import DataFrame

# Import local modules
import config
from models.portfolio import DailyBalance, Account
from core import Periods

def get_account(account_id: int) -> Account:
    """
    look up the specified Acount for the given account_id.

    Arguments:
        account_id -- The ID of the account to retrieve.

    Returns:
        The Account object corresponding to the given account_id.
    """
    # generate a sqlalchemy select statement to retrieve the account
    stmt = select(Account).where(Account.id == account_id)
    with config.DB_ENGINE.connect() as conn:
        result = conn.execute(stmt).first()

    # check if the result is None, which means the account does not exist
    if not result:
        raise ValueError(f"Account with ID {account_id} does not exist.")

    # return the Account object
    return Account(result[0], result[1], trades=[])

def get_balance_history(account_id: int,
                        period: Periods = Periods.ALL,
                        ascending: bool = False) -> DataFrame:
    """
    Retrieve the balance history for the specified account and time period.

    Arguments:
        account_id -- The ID of the account to retrieve balances for.
        period -- The time period for which to retrieve balances.
        ascending -- Whether to sort the results in ascending order by date (default is False).
        
    Returns:
        A pandas DataFrame containing the balance history, indexed by date.
    """
    # set the number of days for the chart based on the selected period
    chart_days = None
    begin_date = None
    match(period):
        case Periods.D30.value:
            chart_days = 30
        case Periods.D50.value:
            chart_days = 50
        case Periods.D90.value:
            chart_days = 90
        case Periods.YTD.value:
            begin_date = date(date.today().year, 1, 1)
        case Periods.YR1.value:
            begin_date = date(date.today().year -1, date.today().month, date.today().day)
        case Periods.ALL.value:
            # no specific period, return all balances
            pass
        case _:
            # raise an error if the period is not recognized
            raise ValueError(f"Invalid period: {period}")

    # generate a sqlalchemy select statement to retrieve the balances
    stmt = select(DailyBalance).where(DailyBalance.account_id == account_id)

    # apply filters based on the provided parameters
    if chart_days is not None:
        stmt = stmt.order_by(DailyBalance.date.desc()).limit(chart_days)
    elif begin_date is not None:
        stmt = stmt.where(DailyBalance.date >= begin_date)

    # execute the query and fetch results
    with config.DB_ENGINE.connect() as conn:
        result = conn.execute(stmt)

    # convert the result to a DataFrame
    df_balances = DataFrame([{
        'date': balance.date,
        'balance': balance.balance
    } for balance in result])

    # ensure the DataFrame is sorted by date as requested in
    # the ascending parameter and reset the index for proper ordering
    df_balances.sort_values('date', ascending=ascending, inplace=True)
    df_balances.reset_index(drop=True, inplace=True)

    return df_balances

#if __name__ == "__main__":
    #print(get_balance_history(1, days=30))
