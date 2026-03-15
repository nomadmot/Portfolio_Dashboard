"""
This page allows users to manage their daily balances.
It displays a dataframe of balance history for a specific account.
"""
# import standard libraries
from datetime import date
from pathlib import Path

# import 3rd party libraries
import streamlit as st
import sqlalchemy.exc

# local imports
from core import (Periods,
                  get_account,
                  get_period_dates,
                  get_balance_history,
                  update_daily_balance,
                  delete_daily_balance,
)
from utility import (get_status_message_component,
                     get_logger,
                     StatusType as stat,
                     )

# initialize the logger
file_stem = Path(__file__).stem
logger_name = f"pages.{file_stem}"
logger = get_logger(logger_name)
# mark entry into the module
logger.debug("In module %s", logger_name)

# local constants
_STATUS_MESSAGE_COMPONENT_KEY = "manage-balances-status-message"
_DAILY_BALANCE_TABLE_SESSION_KEY = "daily_balance_table"
_UPDATE_BALANCE_SESSION_KEY = "update_balance_session_key"
_UPDATE_DATE_SESSION_KEY = "update_date_session_key"


# initialize balance history
from_date, to_date = get_period_dates(Periods.ALL)
history = get_balance_history(account_id=1,
                              begin_date=from_date,
                              end_date=to_date,
                              ascending=False)

# if a row is selected, retrieve the date and balance
selected_row = st.session_state.get(_DAILY_BALANCE_TABLE_SESSION_KEY)
if selected_row is not None and selected_row != [] and selected_row["selection"]["rows"] != []:
    selected_row = selected_row["selection"]["rows"][0]
    # set the values for the update date and balance widgets
    st.session_state[_UPDATE_DATE_SESSION_KEY] = history.iloc[selected_row]["date"]
    st.session_state[_UPDATE_BALANCE_SESSION_KEY] = float(history.iloc[selected_row]["balance"])
# if the update date is not set, initialize it to today's date
elif _UPDATE_DATE_SESSION_KEY not in st.session_state:
    st.session_state[_UPDATE_DATE_SESSION_KEY] = date.today()

# header elements for the page
st.title(f"Manage Daily Balances for Account {get_account(1).name}")

# create the status message component
status_message = get_status_message_component(_STATUS_MESSAGE_COMPONENT_KEY)

# add user input widgets for maintaining balances to the sidebar
with st.sidebar:
    update_date = st.date_input("Select Date",
                    key=_UPDATE_DATE_SESSION_KEY,
                    help="Select the date for which you want to manage the balance",
                    )
    update_balance = st.number_input("Daily Balance",
                    key=_UPDATE_BALANCE_SESSION_KEY,
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


# handle the update button click
if update_record:
    if update_balance is not None and update_date is not None:
        try:
            update_daily_balance(1, update_balance, update_date)
        except ValueError as e:
            status_message.set_status_message(
                                            stat.WARNING,
                                            str(e),
                                            )
        except sqlalchemy.exc.IntegrityError as e:
            status_message.set_status_message(
                                            stat.WARNING,
                                            "The balance for this date already exists",
                                            )
        except sqlalchemy.exc.SQLAlchemyError as e:
            status_message.set_status_message(
                                            stat.ERROR,
                                            f"Unexpected SQL error: {str(e)}",
                                            )
        else:
            # if the update is successful, display a success message and refresh the dataframe
            status_message.set_status_message(
                                        stat.SUCCESS,
                                        f"Balance for {update_date} updated to"
                                        f" {update_balance:.2f} successfully!",
                                        )

# handle the delete button click
if delete_record:
    if update_date is not None:
        try:
            delete_daily_balance(1, update_date)
        except ValueError as e:
            status_message.set_status_message(
                                        stat.WARNING,
                                        str(e),
                                        )
        except sqlalchemy.exc.SQLAlchemyError as e:
            status_message.set_status_message(
                                        stat.ERROR,
                                        f"Unexpected SQL error: {str(e)}",
                                        )

        else:
            # if the update is successful, display a success message
            status_message.set_status_message(
                                        stat.SUCCESS,
                                        f"Balance for {update_date} deleted successfully!",
                                        )

# fetch the updated balance history
from_date, to_date = get_period_dates(Periods.ALL)
history = get_balance_history(account_id=1,
                              begin_date=from_date,
                              end_date=to_date,
                              ascending=False)

# display the balance history for a specific account
daily_balance_table = st.dataframe(
            history,
            key=_DAILY_BALANCE_TABLE_SESSION_KEY,
            width=500,
            hide_index=True,
            selection_mode="single-row",
            on_select="rerun",
            column_config={
                "date": st.column_config.DateColumn("Date"),
                "balance": st.column_config.NumberColumn("Balance", format="accounting"),
                },
            )

# display any status messages
status_message.show_status_messages()
