"""
This module contains functions to access and manipulate daily balance data.
"""
# Import standard libraries
from typing import List
from datetime import date

# Import 3rd party libraries
from pandas import DataFrame
import duckdb

# Import local modules
from schemas import Account, SecurityType
from utility import DATABASE_CONNECTION, get_logger

# Initialize logger for this module
_logger = get_logger(__name__)
_logger.debug("In module %s", __name__)

def get_account(account_id: int) -> Account:
    """
    Look up the specified Account for the given account_id. 

    Arguments:
        account_id -- The ID of the account to retrieve.

    Returns:
        The Account object corresponding to the given account_id.
    """
    # mark entry into the method
    _logger.debug("Entering get_account with account_id = %s", account_id)

    try:
        # Select the account details directly.
        select_sql = """
        SELECT * FROM accounts WHERE account_id = ? LIMIT 1;
        """
        # Execute the query using the connection object
        result = DATABASE_CONNECTION.execute(select_sql, (account_id,)).fetchone()

        if not result:
            raise ValueError(f"Account with ID {account_id} does not exist.")

        # Manually map the raw tuple result back into the Account Pydantic model.
        return Account(
            account_id=result[0],
            account_name=result[1]
        )
    except duckdb.Error as e:
        _logger.error("DuckDB Error retrieving account:", exc_info=True)
        raise RuntimeError(f"Database error during account retrieval: {e}") from e
    except ValueError as e:
        # Re-raise specific business logic errors
        raise e


def get_balance_history(account_id: int,
                        begin_date: date,
                        end_date: date,
                        ascending: bool = False) -> DataFrame:
    """
    Retrieve the balance history for the specified account and time period.

    Arguments:
        account_id -- The ID of the account to retrieve balances for.
        begin_date -- The begin date for which to retrieve balances.
        end_date -- The end date for which to retrieve balances.
        ascending -- Whether to sort the results in ascending order by date (default is False).

    Returns:
        A pandas DataFrame containing the balance history, indexed by date.
    """
    # mark entry into the method
    _logger.debug(("Entering method get_balance_history with: ",
                 "account_id = %s ",
                 "from_date = %s ",
                 "to_date = %s ",
                 "ascending = %s"),
                 account_id, begin_date, end_date, ascending,
                 )

    # Select the required fields.
    select_sql = f"""
        SELECT date, balance FROM daily_balances 
        WHERE account_id = ? AND date BETWEEN ? AND ?
        ORDER BY date {'ASC' if ascending else 'DESC'};
        """

    result = DATABASE_CONNECTION.execute(select_sql, (account_id, begin_date, end_date)).fetchall()

    # Mapping and DataFrame Creation
    if not result:
        # no results found
        return DataFrame(columns=['date', 'balance'])

    # Convert the list of tuples into the required DataFrame format
    df_data = [{'date': row[0], 'balance': row[1]} for row in result]
    df_balances = DataFrame(df_data)

    return df_balances


def get_last_trade_date():
    """Get the last trade date from the Trades table."""
    # mark entry into the method
    _logger.debug("Entering method get_last_trade_date")

    sql = """
    SELECT 
        MAX(T.trade_date) 
    FROM trades T;
    """

    result = DATABASE_CONNECTION.execute(sql).fetchone()

    if result:
        # The result is a tuple (date,)
        return result[0]
    else:
        return None

def get_security_symbols(include_options: bool = False) -> List[str]:
    """
    Get a list of security symbols from the database

    Keyword Arguments:
        include_options -- Select whether or not options are included in the results
        (default: False).  

    Returns:
        A list of all security symbols in the database, optionally including options.
    """
    # mark entry into the method
    _logger.debug(("Entering method get_security_symbols with: ",
                 "include_options = %s "),
                 include_options,
                 )

    # Build the base query
    if include_options:
        # If including options, the query logic changes slightly.
        base_sql = "SELECT DISTINCT symbol FROM securities WHERE security_type = ?"
        params = (SecurityType.OPTION,)
    else:
        base_sql = "SELECT DISTINCT symbol FROM securities WHERE security_type != ?"
        params = (SecurityType.OPTION,)

    # Execute the query
    result = DATABASE_CONNECTION.execute(base_sql, params).fetchall()

    # Extract symbols
    symbols = [row[0] for row in result]

    symbols.sort()
    return symbols


def lookup_associated_symbols(symbols: List[str]) -> List[str]:
    """
    Append associated options symbols from the database to the input list of stock symbols. 

    Keyword Arguments:
        symbols: -- A list of stock symbols to add associated options for.

    Returns:
        The input list of security symbols, including associated options.
    """
    # mark entry into the method
    _logger.debug(("Entering method lookup_associated_symbols with: ",
                 "symbols = %s "),
                 symbols,
                 )

    # Dynamically build the parameter list for the IN clause
    placeholders = ', '.join(['?'] * len(symbols))
    final_sql = f"""
        SELECT DISTINCT symbol FROM securities
        WHERE associated_symbol IN ({placeholders});
    """
    _logger.debug("Generated SQL statement: %s", final_sql)

    # Execute the query
    result = DATABASE_CONNECTION.execute(final_sql, tuple(symbols)).fetchall()
    _logger.debug("SQL result is: %s", result)

    # Compile and return the list
    associated_symbols = [row[0] for row in result]

    # Use a set to ensure uniqueness before converting back to a sorted list
    unique_symbols = list(set(symbols) | set(associated_symbols))
    unique_symbols.sort()
    return unique_symbols


def get_trades(symbols: List[str],
               begin_date: date,
               end_date: date,
               ascending: bool = False) -> DataFrame:
    """
    Query the Trades table for the selected security symbols.  

    Arguments:
        symbols -- a list of security symbols to query trades for.
        begin_date -- The begin date for which to retrieve trades
        end_date -- The end date for which to retrieve trades
        ascending -- Whether to sort the results in ascending order by date (default is False).

    Returns:
        A pandas DataFrame containing the trades for the specified symbols.
    """
    # mark entry into the method
    _logger.debug(("Entering method get_trades with: ",
                 "symbols = %s ",
                 "begin_date = %s ",
                 "end_date = %s ",
                 "ascending = %s"),
                 symbols, begin_date, end_date, ascending,
                 )

    # Dynamically build the parameters list for the IN clause
    placeholders = ', '.join(['?'] * len(symbols))
    final_sql = f"""
    SELECT 
        T.symbol,
        S.name,
        T.symbol,
        T.trade_date,
        T.trade_type,
        T.quantity,
        T.price,
        T.fees
    FROM trades T
    JOIN securities S ON T.symbol = S.symbol
    WHERE T.symbol IN ({placeholders})
    AND T.trade_date BETWEEN ? AND ?;
    """

    # Execute the query
    params = tuple(symbols) + (begin_date, end_date)
    result = DATABASE_CONNECTION.execute(final_sql, params).fetchall()

    # Process Results and Build DataFrame
    trades = []
    for row in result:
        # row structure: (symbol, name, symbol, trade_date, trade_type, quantity, price, fees)
        symbol = row[0]
        trade_amount = row[6] * row[5] # price * quantity

        # Option contracts are 100 shares per contract
        if row[3] == SecurityType.OPTION:
            trade_amount *= 100

        # Negate the amount for the final 'Amount' column
        final_amount = -trade_amount

        trades.append({
            'Symbol': symbol,
            'Date': row[3],
            'Type': row[4],
            'Quantity': row[5],
            'Price': row[6],
            'Amount': final_amount,
        })

    # Return DataFrame
    if trades:
        df = DataFrame(trades)
        # Sort values according to input parameter
        df.sort_values(
            by=['Date', 'Type'],
            ascending=ascending,
            inplace=True
        )
        df.reset_index(drop=True, inplace=True)
        return df
    else:
        # No trades found
        return DataFrame(columns=['Symbol', 'Date', 'Type', 'Quantity', 'Price', 'Amount'])
