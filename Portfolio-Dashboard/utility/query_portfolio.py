"""
This module contains functions to access and manipulate daily balance data.
"""
from datetime import date
from sqlalchemy import select
from pandas import DataFrame
import config
from models.portfolio import DailyBalance, Account

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
    
    # return the Account object or None if not found
    return result

def get_balance_history(account_id:int, days=None, begin_date=None) -> DataFrame:
    """
    Retrieve the balance history for the specified account and time period.

    Arguments:
        account_id -- The ID of the account to retrieve balances for.

    Keyword Arguments:
        days -- If present, returns history for the specified number of
         trading days. NOTE: you may specify days OR begin_date, but not
          both. (default: {None})
        begin_date -- If present, returns history starting from the
         specified date. NOTE: you may specify begin_date OR days, but not
          both. (default: {None})

    Returns:
        A pandas DataFrame containing the balance history, indexed by date.
    """
    # check input for validity
    if days is not None and begin_date is not None:
        raise ValueError("You may specify days OR begin_date, but not both.")

    # generate a sqlalchemy select statement to retrieve the balances
    stmt = select(DailyBalance).where(DailyBalance.account_id == account_id)

    # apply filters based on the provided parameters
    if days is not None:
        stmt = stmt.order_by(DailyBalance.date.desc()).limit(days)
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

    # ensure the DataFrame is sorted by date ascending
    df_balances.sort_values('date', ascending=True, inplace=True)
    df_balances.reset_index(drop=True, inplace=True)

    return df_balances

if __name__ == "__main__":
    print(get_balance_history(1, days=30))
