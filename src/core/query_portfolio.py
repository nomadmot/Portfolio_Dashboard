"""
This module contains functions to access and manipulate daily balance data.
"""
# Import necessary libraries
from typing import List
from datetime import date
from sqlalchemy import select, distinct
from sqlalchemy.orm import Session
from pandas import DataFrame

# Import local modules
import config
from models.portfolio import DailyBalance, Account, Security, Trade, SecurityType
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
    with Session(config.DB_ENGINE) as session:
        result = session.execute(
            select(Account).where(Account.id == account_id)
            ).first()

    # check if the result is None, which means the account does not exist
    if not result:
        raise ValueError(f"Account with ID {account_id} does not exist.")

    # return the Account object
    return result[0]

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
        case Periods.D30:
            chart_days = 30
        case Periods.D50:
            chart_days = 50
        case Periods.D90:
            chart_days = 90
        case Periods.YTD:
            begin_date = date(date.today().year-1, 12, 31)
        case Periods.YR1:
            begin_date = date(date.today().year -1, date.today().month, date.today().day)
        case Periods.ALL:
            # no specific period, return all balances
            pass
        case _:
            # raise an error if the period is not recognized
            raise ValueError(f"Invalid period: {period}")

    # generate a sqlalchemy select statement to retrieve the balances
    stmt = select(DailyBalance).where(DailyBalance.account_id == account_id)

    # apply filters based on the provided parameters
    if chart_days is not None and begin_date is not None:
        raise ValueError("Chart days and begin date cannot both be specified.")
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

# function to get a list of security symbols from the database
def get_security_symbols(include_options=False) -> List[str]:
    # get a list of security symbols from the database
    # get the symbols for all securities except options
    stmt = select(distinct(Security.symbol)).where(
        Security.security_type != SecurityType.OPTION
    )
    with Session(config.DB_ENGINE) as session:
        result = session.execute(stmt)
    symbols = [symbol[0] for symbol in result]

    # add the associated symbols for options if include_options is True
    if include_options:
        stmt = select(distinct(Security.symbol)).where(
            Security.security_type == SecurityType.OPTION
        )
        with Session(config.DB_ENGINE) as session:
            result = session.execute(stmt)
        for row in result:
            symbol = row[0]
            if symbol not in symbols:
                symbols.append(symbol)

    # return the sorted list
    symbols.sort()
    return symbols

# function to query the database for trades of the selected security
def get_trades(symbols: List[str]) -> DataFrame:
    # query the trades for the selected security symbol
    stmt = select(
                Security.security_type,
                Security.name,
                Trade.symbol,
                Trade.trade_date,
                Trade.trade_type,
                Trade.quantity,
                Trade.price,
                Trade.fees
        ).join(
            Trade, Security.symbol == Trade.symbol
        ).where(
            Security.symbol.in_(symbols)
        )

    # add options trades if include_options is True
    # if include_options:
    #     stmt = union_all(
    #         stmt,
    #         select(
    #                         Security.security_type,
    #                         Security.name,
    #                         Trade.symbol,
    #                         Trade.trade_date,
    #                         Trade.trade_type,
    #                         Trade.quantity,
    #                         Trade.price,
    #                         Trade.fees
    #         ).where(and_(
    #             Security.security_type == SecurityType.OPTION,
    #             Security.associated_symbol == symbol
    #         )).join(Security).filter(Security.associated_symbol == symbol)
    #     )

    with Session(config.DB_ENGINE) as session:
        db_result = session.execute(stmt)

    # convert the trades to a list of Dict objects
    trades = []
    for row in db_result:
        if row.security_type == SecurityType.OPTION:
            # for options, multiply quantity by 100
            trade_amount = row.quantity * row.price * 100
        else:
            trade_amount = row.quantity * row.price

        trades.append({
                    'Symbol': row.symbol,
                    'Date': row.trade_date,
                    'Type': row.trade_type,
                    'Quantity': row.quantity,
                    'Price': row.price,
                    'Amount': -round(trade_amount),
                    })

    # sort the results and return a pandas Dataframe
    return DataFrame(trades).sort_values('Date')
