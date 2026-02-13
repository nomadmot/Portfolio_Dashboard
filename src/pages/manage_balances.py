"""
This page allows users to manage their daily balances.
It displays a dataframe of balance history for a specific account.
"""
from datetime import date
import streamlit as st
import sqlalchemy.exc

from core import (
    get_account,
    get_period_dates,
    get_balance_history,
    update_daily_balance,
    delete_daily_balance
)
from core import Periods
from utility import get_status_message_component

# local constants
_STATUS_MESSAGE_COMPONENT_KEY = "manage-balances-status-message"
_DAILY_BALANCE_TABLE = "daily_balance_table"
_UPDATE_BALANCE = "update_balance_session_key"
_UPDATE_DATE = "update_date_session_key"


# initialize data variables
from_date, to_date = get_period_dates(Periods.ALL)
history = get_balance_history(account_id=1,
                              from_date=from_date,
                              to_date=to_date,
                              #period=Periods.ALL,
                              ascending=False)

# if a row is selected, retrieve the date and balance
selected_row = st.session_state.get(_DAILY_BALANCE_TABLE)
if selected_row is not None and selected_row != [] and selected_row["selection"]["rows"] != []:
    selected_row = selected_row["selection"]["rows"][0]
    # set the values for the update date and balance widgets
    st.session_state[_UPDATE_DATE] = history.iloc[selected_row]["date"]
    st.session_state[_UPDATE_BALANCE] = float(history.iloc[selected_row]["balance"])
# if the update fate is not set, initialize it to today's date
elif _UPDATE_DATE not in st.session_state:
    st.session_state[_UPDATE_DATE] = date.today()

# configure the page layout
st.set_page_config(layout="centered")

# header elements for the page
st.title(f"Manage Daily Balances for Account {get_account(1).name}")

# create the status message component
status_message = get_status_message_component(
                                            _STATUS_MESSAGE_COMPONENT_KEY,
                                            "Status messages will appear here"
                                            )

# add user inputwidgets for maintaining balances to the sidebar
with st.sidebar:
    status_message.render()
    update_date = st.date_input("Select Date",
                    value=st.session_state.get(_UPDATE_DATE),
                    help="Select the date for which you want to manage the balance",
                    )
    update_balance = st.number_input("Daily Balance",
                    value=st.session_state.get(_UPDATE_BALANCE),
                    placeholder="Balance Amount",
                    step=0.01,
                    format="%.2f",
                    help="Enter the daily balance amount",
                    )
    st.caption("Update Database",
                help="Click the buttons to update the database "
                     "with the new balance or delete an existing balance",
                )

    # line up the database update buttons horizontally
    with st.container(horizontal=True, width="stretch"):
        # button to update the balance in the database
        update_record = st.button("Update",
                        help="Click to update the database with the new balance",
                )
        # button to delete the balance for the selected date
        delete_record = st.button("Delete",
                        help="Click to delete the balance for the selected date",
                )

# display the balance history for a specific account
daily_balance_table = st.dataframe(
            history,
            key=_DAILY_BALANCE_TABLE,
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
    if update_balance is not None and update_date is not None:
        try:
            update_daily_balance(1, update_balance, update_date)
        except ValueError as e:
            status_message.set_status_message(
                                            st.warning,
                                            str(e),
                                            "⚠️"
                                            )
        except sqlalchemy.exc.IntegrityError as e:
            status_message.set_status_message(
                                            st.warning,
                                            "The balance for this date already exists",
                                            "⚠️"
                                            )
        except sqlalchemy.exc.SQLAlchemyError as e:
            status_message.set_status_message(
                                            st.error,
                                            f"Unexpected SQL error: {str(e)}",
                                            "❗"
                                            )
        else:
            # if the update is successful, display a success message and refresh the dataframe
            status_message.set_status_message(
                                        st.success,
                                        f"Balance for {update_date} updated to"
                                        f" {update_balance:.2f} successfully!",
                                        "✅"
                                        )
            # rerun now to display the results of the operatio
            st.rerun()

    # handle the delete button click
if delete_record:
    if update_date is not None:
        try:
            delete_daily_balance(1, update_date)
        except ValueError as e:
            status_message.set_status_message(
                                        st.warning,
                                        str(e),
                                        "⚠️"
                                        )
        except sqlalchemy.exc.SQLAlchemyError as e:
            status_message.set_status_message(
                                        st.error,
                                        f"Unexpected SQL error: {str(e)}",
                                        "❗"
                                        )

        else:
            # if the update is successful, display a success message
            status_message.set_status_message(
                                        st.success,
                                        f"Balance for {update_date} deleted successfully!",
                                        "✅"
                                        )
            # rerun now to display the results of the operatio
            st.rerun()

# clear the status message
status_message.clear_status_message()
