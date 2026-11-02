"""
This module contains functions to access and manipulate daily balance data.
"""
# Import standard libraries
from typing import List
from datetime import date

# Import 3rd party libraries
import polars as pl
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


def get_accounts() -> List[Account]:
    """
    Look up all accounts in the directory.

    Returns:
        A list of Account objects ordered by account name.
    """
    # mark entry into the method
    _logger.debug("Entering get_accounts")

    try:
        select_sql = """
        SELECT account_id, account_name FROM accounts ORDER BY account_name;
        """
        result = DATABASE_CONNECTION.execute(select_sql).fetchall()
        return [Account(account_id=row[0], account_name=row[1]) for row in result]
    except duckdb.Error as e:
        _logger.error("DuckDB Error retrieving accounts:", exc_info=True)
        raise RuntimeError(f"Database error during account retrieval: {e}") from e


def get_balance_history(account_id: int,
                        begin_date: date,
                        end_date: date,
                        ascending: bool = False) -> pl.DataFrame:
    """
    Retrieve the balance history for the specified account and time period.

    Arguments:
        account_id -- The ID of the account to retrieve balances for.
        begin_date -- The begin date for which to retrieve balances.
        end_date -- The end date for which to retrieve balances.
        ascending -- Whether to sort the results in ascending order by date (default is False).

    Returns:
        A polars DataFrame containing the balance history.
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
        SELECT balance_date, balance FROM daily_balances 
        WHERE account_id = ? AND balance_date BETWEEN ? AND ?
        ORDER BY balance_date {'ASC' if ascending else 'DESC'};
        """

    # Convert the query result directly to a polars DataFrame. DuckDB carries the
    # column names and types from the database, so the frame's schema is derived
    # from the live tables rather than re-declared here (and an empty result still
    # yields the correct, typed empty schema).
    return DATABASE_CONNECTION.execute(
        select_sql, (account_id, begin_date, end_date)
    ).pl()


def get_first_balance_date(account_id: int | None = None):
    """
    Get the earliest balance date from the daily_balances table.

    Arguments:
        account_id -- Restrict the search to the given account
            (default is all accounts).
    """
    # mark entry into the method
    _logger.debug("Entering method get_first_balance_date with account_id = %s",
                  account_id)

    sql = """
    SELECT 
        MIN(B.balance_date) 
    FROM daily_balances B
    WHERE ? IS NULL OR B.account_id = ?;
    """

    result = DATABASE_CONNECTION.execute(sql, (account_id, account_id)).fetchone()

    if result:
        # The result is a tuple (date,)
        return result[0]
    else:
        return None


def get_first_trade_date():
    """Get the earliest trade date from the Trades table."""
    # mark entry into the method
    _logger.debug("Entering method get_first_trade_date")

    sql = """
    SELECT 
        MIN(T.trade_date) 
    FROM trades T;
    """

    result = DATABASE_CONNECTION.execute(sql).fetchone()

    if result:
        # The result is a tuple (date,)
        return result[0]
    else:
        return None


def get_last_balance_date(account_id: int | None = None):
    """
    Get the latest balance date from the daily_balances table.

    Arguments:
        account_id -- Restrict the search to the given account
            (default is all accounts).
    """
    # mark entry into the method
    _logger.debug("Entering method get_last_balance_date with account_id = %s",
                  account_id)

    sql = """
    SELECT 
        MAX(B.balance_date) 
    FROM daily_balances B
    WHERE ? IS NULL OR B.account_id = ?;
    """

    result = DATABASE_CONNECTION.execute(sql, (account_id, account_id)).fetchone()

    if result:
        # The result is a tuple (date,)
        return result[0]
    else:
        return None


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


def get_traded_symbols(account_ids: List[int], include_options: bool = False) -> List[str]:
    """
    Get a list of symbols that have at least one transaction for any of the
    given accounts over the full trade history.

    Keyword Arguments:
        account_ids -- the account IDs to query transactions for.
        include_options -- Select whether or not options are included in the
            results (default: False).

    Returns:
        A sorted list of unique symbols with transactions for the given
        accounts. An empty account list yields an empty list.
    """
    # mark entry into the method
    _logger.debug(("Entering method get_traded_symbols with: ",
                   "account_ids = %s ",
                   "include_options = %s "),
                   account_ids,
                   include_options,
                   )

    if not account_ids:
        # no accounts to query; nothing to return
        return []

    # Dynamically build the parameter list for the IN clause
    account_placeholders = ', '.join(['?'] * len(account_ids))

    if include_options:
        # include options but still exclude the cash pseudo-security
        security_filter = "S.security_type != ?"
        params = tuple(account_ids) + (SecurityType.CASH,)
    else:
        # standard securities only: exclude options and the cash pseudo-security
        security_filter = "S.security_type NOT IN (?, ?)"
        params = tuple(account_ids) + (SecurityType.OPTION, SecurityType.CASH)

    final_sql = f"""
    SELECT DISTINCT
        T.symbol
    FROM trades T
    JOIN securities S ON T.symbol = S.symbol
    WHERE T.account_id IN ({account_placeholders})
    AND {security_filter}
    ORDER BY T.symbol;
    """
    _logger.debug("Generated SQL statement: %s", final_sql)

    # Execute the query
    result = DATABASE_CONNECTION.execute(final_sql, params).fetchall()

    symbols = sorted({row[0] for row in result})
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

    if not symbols:
        # nothing to look up; an empty IN clause is a SQL syntax error
        return []

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
               account_ids: List[int],
               begin_date: date,
               end_date: date,
               ascending: bool = False) -> pl.DataFrame:
    """
    Query the Trades table for the selected security symbols and accounts.

    Arguments:
        symbols -- a list of security symbols to query trades for.
        account_ids -- a list of account IDs to query trades for.
        begin_date -- The begin date for which to retrieve trades
        end_date -- The end date for which to retrieve trades
        ascending -- Whether to sort the results in ascending order by date (default is False).

    Returns:
        A polars DataFrame containing the trades for the specified symbols and accounts.
    """
    # mark entry into the method
    _logger.debug(("Entering method get_trades with: ",
                   "symbols = %s ",
                   "account_ids = %s ",
                   "begin_date = %s ",
                   "end_date = %s ",
                   "ascending = %s"),
                   symbols, account_ids, begin_date, end_date, ascending,
                   )

    # Dynamically build the parameters list for the IN clauses
    account_placeholders = ', '.join(['?'] * len(account_ids))
    symbol_placeholders = ', '.join(['?'] * len(symbols))
    final_sql = f"""
    SELECT 
        T.symbol,
        S.security_name,
        S.security_type,
        T.trade_date,
        T.trade_type,
        T.quantity,
        T.price,
        T.fees
    FROM trades T
    JOIN securities S ON T.symbol = S.symbol
    WHERE T.account_id IN ({account_placeholders})
    AND T.symbol IN ({symbol_placeholders})
    AND T.trade_date BETWEEN ? AND ?;
    """

    # Execute the query and read the raw rows as a polars frame. Column values
    # are accessed by name (not position) so the result schema is derived from
    # the live database tables rather than a hard-coded column order.
    params = tuple(account_ids) + tuple(symbols) + (begin_date, end_date)
    raw = DATABASE_CONNECTION.execute(final_sql, params).pl()

    # Process the results into the presentation frame. The ``Amount`` column is
    # the signed dollar value of the trade (negative = money leaving the
    # account); option contracts are valued at 100 shares per contract.
    trades = []
    for row in raw.iter_rows(named=True):
        trade_amount = row["price"] * row["quantity"]

        # Option contracts are 100 shares per contract
        if row["security_type"] == SecurityType.OPTION:
            trade_amount *= 100

        # Negate the amount for the final 'Amount' column
        final_amount = -trade_amount

        trades.append({
            'Symbol': row["symbol"],
            'Date': row["trade_date"],
            'Type': row["trade_type"],
            'Quantity': row["quantity"],
            'Price': row["price"],
            'Amount': final_amount,
        })

    if not trades:
        # No trades found; return an empty frame with the presentation schema.
        return pl.DataFrame(
            schema={
                'Symbol': pl.String,
                'Date': pl.Date,
                'Type': pl.String,
                'Quantity': pl.Float64,
                'Price': pl.Float64,
                'Amount': pl.Float64,
            }
        )

    df = pl.DataFrame(trades)
    df = df.sort(by=['Date', 'Type'], descending=not ascending, maintain_order=True)
    return df


def get_cash_flows(account_id: int,
                   begin_date: date,
                   end_date: date,
                   trade_types: List[str]) -> pl.DataFrame:
    """
    Query the Trades table for net external cash flows per date.

    A cash flow is the signed dollar amount of a trade whose type is one of the
    given ``trade_types`` (e.g. deposits, withdrawals, dividends, fees). For
    cash-type rows the amount is stored in ``price`` with a ``quantity`` of 0;
    for position rows it is ``price * quantity``. The per-date sum is returned
    so callers can net these flows out of a return calculation.

    Arguments:
        account_id -- The ID of the account to retrieve cash flows for.
        begin_date -- The begin date for which to retrieve cash flows.
        end_date -- The end date for which to retrieve cash flows.
        trade_types -- A list of trade_type values to include in the sum.

    Returns:
        A polars DataFrame with columns ['trade_date', 'cash_flow'], one row per
        date that has at least one matching trade, sorted ascending by date.
    """
    # mark entry into the method
    _logger.debug(("Entering method get_cash_flows with: ",
                   "account_id = %s ",
                   "begin_date = %s ",
                   "end_date = %s ",
                   "trade_types = %s"),
                   account_id, begin_date, end_date, trade_types)

    if not trade_types:
        # no types requested; nothing to sum
        return pl.DataFrame(
            schema={"trade_date": pl.Date, "cash_flow": pl.Float64}
        )

    # Dynamically build the parameter list for the IN clause
    placeholders = ', '.join(['?'] * len(trade_types))
    final_sql = f"""
    SELECT
        trade_date,
        SUM(CASE WHEN quantity = 0 THEN price ELSE price * quantity END) AS cash_flow
    FROM trades
    WHERE account_id = ?
    AND trade_type IN ({placeholders})
    AND trade_date BETWEEN ? AND ?
    GROUP BY trade_date
    ORDER BY trade_date ASC;
    """

    params = (account_id, *tuple(trade_types), begin_date, end_date)

    # Convert the result directly to a polars frame. The column names and types
    # come from the database (including the empty case), so there is no hard-
    # coded schema to keep in sync with the trades table.
    return DATABASE_CONNECTION.execute(final_sql, params).pl()
