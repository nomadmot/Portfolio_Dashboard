"""
Routines for accessing and manipulating the portfolio database.
"""
# Import necessary libraries
from datetime import date, datetime as dt
from typing import Optional
from sqlalchemy.orm import Session

# Import local modules
from models.portfolio import DailyBalance, Account
import config

# function to update the portfolio balance for a specified account and day
def update_daily_balance(
    balance_amount: float,
    account_id: int,
    balance_date: date
) -> None:
    """
    Update the daily balance for a given account on a specific date.

    :param balance: The current balance of the account.
    :param account: The account number to update.
    :param date: The date for which the balance is being updated.
    """
    # ensure the account exists and get the account name
    with Session(config.DB_ENGINE) as session:
        account: Optional[Account] = session.get(Account, account_id)
        if not account:
            raise ValueError(f"Account with ID {account_id} does not exist.")
        account_name: str = account.name
        session.close()

    print(f"Adding daily balance for {account_name} on {balance_date} with balance {balance_amount}")
    
    # create a new DailyBalance object
    daily_balance: DailyBalance = DailyBalance(
        balance=balance_amount,
        account_id=account_id,
        date=balance_date
    )
    print(f"Daily balance object created: {daily_balance}")

    # # save the daily balance to the database
    # with Session(config.DB_ENGINE) as session:
    #     session.add(daily_balance)
    #     session.commit()
    #     print("Daily balance updated successfully.")

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
    # ensure the account exists and get the account name
    with Session(config.DB_ENGINE) as session:
        account: Optional[Account] = session.get(Account, account_id)
        if not account:
            raise ValueError(f"Account with ID {account_id} does not exist.")
        account_name: str = account.name
        session.close()

    with Session(config.DB_ENGINE) as session:
        daily_balance: Optional[DailyBalance] = session.query(DailyBalance).filter(
            DailyBalance.account_id == account_id,
            DailyBalance.date == balance_date
        ).first()
        if not daily_balance:
            raise ValueError(f"No daily balance found for account {account_name} on {balance_date}")
        session.delete(daily_balance)
        session.commit()
        print(f"Daily balance for account {account_name} on {balance_date} deleted successfully.")

#update_daily_balance(balance_amount=1000.0, account_id=1, balance_date=date.today())
