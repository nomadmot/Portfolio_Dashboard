"""
Routines for accessing and manipulating the portfolio database.
"""
# Import standard libraries
from datetime import date

# Import 3rd party libraries
import duckdb

# Import local modules
from utility import get_logger, DATABASE_CONNECTION
from schemas import DailyBalance

# Initialize logger for this module
_logger = get_logger(__name__)
_logger.debug("In module: %s", __name__)

# --- Function to Update Daily Balance ---
def update_daily_balance(
    account_id: int,
    balance_amount: float,
    balance_date: date
) -> None:
    """
    Update the daily balance for a given account on a specific date using pure DuckDB.
    ***STRICT MODE: Throws an exception if a record for (date, account_id) already exists.***

    :param balance: The current balance of the account.
    :param account: The account number to update.
    :param date: The date for which the balance is being updated.
    """

        # 1. Input Validation (Using Pydantic for safety)
    try:
        _ = DailyBalance(
            date=balance_date,
            account_id=account_id,
            balance=balance_amount
        )
    except Exception as e:
        # Catching Pydantic validation errors specifically
        raise ValueError(f"Input validation failed: {e}") from e

    # 2. Transaction Management (Manual BEGIN/COMMIT/ROLLBACK)
    try:
        # Start a transaction manually to ensure atomicity
        DATABASE_CONNECTION.execute("BEGIN;")

        # --- A. Check Account Existence ---
        account_check_sql = "SELECT count(*) FROM accounts WHERE account_id = ?"
        account_count = DATABASE_CONNECTION.execute(account_check_sql, (account_id,)).fetchone()

        if account_count is None:
            # Raise a specific ValueError for business logic failure
            raise ValueError(f"Account with ID {account_id} does not exist.")

        # --- B. Check for Existing Record (The strict check) ---
        check_existence_sql = """
        SELECT count(*) FROM daily_balances 
        WHERE account_id = ? AND date = ?;
        """
        existing_count = DATABASE_CONNECTION.execute(
            check_existence_sql,
            (account_id, balance_date)).fetchone()

        if existing_count is not None and existing_count[0] > 0:
            # Raise a specific ValueError for business logic failure
            raise ValueError(
                f"Balance record already exists for Account {account_id} on {balance_date}. "
            )

        # --- C. Write New Record ---
        insert_sql = """
        INSERT INTO daily_balances (date, account_id, balance) 
        VALUES (?, ?, ?);
        """
        # Execute the write operation using the connection object
        DATABASE_CONNECTION.execute(insert_sql, (balance_date, account_id, balance_amount))

        # COMMIT TRANSACTION
        DATABASE_CONNECTION.execute("COMMIT;")

        _logger.info(
            "Daily balance for account %s on %s successfully created. Balance: %s",
            account_id,
            balance_date,
            balance_amount
        )

    except duckdb.Error as e:
        # ROLLBACK on DB error
        DATABASE_CONNECTION.execute("ROLLBACK;")
        _logger.error("DuckDB Transaction Failed:", exc_info=True)
        raise RuntimeError(f"Database transaction failed: {e}") from e
    except ValueError as e:
        # ROLLBACK on business logic error
        DATABASE_CONNECTION.execute("ROLLBACK;")
        _logger.warning("Balance update failed due to business logic error: %s", e)
        raise e
    # No general 'except Exception' block here.

# --- Function to Delete Daily Balance ---
def delete_daily_balance(
    account_id: int,
    balance_date: date
) -> None:
    """
    Delete the daily balance for a given account on a specific date using pure DuckDB.
    """
    _logger.debug("Entering delete_daily_balance, account_id: %s balance_date: %s",
                 account_id,
                 balance_date)

    try:
        # BEGIN TRANSACTION
        DATABASE_CONNECTION.execute("BEGIN;")

        # --- A. Check Account Existence (Validation) ---
        account_check_sql = "SELECT count(*) FROM accounts WHERE account_id = ?"
        account_count = DATABASE_CONNECTION.execute(account_check_sql, (account_id,)).fetchone()

        if account_count is None:
            # Raise a specific ValueError for business logic failure
            raise ValueError(f"Account with ID {account_id} does not exist.")

        # --- B. Delete Operation ---
        delete_sql = """
        DELETE FROM daily_balances
        WHERE account_id = ? AND date = ?;
        """

        # Execute the delete command
        rows_deleted = DATABASE_CONNECTION.execute(delete_sql, (account_id, balance_date)).rowcount

        if rows_deleted == 0:
            # Raise a specific error if nothing was deleted
            raise ValueError(
                f"No daily balance record found for account {account_id} "
                f"on {balance_date}. Nothing to delete."
            )

        # COMMIT TRANSACTION
        DATABASE_CONNECTION.execute("COMMIT;")

        _logger.info(
            "Daily balance for account %s on %s deleted successfully. Rows affected: %d.",
            account_id,
            balance_date,
            rows_deleted
        )

    except duckdb.Error as e:
        # ROLLBACK on DB error
        DATABASE_CONNECTION.execute("ROLLBACK;")
        _logger.error("DuckDB Transaction Failed:", exc_info=True)
        raise RuntimeError(f"Database transaction failed: {e}") from e
    except ValueError as e:
        # ROLLBACK on business logic error
        DATABASE_CONNECTION.execute("ROLLBACK;")
        _logger.warning("Balance deletion failed due to business logic error: %s", e)
        raise e
