"""
This module contains functions to access and manipulate daily balance data.
"""
# Import standard libraries
from typing import List
from datetime import date

# Import 3rd party libraries
from sqlalchemy import select, distinct
from sqlalchemy.orm import Session
from pandas import DataFrame

# Import local modules
from models.portfolio import DailyBalance, Account, Security, Trade, SecurityType
from utility import get_logger, DATABASE_ENGINE

# mark entry into the module
logger = get_logger(__name__)
logger.debug("In module %s", __name__)

def get_account(account_id: int) -> Account:
    """
    look up the specified Acount for the given account_id.

    Arguments:
        account_id -- The ID of the account to retrieve.

    Returns:
        The Account object corresponding to the given account_id.
    """
    # generate a sqlalchemy select statement to retrieve the account
    with Session(DATABASE_ENGINE) as session:
        result = session.execute(
            select(Account).where(Account.id == account_id)
            ).first()

    # check if the result is None, which means the account does not exist
    if not result:
        raise ValueError(f"Account with ID {account_id} does not exist.")

    # return the Account object
    return result[0]

def get_balance_history(account_id: int,
                        from_date: date,
                        to_date: date,
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
    # generate a sqlalchemy select statement to retrieve the balances
    stmt = select(DailyBalance).where(
        DailyBalance.account_id == account_id
        ).where(
            DailyBalance.date >= from_date
        ).where(
            DailyBalance.date <= to_date
        )

    # execute the query and fetch results
    with DATABASE_ENGINE.connect() as conn:
        result = conn.execute(stmt)

    # convert the result to a DataFrame
    df_balances = DataFrame([{
        'date': balance.date,
        'balance': balance.balance
    } for balance in result])

    # ensure the DataFrame is sorted by date as requested in
    # the ascending parameter and reset the index for proper ordering
    if not df_balances.empty:
        df_balances.sort_values('date', ascending=ascending, inplace=True)
        df_balances.reset_index(drop=True, inplace=True)

    return df_balances


# function to get a list of security symbols from the database
def get_security_symbols(include_options=False) -> List[str]:
    """
    Get a list of security symbols from the database

    Keyword Arguments:
        include_options -- Select whether or not options are included
         in the results (default: {False})

    Returns:
        A list of all security symbols in the database, optionally including options.
    """
    stmt = select(distinct(Security.symbol)).where(
        Security.security_type != SecurityType.OPTION
    )
    with Session(DATABASE_ENGINE) as session:
        result = session.execute(stmt)
    symbols = [symbol[0] for symbol in result]

    # add the associated symbols for options if include_options is True
    if include_options:
        stmt = select(distinct(Security.symbol)).where(
            Security.security_type == SecurityType.OPTION
        )
        with Session(DATABASE_ENGINE) as session:
            result = session.execute(stmt)
        for row in result:
            symbol = row[0]
            if symbol not in symbols:
                symbols.append(symbol)

    # return the sorted list
    symbols.sort()
    return symbols


# function to add associated options symbols to a list of security symbols
def lookup_associated_symbols(symbols: List[str]) -> List[str]:
    """
    Append associated options symbols from the database to the input list of stock symbols

    Keyword Arguments:
        symbols: -- A list of stock symbols to add associated options for

    Returns:
        The input list of security symbols, including associated options.
    """
    # add the associated symbols for options if include_options is True
    stmt = select(distinct(Security.symbol)).where(
        (Security.associated_symbol.in_(symbols))
    )
    with Session(DATABASE_ENGINE) as session:
        result = session.execute(stmt)
    for row in result:
        symbol = row[0]
        if symbol not in symbols:
            symbols.append(symbol)

    # return the sorted list
    symbols.sort()
    return symbols


def get_last_trade_date():
    """Get the last trade date from the Trades table."""
    stmt = select(
                Trade.trade_date
        ).order_by(
            Trade.trade_date.desc()
        ).limit(1)

    with Session(DATABASE_ENGINE) as session:
        return list(session.execute(stmt))[0][0]


# function to query the database for trades of the selected security
def get_trades(symbols: List[str],
               begin_date: date,
               end_date: date,
               ascending: bool = False) -> DataFrame:
    """
    Query the Trades table for the selected security symbols.

    Arguments:
        symbols -- a list of security symbols to query trades for.
        period -- The time period for which to retrieve trades (defaut is ALL).
        ascending -- Whether to sort the results in ascending order by date (default is False).

    Returns:
        A pandas DataFrame containing the trades for the specified symbols.
    """

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
        ).where(
            Trade.trade_date >= begin_date
        ).where(
            Trade.trade_date <= end_date
            )

    # execute the query and fetch results
    with Session(DATABASE_ENGINE) as session:
        db_result = session.execute(stmt)

    # convert the trades to a list of Dict objects
    trades = []
    for row in db_result:
        if row.security_type == SecurityType.OPTION:
            # for options, multiply quantity by 100
            trade_amount = row.quantity * row.price * 100
        else:
            trade_amount = row.quantity * row.price
        # need to switch the sign for the trade amount
        trade_amount = -trade_amount

        trades.append({
                    'Symbol': row.symbol,
                    'Date': row.trade_date,
                    'Type': row.trade_type,
                    'Quantity': row.quantity,
                    'Price': row.price,
                    'Amount': trade_amount,
                    })

    # sort the results and return a pandas Dataframe
    # buys are sorted in front of sells if they occur on the same day
    if trades:
        return DataFrame(trades).sort_values(
            by=['Date', 'Type'],
            ascending=ascending).reset_index(drop=True)
    else:
        return DataFrame(columns=['Symbol', 'Date', 'Type', 'Quantity', 'Price', 'Amount'])
