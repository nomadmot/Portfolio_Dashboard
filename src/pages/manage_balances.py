"""
This page allows users to manage their daily balances.
It displays a dataframe of balance history for a specific account.
"""
from datetime import date
import streamlit as st
import sqlalchemy.exc

from data import (
    get_balance_history,
    update_daily_balance,
    delete_daily_balance
)

# constants for streamlit session state
DAILY_BALANCE_TABLE = "daily_balance_table"
UPDATE_BALANCE = "update_balance"
UPDATE_DATE = "update_date"
UPDATE_BALANCE_BUTTON = "update_balance_button"
DELETE_BALANCE_BUTTON = "delete_balance_button"

# initialize data variables
history = get_balance_history(account_id=1)
# sort the history by date in descending order
history.sort_values(by="date", ascending=False, inplace=True)
history.reset_index(drop=True, inplace=True)

# if a row is selected, retrieve the date and balance
selected_row = st.session_state.get("daily_balance_table")
if selected_row is not None and selected_row != [] and selected_row["selection"]["rows"] != []:
    selected_row = selected_row["selection"]["rows"][0]
    # set the values for the update date and balance widgets
    st.session_state[UPDATE_DATE] = history.iloc[selected_row]["date"]
    st.session_state[UPDATE_BALANCE] = float(history.iloc[selected_row]["balance"])
# if the update fate is not set, initialize it to today's date
elif UPDATE_DATE not in st.session_state:
    st.session_state[UPDATE_DATE] = date.today()

# configure the page layout
st.set_page_config(layout="centered")

# header elements for the page
st.subheader("Manage Daily Balances")

# widgets for adding and maintaining balances
update_container = st.container(
                    horizontal_alignment="center",
                    border=True,
                    width=500,
                    )
with update_container:
    with update_container.container(horizontal=True):
        update_date = st.date_input("Select Date",
                        key=UPDATE_DATE,
                        value=None,
                        help="Select the date for which you want to manage the balance",
                        )
        update_balance = st.number_input("Daily Balance",
                        key=UPDATE_BALANCE,
                        value=None,
                        placeholder="Balance Amount",
                        step=0.01,
                        format="%.2f",
                        help="Enter the daily balance amount",
                        )
    st.caption("Update Database",
                help="Click the buttons to update the database /" \
                    "with the new balance or delete an existing balance",
                )

    # line up the database update buttons horizontally
    with st.container(horizontal=True):
        # button to update the balance in the database
        update_record = st.button("Update",
                        help="Click to update the database with the new balance",
                        key=UPDATE_BALANCE_BUTTON,
                        )
        # button to delete the balance for the selected date
        delete_record = st.button("Delete",
                        help="Click to delete the balance for the selected date",
                        key=DELETE_BALANCE_BUTTON,
                        )

    # message area for displaying update results
    update_message = st.empty()
    update_message.info("This area will display messages related to balance updates")

# display the balance history for a specific account
daily_balance_table = st.dataframe(
            history,
            key=DAILY_BALANCE_TABLE,
            width=500,
            hide_index=True,
            selection_mode="single-row",
            on_select="rerun",
            column_config={
                "date": st.column_config.DateColumn("Date"),
                "balance": st.column_config.NumberColumn("Balance", format="accounting"),
                },
            )

# handle the update button click
if update_record:
    try:
        update_daily_balance(1, update_balance, update_date)
    except ValueError as e:
        update_message.warning(str(e), icon="⚠️")
    except sqlalchemy.exc.IntegrityError as e:
        update_message.warning(
            "The balance for this date already exists",
            icon="⚠️"
            )
    except  sqlalchemy.exc.SQLAlchemyError as e:
        update_message.error(
            f"Unexpected SQL error: {str(e)}",
            icon="❗"
            )
    else:
        # if the update is successful, display a success message and refresh the dataframe
        update_message.success(
            f"Balance for {update_date} updated to {update_balance:.2f} successfully!",
            icon="✅"
        )
        st.rerun()

    # handle the delete button click
if delete_record:
    try:
        delete_daily_balance(1, update_date)
    except ValueError as e:
        update_message.warning(str(e), icon="⚠️")
    except  sqlalchemy.exc.SQLAlchemyError as e:
        update_message.error(
            f"Unexpected SQL error: {str(e)}",
            icon="❗"
            )
    else:
        # if the update is successful, display a success message
        update_message.success(
            f"Balance for {update_date} deleted successfully!",
            icon="✅"
        )
        st.rerun()
