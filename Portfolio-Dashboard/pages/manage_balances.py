"""
This page allows users to manage their daily balances.
It displays a dataframe of balance history for a specific account.
"""
import streamlit as st

from utility.query_portfolio import get_balance_history

# header elements for the page
st.subheader("Manage Daily Balances")

# widgets for adding and maintaining balances
update_container = st.container(border=True)
# layout will be in a single row
col1, col2, col3 = update_container.columns(3)
with col1:
    update_date = st.date_input("Select Date",
                    help="Select the date for which you want to manage the balance",
                    key="balance_date_input"
                    )
with col2:
    update_balance = st.number_input("Daily Balance",
                    min_value=0.0,
                    step=0.01,
                    format="%.2f",
                    help="Enter the daily balance amount",
                    key="daily_balance_input"
                    )
with col3:
    st.caption("Update Balance",
                help="Click the button to update the database with the new balance",
                )
    # button to update the balance in the database
    update_button = st.button("Submit",
                    help="Click to update the database with the new balance",
                    key="update_balance_button"
                    )
    
update_message = update_container.empty()
update_message.info("This area will display messages related to balance updates" )

# display the balance history for a specific account
history = get_balance_history(account_id=1)
history.sort_values(by="date", ascending=False, inplace=True)
st.dataframe(history,
             hide_index=True,
             column_config={
                 "date": st.column_config.DateColumn("Date"),
                 "balance": st.column_config.NumberColumn("Balance", format="%.2f"),
             },
             )

# function to check daily balance input data
def check_daily_balance_input(date, balance) -> bool:
    """
    check if the daily balance date and balance are valid.

    Arguments:
        date -- the selected date for the balance
        balance -- the input balance amount

    Returns:
        True if the input is valid, False otherwise
    """
    if date is None or balance is None:
        st.error("Please select a date and enter a balance amount.")
        return False
    if balance < 0:
        st.error("Balance cannot be negative.")
        return False
    return True

# handle the update button click
if update_button:
    if check_daily_balance_input(update_date, update_balance):
        # Here you would typically call a function to update the database
        # For demonstration, we will just show a success message
        update_message.success(
            f"Balance for {update_date} updated to {update_balance:.2f} successfully!",
            icon="✅"
        )
    else:
        update_message.error("Failed to update balance. Please check your input.", icon="❌")
