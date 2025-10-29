'''
Generate a portfolio performance page based on selected symbols
and other criteria.
'''
# Import necessary libraries
from datetime import date
import streamlit as st
import pandas as pd

# Import local modules
from core import get_security_symbols, get_trades

def filter_trades(symbols, trades, begin_date, end_date):
    """Filter trades based on selected symbols and date range."""
    filtered_trades = trades[
        (trades["Symbol"].isin(symbols)) &
        (trades["Date"] >= pd.to_datetime(begin_date).date()) &
        (trades["Date"] <= pd.to_datetime(end_date).date())
    ]
    return filtered_trades

# configure the page layout
st.set_page_config(layout="wide")

# page subheader
st.subheader("Detail Performance Analysis")

# collect user inputs
# begin and end dates for the performance analysis
col1, col2 = st.columns(2)
with col1:
    selected_begin_date = st.date_input(
        "Begin Date:",
        value=date(date.today().year, 1, 1),
        label_visibility="collapsed",
    )
with col2:
    selected_end_date = st.date_input(
        "End Date:",
        value=date.today(),
        label_visibility="collapsed",
    )

# option to include options in the symbol list
include_options = st.checkbox("Include Options")
selected_symbols = st.multiselect(
    "Select Symbol(s):",
    label_visibility="collapsed",
    placeholder="Select Symbol(s)",
    options=get_security_symbols(include_options=include_options),
    )

if selected_symbols:
    selected_trades = filter_trades(
        selected_symbols,
        get_trades(symbols=selected_symbols),
        selected_begin_date,
        selected_end_date,
    )

    st.table(selected_trades)
    st.subheader(f"Total Gain/Loss: ${selected_trades['Amount'].sum():,.2f}")
