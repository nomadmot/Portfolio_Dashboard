"""
Routines for accessing and manipulating the portfolio database.
"""
# Import standard libraries
from datetime import date
# from typing import Optional
# from sqlalchemy.orm import Session

# Import 3rd party libraries
import duckdb

# Import local modules
from utility import get_logger, DATABASE_CONNECTION
# from schemas.portfolio import DailyBalance, Account
from schemas import DailyBalance

# # create the logger for the module
# _logger = get_logger(__name__)
# _logger.debug("In module: %s\n\tfile: %s", __name__, __file__)

# core/manage_portfolio_balances.py

# --- Imports ---
# from datetime import date
# from typing import List
# import duckdb # Direct import for the connection object
# from utility.database import DATABASE_CONNECTION # Import the centralized connection
# from utility.logger import get_logger # Assuming logger utility exists
# from schemas import DailyBalanceBase, AccountBase # Import Pydantic schemas

# Initialize logger for this module
_logger = get_logger(__name__)
_logger.debug("In module: %s", __name__)

# --- Function to Update Daily Balance (STRICT MODE) ---
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
        # BEGIN TRANSACTION
        DATABASE_CONNECTION.execute("BEGIN;")

        # --- A. Check Account Existence ---
        account_check_sql = "SELECT count(*) FROM accounts WHERE account_id = ?"
        account_count = DATABASE_CONNECTION.execute(account_check_sql, (account_id,)).fetchone()[0]

        if account_count == 0:
            # Raise a specific ValueError for business logic failure
            raise ValueError(f"Account with ID {account_id} does not exist.")

        # --- B. Check for Existing Record (The strict check) ---
        check_existence_sql = """
        SELECT count(*) FROM daily_balances 
        WHERE account_id = ? AND date = ?;
        """
        existing_count = DATABASE_CONNECTION.execute(
            check_existence_sql,
            (account_id, balance_date)).fetchone()[0]

        if existing_count > 0:
            # Raise a specific ValueError for business logic failure
            raise ValueError(
                f"Balance record already exists for Account {account_id} on {balance_date}. "
                "Update is disallowed in strict mode."
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
        account_count = DATABASE_CONNECTION.execute(account_check_sql, (account_id,)).fetchone()[0]

        if account_count == 0:
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
    # No general 'except Exception' block here.

# # function to update the portfolio balance for a specified account and day
# def update_daily_balance(
#     account_id: int,
#     balance_amount: float,
#     balance_date: date
# ) -> None:
#     """
#     Update the daily balance for a given account on a specific date.

#     :param balance: The current balance of the account.
#     :param account: The account number to update.
#     :param date: The date for which the balance is being updated.
#     """

#     # mark entry into the function
#     logger.debug(
#         "entering update_daily_balance, account_id: %s balance_date: %s balance_amount %s",
#         account_id,
#         balance_date,
#         balance_amount
#         )

#     # check if the input balance date and amount are valid.
#     if balance_date is None or balance_amount is None:
#         raise ValueError("Please select a date and enter a balance amount.")
#     if balance_amount < 0:
#         raise ValueError("Balance cannot be negative.")

#     # create a new DailyBalance object
#     daily_balance: DailyBalance = DailyBalance(
#         balance=balance_amount,
#         account_id=account_id,
#         date=balance_date
#     )
#     logger.debug(
#         "Daily balance object created: %s",
#         daily_balance
#         )

#     # save the daily balance to the database
#     with Session(DATABASE_ENGINE) as session:
#         session.add(daily_balance)
#         session.commit()

#     logger.info("Daily balance for account %s updated successfully - "
#                 "balance_date: %s balance_amount %s",
#                 account_id,
#                 balance_date,
#                 balance_amount
#                 )


# # function to delete the daily balance for a specified account and day
# def delete_daily_balance(
#     account_id: int,
#     balance_date: date
# ) -> None:
#     """
#     Delete the daily balance for a given account on a specific date.

#     :param account_id: The ID of the account to delete the balance for.
#     :param date: The date for which the balance is being deleted.
#     """

#     # mark entry into the function
#     logger.debug(
#         "entering delete_daily_balance, account_id: %s balance_date: %s",
#         account_id,
#         balance_date,
#         )

#     # ensure the account exists and get the account name
#     with Session(DATABASE_ENGINE) as session:
#         account: Optional[Account] = session.get(Account, account_id)
#         if not account:
#             raise ValueError(
#                 f"Account with ID {account_id} does not exist."
#                 )
#         #account_name: str = account.name
#         session.close()

#     with Session(DATABASE_ENGINE) as session:
#         daily_balance: Optional[DailyBalance] = session.query(DailyBalance).filter(
#             DailyBalance.account_id == account_id,
#             DailyBalance.date == balance_date
#         ).first()
#         if not daily_balance:
#             raise ValueError(
#                 f"No daily balance found for account {account_id} on {balance_date}"
#                 )
#         session.delete(daily_balance)
#         session.commit()
#         logger.info(
#             "Daily balance for account %s on %s deleted successfully.",
#             account_id,
#             balance_date
#             )
