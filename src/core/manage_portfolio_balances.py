"""
Routines for accessing and manipulating the portfolio database.
"""
# Import necessary libraries
from datetime import date
from typing import Optional
import streamlit as st
import streamlit.logger
from sqlalchemy.orm import Session

# Import local modules
from models.portfolio import DailyBalance, Account
from config import DATABASE_ENGINE

# Initialize the logger
logger = streamlit.logger.get_logger(st.__name__)
# mark entry into the module
logger.debug("Entering manage_daily_balances module")


# function to update the portfolio balance for a specified account and day
def update_daily_balance(
    account_id: int,
    balance_amount: float,
    balance_date: date
) -> None:
    """
    Update the daily balance for a given account on a specific date.

    :param balance: The current balance of the account.
    :param account: The account number to update.
    :param date: The date for which the balance is being updated.
    """

    # mark entry into the function
    logger.debug(
        "entering update_daily_balance, account_id: %s balance_date: %s balance_amount %s",
        account_id,
        balance_date,
        balance_amount
        )

    # check if the input balance date and amount are valid.
    if balance_date is None or balance_amount is None:
        raise ValueError("Please select a date and enter a balance amount.")
    if balance_amount < 0:
        raise ValueError("Balance cannot be negative.")

    # create a new DailyBalance object
    daily_balance: DailyBalance = DailyBalance(
        balance=balance_amount,
        account_id=account_id,
        date=balance_date
    )
    logger.debug(
        "Daily balance object created: %s",
        daily_balance
        )

    # save the daily balance to the database
    with Session(DATABASE_ENGINE) as session:
        session.add(daily_balance)
        session.commit()

    logger.info("Daily balance updated successfully")


# function to delete the daily balance for a specified account and day
def delete_daily_balance(
    account_id: int,
    balance_date: date
) -> None:
    """
    Delete the daily balance for a given account on a specific date.

    :param account_id: The ID of the account to delete the balance for.
    :param date: The date for which the balance is being deleted.
    """

    # mark entry into the function
    logger.debug(
        "entering delete_daily_balance, account_id: %s balance_date: %s",
        account_id,
        balance_date,
        )

    # ensure the account exists and get the account name
    with Session(DATABASE_ENGINE) as session:
        account: Optional[Account] = session.get(Account, account_id)
        if not account:
            raise ValueError(
                f"Account with ID {account_id} does not exist."
                )
        #account_name: str = account.name
        session.close()

    with Session(DATABASE_ENGINE) as session:
        daily_balance: Optional[DailyBalance] = session.query(DailyBalance).filter(
            DailyBalance.account_id == account_id,
            DailyBalance.date == balance_date
        ).first()
        if not daily_balance:
            raise ValueError(
                f"No daily balance found for account {account_id} on {balance_date}"
                )
        session.delete(daily_balance)
        session.commit()
        logger.info(
            "Daily balance for account %s on %s deleted successfully.",
            account_id,
            balance_date
            )

#update_daily_balance(balance_amount=1000.0, account_id=1, balance_date=date.today())
